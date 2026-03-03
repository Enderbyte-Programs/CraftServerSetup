"""CRSS user settings"""

import cursesplus
import sys
import os
import shutil

import uicomponents
import appdata
import eptranslate
import staticflags
import backups
import javamanager
import telemetry

def manage_user_settings(stdscr):
    telemetry.telemetric_action("settings")
    
    while True:
        m = uicomponents.menu(stdscr,["BACK","ADVANCED OPTIONS","Java Installations","Change Language","Manage Backup Profiles","Telemetry Level"]+[d["display"] + " : " + str(d["value"]) for d in list(appdata.APPDATA["settings"].values())],"Please choose a setting to modify")
        if m == 0:
            appdata.updateappdata()
            return
        elif m == 1:
            while True:
                n = uicomponents.menu(stdscr,["BACK","Reset settings","Reset all app data","Clear temporary directory"])
                if n == 0:
                    break
                elif n == 1:
                    del appdata.APPDATA["settings"]
                    appdata.self_compatibilize()
                    appdata.updateappdata()
                elif n == 2:
                    if cursesplus.messagebox.askyesno(stdscr,["DANGER","This will destroy all of the data this app has stored!","This includes ALL servers!","This will restore this program to default","Are you sure you wish to continue?"]):
                        if not cursesplus.messagebox.askyesno(stdscr,["THIS IS YOUR LAST CHANCE!","To make sure that you actually intend to reset,","SELECT NO TO WIPE"]):
                            if cursesplus.messagebox.askyesno(stdscr,["Last chance. For real this time","Are you sure you want to reset?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                                os.chdir("/")
                                shutil.rmtree(staticflags.APPDATADIR)
                                cursesplus.messagebox.showinfo(stdscr,["Program reset."])
                                sys.exit()
                    appdata.updateappdata()
                elif n == 3:
                    shutil.rmtree(staticflags.TEMPDIR)
        elif m == 2:
            javamanager.managejavainstalls(stdscr)
        elif m == 3:
            eptranslate.prompt(stdscr,"Welcome to CraftServerSetup! Please choose a language to begin.")
            appdata.APPDATA["language"] = eptranslate.Config.choice
            cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        elif m == 4:
            backups.backup_manager(stdscr)
        elif m == 5:
            telemetry.set_telemetry_level(stdscr)
        else:
            selm = list(appdata.APPDATA["settings"].values())[m-6]
            selk = list(appdata.APPDATA["settings"].keys())[m-6]
            if selm["type"] == "bool":
                selm["value"] = uicomponents.menu(stdscr,["True (Yes)","False (No)"],f"New value for {selm['display']}") == 0
            elif selm["type"] == "int":
                selm["value"] = cursesplus.numericinput(stdscr,f"Please choose a new value for {selm['display']}")
            elif selm["type"] == "str":
                selm["value"] = uicomponents.crssinput(stdscr,f"Please choose a new value for {selm['display']}",prefiltext=selm["value"])
            appdata.APPDATA["settings"][selk] = selm