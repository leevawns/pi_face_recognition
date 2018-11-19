# USAGE run in cmd: python pi_face_recognition.py or python3 pi_face_recognition.py
# type: trcl-c to exit program dfd
from imutils.video import VideoStream
import face_recognition
import imutils
import pickle
import time
from datetime import datetime
import cv2
import pygame
import mysql.connector
import json

#SETTING Sound
pygame.mixer.init()
path_sound = {"startup":"audio/start_up.mp3",
			  "lap":"audio/lap_san.mp3",
			  "shiba":"audio/shiba_san.mp3",
			  "bo":"audio/bo_san.mp3",
			  "nam":"audio/nam_san.mp3",
			  "hoan":"audio/hoan_san.mp3"
			  "cuong":"audio/cuong_san.mp3",
			  "chung":"audio/chung_san.mp3",
			  "thao":"audio/thao_san.mp3"}
id_name={"lap":"e6184",
		 "shiba":"e1111",
		 "bo":"0001",
		 "nam":"0002",
		 "hoan_san.mp3":"0003",
		 "cuong":"0004",
		 "chung":"0005",
		 "thao":"0006"}
#SETTING DATA ENCODING
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open("encodings.pickle", "rb").read())
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

#after this time, program will save data face if it recognigtion
time_login = 20
#setting Database
local = {"host":"localhost",
		 "user":"leevawns",
		 "password":"123",
		 "database":"face_detect"}
server = {"host":"192.168.0.1",
		  "user":"admin",
		  "password":"123",
		  "database":""}
config_default = {"local":local,"server":server}
#################################################
try:
	config = pickle.loads(open("config.pickle","rb").read())
except:
	with open("config.pickle","wb") as f:
		pickle.dump(config_default,f)
	config = config_default
#################################################
print(config)
#connect database
try:
	mydb = mysql.connector.connect(host=config["local"]["host"],
								   user=config["local"]["user"],
								   passwd=config["local"]["password"])
	print("Connect localhost ok")
	#checking database
	mycursor = mydb.cursor()
	#create database
	try:
		mycursor.execute("CREATE DATABASE face_detect")
		print("database ok")
	except:
		pass
except:
	print("Can not connect to server --> EXIT...")
	exit()
# initialize the video stream and allow the camera sensor to warm up
print("[INFO] Starting video stream...")
print("[INFO] type: ctrl-c to exit program...")
print("[INFO] note: wait 2s to camera start...")
#select choose camera from usb or picamera
#vs = VideoStream(src=0).start()
vs = VideoStream(usePiCamera=True).start()

#play sound start up
pygame.mixer.music.load(path_sound["startup"])
pygame.mixer.music.play()
time.sleep(5)
#list save name person detect with time
list_name_dectect = {}
# loop over frames from the video file stream
# try except with keyboard interrupt for exit by ctrl-c
try:
	while True:
		time.sleep(0.01)
		frame = vs.read()
		frame = imutils.resize(frame, width=500)

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		# detect faces in the grayscale frame
		rects = detector.detectMultiScale(gray, scaleFactor=1.1,minNeighbors=5, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
		# OpenCV returns bounding box coordinates in (x, y, w, h) order
		boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

		# compute the facial embeddings for each face bounding box
		encodings = face_recognition.face_encodings(rgb, boxes)
		names = []
		for encoding in encodings:
			matches = face_recognition.compare_faces(data["encodings"],encoding,tolerance = 0.4)
			#dis = face_recognition.face_distance(data["encodings"],encoding)
			name = "Unknown"
			# check to see if we have found a match
			if True in matches:

				matchedIdxs = [i for (i, b) in enumerate(matches) if b]
				counts = {}

				for i in matchedIdxs:
					name = data["names"][i]
					counts[name] = counts.get(name, 0) + 1

				name = max(counts, key=counts.get)
			# update the list of names
			names.append(name)
		# list name detect in camera
		for name in names:
			if name != "Unknown":
				# code processing name login/logou here
				print("Detect person:{}".format(name))
				#return second now and last in list name
				if name in list_name_dectect:
					time_now = datetime.now()
					delta = (time_now - datetime.strptime(list_name_dectect[name],'%Y-%m-%d %H:%M:%S')).total_seconds()
					#compare time
					if delta > time_login:
						print("login again in time > 10 second, save date login !")
						#update time
						list_name_dectect[name] = time_now.strftime('%Y-%m-%d %H:%M:%S')
						#save here
						name_table = "history_" + str(time_now.year) +"_" + str(time_now.month)
						try:
							mycursor.execute("CREATE TABLE `face_detect`.`"+name_table + "` (id VARCHAR(5), time_log DATETIME, confirm VARCHAR(20))")
						except:
							pass
						sql_insert = "INSERT INTO `face_detect`.`"+name_table+"` (`id`,`time_log`, `confirm`) VALUES (%s , %s, %s)"
						val_insert = (id_name[name],time_now.strftime('%Y-%m-%d %H:%M:%S'),None)
						#print(sql_insert)
						#print(val_insert)
						try:
							mycursor.execute(sql_insert,val_insert)
							mydb.commit()
							print(mycursor.rowcount, "record inserted.")
						except:
							print("Can not insert database !")
						#play sound
						pygame.mixer.music.load(path_sound[name])
						pygame.mixer.music.play()
						time.sleep(2)
						##########
					else:
						print("login again in time < 10 second, don't save here !")
				else:
					time_now = datetime.now()
					#initilize time
					list_name_dectect[name] = time_now.strftime('%Y-%m-%d %H:%M:%S')
					print("first time login, save data here !")
					#save
					name_table = "history_" + str(time_now.year) +"_" + str(time_now.month)
					try:
						mycursor.execute("CREATE TABLE `face_detect`.`"+name_table + "` (id VARCHAR(5), time_log DATETIME, confirm VARCHAR(20))")
					except:
						pass
					sql_insert = "INSERT INTO `face_detect`.`"+name_table+"` (`id`,`time_log`, `confirm`) VALUES (%s , %s, %s)"
					val_insert = (id_name[name],time_now.strftime('%Y-%m-%d %H:%M:%S'),None)
					#print(sql_insert)
					#print(val_insert)
					try:
						mycursor.execute(sql_insert,val_insert)
						mydb.commit()
						print(mycursor.rowcount, "record inserted.")
					except:
							print("Can not insert database !")
					#playsound
					pygame.mixer.music.load(path_sound[name])
					pygame.mixer.music.play()
					time.sleep(2)
			else:
				print("Detect unknown !")

except KeyboardInterrupt:
	pass
print(list_name_dectect)
print("Exiting...")
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()