#File: Server.py
#Authors: Aaron Brandel, Shane Ickes, Andrew Siemon

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import socket
import sys
import pickle
import sys
import subprocess
import wolframalpha
from ServerKeys import *
import argparse
from Watson_api import *

app_id_recovered = app_id

#Get arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('-sp', help="Server Post Number", required=True)
parser.add_argument('-z', help="Socket Size", required=True)

args = vars(parser.parse_args())

host = ''
port = int(args['sp'])
size = int(args['z'])
backlog = 5
s = None
#Attemt to bind to Client via TCP
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    
    #Alexander (last name N/A)  from https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
    serverIp = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
    print("[CheckPoint 01] Created socket at ", serverIp," on port ", port)
    
    #Listen for Client
    s.listen(backlog)
          
except socket.error as message:
    if s:
        s.close()
    print("Could not open socket: " + str(message))
    sys.exit(1)

while 1:
    #accept client connection
    print("[Checkpoint 02] Listening for client connections")
    client, address = s.accept()
    
    print("[Checkpoint 03] Accepted client connection from ", address[0], " on port ", address[1])
    
    #receive message from client
    message = client.recv(size)
    
    print("[Checkpoint 04] Received data ", message)
    (key, encrypted_question, md5Hash) = pickle.loads(message)
    
    #Create Hash for checksum
    md5ReceivedHash = hashes.Hash(hashes.MD5(), backend=default_backend())
    md5ReceivedHash.update(encrypted_question)
    md5ClientHash = md5ReceivedHash.finalize()
    
    decrypted_question = None
    answerHashString = None
    
    if md5Hash == md5ClientHash:
        #Decrypt the message from the client
        f = Fernet(key)
        decrypted_question = f.decrypt(encrypted_question)
        print("[Checkpoint 05] Decrypt: Key: ", key, " | Plain text: ", decrypted_question)
        
        #Convert the question from text to speech and play over hardware
        print("[Checkpoint 06] Speaking Question ", decrypted_question)
        watson_speech(decrypted_question)
        
        print("[Checkpoint 07] Sending question to Wolframalpha: ", decrypted_question)
        # from Jason R. Coombs at (https://pypi.org/project/wolframalpha/)
        wolfClient = wolframalpha.Client(app_id)
        res = wolfClient.query(decrypted_question)
        answer = next(res.results).text
        
        #Encrypt answer to send back to 
        print("[Checkpoint 08] Received question from Wolframalpha: ", answer)
        token = f.encrypt(bytes(answer, "utf-8"))
        
        print ("[Checkpoint 09] Encrypt: Key: ", key," Ciphertext: ",token)
        
        #Create hash for return checksum
        answerHash = hashes.Hash(hashes.MD5(), backend=default_backend())
        answerHash.update(token)
        answerHashString = answerHash.finalize()
        
        #Pickle the message to send back to client
        print ("[Checkpoint 10] Generated MD5 Checksum: ",answerHashString)
        message = pickle.dumps((token, answerHashString))
        
        #Send message from server to client
        print("[Checkpoint 11] Sending answer: ", message)
        client.send(message)
        
    else:
        decrypted_question = "Error: corrupted message to server."
        message = pickle.dumps((decrypted_question, ''))
        client.send(message)
        
    client.close()
