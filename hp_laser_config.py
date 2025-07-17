from plugin_system.plugin_loader import autodetect_devices
import json
import os

"""
hp_laser_config - script which sets initial values for the high powered laser driver board.
Initial parameters are kept within a json file (Default_Config.json) which should be located
in the script's directory. If it is not then this script will create it. Uses the following
plugins:

1. CLI_DEBUG_CABLE
2. OPM

Once the inital parameters are loaded the script will then prompt the user for the current
limit from the laser's data sheet and write the register. Finally, the script will increase 
the PLR (Currently only works for APC mode lasers) monitoring the power level until either:

1. Nominal power +0.5dB is reached
2. Current limit is reached

The script will output a test report with all recorded PLR values and recorded power levels.
"""

PRODUCT_VERSION = 1.0

CMD_TABLE = {
"LASER1_TEC": {"register":"src.hp.vtec","channel":0x000,"value_bits":16},
"LASER2_TEC": {"register":"src.hp.vtec","channel":0x001,"value_bits":16},
"RDCO": {"register":"src.hp.dco", "channel":0x00, "value_bits":6},
"LASER1_PLR": {"register":"src.hp.plr","channel":0x00,"value_bits":8},
"LASER2_PLR": {"register":"src.hp.plr", "channel":0x01,"value_bits":8},
"LASER1_MODE": {"register":"src.hp.mode","channel":0x00,"value_bits":8},
"LASER2_MODE": {"register":"src.hp.mode","channel":0x01,"value_bits":8},
"LASER1_IRANGE": {"register":"src.hp.irange","channel":0x00,"value_bits":8},
"LASER2_IRANGE": {"register":"src.hp.irange","channel":0x01,"value_bits":8},
"LASER1_ILIM": {"register":"src.hp.ilim","channel":0x00,"value_bits":8},
"LASER2_ILIM": {"register":"src.hp.ilim","channel":0x01,"value_bits":8},
"LASER1_REG_DELAY_COMP": {"register":"src.hp.regcomp","channel":0x00,"value_bits":8},
"LASER2_REG_DELAY_COMP": {"register":"src.hp.regcomp","channel":0x01,"value_bits":8},
"LASER1_OFFSET_COMP": {"register":"src.hp.offsetcomp","channel":0x00,"value_bits":8},
"LASER2_OFFSET_COMP": {"register":"src.hp.offsetcomp","channel":0x01,"value_bits":8},
"LASER1_STATE": {"register":"src.hp.state","channel":0x00,"value_bits":8},
"LASER2_STATE": {"register":"src.hp.state","channel":0x01,"value_bits":8},
"LASER1_POW": {"register":"src.power","channel":0x00,"value_bits":8},
"LASER2_POW": {"register":"src.power","channel":0x01,"value_bits":8} 
}

#method to prompt the user to enter a serial number (no input requirements)
def get_SN(prompt="Please enter the serial number: "):
    return input(prompt)

#method to get a number (returns as a float)
def get_number(prompt="Please enter the maximum value: "):
    while True:
        try:
            num = float(input(prompt))
            break
        except ValueError:
            print("ERROR! Invalid input!")
    return num

def get_unit_info():
    unit_info = {
        "Laser_SN":None,
        "Unit_SN":None,
        "Laser_OP_Current":None,
        "Laser_Max_Current":None,
        "Laser_Power":None
    }

    #Get the laser serial number:
    unit_info['Laser_SN'] = get_SN("Please enter the laser serial number located on the datasheet: ")
    #get the laser's operating current (used to determine high current or low current)
    unit_info['Laser_OP_Current'] = get_number("Please enter the laser's nominal operating current in mA (located on the datasheet): ")
    #get the laser's maximum current (used to set the MAX_CURRENT register)
    unit_info['Laser_Max_Current'] = get_number("Please enter the laser's maximum current in mA (located on the datasheet): ")
    #get the laser's nominal power
    unit_info['Laser_Power'] = get_number("Please enter the laser's nominal power (in mW): ")

    #print the user's inputs and force them to verify:
    while True:
        #build tuple array to make printing obtained values easier
        data = [
            ("Laser Serial Number:",unit_info['Laser_SN'],""),
            ("Laser Operating Current:",unit_info['Laser_OP_Current']," mA"),
            ("Laser Maximum Current:",unit_info['Laser_Max_Current']," mA"),
            ("Laser Operating Current:",unit_info['Laser_OP_Current']," mW")
        ]

        #print the manu options
        print(f"You have entered the following values:")
        formatted_value = ""
        for i, (label,value,unit) in enumerate(data,1):
            if isinstance(value, float):
                formatted_value = f"{value:>10.2f}"
            else:
                formatted_value = f"{value:>10}"
            print(f"{i}.{label:<30}{formatted_value}{unit}")

        #allow user to make changes    
        sel = input(f"Please verify these are correct and enter 'y' to continue, otherwise enter the selection of the value you would like to change: ")

        #check the menu entry
        if sel == 'y' or sel == 'Y':
            break
        elif sel == '1':
            #print("\n")
            unit_info['Laser_SN'] = get_SN("Please enter the laser serial number located on the datasheet: ")
        elif sel == '2':
            #print("\n")
            unit_info['Laser_OP_Current'] = get_number("Please enter the laser's nominal operating current in mA (located on the datasheet): ")
        elif sel == '3':
            #print("\n")
            unit_info['Laser_Max_Current'] = get_number("Please enter the laser's maximum current in mA (located on the datasheet): ")
        elif sel == '4':
            #print("\n")
            unit_info['Laser_Power'] = get_number("Please enter the laser's nominal power (in mW): ")
        else:
            print(f"ERROR! Invalid input please try again!\n")

    return unit_info

#tries to open the default config file and return JSON data.
def get_default_config(filename="Default_Config.json"):
    default_config = {
        "LASER1_TEC": 2200,
        "LASER2_TEC": 2200,
        "LASER1_PLR": 50,
        "LASER2_PLR": 50,
        "RDCO": 25,
        "LASER1_MODE": 1,
        "LASER2_MODE": 1,
        "LASER1_IRANGE": 1,
        "LASER2_IRANGE": 1,
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

#takes a command and integer value and translates it to the register and hex value
def map_command(cmd = "", val = 0):
    cmd_string = ""
    ch = 0x00
    value_bits = 8
 
    cmd_dict = CMD_TABLE.get(cmd,None)
    cmd_string = cmd_dict["register"]
    ch = cmd_dict["channel"]
    value_bits = cmd_dict["value_bits"]
    max_val = (1 << value_bits) - 1
    if not (0 <= val <= max_val):
        raise ValueError(f"Value {val} exceed {value_bits} - bit range")
    #build the value by combining the channel and the passed in value
    combined = (ch << value_bits) | val
    hex_str = f"0x{combined:05X}"
    #return the command string along with the value string
    return cmd_string, hex_str

def main():
    print(f"***********HP LASER CONFIG V{PRODUCT_VERSION}***********\n")
    keys = []
    values = []

    #connect to the CLI_Cable
    debug_cable = autodetect_devices(package="debug-cable-plugins",type="CLI_Cable")

    while True:
        unit_info = get_unit_info()

        keys,values = get_default_config()

        for i in range(len(keys)):
            cmd,value = map_command(keys[i],values[i])
            debug_cable.write_reg(cmd,value)

        sel = input("Would you like to configure another laser (y/n): ")
        if sel != 'y' or 'Y':
            break

    print(f"***********HP LASER CONFIG Script Complete***********\n")

if __name__ == "__main__":
    main()