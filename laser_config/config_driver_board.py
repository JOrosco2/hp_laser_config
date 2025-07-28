from hp_laser_decorator import auto_connect_instruments
from hp_laser_reg import write_mapped_command, get_command_dict
import os
import json
import time

"""
config_driver_board.py - This script holds all of the functions required to initialize
and check values on the laser driver board. Typically uses a debug cable instrument to 
communicate to the driver.
"""

#tries to open the default config file and return JSON data.
def get_default_config(filename="Default_Config.json"):
    default_config = {
        "LASER1_TEC": 2200,
        "LASER2_TEC": 2200,
        "LASER1_PLR": 50,
        "LASER2_PLR": 50,
        "RDCO": 25,
        "LASER1_MODE": 0,
        "LASER2_MODE": 0,
        "LASER1_IRANGE": 1,
        "LASER2_IRANGE": 1,
        "LASER1_ILIM": 50,
        "LASER2_ILIM": 50,
        "LASER1_POW": 0,
        "LASER2_POW": 0,
        "LASER1_STATE": 0,
        "LASER2_STATE": 0,
        "LASER1_REG_DELAY_COMP": 7,
        "LASER2_REG_DELAY_COMP": 7,
        "LASER1_OFFSET_COMP": 1,
        "LASER2_OFFSET_COMP": 1
    }
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir,filename)
    #load or create config
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config = json.load(file)
    else:
        with open(config_path, 'w') as file:
            json.dump(default_config, file, indet=4)
        config = default_config
    keys = list(config.keys())
    values = list(config.values())
    return keys, values

@auto_connect_instruments(required=["debug_cable"])
def write_mapped_command(debug_cable=None,cmd="",val=0):
    #wrapper to translate a given command and write to the provided debug cable
    #decorator tries to connect to a cable if one does not already exist
    cmd,value = map_command(cmd,val)
    debug_cable.write_reg(cmd,value)

@auto_connect_instruments(required=["debug_cable"])
def set_default_values(debug_cable=None,keys=[],values=[]):
    print(f"Setting HP laser driver board default values...")
    input(f"Please ensure the CLI cable is connected to the laser driver board and that the board is powered (ENTER when done):")
    #Write the default values into the driver board
    for i in range(len(keys)):
        print(f"Setting {keys[i]}")
        write_mapped_command(debug_cable=debug_cable,cmd=keys[i],val=values[i])
    #save the default values for both channels
    write_mapped_command(debug_cable=debug_cable,cmd=f"LASER1_SAVE",val=0)
    write_mapped_command(debug_cable=debug_cable,cmd=f"LASER2_SAVE",val=1)
    print(f"Default values saved into HP laser driver board registers...")

@auto_connect_instruments(required=["debug_cable"])
def verify_board_values(debug_cable=None,keys=[],values=[]):
    #Reads the values from the registers described by keys and compares them to the passed values.
    #Returns a single boolean to inidicate if all values matched or not.
    value_flag = True
    print(f"Verifying HP laser driver board default values...")
    for i in range(len(keys)):
        cmd = get_command_dict(keys[i])
        #read the register for current command
        resp = debug_cable.read_reg(cmd['register'])
        #setup response masking and shifting (shift legnth comes from hp_laser_reg.py)
        bits_per_channel = cmd['value_bits']
        mask = (1 << bits_per_channel) - 1
        #response are always single value EXCEPT for source power.
        if "src.power" in cmd['register'] or "src.state" in cmd['register']:
            shift_resp = int(resp)
        elif cmd['channel'] == 0:
            int_resp = int(resp)
            shift_resp = int_resp & mask
        else:
            int_resp = int(resp)
            shift_resp = (int_resp >> bits_per_channel) & mask
        if shift_resp == values[i]:
            print(f"{keys[i]} Expected Value: {values[i]} Response Value: {shift_resp} : PASS!")
        else:  
            print(f"{keys[i]} Expected Value: {values[i]} Response Value: {shift_resp} : FAIL!")
            value_flag = False
        time.sleep(1)
    return value_flag

@auto_connect_instruments(required=["debug_cable"])
def set_current_limit(debug_cable=None,laser_op_current=1.0,laser_max_current=1.0,laser_channel=1):
    #Calculates and writes the lasers current limit register. Checks if laser needs to be in 
    #low current or high current.
    #laser needs to be in low current mode
    if laser_op_current > 115.00 or laser_max_current > 115.00:
        print(f"Laser operating or maximum current is in range for high current mode")
        ilimit = int((245.0 / 980.0) * laser_max_current)
        print(f"Setting current limit to: {ilimit}")
        print(f"Setting laser mode to 0")
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{laser_channel}_IRANGE",val=0)
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{laser_channel}_ILIM",val=ilimit)
    #laser needs to be in high current mode
    else:
        ilimit = int((245.0 // 110.25) * laser_max_current)
        print(f"Setting current limit to: {ilimit}")
        write_mapped_command(debug_cable=debug_cable,cmd=f"LASER{laser_channel}_ILIM",val=ilimit)
    return ilimit

@auto_connect_instruments(required=["debug_cable"])
def read_board_register(debug_cable=None,reg=""):
    #reads the specified board register (uses map from hp_laser_reg). function tries 5 times to read
    #the register
    error_count = 0
    mapped_reg = get_command_dict(reg)
    reg_resp = debug_cable.read_reg(mapped_reg['register'])
    while reg_resp == "Error reading register":
        #try reading again
        reg_resp = debug_cable.read_reg(mapped_reg['register'])
        error_count+=1
    return reg_resp

@auto_connect_instruments(required=["debug_cable"])
def check_laser_overcurrent(debug_cable=None,laser_ch=1,num_retry=2):
    #reads the driver board's status register and checks if the overcurrent register is asserted. 
    #performs num_retry reads to catch errors in overcurrent status due to overshoot when setting PLR/power
    i=0
    while i < num_retry:
        reg_response = read_board_register(debug_cable=debug_cable,reg=f"LASER_STATUS")
        if "Error reading register" not in reg_response:
            board_status = get_board_status(int(reg_response))
            if getattr(board_status,f"LASER{laser_ch}_OVC"):
                i+=1
                continue #overcurrent detected, try reading again
            else:
                return 1,False #register read properly, no overcurrent detected
        else:
            return -1,False #unable to read status register, return an error
    return 1,True #overcurrent detected after num_retry retries