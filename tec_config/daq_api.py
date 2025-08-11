from hp_laser_decorator import auto_connect_instruments
import logging

"""
daq_api.py - provides an interface to the daq plugin.
"""

class DAQ_api():
    def __init__(self,daq=None,logger=None):
        self.hw=daq
        self.logger = logger or logging.getLogger(__name__)

    @auto_connect_instruments(required=["daq"])
    def _check_hardware(self,daq=None):
        if daq is not None and self.hw is None:
            self.hw = daq #attach the debug_cable from the decorator if there
        if self.hw is None:
            raise RuntimeError("No debug cable available for writing!")
        
    def config_daq(self,ch=[],fcn=[]):
        #configures the daq channels
        self._check_hardware(daq=None)
        for i in range(len(ch)):
            self.hw.set_channel(ch[i],fcn[i])
    
    def get_data(self):
        #returns an array
        self._check_hardware(daq=None)
        readings=self.hw.read_data()
        return readings