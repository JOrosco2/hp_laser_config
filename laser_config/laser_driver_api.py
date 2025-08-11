from laser_config.hp_laser_reg import LaserDriverConfig
from hp_laser_decorator import auto_connect_instruments
import logging
"""
laser_driver_api.py - this script defines the methods to interact with
the hp_laser_reg data object. 
"""

class Laser_Driver_API:
    def __init__(self,debug_cable=None,logger=None):
        self.hw=debug_cable
        self.config=LaserDriverConfig()
        self.logger = logger or logging.getLogger(__name__)

    def _flatten_defaults(self):
        #flattens the LaserDriverConfig defaults so that values can be iterated
        return{
            "LASER1_TEC":self.config.laser_config.laser1.tec,
            "LASER2_TEC":self.config.laser_config.laser2.tec,
            "RDCO":self.config.laser_config.rdco,
            "LASER1_PLR":self.config.laser_config.laser1.plr,
            "LASER2_PLR":self.config.laser_config.laser2.plr,
            "LASER1_MODE":self.config.laser_config.laser1.mode,
            "LASER2_MODE":self.config.laser_config.laser2.mode,
            "LASER1_IRANGE":self.config.laser_config.laser1.irange,
            "LASER2_IRANGE":self.config.laser_config.laser2.irange,
            "LASER1_ILIM":self.config.laser_config.laser1.ilim,
            "LASER2_ILIM":self.config.laser_config.laser2.ilim,
            "LASER1_REG_DELAY_COMP":self.config.laser_config.laser1.reg_delay_comp,
            "LASER2_REG_DELAY_COMP":self.config.laser_config.laser2.reg_delay_comp,
            "LASER1_OFFSET_COMP":self.config.laser_config.laser1.offset_comp,
            "LASER2_OFFSET_COMP":self.config.laser_config.laser2.offset_comp,
            "LASER1_STATE":self.config.laser_config.laser1.state,
            "LASER2_STATE":self.config.laser_config.laser2.state,
            "LASER1_POW":self.config.laser_config.laser1.pow,
            "LASER2_POW":self.config.laser_config.laser2.pow,
        }
     
    @auto_connect_instruments(required=["debug_cable"])
    def _check_hardware(self,debug_cable=None):
        if debug_cable is not None and self.hw is None:
            self.hw = debug_cable #attach the debug_cable from the decorator if there
        if self.hw is None:
            raise RuntimeError("No debug cable available for writing!")
        
    def _build_register_value(self,cmd:str,val:int):
        #gets the command from the table and builds the command string.
        #returns the command values and the value
        cmd_value=self.config.cmd_table.entries.get(cmd)
        max_val = (1 << cmd_value.value_bits) - 1
        if not (0 <= val <= max_val):
            raise ValueError(f"Value {val} exceed {cmd_value.value_bits} - bit range")
        #build the value by combining the channel and the passed in value
        combined = (cmd_value.channel << cmd_value.value_bits) | val
        hex_str = f"0x{combined:05X}"
        #returns the hex string which can be provided to the debug_cable interface
        return cmd_value,hex_str
    
    def _write_command(self,cmd:str,val:str):
        self._check_hardware(debug_cable=None)
        self.hw.write_reg(cmd,val)
    
    def reset_board_to_default(self):
        #writes all of the driver board values to the default values of LaserDriverConfig returns a list of register that were udpated
        result = []
        for cmd, val in self._flatten_defaults().items():
            cmd_value,hex_value=self._build_register_value(cmd,val)
            self.logger.info(f"Writing {cmd} : {val} | {cmd_value.register} : {hex_value}")
            self._write_command(cmd_value.register,hex_value)
            result.append((cmd,val))
        #save values for both channels    
        self.save_values(0)
        self.save_values(1)
        return result
    
    def set_laser_state(self,ch:int,state:int):
        #turns the laser at channel on or off
        self._check_hardware(debug_cable=None)
        reg_map,reg_val = self._build_register_value("LASER1_STATE",state) if ch == 1 else self._build_register_value("LASER2_STATE",state)
        self._write_command(reg_map.register,reg_val)

    def set_laser_power(self,ch:int,pow:int):
        #sets the laser power level 0-255
        self._check_hardware(debug_cable=None)
        reg_map,reg_val = self._build_register_value("LASER1_POW",pow) if ch == 1 else self._build_register_value("LASER2_POW",pow)
        self._write_command(reg_map.register,reg_val)
         
    def set_plr(self,ch:int,plr:int):
        #writes the new value into the plr
        self._check_hardware(debug_cable=None)
        reg_map,reg_val = self._build_register_value("LASER1_PLR",plr) if ch == 1 else self._build_register_value("LASER2_PLR",plr)
        self.logger.info(f"Setting PLR to {plr} | {reg_map.register} : {reg_val}")
        self._write_command(reg_map.register,reg_val)

    def set_current_limit(self,ch:int,max_current:float):
        #receives the max laser current. Sets the limit.
        self._check_hardware(debug_cable=None)
        ilimit,mode = (int((245.0//980.00)*max_current),1) if max_current > 115.00 else (int((245.0//110.25)*max_current),0)
        reg_map,reg_val = self._build_register_value("LASER1_ILIM",ilimit) if ch == 1 else self._build_register_value("LASER2_ILIM",ilimit)
        self.logger.info(f"Setting ILIMIT to {ilimit} | {reg_map.register} : {reg_val}")
        self._write_command(reg_map.register,reg_val)
        #set the current mode (low/high current) FOR FUTURE UPDATES make current mode a parameter or variable so it's not hardlocked to 115.0mA
        reg_map,reg_val = self._build_register_value("LASER1_IRANGE",mode) if ch == 1 else self._build_register_value("LASER2_IRANGE",mode)
        self.logger.info(f"Setting Current mode to {mode}")
        self._write_command(reg_map.register,reg_val)
        self.save_values(ch=ch)

    def save_values(self,ch:int):
        #writes the save registers to burn the values into the ic-ht chip
        self._check_hardware(debug_cable=None)
        self._write_command("src.hp.save","0x00") if ch is 1 else self._write_command("src.hp.save","0x01")

    def read_register(self,reg:str):
        #attempts to read the value at the specified register. If an invalid register is sent
        #returns -9999.
        self._check_hardware(debug_cable=None)
        error_count = 0
        reg_map=self.config.cmd_table.entries.get(reg)
        if reg_map is None:
            return -9999
        resp=self.hw.read_reg(reg_map.register)
        while resp is "Error reading register" and error_count<5:
            #try reading again (5 tries to read the register)
            resp = self.hw.read_reg(reg_map.register)
            error_count+=1
        #translate the response into an numeric value
        bits_per_channel=reg_map.value_bits
        mask=(1<<bits_per_channel)-1
        #responses sometimes are multichannel numbers concatentated together. 
        #get the response for the channel specified in the reg_map
        if "src.power" in reg_map.register or "src.state" in reg_map.register: #src.power and src.state always just retrun a single unshifted value
            return int(resp)
        elif reg_map.channel is 0:
            int_resp = int(resp)
            shift_resp = int_resp & mask
        else:
            int_resp = int(resp)
            shift_resp = (int_resp >> bits_per_channel) & mask
        return shift_resp
    
    def get_board_status(self):
        #Read the board's status register to get the laser status
        result = {}
        board_status = self.read_register("LASER_STATUS")
        for name, offset in self.config.status_flags.flags.items():
            bit_value = (board_status >> offset) & 1
            result[name] = bit_value
        return result


 

