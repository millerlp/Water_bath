'''
Created on Jul 21, 2013

@author: millerlp
'''
import time
import serial
import sys # for user input

try: 
    bath = serial.Serial(
                         'COM1',
                         baudrate = 57600,
                         timeout = 1)
    print "Serial connection established"
    print bath.portstr # print port info
except:
    print "Serial connection failed"

#####################
#### Get the various temperature parameters from the user    
init_temp = raw_input("Enter the starting temperature: ")
init_temp = float(init_temp) # Convert to float

target_temp = raw_input("Enter the target temperature: ")
target_temp = float(target_temp) # convert to float

rise_rate = raw_input("Enter temp rise rate (Degrees per hour): ")
rise_rate = float(rise_rate)

# The first step will be to set the initial temperature on the water bath and
# wait around until it reaches that temp.
test = False

while test != True:
    print "Setting initial temperature: %2.2f" % init_temp
    # Assemble the command to send to the water bath
    command = "SS0" + "%2.2f\r" % init_temp 
    bath.write(command)
    response = bath.readline()
    # Now check that the set point worked
    bath.write("RS\r")
    response = float(bath.readline())
    if response == init_temp:
        print "Success"
        test = True  # set True to kill while loop
        
# Next we need to wait around for the water bath to get to the initial 
# temperature.         
test = False
while test != True:
    time.sleep(2)
    bath.write("RT\r") # request current bath internal temperature
    response = float(bath.readline())
    print "Current bath temp: %2.2f" % response
    if (abs(init_temp - response) < 0.05):
        print "Initial temperature reached"
        test = True # set True to kill while loop
  
# The script will now hold at the initial temperature until the user tells it
# to begin ramping the temperature to the target_temp.

junk = raw_input("Press return to start temperature ramp")
print("Starting temperature ramp")

############################################################
# The next step is to raise the water bath temperature at the specified rate
# until it hits the target_temp

# Calculate the number of degrees to be covered
temp_diff = target_temp - init_temp
# Calculate the time needed for the ramp (degrees / degrees per hour)
ramp_duration = temp_diff / rise_rate # units hours
ramp_duration_m = ramp_duration * 60 # convert to minutes
print "Ramp will take %2.2f hrs (%3.0f minutes)" % (ramp_duration,ramp_duration_m)

# Calculate per-minute temperature step 
rise_rate_m = rise_rate / 60

prev_time = time.time() # get starting time (in seconds)
bath.write("RS\r") # get current setpoint
current_set = float(bath.readline())
current_set = current_set + rise_rate_m # add temp step to current setpoint
command = "SS0" + "%2.2f\r" % current_set 
bath.write(command) # change set point

test = False # set initial flag
while test != True:
    time.sleep(2)
    new_time = time.time() # get time again
    # Compare new_time to prev_time, if more than 60 seconds have elapsed, 
    # update the setpoint to the next temperature
    if (new_time > prev_time + 60):
        prev_time = new_time # update to new time
        current_set = current_set + rise_rate_m # add temp step to setpoint
        if (current_set < target_temp):
            command = "SS0%2.2f\r" % current_set
            bath.write(command) # update water bath setpoint
            # Calculate remaining temperature to cover
            temp_left = target_temp - current_set
            # Calculate remaining time in minutes
            time_left = temp_left / rise_rate_m
            if (time.localtime().tm_min % 5 == 0):
                # If the current minute is evenly divisible by 5, print out
                # an update of the setpoint and remaining minutes
                print "Current setpoint: %2.2f,  %3f minutes remaining" % (current_set,time_left)
        elif (current_set > target_temp):
            current_set = target_temp # set current_set to the final target_temp
            command = "SS0%2.2f\r" % current_set
            bath.write(command) 
            print("Target temperature reached")
            test = True # set test flag True to kill while loop
    
    
    
    
    
# RS = get setpoint temperature
# SSxxx.xx\r = set setpoint