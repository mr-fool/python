#python3 client.py [write/read] filename hostname:port [aes128,aes256,null] key
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
import string 
import random
import hashlib
import fileinput
import binascii
import codecs
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes)
site = ''
destport = 0
portnum = 0
option = ''
randomport = None
command = ''
filename = ''
cipher = ''
key = ''
non = ''
backend = default_backend()
key128 = b'\x0eAP\xe1\xad9\x01\x1f\xb3g\xfdz)\xea\xec\xd4'
key256 = b'1@\xe8\xb5#J\x9f8\x82\xe2\xe6\x0f\xa3|\xb6\xaf\x86\x0e\xfc\xc4BP\xaf\xda\x16\x90nmPB\x01\xc0'
aesIv  = b'\x9c\xb9\x0b\xf8;\xcc\x17\x91n2\x97\xda\xc0<\x82h'
class MyTCPHandler():
        #aes128
        def weakEncrypt(self,ptext):
            pad = padding.PKCS7(128).padder()
            ptext = pad.update(ptext) + pad.finalize()

            alg = algorithms.AES(key128)
            mode = modes.CBC(aesIv)
            cipher = Cipher(alg, mode, backend=backend)
            encryptor = cipher.encryptor()
            ctext = encryptor.update(ptext) + encryptor.finalize()

            return ctext
        #aes256
        def encrypt(self,ptext):
            pad = padding.PKCS7(128).padder()
            ptext = pad.update(ptext) + pad.finalize()

            alg = algorithms.AES(key256)
            mode = modes.CBC(aesIv)
            cipher = Cipher(alg, mode, backend=backend)
            encryptor = cipher.encryptor()
            ctext = encryptor.update(ptext) + encryptor.finalize()

            return ctext
        def decrypt(self,key, iv, ctext):
            alg = algorithms.AES(key)
            mode = modes.CBC(iv)
            cipher = Cipher(alg, mode, backend=backend)
            decryptor = cipher.decryptor()
            ptext = decryptor.update(ctext) + decryptor.finalize()

            unpadder = padding.PKCS7(128).unpadder() # 128 bit
            ptext = unpadder.update(ptext) + unpadder.finalize()

            return ptext
        def handle(self):
                BUFFER_SIZE = 4096
                s = socket.socket()
                self.port = portnum
                self.nonce = non
                self.cipherMode = cipher
                #print(site)
                s.connect((site,self.port))
                s.settimeout(900)
                #print("the nonce is " + self.nonce)
                #send nonce
                s.sendall(bytearray(self.cipherMode+"!"+ self.nonce, "utf-8"))
                #generating iv
                hash_object = hashlib.sha256(key.encode('utf-8')+self.nonce.encode('utf-8')+"IV".encode('utf-8'))
                self.IV = hash_object.hexdigest()
                #print("IV=" +self.IV)
                #generating session-key
                hash_key = hashlib.sha256(key.encode('utf-8')+self.nonce.encode('utf-8')+"SK".encode('utf-8'))
                self.sessionKey = hash_key.hexdigest()
                #print ("SK=" +self.sessionKey)
                
                #Compare IV and session key
                comparison = s.recv(BUFFER_SIZE, socket.MSG_DONTWAIT)
                if len(comparison) == BUFFER_SIZE:
                        try:  # error means no more data
                                comparison = self.request.recv(BUFFER_SIZE, socket.MSG_DONTWAIT)
                        except:
                                print("cannot receive sk and iv from the server")


                comparison = comparison.decode("utf-8")
                split = comparison.split("!")
                serverIV = split[0]
                serverSessionKey = split[1]
                #print("serverIV is " + serverIV)
                #print("serverSessionKey is " + serverSessionKey)
                
                #bad key
                if self.IV != serverIV or self.sessionKey != serverSessionKey:
                    #print("Error: Wrong Key")
                    s.sendall(bytearray("bad","utf-8"))
                    sys.exit("Error: Wrong Key")
                #good key   
                if self.IV == serverIV and self.sessionKey == serverSessionKey:
                    #print("Good Key")
                    s.sendall(bytearray("good"+"!"+command+"!"+filename, "utf-8"))
                    
                #null cipher write
                if self.cipherMode == "null" and command == "write":

                   while True:
                        data = sys.stdin.buffer.read()
                        if  not data:
                            break
                        s.sendall(data)
                        print("OK", file=sys.stderr)
                #aes256 cipher write
                if self.cipherMode == "aes256" and command == "write":

                   while True:
                        data = sys.stdin.buffer.read()
                        if  not data:
                            break
                        locked = self.encrypt(data)
                        s.sendall(locked)
                        print("OK", file=sys.stderr)
                #aes128 cipher write
                if self.cipherMode == "aes128" and command == "write":

                   while True:
                        data = sys.stdin.buffer.read()
                        if  not data:
                            break
                        locked = self.weakEncrypt(data)
                        s.sendall(locked)
                        print("OK", file=sys.stderr)
                #null cipher read
                if self.cipherMode == "null" and command == "read":
                        buff = b""
                        size = b""
                        start = time.monotonic()
                        while len(size) < 4:
                            size += s.recv(1)
                        [size] = struct.unpack('!I', size)
                        while 1:
                            #print("Inside null read loop")
                            data = s.recv(size)
                            buff += data
                            #print ("buff in read loop: ", buff)
                            if  len(buff) == size:
                                #print("send completed at", time.monotonic() - start)
                                break
                        sys.stdout.buffer.write(buff)
                        print("OK", file=sys.stderr)
                #aes256 cipher read
                if self.cipherMode == "aes256" and command == "read":
                        buff = b""
                        size = b""
                        start = time.monotonic()
                        while len(size) < 4:
                            size += s.recv(1)
                        [size] = struct.unpack('!I', size)
                        while 1:
                            #print("Inside null read loop")
                            data = s.recv(size)
                            buff += data
                            #print ("buff in read loop: ", buff)
                            if  len(buff) == size:
                                #print("send completed at", time.monotonic() - start)
                                break
                        #sys.stdout.buffer.write(buff)
                        decoded = self.decrypt(key256,aesIv,buff)
                        sys.stdout.buffer.write(decoded)
                        print("OK", file=sys.stderr)

                #aes128 cipher read
                if self.cipherMode == "aes128" and command == "read":
                        buff = b""
                        size = b""
                        start = time.monotonic()
                        while len(size) < 4:
                            size += s.recv(1)
                        [size] = struct.unpack('!I', size)
                        while 1:
                            #print("Inside null read loop")
                            data = s.recv(size)
                            buff += data
                            #print ("buff in read loop: ", buff)
                            if  len(buff) == size:
                                #print("send completed at", time.monotonic() - start)
                                break
                        #sys.stdout.buffer.write(buff)
                        decoded = self.decrypt(key128,aesIv,buff)
                        sys.stdout.buffer.write(decoded)
                        print("OK", file=sys.stderr)
if __name__ == "__main__":
        if len(sys.argv) == 6:
                command = sys.argv[1]
                filename = sys.argv[2]
                split = sys.argv[3].split(":")
                site = split[0]
                portnum = int(split[1])
                if portnum not in range(0, 65535):
                        print ("port number out of range" + portnum)
                        sys.exit(1)
                cipher = sys.argv[4]
                key = sys.argv[5]
                non = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
                #print ("nonce is " + non)
        else:
                print ("Error: wrong command line arguments")
                sys.exit(1)

        HOST, PORT = '', portnum
        server = MyTCPHandler()
        try:
                server.handle()
        except KeyboardInterrupt:
                sys.exit(1)
