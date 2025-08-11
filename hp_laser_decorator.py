from plugin_system.plugin_loader import autodetect_devices
from functools import wraps
import logging

_instrument_cache = {}
logger = logging.getLogger(__name__)

def connect_debug_cable():
    if "debug_cable" not in _instrument_cache:
        logger.info(f"Connecting to debug cable...")
        _instrument_cache["debug_cable"] = autodetect_devices(package="debug_cable_plugins",type="CLI_Cable")
    return _instrument_cache["debug_cable"]

def connect_opm():
    if "opm" not in _instrument_cache:
        logger.info("Connecting to OPM...")
        _instrument_cache["opm"] = autodetect_devices(package="opm_plugins",type="opm")
    return _instrument_cache["opm"]

def connect_daq():
    if "daq" not in _instrument_cache:
        logger.info("Connecting to DAQ...")
        _instrument_cache["daq"] = autodetect_devices(package="daq_plugins",type="daq")
    return _instrument_cache["daq"]
    
#Define a list of connection functions for the decorator
connect_funcs = {
    "debug_cable": connect_debug_cable,
    "opm": connect_opm,
    "daq": connect_daq
}

def auto_connect_instruments(required=[]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            new_kwargs = kwargs.copy()
            for instrument in required:
                if new_kwargs.get(instrument) is None:
                    connect_function = connect_funcs.get(instrument)
                    if connect_function is None:
                        raise RuntimeError(f"No connection function for {instrument}")
                    new_kwargs[instrument] = connect_function()
                    if new_kwargs[instrument] is None:
                        raise RuntimeError(f"Instrument {instrument} could not be found...")
            result = func(*args,**new_kwargs)
            return result
        return wrapper
    return decorator