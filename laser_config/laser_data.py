from dataclasses import dataclass

@dataclass
class LaserConfig:
    laser_sn:str 
    laser_wvl:float
    laser_op_current:float 
    laser_max_current:float
    laser_power_mw:float
    laser_power_db:float
    laser_channel:int
    laser_type:int