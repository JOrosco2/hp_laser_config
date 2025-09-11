from laser_config.laser_driver_api import Laser_Driver_API
from laser_config.laser_data import LaserConfig
from logic.validation import check_overcurrent
from hp_laser_decorator import auto_connect_instruments
import logging
import time
from dataclasses import dataclass, field

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
    laser_max_current: float = 1.0
    power_margin: float = 0.5
    max_plr: int = 255
    power_levels: list = field(default_factory=list)

class APCLaserConfig:
    def __init__(self,opm=None,logger=None):
        self.hw=opm
        self.ctx = None
        self.logger = logger or logging.getLogger(__name__)

    def _ensure_ctx(self):
        if not self.ctx or not self.ctx.laser_driver:
            raise RuntimeError("APC Laser context is not initialized. Please contact engineering!")

    @auto_connect_instruments(required=["opm"])
    def _check_hardware(self,opm=None):
        if opm is not None and self.hw is None:
            self.hw = opm #attach the debug_cable from the decorator
        if self.hw is None:
            raise RuntimeError("No debug cable available for writing")
        
    #Sets the channel and wavelength of the OPM
    def setup_opm(self,wvl=1550.00):
        self._check_hardware(opm=None)
        while True:
            try:
                channel = int(input(f"Please enter the OPM Channel: "))
                self.hw.set_opm_channel(channel)
                break
            except ValueError:
                print(f"Error! Invalid input, please enter a valid OPM channel...")
        self.hw.set_wavelength(wvl)

    #checks the board status to see if the laser at channel has an overcurrent detected
    def _check_overcurrent_status(self,retry_count=2):
        i = 0
        #The module board has a tendency to report an overcurrent if there is a current spike when the laser
        #is enabled. Typically reading board status again will clear the error. 
        while i < retry_count:
            if not check_overcurrent(self.ctx.laser_driver.get_board_status(),self.ctx.laser_channel):
                return False
            i+=1
        return True 

    #Perform power ramp on laser (increment in steps to ensure safety)
    def ramp_laser_power(self):
        #Make sure there's an OPM to measure with and that laser parameters have been properly set
        self._check_hardware(opm=None)
        self._ensure_ctx()
        for i in self.ctx.power_levels:
            self.ctx.laser_driver.set_laser_power(self.ctx.laser_channel,i)
            #make sure laser is enabled after setting power
            self.ctx.laser_driver.set_laser_state(self.ctx.laser_channel,1)
            self.ctx.logger.info(f"Setting laser power to {i} and enabling laser")
            time.sleep(2)
            self.ctx.logger.info(f"Checking board status....")
            if self._check_overcurrent_status(retry_count=2):
                self.ctx.logger.info(f"Overcurrent detected on Channel:{self.ctx.laser_channel}, please contact engineering")
                return -1
            current_power = self.hw.read_power()
            self.ctx.logger.info(f"Output power is {current_power}")
        return 1

    #Ramp the driver board's PLR value to achieve nominal laser power
    def ramp_plr(self,target_power=-80.0):
        #Make sure there's an OPM to measure with and that laser parameters have been properly set
        self._check_hardware(opm=None)
        self._ensure_ctx()
        #Get the current OPM power
        current_power = self.hw.read_power()
        retry = 2

        #Get the current PLR from the driver board
        current_plr = self.ctx.laser_driver.read_register(reg="LASER1_PLR") if self.ctx.laser_channel == 1 else self.ctx.laser_driver.read_register(reg="LASER2_PLR")

        while current_power < (target_power):
            current_plr += 1
            if current_power > self.ctx.max_plr:
                self.ctx.logger.info(f"MAX PLR VALUE REACHED, LASER OUTPUT POWER NOT AT {target_power}, PLEASE CONTACT ENGINEERING")
                return -1
            self.ctx.logger.info(f"Setting PLR to {current_plr}")
            self.ctx.laser_driver.set_plr(self.ctx.laser_channel,current_plr)
            self.ctx.laser_driver.set_laser_state(self.ctx.laser_channel,1)
            self.ctx.laser_driver.save_values(self.ctx.laser_channel)
            time.sleep(2)
            current_power = self.hw.read_power()
            self.ctx.logger.info(f"PLR = {current_plr}, Output Power = {current_power}")

        self.ctx.logger.info(f"Nominal output power reached! PLR: {current_plr} Output Power: {current_power}")
        self.ctx.logger.info(f"Setting laser state to OFF...")
        self.ctx.laser_driver.set_laser_state(self.ctx.laser_channel,0)
        self.ctx.laser_driver.save_values(self.ctx.laser_channel)
        return 1
    
    #configure_apc_laser - sets the current limit on the driver board, does an inital power ramp (at plr=0) to ensure laser safety, then 
    #ramps the plr up until laser power reaches nominal power.
    def configure_apc_laser(self,laser_setup:LaserConfig):
        
        #Setup the config script context
        self.ctx = APCLaserContext(
            logger=self.logger,
            laser_driver=Laser_Driver_API(logger=self.logger),
            laser_channel=laser_setup.laser_channel,
            power_margin=0.5,
            laser_max_current=laser_setup.laser_max_current,
            max_plr=255,
            power_levels=[1,100,255]
        )

        #Configure the opm
        self.setup_opm(laser_setup.laser_wvl)
    
        #Set the current limit on the driver board
        self.ctx.laser_driver.set_current_limit(self.ctx.laser_channel,self.ctx.laser_max_current)

        #Turn on the laser, step up the laser power 
        self.ramp_laser_power()

        #Ramp the plr from 0 to max, checking if power level has reached nominal power
        #use the opm reading from the previous for loop.
        target_power = laser_setup.laser_power_db + self.ctx.power_margin
        plr_ramp_status = self.ramp_plr(target_power)
        return plr_ramp_status > 0

   

        
        
