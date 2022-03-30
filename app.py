# External module imports
import RPi.GPIO as GPIO
import time
import binascii
from threading import Thread
import os
import zlib

clear = lambda: os.system('clear')

RX_PIN=6
TX_PIN=13 #pwm !
MASTER=False
INVERT_RX=False
INVERT_TX=True	#transistor dependant
WAIT_ON_START=False
poolTime = 0.03 #duration of the bit 1 impuls
bitSleep = 0.03 #duration of the time for the laser to sleep beetwen the bits

GPIO.cleanup()

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme

GPIO.setup(TX_PIN, GPIO.OUT) # Laser pin set as output
GPIO.setup(RX_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Sensor pin set as input

def readRX():
	if (INVERT_RX):
		return not GPIO.input(RX_PIN)
	else:
		return (GPIO.input(RX_PIN) == 1)

def setTX(state):	#false LOW, true HIGH
	if(INVERT_TX):
		GPIO.output(TX_PIN, GPIO.LOW if state else GPIO.HIGH)
	else:
		GPIO.output(TX_PIN, GPIO.HIGH if state else GPIO.LOW)
#GPIO.output(fanPin, GPIO.LOW)
#GPIO.output(fanPin, GPIO.HIGH)

#8 bytes per data block
print("Pulling TX Low")
setTX(False)
time.sleep(1)

#it should somehow get the speed of transmision and establish a link?
#send a impuls to the second py and wait for the response

if(WAIT_ON_START):
	if (MASTER):
		print("Sending an impuls...")
		setTX(True)	#pull high and wait for the back signal
		print("Waiting for response...")
		GPIO.wait_for_edge(RX_PIN, GPIO.FALLING if INVERT_RX else GPIO.RISING)
		#while (readRX() == False):
			#time.sleep(0.01)
		print("Got a response!")
		setTX(False)
		time.sleep(1) 	#sleep the same time as the slave
			
	else:
		print("Waiting for an impuls...")
		GPIO.wait_for_edge(RX_PIN, GPIO.FALLING if INVERT_RX else GPIO.RISING)
		#while (readRX() == False):
			#time.sleep(0.01)
		print("Got an impuls, sending back a response")
		setTX(True) #pull high and low after a sec
		time.sleep(1) #sleep the same time as the master
		setTX(False)


BUFFER=[]


#my own protocol #BSDTP #BosnianSlowDataTransferProtocol
#0 = start/end
#1 (t >= poolTime) = 1
#1 (t < poolTime) = 0
#1 (t > poolTime*2) = Call to recieve and clear buffer #to implement!
#on RX=1 get the start time
#wait until RX=0 and then get the endTime
#compare the time difference with poolTime
#check if the byte was 0 or 1 and push it to buffer
#if buffer length is 7 clear the buffer and print the buffer to cli

#https://stackoverflow.com/questions/7396849/convert-binary-to-ascii-and-vice-versa
def text_to_bits(text, encoding='utf-8', errors='surrogatepass'):
    bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
    return bits.zfill(8 * ((len(bits) + 7) // 8))

def text_from_bits(bits, encoding='utf-8', errors='surrogatepass'):
    n = int(bits, 2)
    return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

def waitForRead():
	GPIO.wait_for_edge(RX_PIN, GPIO.FALLING if INVERT_RX else GPIO.RISING)
	#read()

def read():
	#while True:
			#print("looping")
		#print("RX =>",pinState)
		#how to know when to read
		#wait for input to become high
		#measure how long it was high
		#if too long 1 if not 0
		#no signal means no data is being transfered
		#GPIO.wait_for_edge(RX_PIN, GPIO.RISING if INVERT_RX else GPIO.FALLING)
		#if(True):
		while True:	#fixes RecursionError:
			if(readRX() and not setupMode):	
				start = time.time()
				#print("HIGH")
				GPIO.wait_for_edge(RX_PIN, GPIO.RISING if INVERT_RX else GPIO.FALLING)
				#print("LOW")
				end = time.time()
				#while(readRX() is not False):
					#end = time.time()

				duration = end - start
				#print(duration)
				if(duration >= poolTime*2): #header or footer signal
					#print("END/START")
					if(len(BUFFER) > 0):
						#print("Data received:")
						#print(''.join(str(e) for e in BUFFER))
						try:
							print("=>",text_from_bits(''.join(str(e) for e in BUFFER)))
							#GPIO.wait_for_edge(RX_PIN, GPIO.RISING if INVERT_RX else GPIO.FALLING)	#wait now
						except ValueError:
							print("Error decoding data...")
						
					else:
						print("Receiving data...")
					BUFFER.clear() #clear buffer and preapre for incoming data
					
				elif (duration >= poolTime): #1
					BUFFER.append(1)
					#print(1)
				else:	#0
					BUFFER.append(0)
					#print(0)
					
				#read()
				#print(end - start,end,start)
				#if(len(BUFFER) == 7):
					#print(''.join(str(e) for e in BUFFER))
					#BUFFER.clear()
			#else:
			waitForRead()
		
def send(bytes):
	#send a header signal
	setTX(True)
	time.sleep(poolTime * 2)
	setTX(False)
	#send data
	tikSend(bytes)
	time.sleep(0.05) #wait for last byte to be recieved
	#send a footer signal
	setTX(True)
	time.sleep(poolTime * 2)
	setTX(False)
	askForInput()
	
#

setupMode = False
asked = False

def setupModeCall():
	while(setupMode):
		print("RX State => ",readRX())
		time.sleep(0.5)

def askForInput():
	global asked
	global setupMode
	global poolTime
	inp = input("<= " if asked else "Type your text which you want to send: ") 
	asked=True
	if(inp == "SETUP()"):
		clear()
		setupMode = True
		print("INFO: Entering setup mode...")
		time.sleep(0.5)
		print("Position both lasers and recievers acordingly")
		print("Values of the RX Pin will begin printing in 5s")
		print("Press Enter key to end setup mode\n")
		print("WARNING: Laser will light up in 5s!")
		time.sleep(5)
		setTX(True)
		thrd = Thread(target=setupModeCall);
		thrd.start()
		x = input("INFO: WAITING FOR Enter KEY TO BE PRESSED\n") #if 
		setupMode = False
		setTX(False)
		print("INFO: Setup mode finished.")
		time.sleep(2)
		clear()
		asked=False
		askForInput()
	elif(inp == "CLEAR()"):
		clear()
		askForInput()
	elif (inp == "EXIT()"):
		exit()
	elif(inp == "SETBITRATE()"):
		poolTime = float(input("Set the duration of the bit 1 impuls: "))
		askForInput()
	else:
		rawBytes = text_to_bits(inp)
		#compressedBytes = zlib.compress(inp.encode(),2)
		#print(rawBytes, "RAW")
		#print(compressedBytes, "zlib RAW")
		#askForInput()
		send(rawBytes)
	

#direct after TX gets pulled HIGH the reciever caputers the start time of it and waits until it is again pulled low
#if input byte is 1 = the TX High pull stays on the whole time
#if input byte is 0 = the TX High pull stayts less than the poolTime #in my test case half the time of poolTime
def tikSend(bytes):
	#print("<= Sending...")
	for c in bytes:
		#print(c)
		time.sleep(bitSleep)
		if (c == "1"):
			setTX(True)
			time.sleep(poolTime)
			setTX(False)
		else:
			setTX(True)
			time.sleep(poolTime/2)
			setTX(False)
			
clear()
Thread(target=read).start() #start this is anither thread so that it all works at the same time RX and TX
time.sleep(1)
askForInput()