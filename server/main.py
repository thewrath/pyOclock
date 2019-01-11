# -*- coding: utf-8 -*
#!/usr/bin/env python3
import socket
import os
import sys
import datetime
import re
import time
import argparse
import threading 
import re 
import schedule
import json 
#image drawing 
from PIL import Image
from PIL import ImageDraw

from pygame import mixer

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

PORT = 16666

class Server():
	"""[summary]
	
	[description]
	"""
	def __init__(self, *args, **kwargs):
		self.parser = argparse.ArgumentParser()
		self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
		self.parser.add_argument("--led-cols", action="store", help="Panel columns. Typically 32 or 64. (Default: 32)", default=32, type=int)
		self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 1.", default=1, type=int)
		self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
		self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
		self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
		self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], type=str)
		self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
		self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
		self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
		self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 1..100. Default: 1", choices=range(3), type=int)
		self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
		self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
		self.parser.add_argument("--led-pixel-mapper", action="store", help="Apply pixel mappers. e.g \"Rotate:90\"", default="", type=str)
		self.parser.add_argument("--led-row-addr-type", action="store", help="0 = default; 1=AB-addressed panels;2=row direct", default=0, type=int, choices=[0,1,2])
		self.parser.add_argument("--led-multiplexing", action="store", help="Multiplexing type: 0=direct; 1=strip; 2=checker; 3=spiral; 4=ZStripe; 5=ZnMirrorZStripe; 6=coreman; 7=Kaler2Scan; 8=ZStripeUneven (Default: 0)", default=0, type=int)

		self.managers = []
		#self.managers.append(Alarm("alarm"))
		self.managers.append(Display("display", self.parser))

		for manager in self.managers:
			manager.start()

	def run(self):
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('localhost', PORT)
		log("Starting up on {} port {} ".format(*server_address))
		sock.bind(server_address)
		while True:
			sock.listen(1)
			log("Waiting for a connection")
			connection, client_address = sock.accept()
			data = connection.recv(1024)
			log(data.decode("utf-8"))
			self.handle_data(client_address, data.decode("utf-8"))
		log("Server stopped")
		connection.close()
		sock.close()
		for manager in self.managers:
			manager.join()

	def handle_data(self, client_address,data):
		#check format and size
		log("Data received from ".format(client_address)+" : "+data)
		message = re.findall(r'&(.*?)&', data)
		log(message)
		if len(message) > 0 :
			for manager in self.managers:
				if manager.get_name() == message[0]:
					#send to thread 
					manager.receive_message(message)


if __name__ == '__main__':
	#for production mode 
	sys.stdout = open("./%s" % "log.txt", "w")
	log("Welcome in pyOclock Server ! V0.1")
	server = Server()
	server.run()
