"""
A simple echo client that handles some exceptions
Be sure to make this file a function
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import pickle
import socket
import sys

def send_to_server(host, port, size, question):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
    # except socket.error, (value,message):
    except socket.error as message:
        if s:  # see if s is None or not
            s.close()
        print("Unable to open the socket: " + str(message))
        return

    # question = b'Who was the first president of the United States?'
    print("[INFO] Encrypting Question")

    # TODO: encrypt the question here
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(question)
    md5Hash = hashes.Hash(hashes.MD5(), backend=default_backend())
    md5Hash.update(token)
    md5_hash_result = md5Hash.finalize()

    print("[Key] " + str(key))
    print("[Token] " + str(token))
    print("[MD5 Hash] " + str(md5_hash_result))

    # TODO: serialize the question with pickle
    message = pickle.dumps((key, token, md5_hash_result))
    print("[Message] " + str(message))

    # TODO: Send the question to the server
    s.send(message)

    # TODO: Decode the echoed message from the server
    data = s.recv(size)
    print('[RESPONSE] ' + str(data))
    s.close()
    return
