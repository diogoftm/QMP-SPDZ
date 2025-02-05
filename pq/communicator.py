import threading
import socket
import select
import time
import json
from collections import defaultdict, deque


class Communicator:
    def __init__(self, my_ip: str, my_port: int) -> None:
        self.my_ip = my_ip
        self.my_port = my_port
        self._msg_id = 0
        self._message_queues = defaultdict(deque)
        self._running = threading.Event()

    @staticmethod
    def is_acked(msg: dict, msg_id: int):
        ack = msg.get("acked")
        if msg and ack and ack == msg_id:
            return True
        return False

    def _receive_messages(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.my_ip, self.my_port))
            sock.listen(5)
            while self._running.is_set():
                readable, _, _ = select.select([sock], [], [], 0.1)
                for readable_socket in readable:
                    client_socket, addr = readable_socket.accept()
                    data = client_socket.recv(1024*4).decode("utf-8")
                    client_socket.close()
                    session = json.loads(data).get("session_id")
                    self._message_queues[(addr[0], session)].append(data)

    def _get_next_msg_id(self):
        self._msg_id += 1
        return self._msg_id

    def wait_for_ack(
        self, period: float, max_tries: int, msg_id: int, other_sae_ip: str
    ):
        rcv_msg = self.wait_for_message(period, max_tries, other_sae_ip)
        if not Communicator.is_acked(rcv_msg, msg_id):
            raise TimeoutError()

    def send_message(
        self,
        message: str,
        dst_ip: str,
        dst_port: int,
        session: str,
        wait_for_ack: bool = False,
        timeout: int = 5,
    ) -> int:
        msg_id = self._get_next_msg_id()
        message["msg_id"] = msg_id
        message["session_id"] = session
        message = json.dumps(message)
        start_time = time.time()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            while time.time() - start_time < timeout:
                try:
                    sock.connect((dst_ip, dst_port))
                except:
                    continue
                sock.send(message.encode("utf-8"))
                if wait_for_ack:
                    self.wait_for_ack(0.5, 10, msg_id, dst_ip)
                return msg_id
            raise TimeoutError()

    def wait_for_message(self, period: float, max_tries: int, other_sae_ip: str, session: str) -> str:
        tries = 0
        while max_tries == -1 or tries < max_tries:
            if self.has_messages_from(other_sae_ip, session):
                return json.loads(self.get_message_from(other_sae_ip, session))
            time.sleep(period)
            tries += 1
        raise TimeoutError()

    def start_listening(self):
        self._running.set()
        threading.Thread(target=self._receive_messages).start()

    def stop_listening(self):
        self._running.clear()

    def has_messages_from(self, ip, session):
        return bool(self._message_queues[(ip, session)])

    def get_message_from(self, ip, session):
        return self._message_queues[(ip, session)].popleft() if self._message_queues[(ip, session)] else None
