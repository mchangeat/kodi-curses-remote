#!/usr/bin/python
#
# Copyright (c) 2017
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import sys, os
import curses 
import json
import getopt
import requests
from socket import *

actions = {
    curses.KEY_RIGHT : ["right", "analogseekforward"],
    curses.KEY_LEFT : ["left", "analogseekback"],
    curses.KEY_UP : ["up"],
    curses.KEY_DOWN : ["down"],
    27 : ["back"], # echap
    10: ["select", "osd"], # enter
    9 : ["fullscreen"], # tab
    105 : ["info"], # i
    curses.KEY_F8 : ["mute"], # m
    43 : ["volumeup"], # +
    45 : ["volumedown"], # -
    curses.KEY_PPAGE : ["pageup","skipnext"],
    curses.KEY_NPAGE : ["pagedown", "skipprevious"],
    curses.KEY_BACKSPACE : ["backspace"],
    32 : [""], # space bar
}


try:
    from kodi.xbmcclient import *
except:
    sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), '../../lib/python'))
    from xbmcclient import *

def usage():
    print "kodi-python-remote --host=XXX --port=XXX --httpport=XXX"
    print 'Example'
    print '\tkodi-python-remote --host=192.168.0.1 --port=9777 --httpport=8080'
    pass

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "?pa:v", ["help", "host=", "actionport=", "httpport="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    ip = "localhost"
    actionport = 9777
    httpport = 8080
    verbose = False
    r, c= os.popen('stty size', 'r').read().split()
    nbCols = int(c)
    for o, a in opts:
        if o in ("-?", "--help"):
            usage()
            sys.exit()
        elif o == "--host":
            ip = a
        elif o == "--actionport":
            actionport = int(a)
        elif o == "--httpport":
            httpport = int(a)
        else:
            assert False, "unhandled option"
    
    addr = (ip, actionport)
    sock = socket(AF_INET,SOCK_DGRAM)
    
    
    os.environ.setdefault('ESCDELAY', '25')
    screen = curses.initscr() 
    curses.noecho() 
    curses.curs_set(0) 
    screen.keypad(1) 

    try:
        typedText = ""
        readKodiCurrentState(nbCols, screen, httpport, ip)
        while True: 
            event = screen.getch() 
            #screen.addstr(0, 0, str(event)+ "    ")
            screen.refresh()

            action=False
            for e in actions:
                if e == event:
                    if e == curses.KEY_BACKSPACE:
                        typedText = typedText[:len(typedText)-1]
                    elif e == 32:
                        typedText = typedText + " "
                    elif e != 105: #i does not clear typedText
                        typedText = ""
                    action=True
                    for action in actions[e]:
                        sendAction(sock, addr, action, screen)
            
            if action == False or (event >= 65 and event <= 122):
                typedText = typedText + chr(event)
                sendCharacter(ip, httpport, typedText, screen)
            
            readKodiCurrentState(nbCols, screen, httpport)



    finally:
        curses.nocbreak();
        screen.keypad(0);
        curses.echo()
        curses.endwin()
        sock.close()

def readKodiCurrentState(nbCols, screen, httpport, ip):
	time.sleep(0.3)
	r = requests.post("http://" + ip + ":" + str(httpport)+"/jsonrpc", data='{ "jsonrpc": "2.0", "method": "GUI.GetProperties", "params": { "properties" : ["currentwindow","currentcontrol"] }, "id": 1 }')
	js = json.loads(r.text)
	screen.addstr(1,0, js["result"]["currentwindow"]["label"].ljust(nbCols))
	screen.addstr(2,0, " ".ljust(nbCols),curses.A_UNDERLINE)
	screen.addstr(3,0, js["result"]["currentcontrol"]["label"].ljust(nbCols))

def sendAction(sock, addr, action, screen):
	#screen.addstr(1, 0, action+"              ")
	#screen.refresh()
	packet = PacketACTION(actionmessage=action, actiontype=ACTION_BUTTON)
	packet.send(sock, addr)

def sendCharacter(ip, httpport, character, screen):
	r = requests.post("http://" + ip + ":" + str(httpport)+"/jsonrpc", data='{"jsonrpc":"2.0","method":"Input.SendText","params":{"text": "'+character+'","done":false},"id":1}')
	#screen.addstr(2,0, r.text)
	
if __name__=="__main__":
    main()
