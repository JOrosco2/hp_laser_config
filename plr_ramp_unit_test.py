from laser_config.laser_driver_api import Laser_Driver_API
import logging
from datetime import datetime
import os
import time
from hp_laser_decorator import auto_connect_instruments

@auto_connect_instruments(required=["opm"])
def ut_connect_opm(opm=None):
    return opm

def main():
    #Setup a logging file
    file_path = f"C:\\Santec Data\\SLS-200\\Unit Tests\plr_ramp_unit_tests"
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
    logging.getLogger("pyvisa").setLevel(logging.WARNING)

    #Create the Laser_API object
    laser_driver = Laser_Driver_API(logger=logger)

    #Connect to an opm
    logger.info(f"Connecting to an opm...")
    opm = ut_connect_opm(opm=None)
    logger.info(f"Connected to opm {opm}")

    logger.info(f"Setting OPM Channel = 1, wavelength = 1490")
    opm.set_opm_channel(1)
    opm.set_wavelength(1490)

    time.sleep(5)

    logger.info(f"Setting laser power to 100, turning laser on")
    laser_driver.set_laser_power(1,100)
    laser_driver.set_laser_state(1,1)

    time.sleep(5)

    logger.info(f"Reading OPM power...")
    pow = opm.read_power()
    logger.info(f"Current Power Ch1: {pow}")
    time.sleep(5)

    logger.info(f"Setting opm Channel to 14")
    opm.set_opm_channel(14)
    logger.info(f"Reading OPM power...")
    pow = opm.read_power()
    logger.info(f"Current Power Ch15: {pow}")
    logger.info(f"Ch15 should be nearly dark")

    logger.info(f"Turning off laser...")
    laser_driver.set_laser_state(1,0)

if __name__ == "__main__":
    main()