"""Enderbyte Programs Telemetry System - Generic. For all of these, errors will be surpressed"""

import requests
import random
import traceback
import platform
import threading

class Constants:
    TELEMETRY_API_BASE = "https://enderbyteprograms.net/api/telemetry/"
    ACTION_REPORT_ENDPOINT = TELEMETRY_API_BASE + "action.php"
    CRASH_REPORT_ENDPOINT = TELEMETRY_API_BASE + "crash.php"
    telemetry_key = 0
    product_name = ""
    product_version = ""
    os_version = platform.platform()

def _send(endpoint:str,data:dict):
    requests.post(endpoint,json=data)

def startup(telemetrykey:int,product_name:str,product_version:str) -> None:
    """Register a telemetry key - you are responsible for choosing to load an old one or make a new one"""
    Constants.telemetry_key = telemetrykey
    Constants.product_name = product_name
    Constants.product_version = product_version


def generate_telemetry_key() -> int:
    return random.randint(1,2**31)

def send_action(actionname:str) -> None:
    try:
        threading.Thread(target=_send,args=[Constants.ACTION_REPORT_ENDPOINT,{
            "version" : 1,#EPTEL request format v1
            "payload" : {
                "productname" : Constants.product_name,
                "productversion" : Constants.product_version,
                "telemetryid" : Constants.telemetry_key,
                "osversion" : Constants.os_version,
                "actionname" : actionname
            }
        }]).start()
    except:
        pass

def send_crash(ex:Exception) -> None:

    #Process exception
    tb = "\n".join(traceback.format_exception(ex))

    try:
        threading.Thread(target=_send,args=[Constants.CRASH_REPORT_ENDPOINT,{
            "version" : 1,#EPTEL request format v1
            "payload" : {
                "productname" : Constants.product_name,
                "productversion" : Constants.product_version,
                "telemetryid" : Constants.telemetry_key,
                "osversion" : Constants.os_version,
                "traceback" : tb
            }
        }]).start()
    except:
        pass