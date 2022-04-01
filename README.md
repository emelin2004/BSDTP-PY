# BSDTP - Bosnian Slow Data Transfer Protocol
---
## _Transfer data over Pi's GPIO to another Pi (But slowly and/or with light)_
---
This is a small project I did while I had some free time on hand.
It is a Python Script which enables two Raspberry Pis to transfer text (binary data) over the GPIO pins. (Not through RX and TX pins)
# What is the purpose for it?
There are probably way better and faster ways to achieve some kind of communication beetwen two Raspberries but this was a fun learning experience for me on how does the Pi's GPIO work and I learned some basic Python along the way, 
but I could think of a few reasons why:
- To (slowly) transmit text or binary data over light to a second Pi (lasers and photoresistors) (Circuit down below)
- To (again, slowly) transmit some data directly over GPIO pins

## How does this "Protocol" work?
It is actually very simple, it requires no clock signal (hence why it is slow and the reason why is it possible to use it to transmit data over laser impulses).

The way it works is so that both running instances of the script have the same set duration of the bit 1 impuls. Upon receiving the data the Pi (in this case) calculates how long did the impuls take. If the impuls took longer or the same lenght as the preset duration that means that the Pi has recieved a bit-1, if it was shorter than that, then that means that it was a bit-0.

All those bits are being saved into a buffer array and after the footer signal has been recieved, are converted to text or displayed as bytes (e.g. 01101000 01101001).

You can change that duration during the runtime in cli if you type "BITRATE()" or you can edit the Python script itself and change those values.

---

## Why this weird name?
I am really not creative when it comes to naming things, I though it would be funny if I name it this way just because I myself am Bosnian. 

## Example circuit
In this circuit I demonstrated how this protcol could be used.
In the picture I have used an Arduino Uno but the principle is the same as with the pi. (You can change the receive (RX) and transmit (TX) pins by editing the .py script yourself).

NOTE: By RX and TX I do not mean the RX and TX which the Pi already has, instead these names here are used to represent the pins on the GPIO through which the script will send and receive data. For some reason I just named them like that.

![N|Solid](https://cdn.emelinhabibovic.de/git/BSDTP-PY/examples/laser-communication/circuit.png)
(Made using  tinkercad.com) (Schematic can be found in the examples folder)

## Screenshots
CLI:
![N|Solid](https://cdn.emelinhabibovic.de/git/BSDTP-PY/examples/laser-communication/scr1.jpg)
Setting up and adjusting the positions of the receivers and lasers using "SETUP()" function
![N|Solid](https://cdn.emelinhabibovic.de/git/BSDTP-PY/examples/laser-communication/scr2.jpg)

## Info and other
Author: emelinhabibovic.de | Contact: contact@emelinhabibovic.de | Project Page: https://emelinhabibovic.de/github/BSDTP-Page.html

P.S., I mainly speak German, because of that sorry for any grammar mistakes you may stumble upon in this readme or in the code.

## License

GNU AGPLv3
https://choosealicense.com/licenses/agpl-3.0/
---
![N|Solid](https://cdn.emelinhabibovic.de/images/logo.svg)
