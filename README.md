# kodi-curses-remote

Simple remote control written in python for Kodi.

Following keys are supported:
 - right key : right, analogseekforward
 - left key : left, analogseekback
 - key up : up
 - key down : down
 - echap : back
 - enter : select, osd
 - tab : fullscreen
 - i : info
 - F8 : mute
 - + : volume up
 - - : volumedown
 - page up : page up, skip next
 - page down : page down, skip previous
 - backspace : backspace
 - space bar :  space

#Usage

`kodi-curses-remote.py --host=kodi-host --port=eventserver-port --httpport=jsonrpc-port`