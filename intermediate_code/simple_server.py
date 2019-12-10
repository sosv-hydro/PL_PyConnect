import socket
import threading
import sys
import pickle

class Server():
	"""docstring for Server"""
	def __init__(self, host="", port=4000):

		self.clientList = []
		self.userCount = 0

		self.servHost = host
		self.servPort = port

		self.userLimit = 4
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.bind((str(host), int(port)))
		self.sock.listen(10)
		self.sock.setblocking(False)

		self.accept = threading.Thread(target=self.acceptCon)
		self.process = threading.Thread(target=self.processCon)
		
		self.accept.daemon = True
		self.accept.start()

		self.process.daemon = True
		self.process.start()

	# changes limit of clients connected
	def changeClientLimit(self, num):
		if(num >= 2 and num <= 10 and num > len(self.clientList)):
			print("changed client limit to "+ str(num))
			self.userLimit = num
		else:
			print("*** got to have at least 2 connections and less than 10. \n Also, must be more than current total of connected clients: ", str(len(self.clientList)))

	# close connection
	def closeCon(self):
		print("close server connection")
		self.sock.close()
		sys.exit()
	
	# looks up specific client
	def lookUpClient(self, client):
		for c in self.clientList:
			try:
				if c['username'] == client:
					return True
				else:
					return False
			except:
				print("server does not have clients connected")

	# gets clients from client list
	def getClientsList(self):
		message = ''
		if(len(self.clientList) == 0):
			return "no clients are connected"
		else:
			for c in self.clientList:
				message += c['username'] + ', '
			return message

	# call to provide the server info (address and port)
	def getServerInfo(self):
		host = str(self.servHost)
		if (not host):
			host = "all"
		message = "server address: "+ host +", port: "+ str(self.servPort)
		return message

	# prints client list
	def showClientsList(self):
		print(self.getClientsList())
	
	def showServerInfo(self):
		print(self.getServerInfo())

	# close a specific client connection
	def closeClientCon(self, client):
		for c in self.clientList:
			try:
				if c['username'] == client:
					c['conn'].close()
					sys.exit()
			except:
				print("client is no longer connected")

	# send a message to all clients connected to the server fom a client
	def msg_to_all(self, msg, client):
		for c in self.clientList:
			try:
				if c['conn'] != client['conn']:
					new_msg = pickle.dumps(client['username'] + ": "+ pickle.loads(msg))
					c['conn'].send(new_msg)
			except:
				self.clientList.remove(c)
	
	# send a message to a specific client
	def msg_to_specific_client(self, msg, client, source):
		for c in self.clientList:
			if c['username'] == client:
				new_msg = pickle.dumps(source['username'] + ": "+ msg)
				c['conn'].send(new_msg)

	# send message to all clients from the server
	def msg_to_all_from_server(self, msg):
		if(len(self.clientList) == 0):
			print("no clients connected")
		else:
			for c in self.clientList:
				try:
					new_msg = pickle.dumps( "server: "+ msg)
					c['conn'].send(new_msg)
				except:
					print("error sending message to clients")


	# accept connection
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

	def sendServerInfo(self, client):
		message = self.getServerInfo()
		client['conn'].send(pickle.dumps(message))

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
						elif(data and message[0] == 'getServInfo'):
							self.sendServerInfo(c)
						elif data:
							print("received : " + pickle.loads(data) )
							self.msg_to_all(data,c)
					except:
						pass

#s = Server()