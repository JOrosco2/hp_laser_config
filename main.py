import user_io.hp_laser_cli as io
from user_io.unit_info_data import UnitInfo
import logging
import os
from datetime import datetime
from laser_config.config_driver_board import initialize_driver_board
from tec_config.config_tec import run_tec_stability
from laser_config.laser_data import LaserConfig

PRODUCT_VERSION = 1.0        
"""
main.py - python script which sets initial values for the high powered laser driver board.
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

def setup_logging():
    #setup logging object for printing to console and writing to a log file
    #note: this object is global in nature and after this setup is ready to go
    #      in a future update might need to pass this around to change parameters 
    #setup a file path for the log file
    file_path = "C:\Santec Data\SLS-200\Laser Config Data"
    timestamp = datetime.now()
    str_date_time = timestamp.strftime("%m%d%Y-%H%M%S%p")
   
    unit_sn = io.get_unit_sn()
    file_path += "\\" + unit_sn
    log_file_name = f"{unit_sn} - LogFile - {str_date_time}.txt"
    os.makedirs(file_path,exist_ok=True)
    log_path = os.path.join(file_path,log_file_name)
    
    #start some fresh loggers
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
    logger.info(f"Started new config session for SN:{unit_sn}")
    logger.info(f"Logging to file:{log_file_name}")
    #return the serial number
    return logger,unit_sn
 
def main():
    print(f"\n*********************HP LASER CONFIG V{PRODUCT_VERSION}*********************\n")
    log_str = ""
    logger,unit_sn=setup_logging()
    
    while True:
        resp=io.display_menu(unit_sn)
        if resp == 1:
            #initialize the driver board
            init_status = initialize_driver_board()
            log_str = "Driver board initialization - PASS!" if init_status else "Driver board initialization - FAIL"
            logger.info(log_str)
        elif resp == 2:
            #run the TEC stability test
            num_tec=io.setup_tec_test()
            init_status = run_tec_stability(num_tec)
            log_str = "TEC Stability - PASS!" if init_status else "TEC Stability - FAIL!"
            logger.info(log_str)
        elif resp == 3:
            #configure the laser
            laser_info = io.setup_configure_laser()
            logger.info(laser_info)
            laser_config = LaserConfig(**laser_info)
        elif resp == 4:
            #user has changed serial number, so change logger
            logger,unit_sn=setup_logging()
        elif resp == 6:
            #quit
            logger.info(f"*********************HP LASER CONFIG Script Complete*********************\n")
            break

if __name__ == "__main__":
    main()