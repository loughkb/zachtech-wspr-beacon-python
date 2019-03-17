#! /usr/bin/python
#my first python3 script from scratch.  I know it's probably simple
#and could be much neater, but it's a first effort
#script for programming the ZachTech LPT1 WSPR beacon
#written by Kevin Loughin, KB9RLW, March 2019
import time
import os.path
import serial

#defining variables I'll be using later
callsign = "null"
menuentry = ""
serialport = "null"
bands = ["D", "D", "D", "D", "D", "D", "D", "D", "D", "D", "D", "D", "D", "D"]

#defining functions I'll call later.

#serial detection procedure
def setserial():
    clearscreen()
    print("Plug in the device, wait 1 second and press enter.")
    os.sys.stdin.readline()
    exists = os.path.exists('/dev/ttyUSB0')
    if exists:
        print("Found ttyUSB0")
        time.sleep(1)
        ser = serial.Serial('/dev/ttyUSB0')
        s = ser.read(5)
        ser.close()
        if s == "{MIN}":
            print("Success!  Port is ttyUSB0")
            serialport = "/dev/ttyUSB0"
            return serialport

    exists = os.path.exists('/dev/ttyUSB1')
    if exists:
        print("Found ttyUSB1")
        time.sleep(1)
        ser = serial.Serial('/dev/ttyUSB1')
        s = ser.read(5)
        ser.close()
        if s == "{MIN}":
            print("Success!  Port is ttyUSB1")
            serialport = "/dev/ttyUSB1"
            return serialport

    exists = os.path.exists('/dev/ttyUSB2')
    if exists:
        print("Found ttyUSB2")
        time.sleep(1)
        ser = serial.Serial('/dev/ttyUSB2')
        s = ser.read(5)
        ser.close()
        if s == "{MIN}":
            print("Success!  Port is ttyUSB2")
            serialport = "/dev/ttyUSB2"
            return serialport

    exists = os.path.exists('/dev/ttyUSB3')
    if exists:
        print("Found ttyUSB3")
        ser = serial.Serial('/dev/ttyUSB3')
        s = ser.read(5)
        ser.close()
        if s == "{MIN}":
            print("Success!  Port is ttyUSB3")
            serialport = "/dev/ttyUSB3"
            return serialport

    time.sleep(2)    
    serialport = "null"
    return serialport

#check serial security function
def checksec(serialport):
    print("checking security of"), serialport
    time.sleep(2)
    security = os.access(serialport, os.R_OK|os.W_OK)
    if not security:
        clearscreen()
        print("Your username does not have access to serial ports.")
        print("You need to add your user to the dialout group.")
        print("Copy the line below, change your_username to your username and execute it in the terminal.")
        print("Then log out or restart and log back in to activate access.")
        print("")
        print("sudo adduser your_username dialout")
        exit()
    return security

#Print Menu and get choice function
def render_menu(menunum):
    if menunum == "main":
        clearscreen()
        printmain()
    menunum = input("Enter Menu item:")
    return menunum

#Clear Screen procedure
def clearscreen():
    count = 28
    while(count > 1):
        print("")
        count = count - 1

#Print main menu procedure
def printmain():
    print("Main Menu.  Device detected on "), serialport
    print("")
    print("0: exit program")
    print("1: Change current callsign.  >"), callsign
    print("2: Enable or disable bands")
    print("3: Change current live mode, wspr or sig gen.")
    print("4: Set startup mode")

#changecall procedure
def changecall(callsign):
    clearscreen()
    print("Current callsign:"), callsign
    print("")
    newcallsign = raw_input("Enter new callsign, use upper case:")
    newcallsign = newcallsign.rstrip()
    clearscreen()
    choice = "Change callsign from " + callsign + " to " + newcallsign + "? y or n:"
    choice = raw_input(choice)
    if choice == "y":
        print("Updating device with new callsign:")
        # open serial and flush junk
        serdata = "null"
        ser = serial.Serial(serialport)
        time.sleep(.5)
        ser.flushInput()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
        while serdata != "{CCM} N\r\n":        
            serdata = ser.readline()
            ser.write("[CCM] S N\r\n")
            time.sleep(.1)
        # sending new callsign to device
        serout = "[DCS] S " + newcallsign + "\r\n"
        while serdata[:5] != "{DCS}":        
            ser.write(serout)
            time.sleep(.1)
            ser.write("[DCS] G\r\n")
            time.sleep(.1)
            serdata = ser.readline()
            print(serdata)
        ser.write("[CSE] S\r\n")
        time.sleep(.1)
        ser.close()
        callsign = getcallsign()
        return callsign

#changebands procedure
def changebands():
    #open port and flush unneeded stuff
    serdata = "null"
    ser = serial.Serial(serialport)
    time.sleep(.5)
    ser.flushInput()
    ser.write("[CCM] S N\r\n")
    time.sleep(.1)
    while serdata != "{CCM} N\r\n":        
        serdata = ser.readline()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
    #Get current band status
    serdata = "null"
    while serdata[:5] != "{OBD}":
        ser.write("[OBD] G\r\n")
        time.sleep(.1)
        serdata = ser.readline()
    count = 1
    while count < 14:        
        bands[count] = serdata[9:].rstrip()
        serdata = ser.readline()
        count = count + 1
    ser.close()
    printbands()
    togglebands()
    clearscreen()
    #open port and flush unneeded stuff
    serdata = "null"
    ser = serial.Serial(serialport)
    time.sleep(.5)
    ser.flushInput()
    ser.write("[CCM] S N\r\n")
    time.sleep(.1)
    while serdata != "{CCM} N\r\n":        
        serdata = ser.readline()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
    print("Updating device with new configuration.")
    count = 1
    while count < 14:
        bcount = count - 1
        if bcount < 10:        
            serdata = "[OBD] S " + "0" + str(bcount) + " " + str(bands[count]) + "\r\n"
        else:serdata = "[OBD] S " + str(bcount) + " " + str(bands[count]) + "\r\n"
        ser.write(serdata)
        time.sleep(.1)
        count = count + 1
    ser.write("[CSE] S\r\n")
    time.sleep(.5)
    ser.close()
    
    time.sleep(2)
#printbands procedure
def printbands():
    clearscreen()
    print("Current bands Enabled or Disabled")
    print("")
    print("1:  2190m--->"), bands[1]
    print("2:  630m---->"), bands[2]
    print("3:  160m---->"), bands[3]
    print("4:  80m----->"), bands[4]
    print("5:  40m----->"), bands[5]
    print("6:  30m----->"), bands[6]
    print("7:  20m----->"), bands[7]
    print("8:  17m----->"), bands[8]
    print("9:  15m----->"), bands[9]
    print("10: 12m----->"), bands[10]
    print("11: 10m----->"), bands[11]
    print("12: 6m------>"), bands[12]
    print("13: 4m------>"), bands[13]

#togglebands procedure
def togglebands():
    bandnum = 1
    while bandnum != 0:
        printbands()
        bandnum = input("Enter band number to toggle, zero when done:")
        if bands[bandnum] == "D":
            bands[bandnum] = "E"
        else:bands[bandnum] = "D"

 
#changemode procedure
def changemode():
    clearscreen()
    print("Here we can set a current live mode.")
    print("Setting the device to none.")
    #open port and flush unneeded stuff
    serdata = "null"
    ser = serial.Serial(serialport)
    time.sleep(.5)
    ser.flushInput()
    ser.write("[CCM] S N\r\n")
    time.sleep(.1)
    while serdata != "{CCM} N\r\n":        
        serdata = ser.readline()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
    print("")
    print("Mode choices are:")
    print("")
    print("1: WSPR beacon on")
    print("2: Signal generator mode")
    print("3: Abort back to main menu")
    print("")
    mode = input("Mode choice? :")
    #wspr mode choice
    if mode == 1:            
        ser.write("[CCM] S W\r\n")
        time.sleep(.1)
        serdata = ser.readline()
        print("WSPR mode on, press enter to stop.")
        os.sys.stdin.readline()
        ser.write("[CCM] N\r\n")
        ser.close

    #siggen mode choice
    if mode == 2:
        clearscreen()
        print("Signal generator mode.")
        frequency = input("Enter frequency in Hertz:")
        rawfrequency = frequency * 100
        length = len(str(rawfrequency))
        padlen = 12 - length
        pad = ""
        while padlen > 1:
            pad = pad + "0"
            padlen = padlen -1
        outfrequency = pad + str(rawfrequency) 
        print("")
        print("Setting generator to "), frequency, "Hz"
        #open port and flush unneeded stuff
        serdata = "null"
        ser = serial.Serial(serialport)
        time.sleep(.5)
        ser.flushInput()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
        while serdata != "{CCM} N\r\n":        
            serdata = ser.readline()
            ser.write("[CCM] S N\r\n")
            time.sleep(.1)    
        #set generator on with frequency
        serdata = "null"    
        outstring = "[DGF] S " + str(outfrequency) + "\r\n"            
        ser.write(outstring)
        time.sleep(.1)
        ser.write("[CCM] S S\r\n")
        time.sleep(.1)
        print("Signal generator ON. Hit enter to abort.")
        os.sys.stdin.readline()
        while serdata != "{CCM} N\r\n":        
            serdata = ser.readline()
            ser.write("[CCM] S N\r\n")
            time.sleep(.1)

    time.sleep(2)

#changestartup procedure
def changestartup():
    #open port and flush unneeded stuff
    serdata = "null"
    ser = serial.Serial(serialport)
    time.sleep(.5)
    ser.flushInput()
    ser.write("[CCM] S N\r\n")
    time.sleep(.1)
    while serdata != "{CCM} N\r\n":        
        serdata = ser.readline()
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
    clearscreen()
    print("Set the power up default mode, WSPR, or None.")
    print("")
    print("1: WSPR")
    print("2: None")
    print("")
    choice = input("Choose power up mode:")
    if choice == 1:
        ser.write("[OSM] S W\r\n")
        time.sleep(.2)
        ser.write("[CSE] S\r\n")
        time.sleep(.2)
    else:
        ser.write("[OSM] S N\r\n")
        time.sleep(.2)
        ser.write("[CSE] S\r\n")
    ser.close

    time.sleep(2)

#get current callsign function
def getcallsign():
    serdata = "null"
    ser = serial.Serial(serialport)
    time.sleep(.5)
    ser.flushInput()
    ser.write("[CCM] S N\r\n")
    time.sleep(.1)
    while serdata != "{CCM} N\r\n":
        serdata = ser.readline()
        print(serdata)
        ser.write("[CCM] S N\r\n")
        time.sleep(.1)
    while serdata.startswith("{DCS}") != True:
        ser.write("[DCS] G\r\n")
        time.sleep(.1)
        serdata = ser.readline()
    callsign = serdata[6:].rstrip()
    ser.close()
    return callsign

#Main Program

#get serial port
serialport = setserial()

#check users security for port

security = checksec(serialport)


#get current callsign from device
callsign = getcallsign()

#Clear screen and get first menu input

while(menuentry != 0):
    menunum = "main"
    menuentry = render_menu(menunum)    
    if menuentry == 1:
        menuentry = 99        
        callsign = changecall(callsign)
    if menuentry == 2:
        menuentry = 99
        print("Standby while I read the current band settings.")
        changebands()
    if menuentry == 3:
        menuentry = 99
        changemode()
    if menuentry == 4:
        menuentry = 99
        changestartup()
    if menuentry != 0 and menuentry != 99:
        print("")
        print("Bad entry, I don't understand "), menuentry
        time.sleep(2)

print("User selected:", menuentry)
#end
