def validate_menu_selection(selection:int):
    return selection in (1,2,3,4,5)

def validate_laser_type(selection:int):
    return selection in (1,2)

def validate_laser_channel(selection:int):
    return selection in (1,2)

def get_laser_type_name(laser_type:int):
    return "Constant Power (APC)" if laser_type == 1 else "Constant Current (ACC)"