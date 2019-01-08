# -*- coding: utf-8 -*
#!/usr/bin/env python3
from ... import plugin

@not_declared
@disable(name="alarm")
class Display(Plugin):
	"""[summary]
	
	[description]
	
	Extends:
		Plugin
	"""
	def __init__(self, name, enable, parser):
		"""[summary]
		
		[description]
		
		Arguments:
			name {[type]} -- [description]
			parser {[type]} -- [description]
		"""
		super(Display, self).__init__(name, enable)
		self.args = parser.parse_args()
		self.options = RGBMatrixOptions()
		if self.args.led_gpio_mapping != None:
			self.options.hardware_mapping = self.args.led_gpio_mapping
		self.options.rows = self.args.led_rows
		self.options.cols = self.args.led_cols
		self.options.chain_length = self.args.led_chain
		self.options.parallel = self.args.led_parallel
		self.options.row_address_type = self.args.led_row_addr_type
		self.options.multiplexing = self.args.led_multiplexing
		self.options.pwm_bits = self.args.led_pwm_bits
		self.options.brightness = self.args.led_brightness
		self.options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
		self.options.led_rgb_sequence = self.args.led_rgb_sequence
		self.options.pixel_mapper_config = self.args.led_pixel_mapper
		if self.args.led_show_refresh:
			self.options.show_refresh_rate = 1
		if self.args.led_slowdown_gpio != None:
			self.options.gpio_slowdown = self.args.led_slowdown_gpio
		if self.args.led_no_hardware_pulse:
			self.options.disable_hardware_pulsing = True
		self.matrix = RGBMatrix(options = self.options)
		self.notifications = []

		self.font = graphics.Font()
		self.font.LoadFont("/home/pi/pyOclock/fonts/6x13B.bdf")

		self.canvas = self.matrix.CreateFrameCanvas()
		self.drawing_functions  = {
  			"scrolling_text": self.scroll_text_drawing,
  			"static_text": self.static_text_drawing,
  			"scrolling_image": self.scroll_image_drawing,
  			"static_image": self.static_image_drawing,
		}
		self.images_path = {
			"twitter" : "/home/pi/pyOclock/assets/images/twitter.jpg", 

			"01d" : "/home/pi/pyOclock/assets/images/01d.jpg", 
			"02d" : "/home/pi/pyOclock/assets/images/02d.jpg", 
			"03d" : "/home/pi/pyOclock/assets/images/03d.jpg", 
			"04d" : "/home/pi/pyOclock/assets/images/04d.jpg", 
			"09d" : "/home/pi/pyOclock/assets/images/09d.jpg", 
			"10d" : "/home/pi/pyOclock/assets/images/10d.jpg", 
			"11d" : "/home/pi/pyOclock/assets/images/11d.jpg",
			"13d" : "/home/pi/pyOclock/assets/images/13d.jpg",
			
			"01n" : "/home/pi/pyOclock/assets/images/01n.jpg", 
			"02n" : "/home/pi/pyOclock/assets/images/02n.jpg", 
			"03n" : "/home/pi/pyOclock/assets/images/03n.jpg", 
			"04n" : "/home/pi/pyOclock/assets/images/04n.jpg", 
			"09n" : "/home/pi/pyOclock/assets/images/09n.jpg", 
			"10n" : "/home/pi/pyOclock/assets/images/10n.jpg", 
			"11n" : "/home/pi/pyOclock/assets/images/11n.jpg",
			"13n" : "/home/pi/pyOclock/assets/images/13n.jpg",
		}
		self.default_color = hex_to_rgb("#B10DC9") 

	def receive_message(self, message):
		"""[summary]
		
		[description]
		
		Arguments:
			message {[type]} -- [description]
		"""
		if len(message) >= 4 and len(self.messages) < 100:
    			log("Call to add_notification")
    			self.add_notification(message)
	
	def usleep(self, value):
		"""[summary]
		
		[description]self.default_
		
		Arguments:
			value {[type]} -- [description]
		"""
		time.sleep(value/1000000.0)

	def run(self):
		
		"""[summary]
		
		[description]
		"""
		while True:
			self.canvas.Clear()
			time.sleep(1)
			if len(self.notifications) > 0:
				log("notification display called")
				notification = self.notifications[0]
				self.notifications.pop(0)
				#ajouter verification du type si c'est un int 
				self.drawing_functions[notification[1]](notification)
				log("Return to hour display")
			else :
				graphics.DrawText(self.canvas, self.font, 1, 12, graphics.Color(self.default_color[0], self.default_color[1], self.default_color[2]), self.get_time())
			self.canvas = self.matrix.SwapOnVSync(self.canvas)
	
	def scroll_text_drawing(self, notification):
		log("Scroll drawing called")
		match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', notification[4])
		if match:                      
		  color = hex_to_rgb(notification[4])

		else:
		  color = self.default_color
		textColor = graphics.Color(color[0], color[1], color[2])
		pos = self.canvas.width
		my_text = notification[3]
		length = 0
		while (pos + length >= 0):
			time.sleep(0.1)
			self.canvas.Clear()
			length = graphics.DrawText(self.canvas, self.font, pos, 12, textColor, my_text)
			pos -= 1
			self.canvas = self.matrix.SwapOnVSync(self.canvas)	
		

	def static_text_drawing(self, notification):
		log("Static text drawing called")
		match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', notification[4])
		if match:                      
		  color = hex_to_rgb(notification[4])

		else:
		  color = self.default_color
		textColor = graphics.Color(color[0], color[1], color[2])
		timeout = int(notification[5])
		my_text = notification[3]
		#à refaire 
		x_pos = 1 
		log("taille du texte"+str(len(my_text)))
		if(len(my_text) < 5 ):
		 	x_pos = 6
		length = 0
		while (timeout > 0):
			time.sleep(0.1)
			self.canvas.Clear()
			timeout = timeout - 1
			length = graphics.DrawText(self.canvas, self.font, x_pos, 12, textColor, my_text)
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def scroll_image_drawing(self, notification):
		log("Scroll image drawing called")
		image_name = notification[2]
		if image_name in self.images_path:
			image = Image.open(self.images_path[image_name]).convert('RGB')
			image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
		else:
			return
		img_width, img_height = image.size
		xpos = self.canvas.width
		while xpos + img_width >= 0:
			time.sleep(0.1)
			xpos -= 1
			self.canvas.Clear()
			self.canvas.SetImage(image, xpos)
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def static_image_drawing(self, notification):
		log("Static image drawing called")
		image_name = notification[2]
		if image_name in self.images_path:
			image = Image.open(self.images_path[image_name]).convert('RGB')
			image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
		else:
			return 
		#find xpos with width 
		xpos = 8
		img_width, img_height = image.size
		timeout = int(notification[3])
		while (timeout > 0):
			time.sleep(0.1)
			timeout -= 1
			self.canvas.Clear()
			self.canvas.SetImage(image, xpos)
			self.canvas = self.matrix.SwapOnVSync(self.canvas)

	def get_time(self):
		tdate = datetime.datetime.now()
		return "{:d}:{:02d}".format(tdate.hour, tdate.minute)

	def add_notification(self, notification):
		"""[summary]
		
		[description]
		
		Arguments:
			notification {[type]} -- [description]
		"""
		self.notifications.append(notification)			