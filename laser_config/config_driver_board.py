from laser_config.laser_driver_api import Laser_Driver_API
import logging
"""
config_driver_board.py - This script holds all of the functions required to initialize
and check values on the laser driver board. Typically uses a debug cable instrument to 
communicate to the driver.
"""

def initialize_driver_board():
    #performs the following process:
    #1. Writes the default values into the laser driver board.
    #2. Instructs user to power cycle the board.
    #3. Verifies that the parameters match the internals.

    #create a laser_driver_api object:
    logger=logging.getLogger(__name__)
    #board_config=Laser_Driver_API(logger=logger)
    board_config=Laser_Driver_API()
    init_flag = True
    logger.info(f"Initializing driver board to default values...")
    logger.info(f"Please wait.....")
    resp = board_config.reset_board_to_default()
    logger.info(f"Initiazation complete!")
    input(f"Please power cycle the driver board. ENTER when board is powered: ")
    logger.info(f"Verifying initialized values:")
    for cmd,val in resp:
        reg_val=board_config.read_register(cmd)
        result,init_flag=("Pass!",True) if val == reg_val else ("Fail!",False)
        logger.info(f"{cmd}: Write={val} | Read={reg_val} {result}")
    return init_flag
    #verify that the initialzed values stuck