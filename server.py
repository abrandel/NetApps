
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import socket
import sys
import pickle
import sys
import wolframalpha
from wolfram import *
import argparse
from Watson_api import *
#temp
app_id_recovered = app_id

parser = argparse.ArgumentParser()
parser.add_argument('-sp', help="Server Post Number", required=True)
parser.add_argument('-z', help="Socket Size", required=True)

args = vars(parser.parse_args())

host = ''
port = int(args['sp'])
size = int(args['z'])
backlog = 5
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

    md5ReceivedHash = hashes.Hash(hashes.MD5(), backend=default_backend())
    md5ReceivedHash.update(encrypted_question)
    md5ClientHash = md5ReceivedHash.finalize()
    
    decrypted_question = None
    answerHashString = None
    
    if md5Hash == md5ClientHash:
        f = Fernet(key)
        decrypted_question = f.decrypt(encrypted_question)
        print("[Question] " + str(decrypted_question))
        print("[MD5 Hash] " + str(md5Hash))
        
        watson_speech(decrypted_question)
        
        wolfClient = wolframalpha.Client(app_id)
        res = wolfClient.query(decrypted_question)
        print("[Result from Wolfram Alpha:   ]" + next(res.results).text)
        answer = next(res.results).text
        
        token = f.encrypt(bytes(answer, "utf-8"))
        
        answerHash = hashes.Hash(hashes.MD5(), backend=default_backend())
        answerHash.update(token)
        answerHashString = answerHash.finalize()
        
        print ("[Hash generated for response]")
        message = pickle.dumps((token, answerHashString))
        client.send(message)
        
    else:
        decrypted_question = "Error: corrupted message to server."
        message = pickle.dumps((decrypted_question, ''))
        client.send(message)
        
    client.close()
