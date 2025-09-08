def validate_menu_selection(selection:int):
    return selection in (1,2,3,4,5)

def validate_laser_type(selection:int):
    return selection in (1,2)

def validate_laser_channel(selection:int):
    return selection in (1,2)

def get_laser_type_name(laser_type:int):
    return "Constant Power (APC)" if laser_type == 1 else "Constant Current (ACC)"

def validate_laser_config_update(selection:str):
    return selection in ("1","2","3","4","5","6","7","")

def validate_tec_temp(baseline_temp:float,temp_reading:float,min_temp:float,max_temp:float):
    return ((baseline_temp-1.0<temp_reading<baseline_temp+1.0),(min_temp<temp_reading<max_temp))

def check_overcurrent(board_status: dict,channel: int):
    return board_status["LASER1_OVC"] == 1 if channel == 1 else board_status["LASER2_OVC"] == 1