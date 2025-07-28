import logic.validation as check

"""
hp_laser_cli.py - python file which contains all user prompts and outputs
"""
def display_menu(unit_sn=123456):
    resp = 0
    print(f"Laser Configuration Menu (Current SN={unit_sn}):")
    print("1. Initialize Driver Board")
    print("2. Configure Laser")
    print("3. Run Stability")
    print("4. Update Serial Number")
    print("5. Exit")
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
    print(f"\nLaser Configuration Info:")
    print(f"1. SN: {sn}")
    print(f"2. Wavelength: {wvl} nm")
    print(f"3. Operating Current: {op} mA")
    print(f"4. Max Current: {max} mA")
    print(f"5. Nominal Power: {pow} mW")
    print(f"6. Channel: {ch}")
    print(f"7. Type: {check.get_laser_type_name(type)}")
    choice = input("Press ENTER if these values are correct, otherwise select which value to update: ")
    if choice in ["1", "2", "3", "4", "5", "6", "7"]:
        return True, int(choice)
    return False, 0

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
        "laser_sn":"12345",
        "laser_wvl":1550.00,
        "laser_op_current":1.0,
        "laser_max_current":1.0,
        "laser_power_mw":1.0,
        "laser_power_dbm":0.0,
        "laser_channel":1,
        "laser_type":0
    }
    for key, (func,params) in function_dict.items():
        user_input[f"{key}"]=func(*params)
    _verify_config_info(user_input)
    return user_input


