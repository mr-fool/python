#python proxy.py -raw 2001 www.google.com 80
#python3 proxy.py -auto32 2001 loalhost 22
#python3 proxy.py [logOption] [replaceOption] scrPort Server dstPost
import socket
import sys
import select
import re
import string
import time
import threading
import errno
from socket import error as socket_error

bufsize = 1024

class portForward:
	def __init__(self):
		self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	def start(self, host, port):
		try:
			self.forward.connect((host, port))
			return self.forward
		except Exception as e:
			print (e)
			return False

class ServerClass:
	#defining flags
	#global raw
	#global strip
	#global hexdump
	#global autoN
	#global replace
	#global replaceOpt1
	#global replaceOpt2
	raw = False
	strip = False
	hexdump = False
	autoN = False
	replace = False
	datastream = []
	channels = {}
	client_sockets = []
	server_sockets = []


	def __init__(self, host, port, replaceOpt1, replaceOpt2):
		dstPort = int(sys.argv[-1])
		server = sys.argv[-2]
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind((host, port))
		self.server.listen(200)
		self.opt1 = replaceOpt1
		self.opt2 = replaceOpt2
		print ("Port logger running: scrPort=",port,"host=",server,"dstPort=",dstPort)
		print ("New connection:",time.ctime(),"from localhost")
		
	#def replace(replaceOpt1, replaceOpt2):
		#print("replacement function is being called")

	def StartListening(self):
		self.datastream.append(self.server)
		while 1:
			#time.sleep(delay)
			ss = select.select
			inputready, outputready, exceptready = ss(self.datastream, [], [])
			for self.s in inputready:
				if self.s == self.server:
					self.on_accept()
					break

				self.data = self.s.recv(bufsize)
				if len(self.data) == 0:
					self.on_close()
					break
				else:
					self.on_recv()
					
	def on_accept(self):
		forward = portForward().start(sys.argv[-2], int(sys.argv[-1]))
		clientsock, clientaddr = self.server.accept()
		if forward:
			print (clientaddr, "connected")
			self.datastream.append(clientsock)
			self.datastream.append(forward)

			self.client_sockets.append(clientsock)
			self.server_sockets.append(forward)

			self.channels[clientsock] = forward
			self.channels[forward] = clientsock
		else:
			print ("Can't establish connection with the server.",)
			print ("Closing connection", clientaddr)
			clientsock.close()
			
	def on_close(self):
		print (self.s.getpeername(), "has disconnected")
		self.datastream.remove(self.s)
		self.datastream.remove(self.channels[self.s])
		out = self.channels[self.s]
		self.channels[out].close()		# close client connection
		self.channels[self.s].close()	# close server connection
		del self.channels[out]
		del self.channels[self.s]
		
	def userInput(self):
		self.raw = False
		self.strip = False
		self.hexdump = False
		self.autoN = False
		self.replace = False
		self.chunk = 0
		srcPort = int(sys.argv[-3])
		server = sys.argv[-2]
		dstPort = int(sys.argv[-1])
		#parser = argparse.ArgumentParser()
        #parser.add_argument('-auto', action='append', type=int)
		#check if logOptions are true
        
		if "-raw" in sys.argv:
			self.raw = True
			#print("raw value is",raw)
		if "-strip" in sys.argv:
			self.strip = True
			#print("strip value is",strip)
            
		if "-hex" in sys.argv:
			self.hexdump = True
			#print("hex value is",hexdump)
				
		#checking -autoN
		for x in sys.argv[0:]:
			#print("the argv value",x)
			if re.match("-auto*", x):
				auto,chunk = x.split("o")
				self.autoN = True
				self.chunk = chunk
				#print("autoN value is",self.autoN)
				#print("chuck value is", self.chuck)
		
		if "-replace" in sys.argv:
			self.replace = True
			index = sys.argv.index("-replace")
            #print ("index number %d\n",index)
			self.opt1 = sys.argv[index+1]
			self.opt2 = sys.argv[index+2]
			#print ("replace opt1 %s replace opt2 %s" %(self.opt1,self.opt2))
			#replace(replaceOpt1,replaceOpt2)
	def split_every(self,n, s):
		return [ s[i:i+n] for i in range(0, len(s), n) ]

	def on_recv(self):
		data = self.data
		server = sys.argv[-2]

		#parse and/or modify the data before send forward

		word = data.decode('utf-8','ignore')
		self.userInput()
		#print("the strip value", strip)
		arrow = ""

        # prepend arrow
		if self.channels[self.s] in self.server_sockets:
			arrow = "-->"
		else:
			arrow = "<--"
		#single option cases 
		if self.strip == True and self.replace == False:
			word =''.join(c if c in string.printable else '.' for c in word)
			print (self.insert_arrows(word,arrow))

		elif self.opt1 in word and self.replace == True:
			#print("self.opt1 is ",self.opt1)
			mod = word.replace(self.opt1,self.opt2)
			print(self.insert_arrows(mod,arrow))
		elif self.hexdump == True and self.replace == False:
			word =''.join(hex(ord(x))[2:] for x in word)
			print (self.insert_arrows(word,arrow))
			
		elif self.raw == True and self.replace == False:
			print(self.insert_arrows(data.decode('utf-8','ignore'),arrow))
			
		elif self.autoN == True and self.replace == False: #will come back to it
			#print( self.split_every(int(self.chunk), word))
			#print(self.insert_arrows(mod,arrow))
			myList = self.autoN_insert_arrows(word, arrow)
			for items in myList:
				print(items.encode('utf-8'))
		#cases with replace option
		elif self.strip == True and self.replace == True:
			word =''.join(c if c in string.printable else '.' for c in word)
			mod = word.replace(self.opt1,self.opt2)
			print(self.insert_arrows(mod,arrow))
		elif self.hexdump == True and self.replace == True:
			word =''.join(hex(ord(x))[2:] for x in word)
			mod = word.replace(self.opt1,self.opt2)
			print(self.insert_arrows(mod,arrow))
		elif self.raw == True and self.replace == True:
			mod = data.decode('utf-8','ignore').replace(self.opt1,self.opt2) 
			print(self.insert_arrows(mod,arrow))
		elif self.autoN == True and self.replace == True: #will come back to it
			mod = word.replace(self.opt1,self.opt2)
			myList = self.autoN_insert_arrows(mod, arrow)
			for items in myList:
				print(items.encode('utf-8')	)
		self.channels[self.s].send(data)
		
	def autoN_insert_arrows(self, data, arrow):
		splitted = data.split("\n")
		out_string = ""

		for line in splitted:
			out_string += arrow + " " + line + "\n"
		
		mod = self.split_every(int(self.chunk), out_string)
		return mod
	
	def insert_arrows(self, data, arrow):
		splitted = data.split("\n")
		out_string = ""

		for line in splitted:
			out_string += arrow + " " + line + "\n"

		return out_string

			
if __name__ == "__main__":
	if len(sys.argv) < 3:
		print ("Format : [logOption] [replaceOption] scrPort Server dstPost")
	else:

		srcPort = int(sys.argv[-3])
		server=ServerClass("localhost",srcPort,"none","none")
		try:
			server.StartListening()
		except KeyboardInterrupt:
			print ("Conection closed.")
sys.exit(1)
