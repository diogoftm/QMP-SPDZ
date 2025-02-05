import base64
import ctypes
import traceback
import os

KYBER_CIPHERTEXT_SIZE = (3 * 320) + 128

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
AVAILABLE_KEMS_SO = {
    "mlkem": os.path.join(SCRIPT_DIR, "mlkem_interface.so")
}

def load_interface_from_so(kem: str) -> ctypes.CDLL:
    """Loads the interface respective to the selected KEM.
    
    Load and setups the following two methods from the shared object:
        - uint8_t** gen_key_and_ciphertext(char *key_file_name);
        - char* get_key_from_ciphertext(char *ct, char *key_file_name);
        - int generate_keys(char* pub_filename, char* priv_filename);

    Args:
        kem (str): KEM algorithm to use.

    Returns:
        ctypes.CDDL: interface.
    """
    try:
        so = AVAILABLE_KEMS_SO.get(kem)
        if not so:
            return None
        lib = ctypes.CDLL(so)
        lib.get_key_from_ciphertext.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        lib.get_key_from_ciphertext.restype = ctypes.c_char_p
        lib.gen_key_and_ciphertext.argtypes = [
            ctypes.c_char_p,
        ]
        lib.gen_key_and_ciphertext.restype = ctypes.POINTER(
            ctypes.POINTER(ctypes.c_uint8)
        )
        lib.generate_keys.restype = ctypes.c_int
        lib.generate_keys.argtypes = [
            ctypes.c_char_p, ctypes.c_char_p
        ]
        return lib
    except:
        traceback.print_exc()
        return None
    
def gen_keys(pubic_key_filename: str, private_key_filename: str, kem: str = "mlkem") -> None:
    interface = load_interface_from_so(kem)
    if not interface:
        raise ValueError(f"{kem} not supported.")
    
    status = interface.generate_keys(
        bytes(pubic_key_filename, "utf-8"),
        bytes(private_key_filename, "utf-8")
    )
    
    if status != 0:
        raise RuntimeError("Unable to generate and save keys")

def encaps(public_key_file: str, kem: str = "mlkem") -> tuple[str, str]:
    """Generates a key and encapsulates it.

    Args:
        public_key_file (str): file containing the public key used for encapsulation.
        kem (str, optional): KEM algorithm to use. Defaults to "mlkem".

    Returns:
        tuple[str, str]: key and encapsulated key (both base64 encoded)
    """
    interface = load_interface_from_so(kem)
    if not interface:
        return None

    key_and_ciphertext = interface.gen_key_and_ciphertext(
        bytes(public_key_file, "utf-8"),
    )
    key = ctypes.cast(key_and_ciphertext[0], ctypes.c_char_p).value
    encapsulated_key_base64 = ctypes.cast(
        key_and_ciphertext[1], ctypes.c_char_p
    ).value.decode()

    return key, encapsulated_key_base64

def decaps(encapsulated_key: bytes, private_key_file: str, kem: str = "mlkem") -> str:
    """Decapsulates a key from a encapsulated key.

    Args:
        encapsulated_key (bytes): encapsulated key.
        private_key_file (str): file containing the private key used for decapsulation.
        kem (str, optional): KEM algorithm to use. Defaults to "mlkem".

    Returns:
        str: decapsulated key
    """
    interface = load_interface_from_so(kem)
    if not interface:
        return None

    key = interface.get_key_from_ciphertext(
        bytes(encapsulated_key, "utf-8"),
        bytes(private_key_file, "utf-8"),
    )
    
    return key

def combine_keys(k0: str, k1: str) -> str:
    k0 = base64.b64decode(k0)
    k1 = base64.b64decode(k1)
    result = bytes(x ^ y for x, y in zip(k0, k1))
    combined_key = base64.b64encode(result).decode("utf-8")
    return combined_key