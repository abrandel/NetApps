"""
A simple echo server that handles some exceptions
"""

from cryptography.fernet import Fernet
import socket
import sys
import pickle

host = ''
port = 50000
backlog = 5
size = 1024
s = None
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(backlog)
except socket.error as message:
    if s:
        s.close()
    print("Could not open socket: " + str(message))
    sys.exit(1)

while 1:
    client, address = s.accept()
    message = client.recv(size)

    (key, encrypted_question, md5Hash) = pickle.loads(message)

    f = Fernet(key)
    decrypted_question = f.decrypt(encrypted_question)
    print("[Question] " + str(decrypted_question))
    print("[MD5 Hash] " + str(md5Hash))

    if message:
        client.send(decrypted_question)

    client.close()
