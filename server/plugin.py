# -*- coding: utf-8 -*
#!/usr/bin/env python3
import threading
from plugins import * 
#Add plugins here 
#add global configuration for plugin (pass it by enable )

enabled_plugins = []
disabled_plugins = [] 

def get_enabled_plugins():
	return enabled_plugins

def get_disabled_plugins():
	return enabled_plugins

def get_all_plugins():
	return enabled_plugins + disabled_plugins

def not_declared(plugin):
	pass

def declared(plugin):
	return plugin

def enable(plugin, name):
		for p in disabled_plugins:
			if p.get_name() == name:
				disabled_plugins.remove(p)
		enabled_plugins.append(plugin(name, True))

def disable(plugins, name):
		for p in enabled_plugins:
			if p.get_name() == name:
				enabled_plugins.remove(p)
		disabled_plugins.append(plugin(name, False)) 
	

class Plugin(threading.Thread):
	def __init__(self, name, enable):
		threading.Thread.__init__(self)
		self.name = name
		self.enable = enable
		self.buffer_length = 100;
		self.messages = []

	def run(self):
		pass

	def get_name(self):
		return self.name

	def is_enable(self):
		return self.enable

	def receive_message(self, message):
		if len(self.messages) < buffer_length :
			self.messages.append(message)

	def __repr__(self, ):
		return self.name + "<Plugin>" + "enable: " + self.enable  

	def __str__(self, ):
		return self.name + "<Plugin>" + "enable: " + self.enable 

