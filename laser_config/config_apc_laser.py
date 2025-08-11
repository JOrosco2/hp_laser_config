from laser_config.laser_driver_api import Laser_Driver_API
from laser_config.laser_data import LaserConfig
from logic.validation import check_overcurrent
from hp_laser_decorator import auto_connect_instruments
import logging
import time
from dataclasses import dataclass

"""
config_apc_laser.py - python script which handles configuring a laser in constant power mode (APC).
udpates PLR values on IC-HT series laser driver chips and monitors the output power and overcurrent
status register to optimize laser output power.
"""
@dataclass
class APCLaserContext:
    logger: any
    laser_driver: Laser_Driver_API
    laser_channel: int = 1
    power_margin: float = 0.5
    max_plr: int = 255
    power_levels: list[int] = [1,100,255]


#Sets the channel and wavelength of the OPM
def setup_opm(opm=None,wvl=1550.00):
    while True:
        try:
            channel = int(input(f"Please enter the OPM Channel: "))
            opm.set_opm_channel(channel-1)
            break
        except ValueError:
            print(f"Error! Invalid input, please enter a valid OPM channel...")
    opm.set_wavelength(wvl)

#checks the board status to see if the laser at channel has an overcurrent detected
def _check_overcurrent_status(ctx:APCLaserContext,retry_count=2):
    i = 0
    #The module board has a tendency to report an overcurrent if there is a current spike when the laser
    #is enabled. Typically reading board status again will clear the error. 
    while i < retry_count:
        if not check_overcurrent(ctx.laser_driver.get_board_status(),ctx.laser_channel):
            return False
    return True 

#Perform power ramp on laser (increment in steps to ensure safety)
@auto_connect_instruments(required=["opm"])
def ramp_laser_power(ctx:APCLaserContext,opm=None):
    for i in ctx.power_levels:
        ctx.laser_driver.set_laser_power(ctx.laser_channel,i)
        #make sure laser is enabled after setting power
        ctx.laser_driver.set_laser_state(ctx.laser_channel,1)
        ctx.logger.info(f"Setting laser power to {i} and enabling laser")
        time.sleep(2)
        ctx.logger.info(f"Checking board status....")
        if _check_overcurrent_status(ctx,retry_count=2):
            ctx.logger.info(f"Overcurrent detected on Channel:{ctx.laser_channel}, please contact engineering")
            return -1
        current_power = opm.read_power()
        ctx.logger.info(f"Output power is {current_power}")
    return 1

#Ramp the driver board's PLR value to achieve nominal laser power
@auto_connect_instruments(required=["opm"])
def ramp_plr(ctx:APCLaserContext,opm=None,target_power=-80.0):
    #Get the current OPM power
    current_power = opm.read_power()
    retry = 2

    #Get the current PLR from the driver board
    current_plr = Laser_Driver_API.read_register(reg="LASER1_PLR") if ctx.laser_channel == 1 else Laser_Driver_API.read_register(reg="LASER2_PLR")

    while current_power < (target_power):
        current_plr += 1
        if current_power > ctx.max_plr:
            ctx.logger.info(f"MAX PLR VALUE REACHED, LASER OUTPUT POWER NOT AT {target_power}, PLEASE CONTACT ENGINEERING")
            return -1
        ctx.logger.info(f"Setting PLR to {current_plr}")
        Laser_Driver_API.set_plr(ctx.laser_channel,current_plr)
        Laser_Driver_API.set_laser_state(ctx.laser_channel,1)
        time.sleep(2)
        current_power = opm.read_power()
        ctx.logger.info(f"PLR = {current_plr}, Output Power = {current_power}")


#configure_apc_laser - sets the current limit on the driver board, does an inital power ramp (at plr=0) to ensure laser safety, then 
#ramps the plr up until laser power reaches nominal power.
@auto_connect_instruments(required=["opm"])
def configure_apc_laser(laser_setup:LaserConfig,opm=None):

    current_power = 0.0
    current_plr = 0

    logger=logging.getLogger(__name__)
    laser_driver = Laser_Driver_API(logger=logger)

    #Setup the config script context
    ctx = APCLaserContext(
        logger=logger,
        laser_driver=laser_driver,
        laser_channel=laser_setup.Laser_Channel,
        power_margin=0.5,
        max_plr=255,
        power_levels=[1,100,255]
        )

    #Configure the opm
    setup_opm(opm,laser_setup.Laser_Wavelength)
    
    #Set the current limit on the driver board
    ctx.laser_driver.set_current_limit(laser_setup.Laser_Channel,laser_setup.Laser_Max_Current)

    #Turn on the laser, step up the laser power 
    ramp_laser_power(ctx,opm)

    #Ramp the plr from 0 to max, checking if power level has reached nominal power
    #use the opm reading from the previous for loop.
    target_power = laser_setup.Laser_Power_DB + ctx.power_margin
    ramp_plr(ctx,opm,target_power)

   

        
        
