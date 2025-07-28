from dataclasses import dataclass
import math

@dataclass
class UnitInfo:
    Laser_SN:str = "12345"
    Unit_SN:str = "12345"
    Laser_Wavelength:float = 1550.00
    Laser_OP_Current:float = 1.0
    Laser_Max_Current:float = 1.0
    Laser_Power:float = 1.0
    Laser_Power_DB:float = 0.0
    Laser_Channel:int = 1
    Laser_Type:int = 0 #0 = Constant power, 1 = Constant current

    def set_laser_channel(self,laser_channel:int):
        self.laser_channel=laser_channel
        
    def set_laser_power_dbm(self):
        self.Laser_Power_DB = 10*math.log10(self.Laser_Power)