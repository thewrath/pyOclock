# -*- coding: utf-8 -*
#!/usr/bin/env python3
from plugins.plugin import *

def plugin_main(is_enable):
	return No("no", is_enable)

class No(Plugin):
	"""[summary]
	
	[description]
	
	Extends:
		Plugin
	"""
	def __init__(self, name, enable):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
		"""
		super(No, self).__init__(name, "useless",enable)

	def receive_message(self, message):
		super(No, self).receive_message(message)
		print("No has received a message ")

	def run(self):
		print("no")