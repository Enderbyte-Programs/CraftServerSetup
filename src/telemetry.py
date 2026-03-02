"""Enderbyte Programs Telemetry System - CRSS wrapper"""

import enum
import eptel
import appdata

class TelemetryLevels(enum.Enum):
    UNSET = -1#Temp value
    NOTHING = 0#Send no telemetry
    BASIC = 1#Send only one request per use (so effectively a single analytic saying that somebody used the program)
    CRASHES = 2#Default option - Basic + send a crash report to Enderbyte Programs if there is an error
    COMPREHENSIVE = 3#Detailed usage statistics (how much somebody uses a certain feature). I don't expect people to use this


def get_telemetry_level() -> int:
    return appdata.APPDATA["telemetry"]["level"]

def telemetric_action(actionname:str):

    if (actionname == "startup") and get_telemetry_level() >= 1:
        eptel.send_action(actionname)
    
    #Only the startup action is included with BASIC
    if get_telemetry_level() >= 3:
        eptel.send_action(actionname)
        #Send everything with COMPREHENSIVE

def crash_report(ex:Exception):
    if get_telemetry_level() >= 2:
        eptel.send_crash(ex)