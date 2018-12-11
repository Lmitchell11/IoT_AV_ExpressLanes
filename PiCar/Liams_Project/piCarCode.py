#Liam Mitchell
#12/11/2018
#Runs on SunFounder PiCar -s
import RPi.GPIO as GPIO
import time
import re
import os
import picar
from front_wheels import Front_Wheels
from back_wheels import Back_Wheels

turn_duration = 1 #1 seconds
speed= 75 #Half speed  
back_wheels = Back_Wheels()  
front_wheels = Front_Wheels()
userID="487616678089" #Can change user RFID tag depending on which card you want to attatch to the vehicle 
t="0" #initializing time 't'
timeLeft="0" #initializing time placeholder 'timeLeft'

def stringSearcher(userID, t, i): #searches uDatabase text file on server side
    #To read file from server using SSH
    cmd = os.popen('scp pi@141.209.167.235:/home/pi/MFRC522-python/ServerFiles/uDatabase.txt /home/pi/Liams_Project/uDatabase.txt')
    cmd.read()
    cmd.close()
    
    fileContent= [] #initializes array for holding overwritten lines
    with open("uDatabase.txt", "r+") as f: #Reading file downloaded from server
        for line in f:
            newLine = line
            if re.match(userID, line):      # Uses the match function from re.match(), because of characters in string, and length of string
                global timeLeft
                id1, timeLeft = line.split(',')
                if (i==0): #Checks if this is first time going through iteration from the one added time block
                    t=int(t)+int(timeLeft) #Adds time on account and time bought together
                    t=str(t)
                newLine = id1 + ',' + t #Assigns updated time 't' to newLine
            fileContent.append(newLine)
        with open("uDatabase.txt", "w+") as f:
            for line in fileContent:
                f.write(line) #Overwrites lines in the file
            f.close() #closes file so it can be sent through SSH
            #To Write file to Server using SSH
            os.system("scp /home/pi/Liams_Project/uDatabase.txt pi@141.209.167.235:/home/pi/MFRC522-python/ServerFiles/uDatabase.txt")
        return t
                
            
def mergeDrive(t): #Driving instructions for piCar
    while True:
        try:
            t=int(t) #makes time 't' into a value 'int' which can be used for timing
            front_wheels.turn_straight() #Turns front wheels straight for 1 second   
            front_wheels.turn_left() #Turns front wheels Left for 1 second                      
            back_wheels.forward(speed, turn_duration) #Tells car how fast and long it can drive 
            front_wheels.turn_right()
            back_wheels.forward(speed, 0.75*turn_duration) 
            front_wheels.turn_straight()
            back_wheels.forward(speed, t)
            front_wheels.turn_right() #Turns front wheels Right for 1 second 
            back_wheels.forward(speed, 0.5*turn_duration)
            front_wheels.turn_left()
            back_wheels.forward(speed, 0.75*turn_duration) 
            front_wheels.turn_straight()
            back_wheels.forward(speed, turn_duration)
            back_wheels.stop() #Drive wheels stop
            back_wheels.backward(speed, (4.5*turn_duration/2+t)) #Car rolls backwards to start for demonstration purposes
            back_wheels.stop()
            GPIO.cleanup() #cleans up GPIO for next loop
            break
        except KeyboardInterrupt: #Keep this in here, good for dev 
            back_wheels.stop()
            GPIO.cleanup()
            front_wheels.turn_straight()
            break
    return t


while True: #Loop will not break unless only bottom button is pushed
    while True: #Loop will break once time block selection is finished
        t="0"
        i=0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        if (GPIO.input(5)==GPIO.HIGH): #B5
            time.sleep(0.5) #Sleep so button doesn't get pushed 1000 times in a split second
            t="5" #This would be 15 minutes, but for demonstration purposes and modeling space, it is only 1 second, so are the following times, etc.
            t = stringSearcher(userID,t,i) #Searches for userID, and adds time 't' to timeLeft on account
            t = mergeDrive(t)
            i=i+1 #Iterate once so we can clear text file after drive is done
            t="0" #Resets time back to 0 once all time is used
            print(t) #Shows user in terminal
            t = stringSearcher(userID,t,i) #Go back to loop, this time to update that the user's time has run out
            print("Buy more time")
        elif (GPIO.input(6)==GPIO.HIGH): #B6
            time.sleep(0.5)
            t="10"
            t = stringSearcher(userID,t,i)
            t = mergeDrive(t)
            i=i+1
            t="0"
            print(t)
            t = stringSearcher(userID,t,i)
            print("Buy more time")
        elif (GPIO.input(13)==GPIO.HIGH): #B13
            time.sleep(0.5)
            t="20"
            t = stringSearcher(userID,t,i)
            i=i+1
            t = mergeDrive(t)
            i=i+1
            t="0"
            print(t)
            t = stringSearcher(userID,t,i)
            print("Buy more time")
        elif (GPIO.input(19)==GPIO.HIGH): #B26
            time.sleep(0.5)
            mergeDrive(t)
            t="0" #Add no time and use remainder, or error buy time
            print(t)
            print("You are out of time, Thanks")
            break
    break
