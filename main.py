import user_io.hp_laser_cli as io
from user_io.unit_info_data import UnitInfo
import logging
import os
from datetime import datetime

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

def setup_logging(log_dir="logs",log_file="default_log.txt"):
    #setup logging object for printing to console and writing to a log file
    #note: this object is global in nature and after this setup is ready to go
    #      in a future update might need to pass this around to change parameters 
    os.makedirs(log_dir,exist_ok=True)
    log_path = os.path.join(log_dir,log_file)
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
    
def main():
    print(f"\n*********************HP LASER CONFIG V{PRODUCT_VERSION}*********************\n")
    keys = []
    values = []
    unit_sn = "123456"
    file_path = "C:\Santec Data\SLS-200\Laser Config Data"
    timestamp = datetime.now()
    str_date_time = timestamp.strftime("%m%d%Y-%H%M%S%p")
   
    unit_sn = io.get_unit_sn()
    file_path += "\\" + unit_sn
    log_file_name = f"{unit_sn} - LogFile - {str_date_time}.txt"
    setup_logging(file_path,log_file_name)
    logging.getLogger(__name__).info("Starting Test Config")
   
    print(f"*********************HP LASER CONFIG Script Complete*********************\n")

if __name__ == "__main__":
    main()