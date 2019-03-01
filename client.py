# File: client.py
# Authors: Aaron Brandel, Shane Ickes, Andrew Siemon
# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import sys
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import pickle
import socket
from watson_developer_cloud import TextToSpeechV1
import os
from ClientKeys import *


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

    print("[Checkpoint 01] Connecting to ", host, " on port  ", port)
    # question = b'Who was the first president of the United States?'

    # TODO: encrypt the question here
    key = Fernet.generate_key()
    f = Fernet(key)
    token = f.encrypt(question)
    md5Hash = hashes.Hash(hashes.MD5(), backend=default_backend())
    md5Hash.update(token)
    md5_hash_result = md5Hash.finalize()

    print("[Checkpoint 04] Encrypt: Generated Key: ", str(key), "| Cipher text: ", str(token))
    # TODO: serialize the question with pickle
    message = pickle.dumps((key, token, md5_hash_result))
    
    print("[Checkpoint 05] Sending data: ", str(message))
    # TODO: Send the question to the server
    s.send(message)
	
    # TODO: Decode the echoed message from the server
    response = s.recv(size)
    print("Checkpoint 06] Received data: ", str(response))
    (encrypted_response, md5Hash_response) = pickle.loads(response)
    
    # TODO: Create a checksum on the response
    md5ResponseHash = hashes.Hash(hashes.MD5(), backend=default_backend())
    md5ResponseHash.update(encrypted_response)
    md5_response_hash = md5ResponseHash.finalize()
    
    result = False
    
    # TODO: if the hashes match, print the message and use Watson API
    if md5_response_hash == md5Hash_response:
        decrypted_response = f.decrypt(encrypted_response)
        print("Checkpoint 07] Decrypt: Using Key: ",str(key),"| Plain text: ",str(decrypted_response))
	# TODO: Convert the response to a speech file and play the file
        watson_speech(decrypted_response)
        result = True
    else:
        print('[ERROR] Message from server corrupted.')
    
    # Close the server connection and return
    s.close()
    return result
    

def watson_speech(answer):
    print("[Checkpoint 08] Speaking Answer: ", str(answer))
    text_to_speech = TextToSpeechV1(
        iam_apikey=key1,
        url=url1
    )

    speech_text = str(answer)
	
    with open('answer.mp3', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                speech_text,
                'audio/mp3',
                'en-US_AllisonVoice'
            ).get_result().content)
			
    # TODO: Play the audio file here with OS command
    os.system("omxplayer answer.mp3")
	
    # return to the server 
    return


#START SCRIPT
# construct the argument parser and parse the arguments
parser = argparse.ArgumentParser()
parser.add_argument('-sip', help='Server IP Address', required=True)
parser.add_argument('-sp', help="Server Post Number", required=True)
parser.add_argument('-z', help="Socket Size", required=True)

args = vars(parser.parse_args())

host = args['sip']
port = int(args['sp'])
size = int(args['z'])

# initialize the video stream and allow the camera sensor to warm up
# vs = VideoStream(src=0).start() # use for non Rpi
vs = VideoStream(usePiCamera=True).start()  # use for Rpi
time.sleep(2.0)

# initialize the set of barcodes found thus far
found = set()

print("[Checkpoint 02] Listening for QR codes from RPi Camera that contain questions")
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to
	# have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	
	# find the barcodes in the frame and decode each of the barcodes
	barcodes = pyzbar.decode(frame)
	
	# loop over the detected barcodes
	for barcode in barcodes:
		# extract the bounding box location of the barcode and draw
		# the bounding box surrounding the barcode on the image
		(x, y, w, h) = barcode.rect
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
		
		# the barcode data is a bytes object so if we want to draw it
		# on our output image, we need to convert it to a string first
		barcodeData = barcode.data.decode("utf-8")
		barcodeType = barcode.type
		
		# draw the barcode data and barcode type on the image
		text = "{} ({})".format(barcodeData, barcodeType)
		cv2.putText(frame, text, (x, y - 10),
		    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
		
		# if the barcode text is currently not in our set, then send
		# the decoded question to the server
		if barcodeData not in found:
			question = bytes(barcodeData, "utf-8")
			print('[Checkpoint 03] New Question: ', str(question))
			# Make sure the server response isn't corrupted
			if send_to_server(host, port, size, question):
				found.add(barcodeData)
			
	# show the output frame
	cv2.imshow("Barcode Scanner", frame)
	key = cv2.waitKey(50) & 0xFF
		
	# if the `q` key was pressed, break from the loop
	if key == ord('q'):
		# Do a bit of cleanup
		print("[INFO] cleaning up...")
		cv2.destroyAllWindows()
		vs.stop()
		sys.exit()
