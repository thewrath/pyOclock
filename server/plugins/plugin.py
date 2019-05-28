# -*- coding: utf-8 -*
#!/usr/bin/env python3
import threading

class Plugin(threading.Thread):
	def __init__(self, name, type_, enable):
		threading.Thread.__init__(self)
		self.name = name
		self.type = type_;
		self.enable = enable
		self.buffer_length = 100;
		self.messages = []

	def terminate(self):
		pass	

	def run(self):
		pass

	def get_name(self):
		return self.name

	def get_type(self):
		return self.type

	def is_enable(self):
		return self.enable

	def receive_message(self, message):
		if len(self.messages) < self.buffer_length :
			self.messages.append(message)

	def __repr__(self, ):
		return "<Plugin: "+self.name + ">" + " <Enable: " + str(self.enable) + ">"  

	def __str__(self, ):
		return "<Plugin: "+self.name + ">" + " <Enable: " + str(self.enable) + ">" 
