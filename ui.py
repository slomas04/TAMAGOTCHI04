###### IMPORTS ######

import tkinter as tk        # for user interface
import faces
import time as t
import psutil as p          # For monitoring CPU and peripherals
import os
import datetime as dt
import csv as c

###### GLOBALS ######

LOGGING = True
R = '\033[91m'                  # Red Text
B = '\033[94m'                  # Blue Text
G = '\033[92m'                  # Green Text
W = '\033[0m'                   # White Text

def uilog(phrase): #replaces print function, end user should not be able to see the terminal anyway.
    if (LOGGING == True): #printing also uses precious CPU space, so having it easily disabled is a benefit.
        print(R + "[ LOG ] - " + G + "[ INTERFACE ] - " + B + str(phrase) + W) #prints out a formatted log message

def makearr(a): #Makes array of a CSV file
    r = []
    for row in a:
        r.append(row)
    return r



def __uirun__():
    startTime = dt.datetime.now()
    
    uilog("HELLO WORLD!")
    uilog("Setting Window variables...")
    
    window = tk.Tk()  # Init main window
    window.geometry("640x480") # set resolution
    
    ## Setting Vars

    emotion = tk.StringVar()
    emotion.set(faces.facearr[2])
    
    vhappiness = tk.StringVar()
    vhappiness.set("Happiness: ")

    vhunger = tk.StringVar()
    vhunger.set("Hunger: ")

    totalScanned = tk.StringVar()
    totalScanned.set("Total Scanned: ")
    
    currentScan = tk.StringVar()
    currentScan.set("Currently Scanning: ")
    
    shakesTaken = tk.StringVar()
    shakesTaken.set("Total shakes taken: ")
    
    vuptime = tk.StringVar()
    vuptime.set("Uptime: ")
    
    vbattery = tk.StringVar()
    vbattery.set("Battery Left: ")
    
    vcpu = tk.StringVar()
    vcpu.set("CPU usage: ")
    
    ## Defining objects

    face = tk.Label(window, textvariable=emotion, font=("Monospace", 15))
    face.grid(column=0, row=0, padx=10, pady=10) #label and pack the face
    
    frame1 = tk.Frame(window)
    frame1.grid(row=0, column=1, padx=10, pady=10) # Name, Hunger, Happiness labels are all in a frame for organisation

    name = tk.Label(frame1, text="Hackagotchi v0.05", font=("Monospace", 13), fg="white")
    name.grid(row=0, column=0, padx=10, pady=10) #label and pack the name
    
    happiness = tk.Label(frame1, textvariable=vhappiness, font=("Monospace", 13), fg="white")
    happiness.grid(row=1, column=0, padx=10, pady=10) #Label and pack the happiness, dependant on vhappiness str
    
    hunger = tk.Label(frame1, textvariable=vhunger, font=("Monospace", 13), fg="white")
    hunger.grid(row=2, column=0, padx=10, pady=10) #Label and pack hunger, dependant on vhunger str

    frame2 = tk.Frame(window)
    frame2.grid(row=1, column=0, columnspan = 2, padx = 10, pady = 10)

    totalScannedLabel = tk.Label(frame2, textvariable=totalScanned, font=("Monospace", 13), fg="white")
    totalScannedLabel.grid(row=0,column=0,padx=25,pady=25)
    
    currentScanLabel = tk.Label(frame2, textvariable=currentScan, font=("Monospace", 13), fg="white")
    currentScanLabel.grid(row=1,column=0,padx=25,pady=25)

    shakesTakenLabel = tk.Label(frame2, textvariable=shakesTaken, font=("Monospace", 13), fg="white")
    shakesTakenLabel.grid(row=2,column=0,padx=25,pady=25)
    
    uptimeLabel = tk.Label(frame2, textvariable=vuptime, font=("Monospace", 13), fg="white")
    uptimeLabel.grid(row=0,column=1,padx=25,pady=25)
    
    batteryLabel = tk.Label(frame2, textvariable=vbattery, font=("Monospace", 13), fg="white")
    batteryLabel.grid(row=1,column=1,padx=25,pady=25)

    cpuLabel = tk.Label(frame2, textvariable=vcpu, font=("Monospace", 13), fg="white")
    cpuLabel.grid(row=2,column=1,padx=25,pady=25)

    # Now the main loop begins, where we will update the window after loading everything
    while True:
        ## Import Data
        f = open("save.csv", "r")                               # open save.csv, if it doesn't exist this will call an exception
        f_read = c.reader(f, delimiter=',')
        rows = makearr(f_read)[0]
        f.close()
        
        ## Calculate Uptime
        up = dt.datetime.now() - dt.timedelta(seconds = int(startTime.strftime("%s")))
        UPTIME = up.strftime("%H") + ":" + up.strftime("%M") + ":" + up.strftime("%S")

        ## Set variables
        HUNGER = int(rows[0])
        if int(rows[1]) > 10:
            tcs = 10
        else:
            tcs = int(rows[1])
        HAPPINESS = round((HUNGER + (tcs*10))/2) # The Happiness of the pet is determined by the hunger and the amount of networks being scanned, being capped at 10.
        func = 6 - round((0.6)*(HAPPINESS/10)) # The face of the pet is dependant on the Happiness, being leveled with a custom linear function.

        emotion.set(faces.facearr[func]) #set the face
        vhappiness.set("Happiness: " + str(HAPPINESS) + "%") #set the happiness status
        vhunger.set("Hunger: " + str(HUNGER) + "%") #set the hunger status
        totalScanned.set("Total scanned: " + str(rows[2]))
        currentScan.set("Currently Scanning: " + str(rows[1]))
        shakesTaken.set("Total shakes taken: " + str(rows[3]))
        vuptime.set("Uptime: " + str(UPTIME))
        vbattery.set("Battery left: " + str(round(p.sensors_battery().percent)) + "%") # This shows up as an error in my IDE but works at runtime anyway.
        vcpu.set("CPU usage: " + str(p.cpu_percent()) + "%")

        window.update_idletasks() # Update the screen
        t.sleep(1)
    
