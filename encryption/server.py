#python3 server.py port key
from __future__ import print_function, unicode_literals
import struct
import os
import select
import signal
import socket, threading
import socketserver
import subprocess
import sys
import time
import random
import string
import hashlib
from time import localtime, strftime
#from binascii import unhexlify
#from binascii import hexlify
import binascii
import codecs
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes)
portnum = 0
key = ''

class MyTCPHandler(socketserver.BaseRequestHandler):
        BUFFER_SIZE = 4096
        def handle(self):

                while 1:
                        data = self.request.recv(self.BUFFER_SIZE)
                        if len(data) == self.BUFFER_SIZE:
                                while 1:
                                        try:  # error means no more data
                                                data += self.request.recv(self.BUFFER_SIZE, socket.MSG_DONTWAIT)
                                        except:
                                                break
                        if len(data) == 0:
                                break

                        data = data.decode("utf-8")
                        split = data.split("!")
                        self.cipher = split[0]
                        self.nonce = split[1]
                        print (strftime("%H:%M:%S",localtime())+ ": new connection from " + self.client_address[0], "cipher=", self.cipher)
                        print (strftime("%H:%M:%S",localtime())+ ": nonce=" +self.nonce)
                        #generating iv
                        hash_object = hashlib.sha256(key.encode('utf-8')+self.nonce.encode('utf-8')+"IV".encode('utf-8'))
                        self.IV = hash_object.hexdigest()
                        print (strftime("%H:%M:%S",localtime())+ ": IV=" +self.IV)
                        
                        #generating session-key
                        hash_key = hashlib.sha256(key.encode('utf-8')+self.nonce.encode('utf-8')+"SK".encode('utf-8'))
                        self.sessionKey = hash_key.hexdigest()
                        print (strftime("%H:%M:%S",localtime())+ ": SK=" +self.sessionKey)
                        
                        #send generated IV and SK
                        self.request.sendall(bytearray(self.IV+"!"+ self.sessionKey, "utf-8"))
                        
                        #check if the key is correct
                        checking = self.request.recv(self.BUFFER_SIZE)
                        checking = checking.decode("utf-8")
                        split = checking.split("!")
                        keyStatus = split[0]
                        if keyStatus == "bad":
                                print("status: error - bad key")
                                self.request.shutdown(1)
                                self.request.close()
                                os._exit(0)
                        if keyStatus == "good":
                                #print("key is good")
                                self.operation = split[1]
                                self.filename = split[2]
                                print (strftime("%H:%M:%S",localtime())+ ": command:" + self.operation + "," + " filename:" + self.filename)
                                
                                #null and write
                                if self.cipher == "null" and self.operation == "write":
                                    with open(self.filename, 'wb') as f:
                                        #print ('file opened')
                                        while True:
                                                try:
                                                        dataChunk = self.request.recv(600000)
                                                except:
                                                        break

                                                if len(dataChunk) == 600000:
                                                        while 1:
                                                                try:  # error means no more data
                                                                        #time.sleep(0.05)
                                                                        data2 = self.request.recv(600000, socket.MSG_DONTWAIT)
                                                                        if (len(data2) == 0):
                                                                                break
                                                                        dataChunk += data2
                                                                        #print(len(dataChunk))
                                                                except:
                                                                        break
                                                f.write(dataChunk)
                                                if (len(dataChunk)==0):
                                                        break

                                        f.close()
                                    print(strftime("%H:%M:%S",localtime())+ ': status: success')

                                #aes256 and write
                                if self.cipher == "aes256" and self.operation == "write":
                                    with open(self.filename, 'wb') as f:
                                        #print ('file opened')
                                        while True:
                                                try:
                                                        dataChunk = self.request.recv(600000)
                                                except:
                                                        break

                                                if len(dataChunk) == 600000:
                                                        while 1:
                                                                try:  # error means no more data
                                                                        #time.sleep(0.05)
                                                                        data2 = self.request.recv(600000, socket.MSG_DONTWAIT)
                                                                        if (len(data2) == 0):
                                                                                break
                                                                        dataChunk += data2
                                                                        #print(len(dataChunk))
                                                                except:
                                                                        break
                                                f.write(dataChunk)
                                                if (len(dataChunk)==0):
                                                        break

                                        f.close()
                                    print(strftime("%H:%M:%S",localtime())+ ': status: success')
                                #aes128 and write
                                if self.cipher == "aes128" and self.operation == "write":
                                    with open(self.filename, 'wb') as f:
                                        #print ('file opened')
                                        while True:
                                                try:
                                                        dataChunk = self.request.recv(600000)
                                                except:
                                                        break

                                                if len(dataChunk) == 600000:
                                                        while 1:
                                                                try:  # error means no more data
                                                                        #time.sleep(0.05)
                                                                        data2 = self.request.recv(600000, socket.MSG_DONTWAIT)
                                                                        if (len(data2) == 0):
                                                                                break
                                                                        dataChunk += data2
                                                                        #print(len(dataChunk))
                                                                except:
                                                                        break
                                                f.write(dataChunk)
                                                if (len(dataChunk)==0):
                                                        break

                                        f.close()
                                    print(strftime("%H:%M:%S",localtime())+ ': status: success')
                                #null and read
                                if self.cipher == "null" and self.operation == "read":
                                        if os.path.exists(self.filename):
                                                size = os.path.getsize(self.filename)
                                                self.request.sendall(struct.pack('!I', size))
                                                f = open(self.filename,'rb')
                                                lines = f.read().splitlines(True)
                                                f.close()
                                                for line in lines:
                                                        #try:
                                                        #    self.request.send(bytearray(line,'utf-8'))
                                                        #except:
                                                        self.request.sendall(line)
                                                print(strftime("%H:%M:%S",localtime())+ ": finish sending")
                                        else:
                                                print("Error: File "+ self.filename + " does not exist")
                
                                        #print("done sending")
                                #aes256 and read
                                if self.cipher == "aes256" and self.operation == "read":
                                        if os.path.exists(self.filename):
                                                size = os.path.getsize(self.filename)
                                                self.request.sendall(struct.pack('!I', size))
                                                f = open(self.filename,'rb')
                                                lines = f.read().splitlines(True)
                                                f.close()
                                                for line in lines:
                                                        #try:
                                                        #    self.request.send(bytearray(line,'utf-8'))
                                                        #except:
                                                        #print(line)
                                                        self.request.sendall(line)
                                                print(strftime("%H:%M:%S",localtime())+ ": finish sending")
                                        else:
                                                print("Error: File "+ self.filename + " does not exist")
                
                                        #print("done sending")
                                #aes128 and read
                                if self.cipher == "aes128" and self.operation == "read":
                                        if os.path.exists(self.filename):
                                                size = os.path.getsize(self.filename)
                                                self.request.sendall(struct.pack('!I', size))
                                                f = open(self.filename,'rb')
                                                lines = f.read().splitlines(True)
                                                f.close()
                                                for line in lines:
                                                        #try:
                                                        #    self.request.send(bytearray(line,'utf-8'))
                                                        #except:
                                                        #print(line)
                                                        self.request.sendall(line)
                                                print(strftime("%H:%M:%S",localtime())+ ": finish sending")
                                        else:
                                                print("Error: File "+ self.filename + " does not exist")
                
                                        #print("done sending")
  
if __name__ == "__main__":
        if len(sys.argv) == 3:
                portnum = int(sys.argv[1])
                key = sys.argv[2]
                print("Listening on Port " + str(portnum))
                print("Using secret key: " + key)
        else:
                print ("Error: wrong command line arguments")
                sys.exit(1)

        HOST, PORT = "localhost", portnum
        server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
        server.serve_forever()
