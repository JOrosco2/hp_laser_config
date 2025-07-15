from plugin_system.plugin_loader import autodetect_devices
import json

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



def main():
    print(f"***********HP LASER CONFIG V{PRODUCT_VERSION}***********\n")
    
    while True:
        unit_info = get_unit_info()

        sel = input("Would you like to configure another laser (y/n): ")
        if sel != 'y' or 'Y':
            break
    

if __name__ == "__main__":
    main()