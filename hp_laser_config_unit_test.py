from laser_config.laser_driver_api import Laser_Driver_API
import logging
from datetime import datetime
import os
"""
Unit test on laser_driver_api.py. Tests that the script can write values to the module
board, read them back. Update status and laser.
"""

def main():

    reg_list = [
        "LASER1_TEC",
            "LASER2_TEC",
            "RDCO",
            "LASER1_PLR",
            "LASER2_PLR",
            "LASER1_MODE",
            "LASER2_MODE",
            "LASER1_IRANGE",
            "LASER2_IRANGE",
            "LASER1_ILIM",
            "LASER2_ILIM",
            "LASER1_REG_DELAY_COMP",
            "LASER2_REG_DELAY_COMP",
            "LASER1_OFFSET_COMP",
            "LASER2_OFFSET_COMP",
            "LASER1_STATE",
            "LASER2_STATE",
            "LASER1_POW",
            "LASER2_POW"
    ]

    #Setup a logging file
    file_path = f"C:\\Santec Data\\SLS-200\\Unit Tests"
    timestamp = datetime.now()
    str_date_time = timestamp.strftime("%m%d%Y-%H%M%S%p")
    log_file_name = f"LogFile - {str_date_time}.txt"
    os.makedirs(file_path,exist_ok=True)
    log_path = os.path.join(file_path,log_file_name)
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path,mode='a',encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logger=logging.getLogger(__name__)

    #Create the Laser_API object
    laser_driver = Laser_Driver_API(logger=logger)

    input(f"Verify that debug cable is connected to test board, press ENTER to continue: ")

    logger.info(f"Resetting board to default...")
    laser_driver.reset_board_to_default()

    input(f"Power cycle the driver board. Press ENTER when the board has reinitialized: ")
    logger.info(f"User has confirmed a power cycle...")
    logger.info(f"Reading back register values:")

    for i in reg_list:
        resp = laser_driver.read_register(i)
        logger.info(f"Register: {i} Value: {resp}")

    logger.info(f"**********************************************")
    logger.info(f"Enabling laser and checking board status:")
    logger.info(f"Setting laser 1 to ON")
    laser_driver.set_laser_power(1,50)
    laser_driver.set_laser_state(1,1)
    logger.info(f"Getting board status:")
    board_status = laser_driver.get_board_status()
    for key,value in board_status.items(): logger.info(f"{key} : {value}")
    logger.info(f"Setting laser 2 to ON")
    laser_driver.set_laser_power(2,50)
    laser_driver.set_laser_state(2,1)
    logger.info(f"Getting board status")
    board_status = laser_driver.get_board_status()
    for key,value in board_status.items(): logger.info(f"{key} : {value}")

if __name__ == "__main__":
    main()