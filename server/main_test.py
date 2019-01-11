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
import ConfigParser
import importlib

#ajouter un join lors de la desactivation du plugin 

class Server():
	"""docstring for Server"""
	def __init__(self, config_path):
		self.config = ConfigParser.ConfigParser()
		self.config.read(config_path)
		self.enabled_plugins = []
		self.disabled_plugins = [] 
		self.init_plugins()
		print("Plugins :")
		print("Enabled :")
		print(self.get_enabled_plugins())
		print("Disabled :")
		print(self.get_disabled_plugins())

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
		for plugin in self.enabled_plugins:
			plugin.join()

	def handle_data(self, client_address,data):
		#check format and size
		log("Data received from ".format(client_address)+" : "+data)
		message = re.findall(r'&(.*?)&', data)
		log(message)
		if len(message) > 0 :
			for plugin in self.enabled_plugins:
				if plugin.get_name() == message[0]:
					#send to thread 
					plugin.receive_message(message)

	def get_enabled_plugins(self):
		return self.enabled_plugins

	def get_disabled_plugins(self):
		return self.disabled_plugins

	def get_all_plugins(self):
		return self.enabled_plugins + self.disabled_plugins

	def load_plugin(self, name):
		module_name = 'plugins.plugin_' + str(name)
		mod = importlib.import_module(module_name)
		return mod 

	def init_plugins(self):
		names = Server.config_section_map(self.config, "plugins")
		for name in names:
			self.init_plugin(str(name), True if names[name] == "enable" else False)
		
	def init_plugin(self, name, is_enable):
		plugin = self.load_plugin(name)
		plugin = plugin.plugin_main(is_enable)
		if plugin.is_enable() == True :
			self.enabled_plugins.append(plugin)
		else : 
			self.disabled_plugins.append(plugin)	

	@staticmethod
	def config_section_map(config, section):
	    dict1 = {}
	    options = config.options(section)
	    for option in options:
	        try:
	            dict1[option] = config.get(section, option)
	            if dict1[option] == -1:
	                DebugPrint("skip: %s" % option)
	        except:
	            print("exception on %s!" % option)
	            dict1[option] = None
	    return dict1

if __name__ == '__main__':
 	server = Server("config.ini")


