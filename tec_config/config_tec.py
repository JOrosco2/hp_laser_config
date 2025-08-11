from laser_config.laser_driver_api import Laser_Driver_API
from tec_config.daq_api import DAQ_api
from tec_config.tec_data import TecData
import logic.validation as check
import logging
import time

"""
config_tec.py - This script will monitor up to 2 Laser Diode TECs.
Connects to the SLS-TEC-DAQ (see work instruction) to monitor LD thermistor
current as well as thermistor voltage. From those values the LD temp is calculated.
The script will monitor the calculated voltage with the laser diodes off to ensure that the 
temperature remains stable at ambient conditon (~25C).

NOTE: currently the thermistor's B value, along with 25C resistance are hardcoded (3900 & 10Kohm)
this script will need to be updated later if another thermistor type is encountered.
"""

def calc_temp_readings(calc_obj:TecData,log_str:str,daq_readings=[],num_ch=0):
    temp = []
    for i in range(0,2*num_ch,2):
        calculated_temp = calc_obj.calc_temp(ch=(i//2)+1,v_therm=daq_readings[i+1],i_therm=daq_readings[i])
        log_str += f" CH{(i//2)+1}: {calculated_temp:.2f}C |"
        temp.append(calculated_temp)
    return log_str,temp

def run_tec_stability(num_ch=0):
    calc_obj = TecData()
    daq_readings=[]
    baseline_temp=[]
    min_temp = 0.0
    max_temp = 70.0
    meas_in_tol = 0
    idx = 0
    ch = [i + 1 for i in range(2*num_ch)]
    fcn = [0] * (2*num_ch)
    stability_flag = True
    logger=logging.getLogger(__name__)
    daq=DAQ_api()

    #configure the daq for measuring voltage
    daq.config_daq(ch=ch,fcn=fcn)

    logger.info(f"Starting TEC stability test...")
    logger.info(f"Monitoring laser diode temperature over 1 minute to confirm stabiltiy (+/-1deg)")
    #monitor tec voltage for all channels over ~1 min to ensure temp is stable
    #get a baseline temperature reading
    daq_readings=daq.get_data()
    log_str,baseline_temp = calc_temp_readings(calc_obj=calc_obj,log_str="Baseline Reading:",daq_readings=daq_readings,num_ch=num_ch)
    logger.info(log_str)
    
    #Start a loop, need at least 6 consectutive measurements to ensure DAQ stability
    while meas_in_tol <= 6 and idx < 12:

        daq_readings=daq.get_data()
        log_str,temp_calc = calc_temp_readings(calc_obj=calc_obj,log_str="Current Reading:",daq_readings=daq_readings,num_ch=num_ch)
        
        #check if the temperature readings are stable and check if any readings exceed the maximums
        for i in range(len(temp_calc)):
            stability_check, overtemp_check = check.validate_tec_temp(baseline_temp[i],temp_calc[i],min_temp,max_temp)
            if not stability_check:
                stability_flag = False

        #if overtemp condition is reached break loop and display error message:
        if not overtemp_check:
            logger.info("ERROR! Overtemp conditon encountered! Please power off the board and inform engineering!!!!")
            return False
        
        log_str += "Pass!" if stability_flag else "Fail!"
        meas_in_tol += 1 if stability_flag else 0
        logger.info(log_str)
        time.sleep(10)

    return stability_flag
    
    
