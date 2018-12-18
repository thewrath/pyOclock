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

#Managers
class Manager(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.messages = []

	def run(self):
		pass

	def get_name(self):
		return self.name

	def receive_message(self, message):
		if len(self.messages) < 100 :
			self.messages.append(message)

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
		self.alarm_song = "/home/pi/pyOclock/assets/audio/alarm_0.mp3"
		mixer.init()
		mixer.music.load(self.alarm_song)
		
		with open('alarm_options.json') as json_data:
			self.alarm_data = json.load(json_data)

		if not self.alarm_data :
			sys.exit()	

		self.clocks = self.alarm_data["Clocks"]
		log("All availables alarms : ")
		log(self.clocks)	
		self.current_clock = 1717
		self.find_next_clock()
		self.alarm_functions  = {
  			"set_option": self.set_option,
		}


	def run(self):
		"""[summary]
		
		[description]
		"""
		while True:
			schedule.run_pending()
			time.sleep(30)
			if len(self.messages) > 0:
				log("notification display called")
				message = self.messages[0]
				self.messages.pop(0)
				#ajouter verification du type si c'est un int 
				self.alarm_functions[message[1]](message)

	def find_next_clock(self):
		#"[0-9]+(,[0-9]+)*"
		#si marche pas bien pour le tri, chercher le minimum ici et faire en sorte d'affecter le minimum au schedule si il est superieur à tout les autres 
		with open('alarm_options.json') as json_data:
			self.alarm_data = json.load(json_data)
		self.clocks = self.alarm_data["Clocks"]
		index = "0" 
		for clock in self.clocks:
			if(int(self.clocks[clock]) > int(self.get_time())):
				index = clock
				break 
		log("Next selected alarm : "+self.clocks[index])
 
		schedule_time = "{:d}:{:02d}".format(int(self.clocks[index][:2]), int(self.clocks[index][2:]))
		schedule.every().day.at(schedule_time).do(self.turn_on_alarm)

	def get_time(self):
		tdate = datetime.datetime.now()
		return "{:d}{:02d}".format(tdate.hour, tdate.minute)	

	def set_option(self, message):
		pass

	def turn_on_alarm(self):
		log("Alarm is rigging")
		mixer.music.play()
		self.find_next_clock()



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
		self.font.LoadFont("/home/pi/pyOclock/fonts/6x13B.bdf")

		self.canvas = self.matrix.CreateFrameCanvas()
		self.drawing_functions  = {
  			"scrolling_text": self.scroll_text_drawing,
  			"static_text": self.static_text_drawing,
  			"scrolling_image": self.scroll_image_drawing,
  			"static_image": self.static_image_drawing,
		}
		self.images_path = {
			"twitter" : "/home/pi/pyOclock/assets/images/twitter.jpg", 

			"01d" : "/home/pi/pyOclock/assets/images/01d.jpg", 
			"02d" : "/home/pi/pyOclock/assets/images/02d.jpg", 
			"03d" : "/home/pi/pyOclock/assets/images/03d.jpg", 
			"04d" : "/home/pi/pyOclock/assets/images/04d.jpg", 
			"09d" : "/home/pi/pyOclock/assets/images/09d.jpg", 
			"10d" : "/home/pi/pyOclock/assets/images/10d.jpg", 
			"11d" : "/home/pi/pyOclock/assets/images/11d.jpg",
			"13d" : "/home/pi/pyOclock/assets/images/13d.jpg",
			
			"01n" : "/home/pi/pyOclock/assets/images/01n.jpg", 
			"02n" : "/home/pi/pyOclock/assets/images/02n.jpg", 
			"03n" : "/home/pi/pyOclock/assets/images/03n.jpg", 
			"04n" : "/home/pi/pyOclock/assets/images/04n.jpg", 
			"09n" : "/home/pi/pyOclock/assets/images/09n.jpg", 
			"10n" : "/home/pi/pyOclock/assets/images/10n.jpg", 
			"11n" : "/home/pi/pyOclock/assets/images/11n.jpg",
			"13n" : "/home/pi/pyOclock/assets/images/13n.jpg",
		}
		self.default_color = hex_to_rgb("#B10DC9") 

	def receive_message(self, message):
		"""[summary]
		
		[description]
		
		Arguments:
			message {[type]} -- [description]
		"""
		if len(message) >= 4 and len(self.messages) < 100:
    			log("Call to add_notification")
    			self.add_notification(message)
	
	def usleep(self, value):
		"""[summary]
		
		[description]self.default_
		
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
			time.sleep(1)
			if len(self.notifications) > 0:
				log("notification display called")
				notification = self.notifications[0]
				self.notifications.pop(0)
				#ajouter verification du type si c'est un int 
				self.drawing_functions[notification[1]](notification)
				log("Return to hour display")
			else :
				graphics.DrawText(self.canvas, self.font, 1, 12, graphics.Color(self.default_color[0], self.default_color[1], self.default_color[2]), self.get_time())
			self.canvas = self.matrix.SwapOnVSync(self.canvas)
	
	def scroll_text_drawing(self, notification):
		log("Scroll drawing called")
		match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', notification[4])
		if match:                      
		  color = hex_to_rgb(notification[4])

		else:
		  color = self.default_color
		textColor = graphics.Color(color[0], color[1], color[2])
		pos = self.canvas.width
		my_text = notification[3]
		length = 0
		while (pos + length >= 0):
			time.sleep(0.1)
			self.canvas.Clear()
			length = graphics.DrawText(self.canvas, self.font, pos, 12, textColor, my_text)
			pos -= 1
			self.canvas = self.matrix.SwapOnVSync(self.canvas)	
		

	def static_text_drawing(self, notification):
		log("Static text drawing called")
		match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', notification[4])
		if match:                      
		  color = hex_to_rgb(notification[4])

		else:
		  color = self.default_color
		textColor = graphics.Color(color[0], color[1], color[2])
		timeout = int(notification[5])
		my_text = notification[3]
		#à refaire 
		x_pos = 1 
		log("taille du texte"+str(len(my_text)))
		if(len(my_text) < 5 ):
		 	x_pos = 6
		length = 0
		while (timeout > 0):
			time.sleep(0.1)
			self.canvas.Clear()
			timeout = timeout - 1
			length = graphics.DrawText(self.canvas, self.font, x_pos, 12, textColor, my_text)
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def scroll_image_drawing(self, notification):
		log("Scroll image drawing called")
		image_name = notification[2]
		if image_name in self.images_path:
			image = Image.open(self.images_path[image_name]).convert('RGB')
			image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
		else:
			return
		img_width, img_height = image.size
		xpos = self.canvas.width
		while xpos + img_width >= 0:
			time.sleep(0.1)
			xpos -= 1
			self.canvas.Clear()
			self.canvas.SetImage(image, xpos)
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def static_image_drawing(self, notification):
		log("Static image drawing called")
		image_name = notification[2]
		if image_name in self.images_path:
			image = Image.open(self.images_path[image_name]).convert('RGB')
			image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
		else:
			return 
		#find xpos with width 
		xpos = 8
		img_width, img_height = image.size
		timeout = int(notification[3])
		while (timeout > 0):
			time.sleep(0.1)
			timeout -= 1
			self.canvas.Clear()
			self.canvas.SetImage(image, xpos)
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

def hex_to_rgb(value):
	value = value.lstrip('#')
	lv = len(value)
	return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def log(message):
	"""[summary]
	
	[description]
	
	Arguments:
		message {[type]} -- [description]
	"""
	time = datetime.datetime.now()
	print(str(time).encode('utf-8')+ b" : "+ str(message).encode('utf8'))


if __name__ == '__main__':
	#for production mode 
	sys.stdout = open("./%s" % "log.txt", "w")
	log("Welcome in pyOclock Server ! V0.1")
	server = Server()
	server.run()
