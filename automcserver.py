#!/usr/bin/python3

print("Auto Minecraft Server by Enderbyte Programs (c) 2023")

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


print("Loading libraries:")
import shutil
import sys
import os
from time import sleep
import curses
import curses.textpad
import json

import datetime
import subprocess
print("Checking for libcursesplus")
try:
    import cursesplus
except:
    lop = os.system("pip3 install --quiet cursesplus")
    if lop != 0:
        print("Failed to install cursesplus")
        sys.exit(1)
    import cursesplus
import cursesplus.messagebox
import cursesplus.filedialog
print("Checking for librequests")
try:
    import requests
except:
    lop = os.system("pip3 install --quiet requests")
    if lop != 0:
        print("Failed to install requests")
        sys.exit(1)
    import requests
print("Checking for urllib3")
try:
    import urllib.request
except:
    lop = os.system("pip3 install --quiet urllib")
    if lop != 0:
        print("Failed to install urllib")
        sys.exit(1)
    import urllib.request
import urllib.error
print("Checking internet connection")

def internet_on():
    try:
        urllib.request.urlopen('http://google.com', timeout=5)
        return True
    except urllib.error.URLError as err: 
        return False
APPDATADIR = os.path.expanduser("~/.local/share/mcserver")
SERVERSDIR = APPDATADIR + "/servers"
if not os.path.isdir(APPDATADIR):
    os.mkdir(APPDATADIR)
if not os.path.isdir(SERVERSDIR):
    os.mkdir(SERVERSDIR)
__DEFAULTAPPDATA__ = {
    "servers" : [

    ],
    "hasCompletedOOBE" : False
}
def parse_size(data: int) -> str:
    if data < 0:
        neg = True
        data = -data
    else:
        neg = False
    if data < 2000:
        result = f"{data} bytes"
    elif data > 2000000000:
        result = f"{round(data/1000000000,2)} GB"
    elif data > 2000000:
        result = f"{round(data/1000000,2)} MB"
    elif data > 2000:
        result = f"{round(data/1000,2)} KB"
    if neg:
        result = "-"+result
    return result
def get_java_version() -> str:
    try:
        return subprocess.check_output(r"java -version 2>&1 | grep -Eow '[0-9]+\.[0-9]+' | head -1",shell=True).decode().strip()
    except:
        return "Error"

class PropertiesParse:
    @staticmethod
    def load(s: str) -> dict:
        dat = s.splitlines()
        dat = [d for d in dat if d.replace(" ","") != ""]
        dat = [d for d in dat if d[0] != "#"]
        final = {}
        for d in dat:
            key = d.split("=")[0]
            val = "=".join(d.split("=")[1:])
            final[key] = val
        return final
    @staticmethod
    def dump(d: dict) -> str:
        l = ""
        for f in d.items():
            l += f[0] + "=" + f[1] + "\n"
        return l
def setupnewserver(stdscr):
    stdscr.erase()
    serversoftware = cursesplus.displayops(stdscr,["Vanilla","Cancel"],"Please choose your server software")
    if serversoftware == 1:
        return
    elif serversoftware == 0:
        stdscr.clear()
        stdscr.erase()
        downloadversion = cursesplus.displayops(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
        if downloadversion == 0:
            return
        else:
            stdscr.clear()
            cursesplus.displaymsgnodelay(stdscr,["Getting version manifest..."])
            PACKAGEDATA = requests.get(VERSION_MANIFEST_DATA["versions"][downloadversion-1]["url"]).json()
            cursesplus.displaymsgnodelay(stdscr,["Preparing new server"])
            while True:
                servername = cursesplus.cursesinput(stdscr,"What is the name of your server?").strip()
                if not os.path.isdir(SERVERSDIR):
                    os.mkdir(SERVERSDIR)
                if os.path.isdir(SERVERSDIR+"/"+servername):
                    cursesplus.displaymsg(stdscr,["Name already exists."])
                    continue
                else:
                    try:
                        os.mkdir(SERVERSDIR+"/"+servername)
                    except:
                        cursesplus.displaymsg(stdscr,["Error","Server path is illegal"])
                    else:
                        break
    S_INSTALL_DIR = SERVERSDIR+"/"+servername
    p = cursesplus.ProgressBar(stdscr,6,1,True,True,"Setting up server")
    p.step("Getting download data",True)
    S_DOWNLOAD_data = PACKAGEDATA["downloads"]["server"]
    S_DOWNLOAD_size = parse_size(S_DOWNLOAD_data["size"])
    p.appendlog(f"SIZE: {S_DOWNLOAD_size}")
    p.appendlog(f"URL: {S_DOWNLOAD_data['url']}")
    p.step("Downloading",True)
    urllib.request.urlretrieve(S_DOWNLOAD_data["url"],S_INSTALL_DIR+"/server.jar")
    p.step("Checking stuff",True)
    setupeula = cursesplus.messagebox.askyesno(stdscr,["To proceed, you must agree","To Mojang's EULA","","Do you agree?"])
    if setupeula:
        with open(S_INSTALL_DIR+"/eula.txt","w+") as f:
            f.write("eula=true")# Agree
    p.step("Loading java",True)
    usecustomjavaversion = cursesplus.messagebox.askyesno(stdscr,["Do you want to use the default java install (program java)?",f"Version {get_java_version()}"])
    stdscr.clear()
    stdscr.erase()
    if not usecustomjavaversion:
        while True:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a new java executable",directory="/")
            if os.system(njavapath+" -version &> /dev/null") != 0:
                cursesplus.displaymsg(stdscr,["Bad java file"])
            else:
                break
    else:
        njavapath = "java"
    p.step("Preparing scripts",True)
    while True:
        memorytoall: str = cursesplus.cursesinput(stdscr,"How much memory should the server get? (EX: 1024M, 5G)")
        if memorytoall.endswith("M") or memorytoall.endswith("G"):
            try:
                l = int(memorytoall[0:-1])
                if (memorytoall.endswith("M") and l < 512) or (memorytoall.endswith("G") and l < 1):
                    raise Exception()
            except:
                continue
            else:
                break
        else:
            continue
    njavapath = njavapath.replace("//","/")
    __SCRIPT__ = f"#!/usr/bin/sh\n{njavapath} -jar -Xms{memorytoall} -Xmx{memorytoall} {S_INSTALL_DIR}/server.jar nogui"
    with open(S_INSTALL_DIR+"/start","w+") as f:
        f.write(__SCRIPT__)
    os.system(f"chmod +x '{S_INSTALL_DIR+'/start'}'")
    p.step("All done!",True)
    startnow = cursesplus.messagebox.askyesno(stdscr,["Do you want to start your server now","to generate remaining config files","and to generate a default world?"])
    APPDATA["servers"].append({"name":servername,"javapath":njavapath,"memory":memorytoall,"dir":S_INSTALL_DIR,"version":PACKAGEDATA["id"]})
    updateappdata()
    if not startnow:
        return
    curses.reset_shell_mode()
    _OLDDIR = os.getcwd()
    os.chdir(S_INSTALL_DIR)
    os.system(f"'{S_INSTALL_DIR}/start'")
    
    curses.reset_prog_mode()
    os.chdir(_OLDDIR)
    stdscr.clear()
    
def servermgrmenu(stdscr):
    stdscr.clear()
    global APPDATA
    chosenserver = cursesplus.displayops(stdscr,["Back"]+[a["name"] for a in APPDATA["servers"]],"Please choose a server")
    if chosenserver == 0:
        return
    else:
        _sname = [a["name"] for a in APPDATA["servers"]][chosenserver-1]
        if os.path.isdir(SERVERSDIR+"/"+_sname):
            SERVER_DIR = SERVERSDIR+"/"+_sname
            _ODIR = os.getcwd()
            os.chdir(SERVER_DIR)

            #Manager server
            while True:
                w = cursesplus.displayops(stdscr,["Back","Start Server","Change MOTD","Advanced config","Delete server"])
                if w == 0:
                    break
                elif w == 1:
                    stdscr.clear()
                    stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}")
                    stdscr.refresh()
                    curses.reset_shell_mode()
                    os.system("./start")
                    curses.reset_prog_mode()
                    stdscr.clear()
                    stdscr.refresh()
                elif w == 2:
                    if not os.path.isfile("server.properties"):
                        cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
                    else:
                        with open("server.properties") as f:
                            config = PropertiesParse.load(f.read())
                        cursesplus.displaymsg(stdscr,["Current Message Is",config["motd"]])
                        newmotd = cursesplus.cursesinput(stdscr,"Please input a new MOTD")
                        config["motd"] = newmotd
                        with open("server.properties","w+") as f:
                            f.write(PropertiesParse.dump(config))
                elif w == 3:
                    if not os.path.isfile("server.properties"):
                        cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
                    else:
                        with open("server.properties") as f:
                            config = PropertiesParse.load(f.read())
                        while True:
                            chc = cursesplus.optionmenu(stdscr,["BACK"]+[f for f in list(config.keys())])
                            if chc == 0:
                                break
                            else:
                                cursesplus.displaymsg(stdscr,["Current value of Is",list(config.values())[chc-1]])
                                newval = cursesplus.cursesinput(stdscr,f"Please input a new value for {list(config.keys())[chc-1]}")
                                config[list(config.keys())[chc-1]] = newval
                        with open("server.properties","w+") as f:
                            f.write(PropertiesParse.dump(config))
                elif w == 4:
                    if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER"]):
                        if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER","THIS IS YOUR LAST CHANCE"]):
                            os.chdir(SERVERSDIR)
                            shutil.rmtree(SERVER_DIR)
                            del APPDATA["servers"][chosenserver-1]
                            cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                            stdscr.clear()
                            break

        else:
            cursesplus.displaymsg(stdscr,["ERROR","Server not found"])

def updateappdata():
    global APPDATA
    global APPDATAFILE
    with open(APPDATAFILE,"w+") as f:
        f.write(json.dumps(APPDATA))

def main(stdscr):
    global VERSION_MANIFEST
    global VERSION_MANIFEST_DATA
    global APPDATAFILE
    try:
        curses.start_color()

        cursesplus.displaymsgnodelay(stdscr,["Auto Minecraft Server","Starting..."])
        global APPDATA
        APPDATAFILE = os.path.expanduser("~/.local/share/mcserver")+"/config.json"
        if not os.path.isdir(os.path.expanduser("~/.local/share/mcserver")):
            os.mkdir(os.path.expanduser("~/.local/share/mcserver"))
        if not os.path.isfile(APPDATAFILE):
            with open(APPDATAFILE,"w+") as f:
                f.write(json.dumps(__DEFAULTAPPDATA__))
            APPDATA = __DEFAULTAPPDATA__
        else:
            try:
                with open(APPDATAFILE) as f:
                    APPDATA = json.load(f)
            except:
                with open(APPDATAFILE,"w+") as f:
                    f.write(json.dumps(__DEFAULTAPPDATA__))
                APPDATA = __DEFAULTAPPDATA__
        #Graphics support loading
        if not internet_on():
            if not cursesplus.messagebox.askyesno(stdscr,["WARNING","No internet connection could be found!","You may run in to errors","Are you sure you want to continue?"]):
                return
        VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
        
        setupservernow = False
        if not APPDATA["hasCompletedOOBE"]:
            stdscr.clear()
            cursesplus.displaymsg(stdscr,["AMCS OOBE","","Welcome to AutoMinecraftServer: The best way to make a Minecraft server","This guide will help you set up your first Minecraft Server","","v1.0"])
            
            setupservernow = cursesplus.messagebox.askyesno(stdscr,["AMCS OOBE","","Would you like to set up a server now?"])
            stdscr.clear()
            if setupservernow:
                
                setupnewserver(stdscr)

        APPDATA["hasCompletedOOBE"] = True
        updateappdata()
        mx,my = os.get_terminal_size()
        if mx < 120 or my < 20:
            cursesplus.messagebox.showwarning(stdscr,["Your terminal size may be too small","Some instability may occur","For best results, set size to","at least 120x20"])
        while True:
            m = cursesplus.displayops(stdscr,["Set up new server","View list of servers","Quit"],"AMCS 1.0")
            if m == 2:

                return
            elif m == 0:

                setupnewserver(stdscr)
            elif m == 1:
                servermgrmenu(stdscr)
    except KeyboardInterrupt:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to quit?"]):
            sys.exit()
    except Exception as e:
        cursesplus.displaymsg(stdscr,["An error occured",str(e)])


curses.wrapper(main)