#Liam Mitchell
#12/11/2018
#Autonomous Vehicle Express Lanes Project
#This python file must remain in the folder inorder for the RFID reader to work accordingly
#!/usr/bin/env python
import RPi.GPIO as GPIO #import all these cool widgets, some need to be downloaded
import SimpleMFRC522
import os
import time
import datetime
import sys
import re
import subprocess
import thread
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

reader = SimpleMFRC522.SimpleMFRC522() #Declare variable used to call RFID reader


#SERVER SIDE LIST, UPDATES LIST FROM OTHER RPi through SSH, (keygenned for passwordless entry)
#keylessSSH.txt should be attatched to help with future tutorials for SSH (can get confusing)
cmd = os.popen('scp pi@141.209.167.235:/home/pi/MFRC522-python/ServerFiles/uDatabase.txt /home/pi/MFRC522-python/Database.txt')
cmd.read()
cmd.close() #close file to help processing
i=0 #Must declare i=0 for key/id validation loop

#CAMERA MODULE
def takePicture(i): #Take picture of using camera & puts it in webcam folder
    if (i==5):
        i = "Car did not scan RFID or took too long"
    elif (i==2):
        i = "Car had an Invalid ID not in database or out of time"
    # read the absolute path
    script_dir = os.path.dirname("/home/pi/MFRC522-python/webcam/")
    # call the .sh to capture the image
    os.system('./webcam.sh')
    #get the date and time, set the date and time as a filename.
    currentdate = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    # create the real path
    rel_path = currentdate +".jpg"
    #  join the absolute path and created file name
    abs_file_path = os.path.join(script_dir, rel_path)
    print(abs_file_path) 
    
    fromaddr = "avelstation0.1@gmail.com"
    toaddr = "avelstation0.0@yahoo.com"

    msg = MIMEMultipart()
     
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Illegal car in Express Lane" #Maybe add an array if in big while loop
  
    body = (currentdate + " " + i)
     
    msg.attach(MIMEText(body, 'plain'))
     
    filename = rel_path
    attachment = open(abs_file_path, "rb")
     
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
     
    msg.attach(part)
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, "***************") #Password
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    print("Authorities Alerted")
    server.quit()


def stringSearcher(id): #searches database text file that contains all users unique ID's paired with their cars & Information
        f = open("Database.txt", "r")
        currentLine = f.readline()
        for line in f:
                if re.match(id, line):      # Uses the match function from re.match(), because of characters in string, and length of string
                    id1, timeLeft = line.split(',')
                    f.close()
                    return id1, timeLeft


##RFID READER CODE:
def reader_with_tLimit(prompt, timeout=1.5): #timeout is very delayed apparently 2.35=5ish seconds in real time, can change later
    print("Waiting for scan \n") #Prompting car to scan RFID tag for demonstration purposes
    timer = threading.Timer(timeout, thread.interrupt_main)
    try:
        i=5 #5=Timeout if RFID is not read, (stays the same)
        timer.start() #Begin timeout="Amount of seconds" timer
        id, text = reader.read() #Scans RFID badge and assigns read values to id and text
        id=str(id) #Need to convert id to a string so we can search for it in database
        id1, timeLeft = stringSearcher(id) #calls stringSearcher definition, searching for str(id), also returns values for variables
        timeLeft=int(timeLeft)
        #The following if statement will actually be a check/request with
        #a database that will contain all users with valid amounts of EL time
        if (id==id1): #Compares
            if (timeLeft>0):
                i=1 #1=Good/Valid
            elif (timeLeft<=0):
                i=2
            timer.cancel() #stops timer
        elif (id!=id1): 
            i=3 #3=Bad/Invalid
            timer.cancel()
    except KeyboardInterrupt:
        timer.cancel()
        pass
    finally:
        GPIO.cleanup() #Cleanup GPIO
        timer.cancel() 
    timer.cancel() #This is here because it code doesn't seem to work without it
    return i

while True:
    ##FSR (FORCE SENSITVE RESISTOR):
    ##Using a comparator through Op-Amp to read a High input on Rpi GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.IN) #Declare GPIO(pin 4) as input we will use for FSR 
    print("Waiting for next car to pass...") #Prompting car to drive over FSR for demonstration purposes
    while True: #Loops until recieves pressure input
        if (GPIO.input(4) == 1): #GPIO(pin 4) recieves a HIGH signal when FSR recieves any sort of pressure, (0-3.4)V
            cmd = os.popen('scp pi@141.209.167.235:/home/pi/MFRC522-python/ServerFiles/uDatabase.txt /home/pi/MFRC522-python/Database.txt')
            cmd.read()
            cmd.close()
            print("Car has triggered FSR") #Shows that the car has triggered the FSR for demonstration purposes
            break


    #COMPARATOR Will take input from 'i' from SQL server
    while True: 
        i = reader_with_tLimit(i) #calls the timer definition, and asks for its return value 'i'
        if (i==5): #Car did not scan RFID or took too long
            print("Time limit exceeded - Taking picture") #Prints for demonstration purposes
            takePicture(i) #calls takePicture Definition
            break #Ends loop
        elif (i==2): #Car had an Invalid ID not in database or out of time
            print("Invalid ID or No Purchased Time - Taking picture") #Prints for demonstration purposes
            takePicture(i)
            break
        else: #i=1, but don't need an elif for this as it does not meet other branch statements comparators
            print("Valid ID") #Prints for demonstration purposes
            break
