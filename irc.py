import socket
import sys
import time
import ssl

#default setting
server = "irc.freenode.net" 
channel = "#programming"
botnick = "bot1"
password = " "
secretPhrase = "meme"
port = 6667
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #defines the socket

#user input setting
botnick = raw_input("Please enter bot name\n")
password = raw_input("If you nick is not registered press none\n")
server = raw_input("Please enter the hostname\n")
channel = raw_input("Please enter the channel name\n")
secretPhrase = raw_input("Please enter the secretPhrase\n")
port = raw_input("Please enter the port number\n")

def connecting():
	print "connecting to:"+server
	irc.connect((server, int(port)))                                                         #connects to the server
	irc.send("USER "+ botnick +" "+ "localhost" +" "+ "localhost" +" :meme bot\n") #user authentication
	irc.send("NICK "+ botnick +"\n")                            #sets nick
	if password != "none":
		irc.send("nickserv identify " + botnick + " " + password +"\r\n")    #auth
	irc.send("JOIN "+ channel +"\n")        #join the chan

#def cctp():
#	if text.find('PING') != -1:                        
#		irc.send('PONG ' + text.split() [1] + '\r\n') #returnes 'PONG' back to the server (prevents pinging out!)	

def main():
	timer = [1,2,3,4,5]
	connecting()
	
	while 1:    #puts it in a loop
		text=irc.recv(2040)  #receive the text
		print text   #print text to console

		#ping
		if text.find('PING') != -1:                        
			irc.send('PONG ' + text.split() [1] + '\r\n') #returnes 'PONG' back to the server (prevents pinging out!)	
		
		#rejoin after kick
		if text.find('KICK') != -1:
			for item in timer:
				irc.send("JOIN "+ channel +"\n")
				
		#Secret Phrase
		if text.find(secretPhrase) != -1:
			irc.send("privmsg " + channel + " :Did I just hear the word " + secretPhrase +"\n")
	

main()
