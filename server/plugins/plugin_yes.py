# -*- coding: utf-8 -*
#!/usr/bin/env python3
from plugins.plugin import *

def plugin_main(is_enable):
	return Yes("yes", is_enable)

class Yes(Plugin):
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
		super(Yes, self).__init__(name, enable)
	
	def run(self):
		print("yes") 