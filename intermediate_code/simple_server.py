import socket
import threading
import sys
import pickle

class Server():
	"""docstring for Server"""
	def __init__(self, host="", port=4000):

		self.clientList = []
		self.userCount = 0

		self.userLimit = 4
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((str(host), int(port)))
		self.sock.listen(10)
		self.sock.setblocking(False)

		accept = threading.Thread(target=self.acceptCon)
		process = threading.Thread(target=self.processCon)
		
		accept.daemon = True
		accept.start()

		process.daemon = True
		process.start()

#		while True:
#			msg = input('->')
#			if msg == 'exit':
#				self.sock.close()
#				sys.exit()
#			else:
#				pass

	def changeClientLimit(self, num):
		if(num >= 2 and num <= 10 and num > len(self.clientList)):
			print("changed client limit to "+ str(num))
			self.userLimit = num
		else:
			print("*** got to have at least 2 connections and less than 10. \n Also, must be more than current total of connected clients: ", str(len(self.clientList)))

	def closeCon(self):
		print("close server connection")
		self.sock.close()
		sys.exit()
	
	def lookUpClient(self, client):
		for c in self.clientList:
			try:
				if c['username'] == client:
					return True
				else:
					return False
			except:
				print("server does not have clients connected")

	def getClientsList(self):
		message = ''
		if(len(self.clientList) == 0):
			return "no clients are connected"
		else:
			for c in self.clientList:
				message += c['username'] + ', '
			return message

	def showClientsList(self):
		print(self.getClientsList())

	def closeClientCon(self, client):
		for c in self.clientList:
			try:
				if c['username'] == client:
					c['conn'].close()
			except:
				print("client is no longer connected")

	def msg_to_all(self, msg, client):
		for c in self.clientList:
			try:
				if c['conn'] != client['conn']:
					new_msg = pickle.dumps(client['username'] + ": "+ pickle.loads(msg))
					c['conn'].send(new_msg)
			except:
				self.clientList.remove(c)
	
	def msg_to_specific_client(self, msg, client, source):
		for c in self.clientList:
			if c['username'] == client:
				new_msg = pickle.dumps(source['username'] + ": "+ msg)
				c['conn'].send(new_msg)

	
	def msg_to_all_from_server(self, msg):
		if(len(self.clientList) == 0):
			print("no clients connected")
		else:
			for c in self.clientList:
				try:
					new_msg = pickle.dumps(msg)
					c['conn'].send(new_msg)
				except:
					print("error sending message to clients")

	def acceptCon(self):
		print("accepting new clients")
		while True:
			try:
				conn, addr = self.sock.accept()
				if(self.userCount < self.userLimit):
					self.userCount += 1
					conn.setblocking(False)
					username = "user" + str(self.userCount)
					self.clientList.append({'username': username, 'conn': conn})
					print(username, " Just joined chat !")
					conn.send(pickle.dumps("allowCon,"+username))
				else:
					conn.send(pickle.dumps("closeCon"))
					conn.close()
			except:
				pass

	def sendClientList(self, client):
		message = self.getClientsList()
		client['conn'].send(pickle.dumps(message))

	def processCon(self):
		print("processing requests")
		while True:
			if len(self.clientList) > 0:
				for c in self.clientList:
					try:
						data = c['conn'].recv(1024)
						message = pickle.loads(data).split(",")
						if(data and message[0] == 'getClients'):
							self.sendClientList(c)
						elif(data and message[0] == 'sendSpecMessage'):
							print(message)
							self.msg_to_specific_client(message[2],message[1], c)
						elif data:
							print("received : " + pickle.loads(data) )
							self.msg_to_all(data,c)
					except:
						pass

#s = Server()