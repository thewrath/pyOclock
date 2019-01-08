# -*- coding: utf-8 -*
#!/usr/bin/env python3

class Utils():
	"""docstring for Utils"""
	def __init__(self):
		pass

	@staticmethod
	def hex_to_rgb(self):
		value = value.lstrip('#')
		lv = len(value)
		return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

	@staticmethod
	def log(message):
		"""[summary]
		
		[description]
		
		Arguments:
			message {[type]} -- [description]
		"""
		time = datetime.datetime.now()
		print(str(time).encode('utf-8')+ b" : "+ str(message).encode('utf8'))