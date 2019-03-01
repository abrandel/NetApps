# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import sys
from network_interface import *

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
print("[INFO] starting the video stream...")
# vs = VideoStream(src=0).start() # use for non Rpi
vs = VideoStream(usePiCamera=True).start()  # use for Rpi
time.sleep(2.0)

# initialize the set of barcodes found thus far
found = set()

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
			print('[Question] ' + str(question))
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


