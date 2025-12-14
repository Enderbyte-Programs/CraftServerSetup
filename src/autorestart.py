"""A module to control the automatic server restart feature for v1.53"""
import enum
import os
import cursesplus
import uicomponents

class AutoRestartSourceOptions(enum.Enum):
    NOAUTORESTART = 0#Auto restart will never occur, no matterwhat
    EXTERNALFILE = 1#CRSS will search for the SERVERDIR/autorestart file and attempt to follow it. If it cannot find it, it will execute the insturction in the CRSS options
    CRSSONLY = 2#CRSS will only honour the setting in the internal configuration (CRSS options)

class AutoRestartOptions(enum.Enum):
    NORESTART = 0#No auto restart, no matter what
    SAFEEXIT = 1#Auto restart only if exit code is 0 (signifying a safe shutdown)
    ALWAYS = 2 #Auto restart no matter what

class ExternalAutoRestartProfile:
    """Store a friendly representation of the auto restart profile stored in a file"""
    def __init__(self,file_data:str):
        self.restart_always:bool = False
        self.restart_if_safe:bool = False
        self.is_persistent: bool = False

        for word in file_data.lower().strip().split():
            if word == "safe":
                self.restart_if_safe = True
            elif word == "unsafe":
                self.restart_always = True
            elif word == "persistent":
                self.is_persistent = True
            elif word == "disposable":
                self.is_persistent = False
            elif word == "never":
                self.restart_always = False
                self.restart_if_safe = False
        

def does_server_have_autorestart_file(serverdir:str) -> bool:
    """Does the server in serverdir have an autorestart file?"""
    return os.path.isfile(serverdir + os.sep + "autorestart")

def get_recommended_action(server_configuration:dict,clear_nonpersistent=True) -> AutoRestartOptions:
    """Using all of the configurations, suggest the action to restart or not"""
    serverdir:str = server_configuration["dir"]
    startsource = server_configuration["settings"]["restartsource"]

    if startsource == AutoRestartSourceOptions.NOAUTORESTART.value:
        return AutoRestartOptions.NORESTART
    
    elif startsource == AutoRestartSourceOptions.CRSSONLY.value or not does_server_have_autorestart_file(serverdir):#Disregard foreign if startsource is set to or if there is no autorestart file
        return AutoRestartOptions(server_configuration["settings"]["autorestart"])
    
    elif startsource == AutoRestartSourceOptions.EXTERNALFILE.value:
        with open(serverdir+os.sep+"autorestart") as f:
            rd = f.read()

        ob = ExternalAutoRestartProfile(rd)
        if not ob.is_persistent and clear_nonpersistent:
            os.remove(serverdir+os.sep+"autorestart")

        if ob.restart_always:
            return AutoRestartOptions.ALWAYS

        if ob.restart_if_safe:
            return AutoRestartOptions.SAFEEXIT
        
        return AutoRestartOptions.NORESTART
    
    return AutoRestartOptions.NORESTART
    
def autorestart_settings(stdscr,serverdata:dict) -> dict:
    """UI portion for configuring autorestart"""
    while True:
        wtd = uicomponents.menu(stdscr,["Back","Autorestart Mode","Autorestart Source"])
        if wtd == 0:
            return serverdata
        elif wtd == 1:
            serverdata["settings"]["autorestart"] = uicomponents.menu(stdscr,["Do not automatically restart","Automatically restart only if the server has not crashed","Always automatically restart the server"],"Select the CRSS-based autorestart mode to use","If you set the source to be external, this setting will be ignored.")
        elif wtd == 2:
            serverdata["settings"]["restartsource"] = uicomponents.menu(stdscr,["Do not automatically restart","Pull settings from $DIR/autorestart file, then CRSS.","Pull settings from CRSS only"],"Choose a data source for autorestart")