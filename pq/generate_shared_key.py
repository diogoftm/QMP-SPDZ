import interface
from communicator import Communicator

import os
import sys
import base64

TMP = "/tmp/"
INITIAL_TIMEOUT = 60

def get_file_content(filename: str) -> bytes:
    with open(filename, "rb") as f:
       content = f.read() 
    return content

def save_to_file(filename: str, content: str) -> None:
    with open(filename, "wb") as f:
       f.write(content)

def delete_list_of_files(l: list[str]) -> None:
    for f in l:
        try:
            os.remove(f)
        except OSError:
            pass

def read_parties_file(parties_file: str, my_party_number: int):
    my_ip = None
    my_port = None
    peers = []
    
    with open(parties_file, "r") as f:
        lines = f.readlines()
    
    if int(my_party_number) >= len(lines):
        print(f"Invalid party number: {my_party_number} >= {len(lines)}", file=sys.stderr)
        sys.exit(-1)
    
    for i, line in enumerate(lines):
        t = line.split(" ")
        if i == my_party_number:
            my_ip, my_port = t[0].split(":")
        else:
            peer_ip, peer_port = t[0].split(":")
            peers.append([peer_ip, int(peer_port)])
    
    return my_ip, int(my_port), peers
    
def set_psk_parties_file(file_path, line_number, text_to_append):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    if line_number < 0 or line_number > len(lines)-1:
        raise ValueError("Invalid line number")

    # Append text at the end of the specified line
    padding_n = 4 - len(lines[line_number].split(' '))
    padding_str = ""
    for _ in range(padding_n):
        padding_str += " -"
    padding_str += " " 
    
    trailing_str = lines[line_number].rstrip() if padding_n > 0 else " ".join(lines[line_number].rstrip().split(" ")[:-1])
    
    lines[line_number] = trailing_str + padding_str + text_to_append + '\n'
    with open(file_path, 'w') as file:
        file.writelines(lines)
        
def combine_keys(k0: str, k1: str) -> str:
    k0 = base64.b64decode(k0)
    k1 = base64.b64decode(k1)
    result = bytes(x ^ y for x, y in zip(k0, k1))
    combined_key = base64.b64encode(result).decode("utf-8")
    return combined_key

def generate_key(c: Communicator, peer_ip: str, peer_port: int, session: str, master:bool = False, kem="mlkem") -> str:
    # generate ephemeral keys
    my_pub = os.path.join(TMP, f"{my_ip}{my_port}{peer_ip}_pub")
    my_priv = os.path.join(TMP, f"{my_ip}{my_port}{peer_ip}_priv")
    peer_pub = os.path.join(TMP, f"{my_ip}{my_port}{peer_ip}_peer_pub")
    interface.gen_keys(my_pub, my_priv)
    final_key = None
    
    if master:
        save_to_file(
            peer_pub,
            base64.b64decode(c.wait_for_message(0.1, INITIAL_TIMEOUT*10, peer_ip, session).get("pub_key").encode("utf-8"))
        )
        c.send_message({"pub_key": base64.b64encode(get_file_content(my_pub)).decode("utf-8")}, peer_ip, peer_port, session)
        ek0 = c.wait_for_message(0.1, 50, peer_ip, session).get("encaps_key")
        k0 = interface.decaps(ek0, my_priv, kem)
        k1, ek1 = interface.encaps(peer_pub, kem)
        c.send_message({"encaps_key": ek1}, peer_ip, peer_port, session)
        final_key = combine_keys(k0, k1)
    else:
        c.send_message({"pub_key": base64.b64encode(get_file_content(my_pub)).decode("utf-8")}, peer_ip, peer_port, session, timeout=INITIAL_TIMEOUT)
        save_to_file(
            peer_pub,
            base64.b64decode(c.wait_for_message(0.1, 50, peer_ip, session).get("pub_key").encode("utf-8"))
        )
        k0, ek0 = interface.encaps(peer_pub, kem)
        c.send_message({"encaps_key": ek0}, peer_ip, peer_port, session)
        ek1 = c.wait_for_message(0.1, 50, peer_ip, session).get("encaps_key")
        k1 = interface.decaps(ek1, my_priv, kem)
        final_key = combine_keys(k0, k1)
    
    delete_list_of_files([my_pub, my_priv, peer_pub])

    return final_key

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python3 {sys.argv[0]} <parties_file> <party_number>", file=sys.stderr)
        sys.exit(-1)
    
    my_n = int(sys.argv[2])
    my_ip, my_port, peers = read_parties_file(sys.argv[1], my_n)
    
    c = Communicator(
        my_ip=my_ip,
        my_port=my_port
    )
    c.start_listening()
    
    for i, peer in enumerate(peers):
        print(f"Performing key exchange with {peer[0]}:{peer[1]}")
        line_n = i if my_n > i else i + 1
        session_id = f"{my_n}{line_n}" if my_n <= i else f"{line_n}{my_n}"
        shared_key = generate_key(c, peer[0], peer[1], session_id, master=my_n <= i)
        set_psk_parties_file(sys.argv[1], line_n, shared_key)
    
    c.stop_listening()