from hp_laser_decorator import auto_connect_instruments

"""
config_apc_laser.py - python script which handles configuring a laser in constant power mode (APC).
udpates PLR values on IC-HT series laser driver chips and monitors the output power and overcurrent
status register to optimize laser output power.
"""
POWER_MARGIN = 0.5
MAX_PLR = 255
POWER_LEVELS = [1,100,255]

@auto_connect_instruments(required=["debug_cable","opm"])
def ramp_plr_to_power(debug_cable=None,opm=None,plr_range=MAX_PLR,unit_info=UnitInfo()):
    #function which incremnts the lasers PLR from 0 until either nominal power is reached, max PLR is reached
    #or an overcurrent condition is reached
    i=0
    for i in range(plr_range):
        print(f"Setting laser {unit_info.Laser_Channel} to PLR: {i} and ensuring laser is ON")
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_PLR",val=i)
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_SAVE",val=unit_info.Laser_Channel-1)
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_STATE",val=1)
        time.sleep(2)
        #check for an overcurrent status
        ovc_status,ovc = check_laser_overcurrent(debug_cable=debug_cable,laser_ch=unit_info.Laser_Channel,num_retry=2)
        if ovc_status > 0 and not ovc:
            #check the output power and see if nominal power has been reached
            opm_reading = opm.read_power()
            if opm_reading >= unit_info.Laser_Power_DB + POWER_MARGIN:
                print(f"Optimal PLR found: {i}, Laser output: {opm_reading}. Saving value to register...")
                write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_SAVE",val=unit_info.Laser_Channel-1)
                print(f"Laser Configuration Completed!")
                #check if user wants to turn laser off after configuring
                if ask_yes_no("Would you like to turn the laser off?"):
                    #turn off the laser and make sure to save the state
                    write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_STATE",val=0)
                    write_mapped_command(debug_cable=debug_cable,cmd=f"LASAER{unit_info.Laser_Channel}_SAVE",val=unit_info.Laser_Channel-1)
                break   
            print(f"PLR {i}, Output Power: {opm_reading} dBm has not reached optimal power level {unit_info.Laser_Power_DB + POWER_MARGIN} dBm")     
        else:
            print(f"**********************************************************************************")
            print(f"Overcurrent is {ovc}, status register read status is {ovc_status}. Breaking loop, please contact engineering")
            print(f"**********************************************************************************")
            print(f"Ensuring laser is turned off")
            write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_STATE",val=0)
            return -1
    return 1

@auto_connect_instruments(required=["opm"])
def setup_opm(opm=None,wvl=1550.00):
    #Sets the channel and wavelength on the connected opm
    while True:
        try:
            channel = int(input(f"Please enter the OPM Channel: "))
            opm.set_opm_channel(channel-1)
            break
        except ValueError:
            print(f"Error! Invalid input, please enter a valid OPM channel...")
    opm.set_wavelength(wvl)

@auto_connect_instruments(required=["debug_cable","opm"])
def configure_laser_diode_apc(debug_cable=None,opm=None,unit_info=UnitInfo()):
    #Receives a unit_info dictionary from the caller. The unit info dictionary must have the following structure:
    #unit_info {"Laser_SN":str,
    #           "Unit_SN":int,
    #           "Laser_Wavelength":float,
    #           "Laser_OP_Current":float,
    #           "Laser_Max_Current":float,
    #           "Laser_Power":float
    #           }
    #Also receives a debug_cable object, opm object, and channel integer (either 1 or 2). From these parameters
    #sets the current mode (high or low) and the current limit register for the board. Then starts incrementing the
    #PLR while monitoring the output power until the power reaches at least Laser_Power + 0.5dB. If that power cannot 
    #be reached before the current limit then, returns an error. Addtionally if any of the parameters are invalid returns
    #an error.
    #This function currently is only setup for APC laser operation mode. 
    opm_reading = 0.0
    ilimit = 1
    status = BoardStatus()
 
    #set opm channel for the measurement
    setup_opm(wvl=unit_info.Laser_Wavelength)
    #calculate and write the current limit
    ilimit=set_current_limit(debug_cable=debug_cable,unit_info=unit_info)
    #save the irange (if changed) and the ilimt registers.
    print(f"Saving updated registers...")
    #save values for the specified channel (zero indexed so subtract 1)
    write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_SAVE",val=unit_info.Laser_Channel-1)
    #instruct user to power off unit, connect laser board and power on the unit
    print(f"Please perform the following:")
    input(f"1. Power off the board (press ENTER when done)")
    input(f"2. Connect the Laser carrier board (press ENTER when done)")
    input(f"3. Power on the unit (press ENTER when done)")
    input(f"4. Verify the board has reconnected (usb beep) AND that the TEC LED is green (IF TEC LED REMAINS RED POWER OFF UNIT AND CONTACT ENGINEERING) (press ENTER when done)")
    #perform a final verification of necessary values
    keys = [f"LASER{unit_info.Laser_Channel}_PLR",f"LASER{unit_info.Laser_Channel}_ILIM"]
    values = [0,ilimit]
    if verify_board_values(debug_cable=debug_cable,keys=keys,values=values):
        print(f"PLR and Current limit values verified, starting laser configuration")
        print(f"Turning laser on...")
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_POW",val=1)
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_STATE",val=1)
        time.sleep(1)
        #read from OPM and verify power level is still relatively dark (power register set to 0, and plr set to 0)
        opm_reading = opm.read_power()
        print(f"Current OPM reading: {opm_reading} dBm")
        if opm_reading > 0:
            print(f"ERROR! OUTPUT POWER IS TOO HIGH WITH PLR AND LASER POWER SET TO 0. SHUTTING OFF LASER")
            write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_STATE",val=0)
            write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_SAVE",val=unit_info.Laser_Channel-1)
            print(f"CONTACT ENGINEERING FOR TROUBLESHOOTING")
            return -1
        else:
            #step up the laser power setting to ensure that an overcurrent condition is not reached
            #this still should not generate much output power as the PLR is still 0
            for i in POWER_LEVELS:
                print(f"Setting laser {unit_info.Laser_Channel} to power: {i}")
                write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{unit_info.Laser_Channel}_POW",val=i)
                time.sleep(1)
                #read the laser power and get the laser status
                opm_reading = opm.read_power()
                print(f"Current output power: {opm_reading} dBm")
                status = get_board_status(int(read_board_register(debug_cable=debug_cable,reg="LASER_STATUS")))
                if getattr(status,f"LASER{unit_info.Laser_Channel}_OVC"):
                    print(f"**********************************************************************************")
                    print(f"Laser {unit_info.Laser_Channel} over current condition reached, breaking loop. Please contact engineering!")
                    print(f"**********************************************************************************")
                    return -1
                print(f"Going to next power level...")
                #input(f"Press ENTER to continue...") #pause the loop for testing
            #once laser level has been set start to ramp PLR to get to the nominal output power
            return ramp_plr_to_power(debug_cable=debug_cable,plr_range=MAX_PLR,unit_info=unit_info) #return the status of the PLR ramp
    else:
        print(f"ERROR! Unable to verify board parameters. Unsafe to turn-on laser, please contact engineering")
        return -1
