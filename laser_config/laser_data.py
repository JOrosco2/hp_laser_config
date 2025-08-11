from dataclasses import dataclass

@dataclass
class LaserConfig:
    Laser_SN:str 
    Laser_Wavelength:float
    Laser_OP_Current:float 
    Laser_Max_Current:float
    Laser_Power:float
    Laser_Power_DB:float
    Laser_Channel:int
    Laser_Type:int