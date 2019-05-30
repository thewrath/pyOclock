# -*- coding: utf-8 -*
#!/usr/bin/env python3
import pygame
import datetime

from plugins.plugin import *
from threading import *
from queue import *
from pygame import *

white = (255, 255, 255) 
green = (0, 255, 0) 
blue = (0, 0, 128) 

def plugin_main(is_enable):
	return TkinterDisplay("tkinter_display", is_enable)

class TkinterDisplay(Plugin):
	"""[summary]
	
	[description]
	This plugin aims to provide a virtual display to test the different behavior of the API etc.... 
	Extends:
		Plugin
	"""
	def __init__(self, name, enable):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
		"""
		super(TkinterDisplay, self).__init__(name, "display", enable)
		pygame.init()
		self.display_surface = pygame.display.set_mode((400, 300))
		pygame.display.set_caption('Hello World!')

		self.font = pygame.font.Font('freesansbold.ttf', 32) 
		self.text = self.font.render(self.get_time(), True, green, blue) 
		self.textRect = self.text.get_rect() 
		self.textRect.center = (400//2, 300//2)

		self.message_queue = Queue()
		self.gui_thread = Thread(target = self.threaded_GUI)
		self.gui_thread.start()

	def terminate(self):
		super(TkinterDisplay, self).terminate()
		self.gui_thread.join()
		pygame.display.quit()
		print("GUI shutdown")		

	def threaded_GUI(self):
		while True:
			#self.display_surface.fill(white)
			if not self.message_queue.empty():
				message = self.message_queue.get()
				print(message)
				self.textRect.center = (400//2, (300//2)+50)
				self.text = self.font.render(message["message"], True, green, blue) 
				self.display_surface.blit(self.text, self.textRect)
			#time display 
			self.textRect.center = (400//2, 300//2)
			self.text = self.font.render(self.get_time(), True, green, blue) 
			self.display_surface.blit(self.text, self.textRect) 
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.display.quit()
			pygame.display.update()

	def receive_message(self, message):
		super(TkinterDisplay, self).receive_message(message)
		if (self.check_message(message)):
			self.message_queue.put(message)

	def check_message(self, message):
		return isinstance(message, dict) and "message" in message
		
	def get_time(self):
		tdate = datetime.datetime.now()
		return "{:d}:{:02d}".format(tdate.hour, tdate.minute)

	def run(self):
		print("yes") 