from dataclasses import dataclass, field
from typing import Dict, Union

"""
hp_laser_reg - defines the data structures for the ic-ht 
laser driver chip.
"""
#default IC-HT configuraiton values
@dataclass
class LaserChannelConfig:
    tec: int = 2200
    plr: int = 50
    mode: int = 0
    irange: int = 1
    ilim: int = 50
    pow: int = 0
    state: int = 0
    reg_delay_comp: int = 7
    offset_comp: int = 1

#define the structure of the driver chip configuraiton (two laser channels channels, rdco value shared)
@dataclass
class LaserConfig:
    laser1: LaserChannelConfig = field(default_factory=LaserChannelConfig)
    laser2: LaserChannelConfig = field(default_factory=LaserChannelConfig)
    rdco: int = 25

#define the structure of the IC-HT data registers
@dataclass
class RegisterMap:
    register: str
    channel: int = 0
    value_bits: int = 8

#define the chip value registers, RegisterMap defines the command structure (reg,ch,val_bits)
@dataclass
class CommandTable:
    entries: Dict[str, RegisterMap] = field(default_factory=lambda: {
        "LASER1_TEC": RegisterMap("src.hp.vtec",0x000,16),
        "LASER2_TEC": RegisterMap("src.hp.vtec",0x001,16),
        "RDCO": RegisterMap("src.hp.dco",0x00,8),
        "LASER1_PLR": RegisterMap("src.hp.plr",0x00,8),
        "LASER2_PLR": RegisterMap("src.hp.plr",0x01,8),
        "LASER1_MODE": RegisterMap("src.hp.mode",0x00,8),
        "LASER2_MODE": RegisterMap("src.hp.mode",0x01,8),
        "LASER1_IRANGE": RegisterMap("src.hp.irange",0x00,8),
        "LASER2_IRANGE": RegisterMap("src.hp.irange",0x01,8),
        "LASER1_ILIM": RegisterMap("src.hp.ilim",0x00,8),
        "LASER2_ILIM": RegisterMap("src.hp.ilim",0x01,8),
        "LASER1_REG_DELAY_COMP": RegisterMap("src.hp.regcomp",0x00,8),
        "LASER2_REG_DELAY_COMP": RegisterMap("src.hp.regcomp",0x01,8),
        "LASER1_OFFSET_COMP": RegisterMap("src.hp.offsetcomp",0x00,8),
        "LASER2_OFFSET_COMP": RegisterMap("src.hp.offsetcomp",0x01,8),
        "LASER1_STATE": RegisterMap("src.state[0]",0x00,8),
        "LASER2_STATE": RegisterMap("src.state[1]",0x01,8),
        "LASER1_POW": RegisterMap("src.power[0]",0x00,8),
        "LASER2_POW": RegisterMap("src.power[1]",0x01,8),
        "LASER1_SAVE": RegisterMap("src.hp.save",0x00,8),
        "LASER2_SAVE": RegisterMap("src.hp.save",0x01,8),
        "LASER_STATUS": RegisterMap("src.hp.stat",0x00,16) #note channel and val bits are not required for this register
    })

#define the bit offsets for the laser driver board status
@dataclass
class StatusBitFlags:
    flags: Dict[str,int] = field(default_factory=lambda: {
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
    })

#define the laser driver board data class (consists of LaserConfig, CommandTable, and StatusBitFlags)
@dataclass
class LaserDriverConfig:
    laser_config: LaserConfig = field(default_factory=LaserConfig)
    cmd_table: CommandTable = field(default_factory=CommandTable)    
    status_flags: StatusBitFlags = field(default_factory=StatusBitFlags)
