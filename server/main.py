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
import configparser
import importlib
import cherrypy

PORT = 16666

class Main(object):
    def __init__(self, config_path):
        self.server = Server(config_path)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
        data = cherrypy.request.json
        Server.log(data)
        return "Hello World!"

class Server(object):
	"""docstring for Server"""
	def __init__(self, config_path):
		self.config = configparser.ConfigParser()
		self.config.read(config_path)
		self.enabled_plugins = []
		self.disabled_plugins = []
		self.init_plugins()
		Server.log("Plugins :")
		Server.log("Enabled :")
		Server.log(self.get_enabled_plugins())
		Server.log("Disabled :")
		Server.log(self.get_disabled_plugins())

    # def run(self):
        # pass
        #for plugin in self.get_all_plugins():
			#plugin.join()

	# def handle_data(self, data):
    #     pass
		#check format and size
        #check message datas send to
		# message = re.findall(r'&(.*?)&', data)
		# log(message)
		# if len(message) > 0 :
		# 	for plugin in self.enabled_plugins:
		# 		if plugin.get_name() == message[0]:
		# 			#send to thread
		# 			plugin.receive_message(message)

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
					Server.log("skip: %s" % option)
			except:
				print("exception on %s!" % option)
				dict1[option] = None
		return dict1

	@staticmethod
	def log(message):
        	time = datetime.datetime.now()
        	print(str(time).encode('utf-8') + b" : " + str(message).encode('utf8'))


if __name__ == '__main__':
	main = Main("config.ini")
	cherrypy.quickstart(main)
