# -*- coding: utf-8 -*
#!/usr/bin/env python3
from ... import plugin

@not_declared
@enable(name="alarm")
class Alarm(Plugin):
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
		super(Alarm, self).__init__(name, enable)
		self.alarm_song = "/home/pi/pyOclock/assets/audio/alarm_0.mp3"
		mixer.init()
		mixer.music.load(self.alarm_song)
		
		with open('alarm_options.json') as json_data:
			self.alarm_data = json.load(json_data)

		if not self.alarm_data :
			sys.exit()	

		self.clocks = self.alarm_data["Clocks"]
		log("All availables alarms : ")
		log(self.clocks)	
		self.current_clock = 1717
		self.find_next_clock()
		self.alarm_functions  = {
  			"set_option": self.set_option,
		}


	def run(self):
		"""[summary]
		
		[description]
		"""
		while True:
			schedule.run_pending()
			time.sleep(30)
			if len(self.messages) > 0:
				log("notification display called")
				message = self.messages[0]
				self.messages.pop(0)
				#ajouter verification du type si c'est un int 
				self.alarm_functions[message[1]](message)

	def find_next_clock(self):
		#"[0-9]+(,[0-9]+)*"
		#si marche pas bien pour le tri, chercher le minimum ici et faire en sorte d'affecter le minimum au schedule si il est superieur à tout les autres 
		with open('alarm_options.json') as json_data:
			self.alarm_data = json.load(json_data)
		self.clocks = self.alarm_data["Clocks"]
		index = "0" 
		for clock in self.clocks:
			if(int(self.clocks[clock]) > int(self.get_time())):
				index = clock
				break 
		log("Next selected alarm : "+self.clocks[index])
 
		schedule_time = "{:d}:{:02d}".format(int(self.clocks[index][:2]), int(self.clocks[index][2:]))
		schedule.every().day.at(schedule_time).do(self.turn_on_alarm)

	def get_time(self):
		tdate = datetime.datetime.now()
		return "{:d}{:02d}".format(tdate.hour, tdate.minute)	

	def set_option(self, message):
		pass

	def turn_on_alarm(self):
		log("Alarm is rigging")
		mixer.music.play()
		self.find_next_clock()