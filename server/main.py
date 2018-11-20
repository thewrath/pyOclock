#!/usr/bin/env python3
import socket
import os
import sys
import datetime
import re
import time
import argparse
import threading 

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

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
		self.managers.append(Alarm("alarm"))
		self.managers.append(Display("display", self.parser))

		for manager in self.managers:
			manager.start()

	def run(self):
		"""[main loop for the tcp server]
		
		[description]
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_address = ('localhost', 16666)
		log("Starting up on {} port {} ".format(*server_address))
		sock.bind(server_address)
		#listen for one icoming connection
		sock.listen(1)

		while True:
		    # Wait for a connection
		    log('waiting for a connection')
		    connection, client_address = sock.accept()
		    try:
		    	log('Connection from'.format(client_address))
		    	# Receive the data in small chunks and retransmit it
		    	data = connection.recv(64)
		    	log(data)
		    	self.handle_data(client_address,data.decode("utf-8"))
		    finally:
		        # Clean up the connection
		        connection.close()
		        # join all threads 
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

#Managers
class Manager(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.message= []

	def run(self):
		pass

	def get_name(self):
		return self.name

	def receive_message(self, message):
		self.message.append(message)

class Alarm(Manager):
	"""[summary]
	
	[description]
	
	Extends:
		Manager
	"""
	def __init__(self, name):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
		"""
		super(Alarm, self).__init__(name)

	def run(self):
		"""[summary]
		
		[description]
		"""
		super(Alarm, self).run()

class Display(Manager):
	"""[summary]
	
	[description]
	
	Extends:
		Manager
	"""
	def __init__(self, name, parser):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
			parser {[type]} -- [description]
		"""
		super(Display, self).__init__(name)
		self.args = parser.parse_args()
		self.options = RGBMatrixOptions()
		if self.args.led_gpio_mapping != None:
			self.options.hardware_mapping = self.args.led_gpio_mapping
		self.options.rows = self.args.led_rows
		self.options.cols = self.args.led_cols
		self.options.chain_length = self.args.led_chain
		self.options.parallel = self.args.led_parallel
		self.options.row_address_type = self.args.led_row_addr_type
		self.options.multiplexing = self.args.led_multiplexing
		self.options.pwm_bits = self.args.led_pwm_bits
		self.options.brightness = self.args.led_brightness
		self.options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
		self.options.led_rgb_sequence = self.args.led_rgb_sequence
		self.options.pixel_mapper_config = self.args.led_pixel_mapper
		if self.args.led_show_refresh:
			self.options.show_refresh_rate = 1
		if self.args.led_slowdown_gpio != None:
			self.options.gpio_slowdown = self.args.led_slowdown_gpio
		if self.args.led_no_hardware_pulse:
			self.options.disable_hardware_pulsing = True
		self.matrix = RGBMatrix(options = self.options)
		self.notifications = []

		self.font = graphics.Font()
		self.font.LoadFont("../fonts/7x13.bdf")

		self.canvas = self.matrix.CreateFrameCanvas()

	def receive_message(self, message):
		"""[summary]
		
		[description]
		
		Arguments:
			message {[type]} -- [description]
		"""
		if len(message) >= 4:
    			log("Call to add_notification")
    			self.add_notification(message)
	
	def usleep(self, value):
		"""[summary]
		
		[description]
		
		Arguments:
			value {[type]} -- [description]
		"""
		time.sleep(value/1000000.0)

	def run(self):
		
		"""[summary]
		
		[description]
		"""
		while True:
			self.canvas.Clear()
			if len(self.notifications) > 0:
				log("notification display called")
				notification = self.notifications[0]
				self.notifications.pop(0)
				textColor = graphics.Color(255, 255, 0)
				pos = self.canvas.width
				my_text = notification[3]
				length = 0
				while not (pos + length < 0):
					self.canvas.Clear()
					length = graphics.DrawText(self.canvas, self.font, pos, 10, textColor, my_text)
					pos -= 1
					time.sleep(0.1)
			else :
				graphics.DrawText(self.canvas, self.font, 0, 10, graphics.Color(120, 120, 255), self.get_time())
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def get_time(self):
		tdate = datetime.datetime.now()
		return "{:d}:{:02d}".format(tdate.hour, tdate.minute)

	def add_notification(self, notification):
		"""[summary]
		
		[description]
		
		Arguments:
			notification {[type]} -- [description]
		"""
		self.notifications.append(notification)

def log(message):
	"""[summary]
	
	[description]
	
	Arguments:
		message {[type]} -- [description]
	"""
	time = datetime.datetime.now()
	print(str(time)+" : "+str(message))


if __name__ == '__main__':
	server = Server()
	server.run()
