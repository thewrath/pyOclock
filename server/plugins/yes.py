# -*- coding: utf-8 -*
#!/usr/bin/env python3
from ... import plugin



@declared
@enable(name="yes")
class Yes(Plugin):
	"""[summary]
	
	[description]
	
	Extends:
		Plugin
	"""
	def __init__(self, name):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
		"""
		super(Yes, self).__init__(name)
	
	def run(self):
		print("yes") 