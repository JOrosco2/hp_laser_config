from dataclasses import dataclass, fields

#Python script responsible for handling translation of commands and values 
#read from the hp laser board's registers.
@dataclass
class BoardStatus:
    LASER1_STATE:bool = False
    LASER1_MON:bool = False
    LASER1_LDKSAT:bool = False
    UNUSED:bool = False
    LASER2_STATE:bool = False
    LASER2_MON:bool = False
    LASER2_LDKSAT:bool = False
    UNUSED_2:bool = False
    INITRAM:bool = False
    PDOVDD:bool = False
    MEMERR:bool = False
    OVT:bool = False
    LASER2_OVC:bool = False
    LASER1_OVC:bool = False
    OSCERR:bool = False
    CFGTIMO:bool = False

CMD_TABLE = {
"LASER1_TEC": {"register":"src.hp.vtec","channel":0x000,"value_bits":16},
"LASER2_TEC": {"register":"src.hp.vtec","channel":0x001,"value_bits":16},
"RDCO": {"register":"src.hp.dco", "channel":0x00, "value_bits":8},
"LASER1_PLR": {"register":"src.hp.plr","channel":0x00,"value_bits":8},
"LASER2_PLR": {"register":"src.hp.plr", "channel":0x01,"value_bits":8},
"LASER1_MODE": {"register":"src.hp.mode","channel":0x00,"value_bits":8},
"LASER2_MODE": {"register":"src.hp.mode","channel":0x01,"value_bits":8},
"LASER1_IRANGE": {"register":"src.hp.irange","channel":0x00,"value_bits":8},
"LASER2_IRANGE": {"register":"src.hp.irange","channel":0x01,"value_bits":8},
"LASER1_ILIM": {"register":"src.hp.ilim","channel":0x00,"value_bits":8},
"LASER2_ILIM": {"register":"src.hp.ilim","channel":0x01,"value_bits":8},
"LASER1_REG_DELAY_COMP": {"register":"src.hp.regcomp","channel":0x00,"value_bits":8},
"LASER2_REG_DELAY_COMP": {"register":"src.hp.regcomp","channel":0x01,"value_bits":8},
"LASER1_OFFSET_COMP": {"register":"src.hp.offsetcomp","channel":0x00,"value_bits":8},
"LASER2_OFFSET_COMP": {"register":"src.hp.offsetcomp","channel":0x01,"value_bits":8},
"LASER1_STATE": {"register":"src.state[0]","channel":0x00,"value_bits":8},
"LASER2_STATE": {"register":"src.state[1]","channel":0x01,"value_bits":8},
"LASER1_POW": {"register":"src.power[0]","channel":0x00,"value_bits":8},
"LASER2_POW": {"register":"src.power[1]","channel":0x01,"value_bits":8},
"LASER1_SAVE": {"register":"src.hp.save","channel":0x00,"value_bits":8},
"LASER2_SAVE": {"register":"src.hp.save","channel":0x01,"value_bits":8},
"LASER_STATUS": {"register":"src.hp.stat","channel":0x00,"value_bits":24} #note channel and val bits are not required for this register
}

STATUS_FLAGS = {
"LASER1_STATE":0,
"LASER1_MON":1,
"LASER1_LDKSAT":2,
"UNUSED":3,
"LASER2_STATE":4,
"LASER2_MON":5,
"LASER2_LDKSAT":6,
"UNUSED_2":7,
"INITRAM":8,
"PDOVDD":9,
"MEMERR":10,
"OVT":11,
"LASER2_OVC":12,
"LASER1_OVC":13,
"OSCERR":14,
"CFGTIMO":15
}

def map_command(cmd = "", val = 0):
    #takes a command and integer value and translates it to the register and hex value
    cmd_string = ""
    ch = 0x00
    value_bits = 8
 
    cmd_dict = CMD_TABLE.get(cmd,None)
    cmd_string = cmd_dict["register"]
    ch = cmd_dict["channel"]
    value_bits = cmd_dict["value_bits"]
    max_val = (1 << value_bits) - 1
    if not (0 <= val <= max_val):
        raise ValueError(f"Value {val} exceed {value_bits} - bit range")
    #build the value by combining the channel and the passed in value
    combined = (ch << value_bits) | val
    hex_str = f"0x{combined:05X}"
    #return the command string along with the value string
    return cmd_string, hex_str

def get_command_dict(cmd=""):
    #get the dictionary values for the given command
    return CMD_TABLE.get(cmd,None)

def get_board_status(status:int):
    #receives the integer status response from the source.sys and translates the statuses to a dictionary for use in other functions
    status_shift = status & 0xFFFF #status is a 2-byte response so make sure that the given status is always expanded to 2 bytes
    #build and return the status dictionary
    board_status = BoardStatus()
    field_names = [f.name for f in fields(BoardStatus)]
    for i in range(len(field_names)):
        setattr(board_status,field_names[i],status_shift & (1 << i))
    return board_status