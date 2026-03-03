"""Enderbyte Programs Telemetry System - CRSS wrapper"""

import enum
import cursesplus

import eptel
import appdata
import uicomponents

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

def set_telemetry_level(stdscr) -> None:
    """Show the user a screen to select their telemetry level, and set this telemetry level"""
    op = uicomponents.menu(stdscr,["Cancel","0 - Nothing","1 - Basic Only","2 - Crash reports","3 - Comprehensive"],f"Please choose a telemetry level. Current level is: {get_telemetry_level()}",peroptionfooters=[
        "Do not change the telemetry level",
        "Send no telemetry whatsoever",
        "Send only a single 'installation exists' telemetry event",
        "Basic + send error details if a crash occurs",
        "Send comprehensive usage statistics"
    ],preselected=3)

    if op == 0:
        return
    
    appdata.APPDATA["telemetry"]["level"] = op - 1
    appdata.updateappdata()

    cursesplus.messagebox.showinfo(stdscr,["Telemetry level updated successfully."])