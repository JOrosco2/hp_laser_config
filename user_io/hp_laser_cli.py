import logic.validation as check
import logging

"""
hp_laser_cli.py - python file which contains all user prompts and outputs
"""

logger=logging.getLogger(__name__)

def display_menu(unit_sn=123456):
    resp = 0
    print(f"Laser Configuration Menu (Current SN={unit_sn}):")
    print("1. Initialize Driver Board")
    print("2. Run TEC Stability Test")
    print("3. Configure Laser")
    print("4. Run Stability")
    print("5. Update Serial Number")
    print("6. Exit")
    while True:
        try:
            resp = int(input("Please select which process you would like to run: "))
            if check.validate_menu_selection(resp):
                return resp
            else:
                print("Invalid input! Please try again!")
        except ValueError:
            print("ERROR! Please enter a valid choice!")

def get_laser_sn():
    return input("Please enter the laser serial number located on the datasheet: ")

def get_unit_sn():
    #for sooner rather than later, add a check for illegal file characters. 
    #this value will be used to create files.
    return input("Please enter the unit's SN: ")

def get_laser_type():
    resp = 0
    print(f"Please select the laser type.")
    print(f"1. Constant Power (APC).")
    print(f"2. Constant Current (ACC).")
    while True:
        try:
            resp = int(input("Your choice: "))
            if check.validate_laser_type(resp):
                return resp
            else:
                print("Invalid input! Please try again!")
        except ValueError:
            print("ERROR! Please enter a valid choice!")

def ask_yes_no(prompt, default=None):
    #asks a yes/no prompt. Returns true if user enters yes, false if no. 
    #checks to ensure some form of yes/no is entered.
    valid_yes = {'y', 'yes'}
    valid_no = {'n', 'no'}

    if default is True:
        prompt += " [Y/n]: "
    elif default is False:
        prompt += " [y/N]: "
    else:
        prompt += " [y/n]: "

    while True:
        response = input(prompt).strip().lower()
        if not response and default is not None:
            return default
        elif response in valid_yes:
            return True
        elif response in valid_no:
            return False
        else:
            print("Please enter 'y' or 'n'.")

def get_number(prompt="Please enter the maximum value: "):
    #method to get a number (returns as a float)
    while True:
        try:
            num = float(input(prompt))
            break
        except ValueError:
            print("ERROR! Invalid input!")
    return num

def get_laser_channel():
    while True:
        try:
            new_ch = int(input("Please enter the laser's channel (1 or 2): "))
            if check.validate_laser_channel(new_ch):
                return new_ch
            print(f"Invalid Laser Channel! Please enter either 1 or 2")
        except ValueError:
            print(f"ERROR! Please enter a valid channel (1 or 2)")

def print_config_info(sn="12345",wvl=1550.00,op=1.0,max=1.0,pow=1.0,ch=1,type=0):
    #prints the enterd config info for the user to verify. Prompts to enter a selection.
    while True:
        logger.info(f"\nLaser Configuration Info:")
        logger.info(f"1. SN: {sn}")
        logger.info(f"2. Wavelength: {wvl} nm")
        logger.info(f"3. Operating Current: {op} mA")
        logger.info(f"4. Max Current: {max} mA")
        logger.info(f"5. Nominal Power: {pow} mW")
        logger.info(f"6. Channel: {ch}")
        logger.info(f"7. Type: {check.get_laser_type_name(type)}")
        choice = input("Press ENTER if these values are correct, otherwise select which value to update: ")
        if check.validate_laser_config_update(choice):
            return (True, int(choice)) if choice is not "" else (False,0)
        logger.info(f"ERROR! Invalid choice, please enter a valid option!")

function_dict = {
    "laser_sn": (get_laser_sn,()),
    "laser_wvl":(get_number,("Please enter the laser's wavelength: ",)),
    "laser_op_current":(get_number,("Please enter the laser's nominal operating current in mA (located on the datasheet): ",)),
    "laser_max_current":(get_number,("Please enter the laser's maximum current in mA (located on the datasheet): ",)),
    "laser_power_mw":(get_number,("Please enter the laser's nominal power (in mW): ",)),
    "laser_channel":(get_laser_channel,()),
    "laser_type":(get_laser_type,())
}

def _verify_config_info(user_input=None):
    #checks if the user would like to update any of the user information they entered
    update = True
    while update:
        update, choice = print_config_info(
            sn=user_input["laser_sn"],
            wvl=user_input["laser_wvl"],
            op=user_input["laser_op_current"],
            max=user_input["laser_max_current"],
            pow=user_input["laser_power_mw"],
            ch=user_input["laser_channel"],
            type=user_input["laser_type"]
        )
        if update:
            key_list = list(function_dict)
            key = key_list[choice - 1] #choice is 1 indexed
            func, params = function_dict[key]
            user_input[key] = func(*params)

def get_config_info():
    #Prompts user to enter laser and unit information. returns a dictionary of inputs to caller.
    user_input = {
        "Laser_SN":"12345",
        "Laser_Wavelength":1550.00,
        "Laser_OP_Current":1.0,
        "Laser_Max_Current":1.0,
        "Laser_Power":1.0,
        "Laser_Power_DB":0.0,
        "Laser_Channel":1,
        "Laser_Type":0
    }
    for key, (func,params) in function_dict.items():
        user_input[f"{key}"]=func(*params)
    _verify_config_info(user_input)
    return user_input

def setup_tec_test():
    #Prompts the user to get the unit ready for a tec stability test
    logger.info(f"Readying TEC Stability Test:")
    num_ch=0
    input(f"Please ensure the laser driver board is powered OFF (press ENTER when done): ")
    input(f"Please connect the DAQ-TEC connectors are connected to the driver board (press ENTER when done): ")
    input(f"Please connect the laser carrier board to the laser driver board (press ENTER when done): ")
    num_ch=int(get_number(f"Please enter the number of TECs that are being tested: "))
    input(f"Please power on the board, confirm the TEC light is green (press ENTER when the light has turned green): ")
    return num_ch

def setup_configure_laser():
    #prompts for the user to get ready to set the power on the laser
    logger.info(f"Readying to configure laser:")
    print(f"Please perform the following:")
    if ask_yes_no("Is the laser board currently connected to the driver board?"):
        input(f"1. Ensure the board is powered on (press ENTER when done)")
    else:
        input(f"1. Ensure the board is powered off (press ENTER when done)")
        input(f"2. Connect the Laser carrier board (press ENTER when done)")
        input(f"3. Power on the unit (press ENTER when done)")
        input(f"4. Verify the board has reconnected (usb beep) AND that the TEC LED is green (IF TEC LED REMAINS RED POWER OFF UNIT AND CONTACT ENGINEERING) (press ENTER when done)")

    #get laser info
    config_info = get_config_info()

    return config_info


