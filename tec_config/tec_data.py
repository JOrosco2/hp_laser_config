import math
from dataclasses import dataclass,field

"""
tec_data.py - this file holds data objects for data collected from the tec
"""
@dataclass
class TecChannelConfig():
    b_value: int = 3900
    therm_res_25c: int = 10000
    r_sense: int = 10000
    r_therm: int = 0.0

class TecData():
    def __init__(self):
        self.tec_ch1 = TecChannelConfig()
        self.tec_ch2 = TecChannelConfig()

    def _set_r_therm(self,ch:int,v_therm:float,i_therm:float):
        #make sure no illegal division are about to happen
        if ch == 1:
            self.tec_ch1.r_therm = v_therm/ (i_therm / self.tec_ch1.r_sense)
        else:
            self.tec_ch2.r_therm = v_therm/ (i_therm / self.tec_ch2.r_sense)
        
    def calc_temp(self,ch:int,v_therm:int,i_therm:float):
        if i_therm != 0:
            self._set_r_therm(ch,v_therm,i_therm)
            #calculate the LD temperature, note the formula has temp in K. This method converts to C so it's usable
            if ch == 1:
                return (-(self.tec_ch1.b_value*297.75)/((297.75*math.log((self.tec_ch1.r_therm/self.tec_ch1.therm_res_25c))-self.tec_ch1.b_value))-273.15)
            else:
                return (-(self.tec_ch2.b_value*297.75)/((297.75*math.log((self.tec_ch2.r_therm/self.tec_ch2.therm_res_25c))-self.tec_ch2.b_value))-273.15)
        