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
import plugin

def main():
	print("Plugins :")
	for p in plugin.get_all_plugins():
		print(p)

if __name__ == '__main__':
 	main() 

