'''
Run a temperature ramp on a Cole-Parmer digital Polystat waterbath (the old blue
units, not the newer models). 
This script uses RS232 serial communication with the water bath to get and set 
the temperature setpoint and to check the current bath temperature. This should 
work with both the basic "digital" model and the "programmable digital" model.

Written under Python 2.7

Created on Jul 21, 2013

@author: Luke Miller
'''
import time
import serial # from http://pyserial.sourceforge.net/pyserial.html
              # beginner's install instructions for Windows here:
              # http://learn.adafruit.com/arduino-lesson-17-email-sending-movement-detector/installing-python-and-pyserial
import sys # for user input

# Establish serial communications with the water bath. Cole-Parmer instructions
# recommend 57600 baud, 8-N-1, no flow control. No linefeeds (\n) should be
# used in the communications with the water bath, only carriage returns (\r). 
# Useful commands for the water bath: 
# RS = get current setpoint temperature
# RT = get current internal bath temperature
# SSxxx.xx\r = change bath setpoint (i.e. SS025.50, units of degrees Celsius)
# SE1 = turn on command echo. It seems counterintuitive, but this seems to be
#         necessary for this script to run.

# Begin by establishing a serial connection with the bath. The entry COM1 below
# will need to be changed to suit your specific serial port name. On a Mac this
# will be something like dev/tty.usbserial-xxxxxxx, on Windows it will be a
# COM port like COM1. 
try: 
    bath = serial.Serial(
                         'COM1',
                         baudrate = 57600,
                         timeout = 1)
    print "***********************************"
    print "Serial connection established on "
    print bath.name # print port info
    print "***********************************"
    time.sleep(2)
    bath.write("SE1\r") # turn on command echo
    response = bath.readline() # always read the response to clear the buffer
    #print "SE0 response: %s" % response
    bath.write("RT\r")
    response = float(bath.readline())
    print "Current bath temperature: %2.2f C" % response
    bath.write("RS\r")
    response = float(bath.readline())
    print "Current bath setpoint: %2.2f C" % response
    continue_flag = True
except:
    print "++++++++++++++++++++++++++"
    print "Serial connection failed"
    print "++++++++++++++++++++++++++"
    time.sleep(5)
    continue_flag = False
    
################################################################################
# Start by asking the user which version of the temperature ramp they want to
# carry out. Option 1 will bring the water bath to a starting temperature and 
# hold it there until the user starts the ramp. Option 2 will immediately 
# start the ramp from the current temperature (useful when the user has 
# manually set the water bath starting temperature already). 
if continue_flag:
        
    print "######################################################"
    print "Choose a routine to run (enter 1 or 2): "
    print "1. Set to starting temperature, pause, then start ramp"
    print "2. Start ramp immediately from current temperature"
    prog = raw_input("Enter 1 or 2: ")

    if prog == "1":
        # Get the various temperature parameters from the user
        init_temp = raw_input("Enter the starting temperature (C): ")
        init_temp = float(init_temp) # Convert to float

        target_temp = raw_input("Enter the target temperature (C): ")
        target_temp = float(target_temp) # convert to float
        
        rise_rate = raw_input("Enter temperature ramp rate (C per hour): ")
        rise_rate = float(rise_rate)

    elif prog == "2":
        target_temp = raw_input("Enter the target temperature (C): ")
        target_temp = float(target_temp) # convert to float
        
        rise_rate = raw_input("Enter temperature ramp rate (C per hour): ")
        rise_rate = float(rise_rate)

    ################################################################################
    # The user chose version 1. Begin by changing the bath setpoint to the 
    # init_temp, and wait for the bath to achieve that temperature. 

    if prog == "1":
        # The first step will be to set the initial temperature on the water  
        # bath and wait around until it reaches that temperature.
        flag = False # set the while-loop flag

        while flag != True:
            print "Setting initial temperature: %2.2f C" % init_temp
            # Assemble the command to send to the water bath
            command = "SS0" + "%2.2f\r" % init_temp 
            bath.write(command)
            response = bath.readline() # always read the response to clear 
                                       # the buffer
            time.sleep(0.01)
            # Now check that the set point worked
            bath.write("RS\r")
            response = float(bath.readline())
            if response == init_temp:
                print "Setpoint set: %2.2f C" % response
                flag = True  # set True to kill while loop
            
        # Next we need to wait around for the water bath to get to the initial 
        # temperature.         
        flag = False # reset test flag
        while flag != True:
            time.sleep(5)
            bath.write("RT\r")  # request current bath internal temperature
            response = float(bath.readline())
            print "Current bath temp: %2.2f C" % response
            # When the bath temperature gets within 0.05 of the target, we're 
            # close enough
            if (abs(init_temp - response) < 0.05):
                flag = True  # set True to kill while loop
        # The script will now hold at the initial temperature until the user 
        # tells it to begin ramping the temperature to the target_temp.
        print "****************************************************"
        print "****************************************************"
        print "Initial temperature reached"
        print ""
        junk = raw_input("Press return to start temperature ramp")
        print "Starting temperature ramp"
        print "****************************************************"


    ############################################################################
    # If the user chose program 2, they skipped the initial temperature change 
    # above. Query the water bath to find its current setpoint and use that 
    # value as the init_temp
    if prog == "2":
        bath.write("RS\r") # Query setpoint
        response = float(bath.readline()) # Read setpoint from bath
        init_temp = response # Set init_temp 

    ############################################################################
    # The next step is to change the water bath temperature at the specified 
    # rate until it hits the target_temp

    # Calculate the number of degrees to be covered
    temp_diff = abs(target_temp - init_temp)

    # Calculate the time needed for the ramp (degrees / degrees per hour)
    ramp_duration = temp_diff / rise_rate # units hours
    ramp_duration_m = ramp_duration * 60 # convert to minutes
    print "Ramp will take %2.2f hrs (%1.0f minutes)" % \
        (ramp_duration,ramp_duration_m)

    # Calculate per-minute temperature step (units of degrees C)
    # rise_rate was specified by the user in units of degrees C per hour
    rise_rate_m = rise_rate / 60
    # In cases where the target_temp is lower than the init_temp, the 
    # rise_rate_m value will need to be a negative number for this to work
    # correctly.
    
    if (target_temp - init_temp) < 0:
        rise_rate_m = rise_rate_m * -1
        decrease_flag = True # This flag will notify the loops below to lower
                             # the temperature instead of raising it.
    else:
        decrease_flag = False # The ramp will be an increasing ramp
            
    prev_time = time.time() # get starting time (in seconds)
    bath.write("RS\r") # get current setpoint
    current_set = float(bath.readline()) # always read response to clear buffer
    current_set = current_set + rise_rate_m # add temp step to current setpoint
    command = "SS0" + "%2.2f\r" % current_set 
    bath.write(command) # change set point
    response = bath.readline()
    
    flag = False # set initial flag
    while flag != True:
        time.sleep(1)
        new_time = time.time() # get time again
        # Compare new_time to prev_time, if more than 60 seconds have elapsed, 
        # update the setpoint to the next temperature
        if new_time > (prev_time + 60):
            prev_time = new_time # update to new time
            current_set = current_set + rise_rate_m # add temp step to setpoint
            if current_set < target_temp and not decrease_flag:
                command = "SS0%2.2f\r" % current_set
                bath.write(command) # update water bath setpoint
                response = bath.readline()
                # Calculate remaining temperature to cover
                temp_left = target_temp - current_set
                # Calculate remaining time in minutes
                time_left = temp_left / rise_rate_m
                if time.localtime().tm_min % 5 == 0:
                    # If the current minute is evenly divisible by 5, print out
                    # an update of the setpoint and remaining minutes
                    time_left_s = time_left * 60 # convert time_left to seconds
                    # calculate finishing time in seconds
                    final_time = new_time + time_left_s + 60
                    # convert final_time to a human-readable string                
                    final_str = time.strftime("%H:%M", 
                                              time.localtime(final_time))
                    print "Current setpoint: %2.2f C, finishing at approx. %s" % \
                        (current_set,final_str)
            elif current_set >= target_temp and not decrease_flag:
                # If the new current_set value is greater than the target_temp, 
                # then the bath has nearly reached the target temp. Make the new 
                # setpoint equal to target_temp and set flag to True to kill 
                # this while loop
                current_set = target_temp # set current_set to the final 
                                          # target_temp
                command = "SS0%2.2f\r" % current_set
                bath.write(command)
                response = bath.readline() # read line to clear buffer
                flag = True # set flag True to kill while loop
                print "Waiting to reach final temperature"
            elif current_set > target_temp and decrease_flag:
                # The temperature should be ramped downward when decrease_flag
                # is True
                command = "SS0%2.2f\r" % current_set
                bath.write(command) # update water bath setpoint
                response = bath.readline()
                # Calculate remaining temperature to cover
                temp_left = target_temp - current_set
                # Calculate remaining time in minutes
                time_left = temp_left / rise_rate_m
                if time.localtime().tm_min % 5 == 0:
                    # If the current minute is evenly divisible by 5, print out
                    # an update of the setpoint and remaining minutes
                    time_left_s = time_left * 60 # convert time_left to seconds
                    # calculate finishing time in seconds
                    final_time = new_time + time_left_s + 60
                    # convert final_time to a human-readable string                
                    final_str = time.strftime("%H:%M", 
                                              time.localtime(final_time))
                    print "Current setpoint: %2.2f C, finishing at approx. %s" % \
                        (current_set,final_str)
                        
            elif current_set <= target_temp and decrease_flag:
                # If the new current_set value is less than the target_temp and
                # the decrease_flag is True (temperature ramp is going down),
                # then the bath has nearly reached the target temperature. 
                # Make the new setpoint equal to target_temp and set flag to 
                # True to kill this while loop 
                current_set = target_temp # set current_set to the final 
                                          # target_temp
                command = "SS0%2.2f\r" % current_set
                bath.write(command)
                response = bath.readline() # read line to clear buffer
                flag = True # set flag True to kill while loop
                print "Waiting to reach final temperature"
                
    # Now hang out and wait for the bath temperature to get close to the final
    # target temperature
    flag = False
    while flag != True:
        time.sleep(1)
        bath.write("RT\r") # Query current bath temperature
        response = float(bath.readline())
        print "Current temperature: %2.2f C" % response
        if (abs(response - target_temp) < 0.05):
            print "**************************************************"
            print "**************************************************"
            print "Target temperature reached"    
            print "**************************************************"
            print "**************************************************"
            flag = True
            time.sleep(2)
    # At this point the water bath should stay at the target_temp setpoint 
    # indefinitely. 
    try: 
        bath.close() # shut down serial connection
        print "Closed serial connection"
        time.sleep(5)
    except: 
        print "Serial connection failed to close"                  
        time.sleep(5)
    
    

