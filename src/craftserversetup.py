#!/usr/bin/python3
#Early load variables
#TODO - Backup profiles and improvements, bungeecord support (if possible)
VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
APP_VERSION = 1#The API Version.
APP_UF_VERSION = "1.47"
#The semver version
UPDATEINSTALLED = False
DOCFILE = "https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/doc/craftserversetup.epdoc"
DEVELOPER = False#Enable developer tools by putting DEVELOPER as a startup flag
MODRINTH_USER_AGENT = f"Enderbyte-Programs/CraftServerSetup/{APP_UF_VERSION}"
SHOW_ADVERT = False
print(f"CraftServerSetup by Enderbyte Programs v{APP_UF_VERSION} (c) 2023-2025")

### Standard Library Imports ###

import shutil                   #File utilities
import sys                      #C Utilities
import os                       #OS System Utilities
import curses                   #NCurses Terminal Library
import curses.textpad           #Geometry drawing extension
import json                     #JSON Parser
import signal                   #Unix Signal Interceptor
import datetime                 #Getting current date
import subprocess               #Starting processes
import glob                     #File system pattern matching
import zipfile                  #Extracting ZIP Archive
from time import sleep          #For delays
import hashlib                  #Calculate file hashes
import platform                 #Get system information
import threading                #Start threads
import random                   #Random number generation
import traceback                #Error management
import webbrowser               #Advertisements
import tarfile                  #Create archives
import gzip                     #Compression utilities
import time                     #Timezone data
import textwrap                 #Text wrapping
import copy                     #Object copies
import enum                     #Just a coding thing
import io                       #File streams
import shlex                    #Data parsing
import re                       #Pattern matching

WINDOWS = platform.system() == "Windows"

if sys.version_info < (3,10):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!! Serious  Error !!!!!!")
    print("!! Python version too old !!")
    print("! Use version 3.7 or newer !")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    input("Press enter to halt -->")
    sys.exit(5)

### SET UP SYS.PATH TO ONLY USE my special library directory
if not WINDOWS:#Windows edition will package libraries already
    sys.path.insert(1,os.path.expanduser("~/.local/lib/craftserversetup"))
    sys.path.insert(1,"/usr/lib/craftserversetup")
    if "bin" in sys.argv[0]:
        sys.path = [s for s in sys.path if not "site-packages" in s]#Removing conflicting dirs TODO!!!! REMOVE THIS LATER
        
        DEBUG=False
      
    else:
        DEBUG=True
        rpr = sys.argv[0]
        if not sys.argv[0].startswith("/"):
            rpr = os.getcwd()+"/"+rpr
        ddr = os.path.split(os.path.split(rpr)[0])[0]+"/lib"
        
        print(ddr)
        if os.path.isdir(ddr):
            sys.path.insert(1,ddr)#Add lib dir to path
        
else:
    DEBUG = False
#Third party libraries below here
import cursesplus               #Terminal Display Control
from cursesplus import CheckBoxItem
import requests                 #Networking Utilities
import urllib.request
import urllib.error
import yaml                     #Parse YML Files
from epadvertisements import *  #Advertisements library (BY ME)
import epdoc                    #Documentations library (BY ME)
import pngdim                   #Calculate dimensions of a PNG file
import epprodkey                #Product key manager
import eptranslate              #Translations
from eptranslate import t       #Shorthand

___DEFAULT_SERVER_PROPERTIES___ = r"""
accepts-transfers=false
allow-flight=false
allow-nether=true
broadcast-console-to-ops=true
broadcast-rcon-to-ops=true
difficulty=easy
enable-command-block=false
enable-jmx-monitoring=false
enable-query=false
enable-rcon=false
enable-status=true
enforce-secure-profile=true
enforce-whitelist=false
entity-broadcast-range-percentage=100
force-gamemode=false
function-permission-level=2
gamemode=survival
generate-structures=true
generator-settings={}
hardcore=false
hide-online-players=false
initial-disabled-packs=
initial-enabled-packs=vanilla
level-name=world
level-seed=
level-type=minecraft:normal
log-ips=true
max-chained-neighbor-updates=1000000
max-players=20
max-tick-time=60000
max-world-size=29999984
motd=A Minecraft Server
network-compression-threshold=256
online-mode=true
op-permission-level=4
player-idle-timeout=0
prevent-proxy-connections=false
pvp=true
query.port=25565
rate-limit=0
rcon.password=
rcon.port=25575
region-file-compression=deflate
require-resource-pack=false
resource-pack=
resource-pack-id=
resource-pack-prompt=
resource-pack-sha1=
server-ip=
server-port=25565
simulation-distance=10
spawn-animals=true
spawn-monsters=true
spawn-npcs=true
spawn-protection=16
sync-chunk-writes=true
text-filtering-config=
use-native-transport=true
view-distance=10
white-list=false
"""

__BEDROCK_DEFAULT_SERVER_PROPERTIES__ = r"""
server-name=Dedicated Server
gamemode=survival
force-gamemode=false
difficulty=easy
allow-cheats=false
max-players=10
online-mode=true
allow-list=false
server-port=19132
server-portv6=19133
enable-lan-visibility=true
view-distance=32
tick-distance=4
player-idle-timeout=30
max-threads=8
level-name=Bedrock level
level-seed=
default-player-permission-level=member
texturepack-required=false
content-log-file-enabled=false
compression-threshold=1
compression-algorithm=zlib
server-authoritative-movement=server-auth
player-position-acceptance-threshold=0.5
player-movement-action-direction-threshold=0.85
server-authoritative-block-breaking-pick-range-scalar=1.5
chat-restriction=None
disable-player-interaction=false
client-side-chunk-generation-enabled=true
block-network-ids-are-hashes=true
disable-persona=false
disable-custom-skins=false
server-build-radius-ratio=Disabled
allow-outbound-script-debugging=false
allow-inbound-script-debugging=false
script-debugger-auto-attach=disabled
"""

PLUGIN_HELP = r"""
So You Can't Find Your Plugin

Sometimes Modrinth can be finicky and you can't find your plugin. Here are some things that could have happened:

- The plugin owner misconfigured the plugin, leading to its exclusion from results
- The plugin is listed to work on (say 1.19 +) but since it is 1.20, it works anyway but you can't find it
- You are using a forge or fabric server. This program does not officially support them but you are allowed to import them anyway

Do not worry; There are things you can do to find your plugin/mod. These are leniency settings. In leniency settings, you can change the following settings:

Enforce Version         If enabled, makes sure that the plugin explicitly lists the server version as a supported version

Enforce Software        If enabled, makes sure that the plugin explicitly supports Bukkit

Enforce Type            If enabled, makes sure that what you are downloading is actually a mod and not something else
"""

COLOURS_ACTIVE = False

def merge_dicts(a,b):
    if sys.version_info < (3,9):
        return {**a,**b}
    else:
        return a | b

def restart_colour():
    global COLOURS_ACTIVE
    if not COLOURS_ACTIVE:
        curses.start_color()
        COLOURS_ACTIVE = True
REPAIR_SCRIPT = """cd ~/.local/share;mkdir crss-temp;cd crss-temp;tar -xf $1;bash scripts/install.sh;cd ~;rm -rf ~/.local/share/crss-temp"""#LINUX ONLY
def sigint(signal,frame):
    restart_colour()
    message = ["Are you sure you want to quit?"]
    if len(SERVER_INITS.items()) > 0:
        message.append(f"Your {len(SERVER_INITS.items())} running servers will be stopped")
    if cursesplus.messagebox.askyesno(_SCREEN,message):
        safe_exit(0)

def verifykey(key:str):
    global SHOW_ADVERT
    f = epprodkey.check(key)
    headers = {
        "product_id" : "gVPMT86BgvfmzlvJ8i9RnQ==",
        "license_key" : key
            }
    r = requests.post("https://api.gumroad.com/v2/licenses/verify",data=headers)
    if r.status_code == 404:
        rz = False
    elif r.json()["success"]:
        rz = True
    else:
        rz = False
    SHOW_ADVERT = not (f or rz)
    return f or rz

def prodkeycheck(a):
    return not SHOW_ADVERT

def compatibilize_appdata(data:dict) -> dict:
    """This function ensures that appdata is brought up to the latest version"""
    try:
        cver = data["version"]
    except:
        data["version"] = APP_VERSION

    if not "language" in data:
        data["language"] = None

    if not "settings" in data:
        data["settings"] = {

        "transitions":{
            "display" : "Show Transitions?",
            "type" : "bool",
            "value" : True
        },
        "oldmenu":{
            "name" : "oldmenu",
            "display" : "Use legacy style menus?",
            "type" : "bool",
            "value" : False
        }
    }
    elif type(data["settings"]) == list:
        #Update data
        data["settings"] = {

        "transitions":{
            "display" : "Show Transitions?",
            "type" : "bool",
            "value" : data["settings"][1]["value"]
        },
        "oldmenu":{
            "name" : "oldmenu",
            "display" : "Use legacy style menus?",
            "type" : "bool",
            "value" : data["settings"][2]["value"]
        }

        }
    if not "showprog" in data["settings"]:
        data["settings"]["showprog"] = {
            "name" : "showprog",
            "display" : "Show progress bar startup?",
            "type" : "bool",
            "value":True
        }
    if not "editor" in data["settings"]:
        data["settings"]["editor"] = {
            "name" : "editor",
            "display" : "Text Editor",
            "type" : "str",
            "value" : "/usr/bin/editor %s"
        }
    if not "autoupdate" in data["settings"]:
        data["settings"]["autoupdate"] = {
            "name":"autoupdate",
            "display":"Update automatically",
            "type":"bool",
            "value":True
        }
    if not "productKey" in list(data.keys()):
        data["productKey"] = ""
    if not "pkd" in list(data.keys()):
        data["pkd"] = False

    if not "idata" in data:
        data["idata"] = {
        "MOTD" : "No Message Yet",
        "dead" : {
            "active" : False,
            "message" : "N/A"
        }
    }
    svri = 0
    for svr in data["servers"]:
        if type(svr) is not dict:
            del svr
            continue#I don't know how this happened
        if not "id" in svr:
            data["servers"][svri]["id"] = random.randint(1111,9999)
        if not "settings" in svr:
            data["servers"][svri]["settings"] = {}#New empty settings
        if data["servers"][svri]["settings"] == {}:
            data["servers"][svri]["settings"] = {"launchcommands":[],"exitcommands":[]}
        if not "legacy" in data["servers"][svri]["settings"]:
            data['servers'][svri]["settings"]["legacy"] = True
        if not "backupdir" in svr:
            data['servers'][svri]["backupdir"] = SERVERS_BACKUP_DIR + os.sep + str(data['servers'][svri]["id"])
        svri += 1

    svk = 0
    for ji in data["javainstalls"]:
        data["javainstalls"][svk] = {"path":ji["path"].replace("\\","/").replace("//","/"),"ver":ji["ver"]}

        svk += 1
    if not "license" in data:
        data["license"] = False
        
    if not "backupprofiles" in data:
        #Works with glob
        data["backupprofiles"] = {
            "everything" : {
                "include" : [
                    "#SD/**"
                ],
                "exclude" : [
                    
                ]
            }
        }

    return data

def internet_on():
    try:
        urllib.request.urlopen('http://google.com', timeout=10)
        return True
    except:
        return False

def assemble_package_file_path(serverdir:str):
    return TEMPDIR+"/packages-spigot-"+serverdir.replace("\\","/").split("/")[-1]+".json"

### DETECT PORTABLE INSTALLATION ###
ogpath = sys.argv[0]
execdir = os.path.split(ogpath)[0]
PORTABLE = False
#Read startup flag
if os.path.isdir(execdir):
    if os.path.isfile(execdir+"/startupflags.txt"):
        with open(execdir+"/startupflags.txt") as f:
            sfd = f.read().lower()
        
        if "portable" in sfd :
            PORTABLE = True
        if "developer" in sfd:
            DEVELOPER = True
if "-p" in sys.argv or "--portable" in sys.argv:
    PORTABLE = True
if "-d" in sys.argv or "--developer" in sys.argv:
    DEVELOPER = True
if not WINDOWS:
    APPDATADIR = os.path.expanduser("~/.local/share/mcserver")
    if PORTABLE:
        APPDATADIR = execdir+"/AppData"
    SERVERSDIR = APPDATADIR + "/servers"
    SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
    TEMPDIR = APPDATADIR + "/temp"
    BACKUPDIR = os.path.expanduser("~/.local/share/crss_backup")
    ASSETSDIR = APPDATADIR + "/assets"
else:
    
    APPDATADIR = os.path.expandvars("%APPDATA%/mcserver")
    if PORTABLE:
        APPDATADIR = execdir+"/AppData"
    SERVERSDIR = APPDATADIR + "/servers"
    SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
    TEMPDIR = APPDATADIR + "/temp"
    BACKUPDIR = os.path.expandvars("%APPDATA%/crss_backup")
    ASSETSDIR = APPDATADIR + "/assets"

DOCDOWNLOAD = ASSETSDIR + "/craftserversetup.epdoc"

if not os.path.isdir(APPDATADIR):
    os.mkdir(APPDATADIR)
if not os.path.isdir(SERVERSDIR):
    os.mkdir(SERVERSDIR)
if not os.path.isdir(TEMPDIR):
    os.mkdir(TEMPDIR)
if not os.path.isdir(BACKUPDIR):
    os.mkdir(BACKUPDIR)
if not os.path.isdir(SERVERS_BACKUP_DIR):
    os.mkdir(SERVERS_BACKUP_DIR)
if not os.path.isdir(ASSETSDIR):
    os.mkdir(ASSETSDIR)
__DEFAULTAPPDATA__ = {
    "servers" : [

    ],
    "hasCompletedOOBE" : False,
    "version" : APP_VERSION,
    "javainstalls" : [

    ],
    "productKey" : "",
    "pkd" : False,
    "settings" : {
        "transitions":{
            "display" : "Show Transitions?",
            "type" : "bool",
            "value" : True
        },
        "oldmenu":{
            "name" : "oldmenu",
            "display" : "Use legacy style menus?",
            "type" : "bool",
            "value" : False
        },
        "showprog" : {
            "name" : "showprog",
            "display" : "Show progress bar on startup?",
            "type" : "bool",
            "value" : True
        }
    },
    "idata" : {
        "MOTD" : "No Message Yet",
        "dead" : {
            "active" : False,
            "message" : "N/A"
        }
    },
    "license" : False,
    "language" : None
}

_transndt = False
try:
    eptranslate.load("translations.toml")
except:
    try:
        eptranslate.load(APPDATADIR+"/translations.toml")
    except:
        print("WARN: Can't find translations file.")
        _transndt = True

def extract_links_from_page(data: str) -> list[str]:
    dl = data.split("href=")
    final = []
    for dm in dl[1:]:
        final.append(dm.split("\"")[1])
    return final

class ServerRunWrapper:
    def __init__(self,command):
        self.command = command
        self.datastream = io.StringIO()
        
    def launch(self):
        devnull = open(os.devnull)
        self.process = subprocess.Popen(shlex.split(self.command),stdin=subprocess.PIPE,stdout=devnull,stderr=devnull,universal_newlines=True,process_group=0)
        self.pid = self.process.pid
        self.runtime = datetime.datetime.now()
    def isprocessrunning(self):
        return self.process.poll() is None
    def send(self,lines):
        if type(lines) == str:
            lines = [lines]
        for line in lines:
            if line.strip() == "":
                continue
            self.process.stdin.write(line+"\n")
            self.process.stdin.flush()
    def safestop(self):
        try:
            self.send("stop")
        except:
            self.fullhalt()
    def fullhalt(self):
        try:
            self.process.kill()
        except:
            return#Already dead
    def getexitcode(self):
        if not self.isprocessrunning() :
            return self.process.returncode
        else:
            return None
    def hascrashed(self):
        if self.getexitcode() is None:
            return None
        else:
            code = self.getexitcode()
            if code != 0:
                if code < 128 or code > 130:
                    return True
                else:
                    return False
            else:
                return False

SERVER_INITS:dict[str,ServerRunWrapper] = {}

def product_key_page(stdscr,force=False):
    if force:
        npk = crssinput(stdscr,"Please insert your product key (case sensitive)")
        if not verifykey(npk):
            cursesplus.messagebox.showwarning(stdscr,["Invalid key","Make sure you have entred it correctly and that you have a stable internet connection"])
        else:
            APPDATA["productKey"] = npk
            cursesplus.messagebox.showinfo(stdscr,["Thank you for upgrading!",":D"],"Success")
            updateappdata()
            return
    else:
        o = crss_custom_ad_menu(stdscr,["Open store website","Insert product key","Cancel"])
        if o == 0:
            webbrowser.open("https://ko-fi.com/s/f44efdb343")
        elif o == 1:
            npk = crssinput(stdscr,"Please insert your product key (case sensitive)")
            if not verifykey(npk):
                cursesplus.messagebox.showwarning(stdscr,["Invalid key","Make sure you have entred it correctly and that you have a stable internet connection"])
            else:
                APPDATA["productKey"] = npk
                cursesplus.messagebox.showinfo(stdscr,["Thank you for upgrading!",":D"],"Success")
                updateappdata()
                return
        elif o == 2:
            return

def package_server_script(indir:str,outfile:str) -> int:
    try:
        pushd(indir)
        with tarfile.open(outfile,"w:xz") as tar:
            tar.add(".")
        popd()
    except:
        return 1
    return 0

def unpackage_server(infile:str,outdir:str) -> int:
    try:
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        pushd(outdir)
        with tarfile.open(infile,"r:xz") as tar:
            tar.extractall(".")
        popd()
    except:
        return 1
    return 0

### END UTILS

def safe_exit(code):
    updateappdata()
    for server in list(SERVER_INITS.values()):
        server.safestop()
    sys.exit(code)

def send_telemetry():
    global APPDATA
    rdx = {
        "OperatingSystem" : platform.platform(),
        "ServerCount" : len(APPDATA["servers"]),
        "IsActivated" : APPDATA["productKey"] != "",
        "ApplicationVersion" : APP_UF_VERSION
        }
    #cursesplus.textview(_SCREEN,text=str(rdx))
    r = requests.post("http://enderbyteprograms.net:11111/craftserversetup/call",data=str(json.dumps(rdx)),headers={"Content-Type":"application/json"})
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
def error_handling(e:Exception,message="A serious error has occured"):
    global COLOURS_ACTIVE
    global _SCREEN
    _SCREEN.clear()
    _SCREEN.nodelay(0)
    _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
    #cursesplus.messagebox.showerror(_SCREEN,[
    #    "o3   /      We are sorry, but a serious error occured     ",
    #    "   - |      In the next menu, you will choose some options",
    #    "o3   \\     You should probably report this as a bug       "
    #])
    while True:
        erz = cursesplus.optionmenu(_SCREEN,["Exit Program","View Error info","Return to main menu","Advanced options","Report bug on GitHub"],f"{message}. What do you want to do?")
        if erz == 0:
            safe_exit(1)
        elif erz == 1:
            cursesplus.textview(_SCREEN,text=f"TYPE: {type(e)}"+"\n"+f"MESSAGE: {str(e)[0:os.get_terminal_size()[0]-1]}"+"\n"+traceback.format_exc(),message="Error info")
           
        elif erz == 2:
            if WINDOWS:
                cursesplus.messagebox.showerror(_SCREEN,["This feature is not yet available on Windows"])
                continue
            if cursesplus.messagebox.askyesno(_SCREEN,["Do you want to update the most recent App data?","If you suspect your appdata is corrupt, do not say yes"]):
                updateappdata()
            _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLACK,cursesplus.WHITE))
            main(_SCREEN)
        elif erz == 3:
            while True:
                aerz = cursesplus.optionmenu(_SCREEN,["Back","Repair CraftServerSetup","Reset CraftServerSetup"],"Please choose an advanced option")
                if aerz == 0:
                    break
                elif aerz == 1:
                    if WINDOWS:
                        cursesplus.messagebox.showerror(_SCREEN,["This feature is not available on Windows"])
                        continue
                    if cursesplus.messagebox.askyesno(_SCREEN,["This will re-install CraftServerSetup and restore any lost files.","You will need to have a release downloaded"]):
                        flz = cursesplus.filedialog.openfiledialog(_SCREEN,"Please choose the release file",[["*.xz","crss XZ Release"],["*","All files"]])
                        _SCREEN.erase()
                        _SCREEN.refresh()
                        curses.reset_shell_mode()
                        z = os.system(REPAIR_SCRIPT.replace("$1","\""+flz+"\""))
                        curses.reset_prog_mode()
                        if z != 0:
                            cursesplus.messagebox.showwarning(_SCREEN,["Error repairing","Please try a manual repair"])
                elif aerz == 2:
                    if cursesplus.messagebox.askyesno(_SCREEN,["This will delete all servers","Are you sure you wish to proceed?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                        os.chdir(os.path.expanduser("~"))
                        try:
                            shutil.rmtree(APPDATADIR)
                            os.mkdir(APPDATADIR)
                            sys.exit(1)
                        except:
                            cursesplus.messagebox.showerror(_SCREEN,["Failed to wipe"])
        elif erz == 4:
            webbrowser.open("https://github.com/Enderbyte-Programs/CraftServerSetup/issues")
            _SCREEN.erase()
            cursesplus.displaymsg(_SCREEN,["In your bug report, please make sure to include","the contents of the","View Error Info screen"])
            
def safe_error_handling(e:Exception):
    global COLOURS_ACTIVE
    global _SCREEN
    _SCREEN.nodelay(0)
    _SCREEN.clear()
    _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
    raw =  f"TYPE: {type(e)}"+"\n"+f"MESSAGE: {str(e)[0:os.get_terminal_size()[0]-1]}"+"\n"+traceback.format_exc()
    #splitext = textwrap.wrap(raw,_SCREEN.getmaxyx()[1]-1)
    splitext = raw.splitlines()
    while True:
        _SCREEN.clear()
        my,mx = _SCREEN.getmaxyx()
        cursesplus.utils.fill_line(_SCREEN,0,cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        cursesplus.utils.fill_line(_SCREEN,1,cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        cursesplus.utils.fill_line(_SCREEN,2,cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        _SCREEN.addstr(3,0,"─"*(mx-1))
        _SCREEN.addstr(0,0,"A fatal error has occured in CraftServerSetup. Info is listed below.",cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        _SCREEN.addstr(1,0,"Press C to return to the main menu.",cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        _SCREEN.addstr(2,0,"Press R to open a bug report on Github. Include information listed below.",cursesplus.set_colour(cursesplus.RED,cursesplus.WHITE))
        ey = 3
        for eline in splitext:
            ey += 1
            try:
                _SCREEN.addstr(ey,0,eline)
            except:
                break
        _SCREEN.refresh()
        c = _SCREEN.getch()
        if c == 99:
            break
        elif c == 114:
            webbrowser.open("https://github.com/Enderbyte-Programs/CraftServerSetup/issues/new")
            _SCREEN.erase()
            cursesplus.displaymsg(_SCREEN,["In your bug report, please make sure to include","the contents of the","error in the previous screen.","You can see the error again by pressing any key."])
    _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLACK,cursesplus.WHITE))
        
__DIR_LIST__ = [os.getcwd()]
def pushd(directory:str):
    global __DIR_LIST__
    os.chdir(directory)
    __DIR_LIST__.insert(0,directory)
def popd():
    global __DIR_LIST__
    __DIR_LIST__.pop(0)
    os.chdir(__DIR_LIST__[0])
def get_java_version(file="java") -> str:
    try:
        if not WINDOWS:
            return subprocess.check_output(fr"{file} -version 2>&1 | grep -Eow '[0-9]+\.[0-9]+' | head -1",shell=True).decode().strip()
        else:
            return subprocess.check_output(f"{file} --version").decode().splitlines()[0].split(" ")[1]
    except:
        return "Unknown"

def manage_whitelist(stdscr,whitefile:str):
    try:
        with open(whitefile) as f:
            dat = json.load(f)
    except:
        dat = []#Fix bug number 18: Running this before setup finish causes crash
    while True:
        dop = crss_custom_ad_menu(stdscr,["ADD PLAYER","FINISH"]+[p["name"] for p in dat],"Choose a player to remove or choose bolded options")
        if dop == 1:
            with open(whitefile,"w+") as f:
                f.write(json.dumps(dat))
            return
        elif dop == 0:
            cursesplus.utils.showcursor()
            name = crssinput(stdscr,"Name(s) of players allowed: (Seperate with commas)")
            cursesplus.utils.hidecursor()
            names = name.split(",")
            for player in names:
                cursesplus.displaymsg(stdscr,[player],False)
                try:
                    pluid = get_player_uuid(player)
                except:
                    cursesplus.messagebox.showerror(stdscr,[f"{player} does not appear to be a valid username.","Please make sure you have typed it correctly."])
                    continue
                dat.append({"uuid":pluid,"name":player})
        else:
            del dat[dop-2]

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
            try:
                val = float(val)# Convert to int if you can
            except:
                pass
            else:
                try:
                    val = int(str(val))
                except:
                    if val == int(val):
                        val = int(val)
                    pass
            if val == "true" or val == "false":
                val = val == "true"# Convert to bool if you can
            final[key] = val
        return final
    @staticmethod
    def dump(d: dict) -> str:
        l = ""
        for f in d.items():
            lout = f[1]
            if isinstance(lout,float):
                if int(lout) == lout:
                    lout = int(lout)#Prevent unnescendsary decimals
            if isinstance(lout,bool):
                if lout:
                    lout = "true"
                else:
                    lout = "false"
            l += f[0] + "=" + str(lout) + "\n"
        return l

def trail(ind,maxlen:int):
    if maxlen < 1:
        return ""
    ind = str(ind)
    if len(ind) > maxlen:
        return ind[0:maxlen-4]+"..."
    else:
        return ind

def dict_to_calctype(inputd) -> list:# Inputd must be dict or list. Fixed because of bug when running on py3.9
    if inputd is None:
        return ["NULL!!"]
    final = []
    if type(inputd) == dict:
        for ik in list(inputd.items()):
            src = ik[0]
            dst = ik[1]
            if type(dst) == int or type(dst) == float:
                obtype = "number"
            elif type(dst) == str:
                obtype = "string"
            elif type(dst) == dict:
                obtype = "folder"
            elif type(dst) == list:
                obtype = "list"
            elif type(dst) == bool:
                obtype = "bool"
            else:
                obtype = str(type(dst))
            final.append(f"{src} ( {obtype} ) = {trail(dst,os.get_terminal_size()[1]-20)}")
    else:
        oi = 0
        for ik in list(inputd):
            if type(ik) == int or type(ik) == float:
                obtype = "number"
            elif type(ik) == str:
                obtype = "string"
            elif type(ik) == dict:
                obtype = "folder"
            elif type(ik) == list:
                obtype = "list"
            elif type(ik) == bool:
                obtype = "bool"
            else:
                obtype = str(type(ik))
            final.append(f"Object {oi} ( {obtype} ) = {trail(ik,os.get_terminal_size()[1]-30)}")
            oi += 1
    return final

def dictpath(inputd:dict,path:str):
    if path == "/":
        return inputd
    final = inputd
    for axx in path.split("/"):
        if axx == "":
            continue
        if type(final) == list:
            final = final[int(axx)]
        else:
            final = final[axx]
    return final

def dictedit(stdscr,inputd:dict,name:str,isflat:bool=False) -> dict:
    """isflat controls if you are allowed to add new folders/list"""
    path = "/"
    while True:
        mx,my = os.get_terminal_size()
        path = path.replace("//","/")
        options = ["Quit","Move up directory","ADD ITEM"]
        currentedit = dictpath(inputd,path)
        options += dict_to_calctype(currentedit)
        e = cursesplus.coloured_option_menu(stdscr,options,f"{name} | Path: {path}",[
            [
                "quit",cursesplus.RED
            ],["ADD",cursesplus.GREEN],
            ["list",cursesplus.YELLOW],
            ["folder",cursesplus.YELLOW],
            ["string",cursesplus.CYAN],
            ["number",cursesplus.MAGENTA]
        ],preselected=2,footer="When editing a key: If you didn't mean to edit, press enter without doing anything")
        if e == 0:
            return inputd
        elif e == 1:
            if path != "/":
                path = "/".join(path.split("/")[0:-1])
            else:
                continue
        elif e == 2:
            if type(dictpath(inputd,path)) == dict:
                keynamne = crssinput(stdscr,"Please input the key name.")
                ktype = crss_custom_ad_menu(stdscr,["Cancel add","String","Number","Boolean (yes/no)","Empty list","Empty folder"],"What is the type of the key")
                if ktype > 3 and isflat:
                    cursesplus.messagebox.showerror(stdscr,["The selected type is not supported by this","file format"])
                    continue
                if ktype == 0:
                    continue
                elif ktype == 1:
                    val = crssinput(stdscr,"What is the value of this key?")
                elif ktype == 2:
                    val = cursesplus.numericinput(stdscr,"What is the value of this key?",True,True)
                    if int(val) == val:
                        val = int(val)
                elif ktype == 3:
                    val = cursesplus.messagebox.askyesno(stdscr,["New value for boolean?"])
                elif ktype == 4:
                    val = []
                elif ktype == 5:
                    val = {}
                paths = [z for z in path.split("/") if z != ""]
                mydata = inputd
                for i in paths:
                    if type(mydata) == list:
                        mydata = mydata[int(i)]
                    else:
                        mydata = mydata[i]
                mydata[keynamne] = val 
            elif type(dictpath(inputd,path)) == list:
                #keynamne = crssinput(stdscr,"Please input the key name.")
                ktype = crss_custom_ad_menu(stdscr,["Cancel add","String","Number","Boolean (yes/no)","Empty list","Empty folder"],"What is the type of the key")
                if ktype == 0:
                    continue
                elif ktype == 1:
                    val = crssinput(stdscr,"What is the value of this key?")
                elif ktype == 2:
                    val = cursesplus.numericinput(stdscr,"What is the value of this key?",True,True)
                    if int(val) == val:
                        val = int(val)
                elif ktype == 3:
                    val = cursesplus.messagebox.askyesno(stdscr,["New value for boolean?"])
                elif ktype == 4:
                    val = []
                elif ktype == 5:
                    val = {}
                paths = [z for z in path.split("/") if z != ""]
                mydata = inputd
                for i in paths:
                    if type(mydata) == list:
                        mydata = mydata[int(i)]
                    else:
                        mydata = mydata[i]
                mydata.append(val)
        else:
            newval = None
            if type(currentedit) == dict:
                path += "/" + list(currentedit.items())[e-3][0]
            elif type(currentedit) == list:
                path += "/" + str(e-3)
            epath = path.split("/")[-1]
            if type(dictpath(inputd,path)) == str:
                cursesplus.utils.showcursor()
                newval = crssinput(stdscr,f"Please input a new value for {path}",prefiltext=dictpath(inputd,path))
                cursesplus.utils.hidecursor()
            elif type(dictpath(inputd,path)) == int or type(dictpath(inputd,path)) == float:
                cursesplus.utils.showcursor()
                newval = cursesplus.numericinput(stdscr,f"Please input a new value for {path}",True,True,prefillnumber=dictpath(inputd,path))
                cursesplus.utils.hidecursor()
            elif type(dictpath(inputd,path)) == bool:
                if dictpath(inputd,path):
                    nv = cursesplus.messagebox.MessageBoxStates.YES
                else:
                    nv = cursesplus.messagebox.MessageBoxStates.NO
                newval = cursesplus.messagebox.askyesno(stdscr,["New boolean value for",path],default=nv)
            if type(dictpath(inputd,path)) != dict and type(dictpath(inputd,path)) != list:
                path = "/".join(path.split("/")[0:-1]) 
            if newval is not None:
                paths = [z for z in path.split("/") if z != ""]
                mydata = inputd
                for i in paths:
                    if type(mydata) == list:
                        mydata = mydata[int(i)]
                    else:
                        mydata = mydata[i]
                mydata[epath] = newval      

def package_server(stdscr,serverdir:str,chosenserver:int):
    sdata = APPDATA["servers"][chosenserver]
    with open(serverdir+"/exdata.json","w+") as f:
        f.write(json.dumps(sdata))
        #Write server data into a temporary file
    wdir=cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a folder for the output server file")
    if os.path.isdir(wdir):
        wxfileout=wdir+"/"+sdata["name"]+".amc"
        nwait = cursesplus.PleaseWaitScreen(stdscr,["Packaging Server"])
        nwait.start()
        package_server_script(serverdir,wxfileout)
        nwait.stop()
        nwait.destroy()
        #if pr != 0:
        #    cursesplus.messagebox.showerror(stdscr,["An error occured packaging your server"])
        os.remove(serverdir+"/exdata.json")
        cursesplus.messagebox.showinfo(stdscr,["Server is packaged."])

def download_vanilla_software(stdscr,serverdir) -> dict:
    cursesplus.displaymsg(stdscr,["Getting version information"],False)
    
    stdscr.clear()
    stdscr.erase()
    downloadversion = crss_custom_ad_menu(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
    if downloadversion == 0:
        return
    else:
        stdscr.clear()
        cursesplus.displaymsg(stdscr,["Getting version manifest..."],False)
        PACKAGEDATA = requests.get(VERSION_MANIFEST_DATA["versions"][downloadversion-1]["url"]).json()
        cursesplus.displaymsg(stdscr,["Preparing new server"],False)
    S_DOWNLOAD_data = PACKAGEDATA["downloads"]["server"]
    S_DOWNLOAD_size = parse_size(S_DOWNLOAD_data["size"])
    cursesplus.displaymsg(stdscr,["Downloading server file",f"Size: {S_DOWNLOAD_size}"],False)
    urllib.request.urlretrieve(S_DOWNLOAD_data["url"],serverdir+"/server.jar")
    return PACKAGEDATA

def download_spigot_software(stdscr,serverdir,javapath) -> dict:
    cursesplus.displaymsg(stdscr,["Downloading server file"],False)
    urllib.request.urlretrieve("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar",serverdir+"/BuildTools.jar")
    os.chdir(serverdir)
    while True:
        build_lver = cursesplus.messagebox.askyesno(stdscr,["Do you want to build the latest version of Spigot?","YES: Latest version","NO: different version"])
        p = cursesplus.ProgressBar(stdscr,13000,cursesplus.ProgressBarTypes.FullScreenProgressBar,show_log=True,message="Building Spigot")
        if not build_lver:
            curses.curs_set(1)
            xver = crssinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
            curses.curs_set(0)
        else:
            xver = "latest"
        PACKAGEDATA = {"id":xver}
        mx = os.get_terminal_size()[0]-4
        proc = subprocess.Popen([javapath,"-jar","BuildTools.jar","--rev",xver],shell=False,stdout=subprocess.PIPE)
        tick = 0
        while True:
            output = proc.stdout.readline()
            if proc.poll() is not None:
                break
            if output:
                tick += 1
                if tick > 100:
                    stdscr.clear() 
                for l in output.decode().strip().splitlines():
                    try:
                        p.step()
                        
                        p.appendlog(l.replace("\r","").replace("\n","")[0:mx])
                    except:
                        p.max += 100
                        p.step()
                        
                        p.appendlog(l.replace("\r","").replace("\n","")[0:mx])
        rc = proc.poll()
        if rc == 0:
            p.done()
            PACKAGEDATA["id"] = glob.glob("spigot*.jar")[0].split("-")[1].replace(".jar","")#Update version value as "latest" is very ambiguous. UPDATE: Fix bug where version is "1.19.4.jar"
            os.rename(glob.glob("spigot*.jar")[0],"server.jar")
            break
        else:
            cursesplus.messagebox.showerror(stdscr,["Build Failed","Please view the log for more info"])
    return PACKAGEDATA

def download_paper_software(stdscr,serverdir) -> dict:
    VMAN = requests.get("https://api.papermc.io/v2/projects/paper").json()
    stdscr.erase()
    pxver = list(reversed(VMAN["versions"]))[crss_custom_ad_menu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
    BMAN = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds").json()
    buildslist = list(reversed(BMAN["builds"]))
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to install the latest build of Paper","It is highly recommended to do so"]):
        builddat = buildslist[0]
    else:
        stdscr.erase()
        builddat = buildslist[crss_custom_ad_menu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
    bdownload = f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'
    #cursesplus.displaymsg(stdscr,[f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'])
    cursesplus.displaymsg(stdscr,["Downloading server file"],False)
    
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id":VMAN["versions"][VMAN["versions"].index(pxver)]}
    return PACKAGEDATA

def download_purpur_software(stdscr,serverdir) -> dict:
    verlist = list(reversed(requests.get("https://api.purpurmc.org/v2/purpur").json()["versions"]))
    verdn = verlist[crss_custom_ad_menu(stdscr,verlist,"Choose a version")]
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to install the latest build?","This is highly recommended"]):
        bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/latest/download"
    else:
        dz = list(reversed(requests.get(f"https://api.purpurmc.org/v2/purpur/{verdn}").json()["builds"]["all"]))
        builddn = crss_custom_ad_menu(stdscr,dz)
        bdownload = bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/{dz[builddn]}/download"
    cursesplus.displaymsg(stdscr,["Downloading file..."],False)
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id" : verlist[verlist.index(verdn)]}
    return PACKAGEDATA

def list_recursive_contains(lst: list,item:str) -> int:
    ii = 0
    for i in lst:
        if item in i:
            return ii
        ii += 1
    raise IndexError("Could not find item")

def get_by_list_contains(lst: list,item:str):
    return lst[list_recursive_contains(lst,item)]

class LogEntry:
    def __init__(self,file:str,date:datetime.date,data:str,indict=None):
        if indict is not None:
            self.data = indict["rawdata"]
            self.file = indict["fromfile"]
            self.logdate = datetime.datetime.strptime(indict["date"],"%Y-%m-%d").date()
            self.playername = indict["player"]
        else:
            self.data = data
            self.file = file
            self.logdate = date
            if is_log_line_a_chat_line(data):
                if "[Server]" in data:
                    self.playername = "[Server]"
                else:
                    self.playername = data.split("<")[1].split(">")[0]
            else:
                self.playername = ""
            
    def __str__(self):
        return f"{self.logdate} {self.data}"
    
    def todict(self):
        return {
            "rawdata" : self.data,
            "date" : str(self.logdate),
            "fromfile" : self.file,
            "player" : self.playername
        }
        
    def fromdict(indict:dict):
        return LogEntry(None,None,None,indict)

def load_log_entries_from_raw_data(data:str,fromfilename:str) -> list[LogEntry]:
    if "latest" in fromfilename:
        ld = datetime.datetime.now().date()
    else:
        ld = datetime.date(
            int(fromfilename.split("-")[0]),
            int(fromfilename.split("-")[1]),
            int(fromfilename.split("-")[2])
        )
    final = []
    for le in data.splitlines():
        final.append(LogEntry(fromfilename,ld,le))
    return final
        
def is_log_line_a_chat_line(line:str) -> bool:
    if (("INFO" in line and "<" in line and ">" in line) or "[Server]" in line) and "chat" in line.lower():
        return True
    else:
        return False
    
def is_log_entry_a_chat_line(le:LogEntry) -> bool:
    return is_log_line_a_chat_line(le.data)

class BedrockWorld:
    def __init__(self,path,name):
        self.path = path
        self.name = name

def bedrock_enum_worlds(serverdir:str) -> list[BedrockWorld]:
    worldsdir = serverdir + "/worlds"
    if not os.path.isdir(worldsdir):
        raise Exception("No worlds could be found")
    else:
        final = []
        for file in os.listdir(worldsdir):
            file = (worldsdir+"/"+file).strip()
            #cursesplus.messagebox.showinfo(stdscr,[file])
            if os.path.isdir(file):
                
                tmp = BedrockWorld("","")
                tmp.path = file
                with open(file+"/levelname.txt") as f:
                    tmp.name = f.read().strip()
                final.append(tmp)
        return final

def uf_toggle_conv(b:bool) -> str:
    if b:
        return "[-] Disable"
    else:
        return "[+] Enable"

def bedrock_whitelist(stdscr,serverdir:str):
    # Oh no! I'm racist!
    
    allowfile = serverdir+"/allowlist.json"
    if not os.path.isfile(allowfile):
        cursesplus.messagebox.showerror(stdscr,["Please start your server at least once","to use this feature.;"])
    else:
        with open(serverdir+"/server.properties") as f:
            r = f.read()
        pdata = PropertiesParse.load(r)
        with open(allowfile) as f:
            data:list = json.load(f)
        while True:
            wtd = crss_custom_ad_menu(stdscr,["FINISH","Add new player",f"{uf_toggle_conv(pdata['allow-list'])} Allowlist"]+["[-] "+d["name"] for d in data],"Managing allowlist",footer="Add a player or delete an existing player from the allowlist.")
            if wtd == 0:
                break
            elif wtd == 1:
                plname = crssinput(stdscr,"What is the player's Xbox/Minecraft username?")
                plxuid = crssinput(stdscr,"If you know it, what is the user's XUID? (Press enter if unknown)")
                data.append({
                    "name" : plname,
                    "xuid" : plxuid
                })
            elif wtd == 2:
                pdata["allow-list"] = not pdata["allow-list"]
            else:
                data.remove(data[wtd-3])
        with open(allowfile,"w+") as f:
            json.dump(data,f)

        with open(serverdir+"/server.properties","w+") as f:
            f.write(PropertiesParse.dump(pdata))

def bedrock_world_settings(stdscr,serverdir:str,data:dict) -> dict:

    while True:
        availableworlds = bedrock_enum_worlds(serverdir)
        op = crss_custom_ad_menu(stdscr,["FINISH","Create New World"]+[a.name for a in availableworlds],footer="Choose a world to select or delete, or create a world",title=f"Current world: {data['level-name']}")
        if op == 0:
            break
        elif op == 1:
            levelname = crssinput(stdscr,"Choose a name for the world")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to choose a custom seed?","If you answer no, a random seed will be chosen."],default=cursesplus.messagebox.MessageBoxStates.NO):
                newseed = crssinput(stdscr,"Choose a seed")
            else:
                newseed = ""
            os.mkdir(serverdir+"/worlds/"+levelname)
            with open(serverdir+"/worlds/"+levelname+"/levelname.txt","x") as f:
                f.write(levelname)
            cursesplus.messagebox.showinfo(stdscr,["The world will be generated","the next time you start your server."])
            data["level-name"] = levelname
            data["level-seed"] = newseed
        else:
            selectedworld = availableworlds[op-2]
            while True:
                stdscr.clear()
                cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
                stdscr.addstr(1,0,"Press C to do nothing and return to the previous menu")
                stdscr.addstr(2,0,"Press S to select this world (load it on the server)")
                stdscr.addstr(3,0,"Press D to delete this world")
                stdscr.addstr(0,0,f"Inspecting {selectedworld.name}",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
                
                stdscr.addstr(5,0,"Name")
                stdscr.addstr(6,0,"File path")
                stdscr.addstr(7,0,"World size")
                stdscr.addstr(5,20,selectedworld.name)
                stdscr.addstr(6,20,selectedworld.path)
                stdscr.addstr(7,20,parse_size(get_tree_size(selectedworld.path)))
                stdscr.refresh()
                
                ch = curses.keyname(stdscr.getch()).decode().lower()
                if ch == "c":
                    break
                elif ch == "s":
                    data["level-name"] = selectedworld.name
                    data["level-seed"] = ""#Clear seed - Hope it doesn't cause problems
                    cursesplus.messagebox.showinfo(stdscr,["This world is now selected","It will be loaded the next time","you start your server."])
                    break
                elif ch == "d":
                    if cursesplus.messagebox.askyesno(stdscr,["Are you sure you wish to delete this world?","It will be gone forever!"],default=cursesplus.messagebox.MessageBoxStates.NO):
                        shutil.rmtree(selectedworld.path)
                        break
    return data

def configure_bedrock_server(stdscr,directory:str,data:dict) -> dict:
    while True:
        wtd = crss_custom_ad_menu(stdscr,["FINISH","Basic options","World settings","Advanced options"])
        if wtd == 0:
            return data
        elif wtd == 1:
            data["server-name"] = crssinput(stdscr,"What is the public name of the server?")
            data["gamemode"] = ["survival","creative","adventure"][crss_custom_ad_menu(stdscr,["Survival","Creative","Adventure"],"Choose gamemode for server")]
            cd = cursesplus.checkboxlist(stdscr,[
                CheckBoxItem("fg","Force Gamemode"),
                CheckBoxItem("cheat","Allow Cheats / commands"),
                CheckBoxItem("secure","Use secure online mode",True),
                CheckBoxItem("al","Use allowlist",False)
            ],"Choose some options")
            data["force-gamemode"] = cd["fg"]
            data["allow-cheats"] = cd["cheat"]
            data["online-mode"] = cd["secure"]
            data["allow-list"] = cd["al"]
            data["view-distance"] = cursesplus.numericinput(stdscr,"What view distance do you want?",minimum=5,maximum=48,prefillnumber=32)
            data["tick-distance"] = cursesplus.numericinput(stdscr,"What simulation distance do you want?",minimum=4,maximum=12,prefillnumber=4)
            data["default-player-permission-level"] = ["visitor","member","operator"][crss_custom_ad_menu(stdscr,["Visitor (very limited access)","Member (Normal player)","Operator (Admin)"],"Select default permissions")]
            data["max-players"] = cursesplus.numericinput(stdscr,"How many players should be allowed on the server?")
        elif wtd == 2:
            data = bedrock_world_settings(stdscr,directory,data)
        elif wtd == 3:
            data["server-port"] = cursesplus.numericinput(stdscr,"What port do you want to host the server on?",minimum=1,maximum=65535,prefillnumber=19132)
            data["server-portv6"] = cursesplus.numericinput(stdscr,"What port do you want the IPV6 server to listen on?",minimum=1,maximum=65535,prefillnumber=19133)
            data["enable-lan-visibility"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to make this server LAN-discoverable?","This will overwrite previous port choices."])
            data["player-idle-timeout"] = cursesplus.numericinput(stdscr,"Choose AFK timeout (0 to disable)",prefillnumber=0)
            data["max-threads"] = cursesplus.numericinput(stdscr,"How many multiprocessing threads should the server use? (0 for as many as possible)")
            ii = cursesplus.checkboxlist(stdscr,[
                cursesplus.CheckBoxItem("texturepack-required","Require use of custom texture pack"),
                cursesplus.CheckBoxItem("content-log-file-enabled","Enable content error logging",True)
            ])
            data = merge_dicts(data,ii)
            data["compression-algorithm"] = ["zlib","snappy"][crss_custom_ad_menu(stdscr,["zlib","snappy"],"Choose compression algorith")]
            data["server-authoritative-movement"] = crss_option_retr_str(stdscr,["client-auth - No anticheat","server-auth - Weak anticheat","server-auth-with-rewind - Strong anticheat"],"Choose anticheat")
            data["chat-restriction"] = crss_option_retr_str(stdscr,["None - Allow chat","Dropped - Disallow chat","Disabled - Silently hide chat"],"Choose chat restriction")
            iii = cursesplus.checkboxlist(stdscr,[
                CheckBoxItem("disable-player-interaction","Discourage players from interaction"),
                CheckBoxItem("client-side-chunk-generation-enabled","Allow players to generate extra chunks",True),
                CheckBoxItem("block-network-ids-are-hashes","Use randomized network ids"),
                CheckBoxItem("disable-custom-skins","Forbid custom skins"),
                CheckBoxItem("allow-outbound-script-debugging","Allow outbound debugging"),
                CheckBoxItem("allow-inbound-script-debugging","Allow inbound debugging"),
                CheckBoxItem("script-debugger-auto-attach","Auto enable debugger")
            ])
            data = merge_dicts(data,iii)

def crss_option_retr_str(stdscr,options:list,header:str) -> str:
    """Strips based on  - : Use as splitter"""
    return options[crss_custom_ad_menu(stdscr,options,header)].split(" - ")[0]

def bedrock_config_server(stdscr,chosenserver):
    __l = crss_custom_ad_menu(stdscr,["Cancel","Modify server.properties","Modify CRSS Server options","Reset server configuration","Rename Server","Startup Options"])#Todo rename server, memory
    if __l == 0:
        return
    elif __l == 1:
        if not os.path.isfile("server.properties"):
            cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
        else:
            with open("server.properties") as f:
                config = PropertiesParse.load(f.read())

            config = dictedit(stdscr,config,"Editing Server Properties",True)
            with open("server.properties","w+") as f:
                f.write(PropertiesParse.dump(config))
    elif __l == 2:
        dt = APPDATA["servers"][chosenserver-1]
        dt = dictedit(stdscr,dt,"More Server Properties")
        APPDATA["servers"][chosenserver-1] = dt
        APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 3:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to reset your server configuration","You won't delete any worlds"]):
            os.remove("server.properties")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up some more server configuration"]):
                sd = setup_server_properties(stdscr)
                with open("server.properties","w+") as f:
                    f.write(PropertiesParse.dump(sd))
    elif __l == 4:
        newname = crssinput(stdscr,"Choose a new name for this server")
        APPDATA["servers"][chosenserver-1]["name"] = newname
        #APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 5:
        APPDATA["servers"][chosenserver-1] = startup_options(stdscr,APPDATA["servers"][chosenserver-1])

def setup_bedrock_server(stdscr):
    while True:
        servername = crssinput(stdscr,"Please choose a name for your server").strip()
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
    p = cursesplus.ProgressBar(stdscr,10,cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.BOTTOM,message="Setting up bedrock server")
    p.step("Getting download information")
    availablelinks = [g for g in extract_links_from_page(requests.get("https://www.minecraft.net/en-us/download/server/bedrock",headers={"User-Agent":MODRINTH_USER_AGENT}).text) if "bedrock" in g]
    link_win_normal = get_by_list_contains(availablelinks,"win/")
    link_lx_normal = get_by_list_contains(availablelinks,"linux/")
    link_win_preview = get_by_list_contains(availablelinks,"win-preview/")
    link_lx_preview = get_by_list_contains(availablelinks,"linux-preview/")
    if WINDOWS:
        availablelinks = [link_win_normal,link_win_preview]
    else:
        availablelinks = [link_lx_normal,link_lx_preview]
    
    l2d = availablelinks[crss_custom_ad_menu(stdscr,["Latest Version","Latest Preview Version"],"Please select a version")]
    p.step("Downloading server file")
    urllib.request.urlretrieve(l2d,S_INSTALL_DIR+"/server.zip")
    p.step("Extracting server file")
    pushd(S_INSTALL_DIR)#Make install easier
    zf = zipfile.ZipFile(S_INSTALL_DIR+"/server.zip")
    zf.extractall(S_INSTALL_DIR)
    zf.close()
    p.step("Removing excess files")
    os.remove(S_INSTALL_DIR+"/server.zip")
    p.step("Preparing exec")
    if not WINDOWS:
        os.chmod(S_INSTALL_DIR+"/bedrock_server",0o777)
    
    
    sd = {
        "name" : servername,
        "javapath" : "",
        "memory" : "",
        "dir" : S_INSTALL_DIR,
        "version" : l2d.split("-")[-1].replace(".zip",""),
        "moddable" : False,
        "software" : 0,
        "id" : random.randint(1111,9999),
        "settings": {
            "launchcommands": [],
            "exitcommands": [],
            "safeexitcommands": []
        },
        "script" : S_INSTALL_DIR+"/bedrock_server",
        "linkused" : l2d,
        "ispreview" : l2d == link_lx_preview or l2d == link_win_preview
    }
    try:
        shutil.copyfile(ASSETSDIR+"/defaulticon.png",S_INSTALL_DIR+"/server-icon.png")
    except:
        pass
    sd["script"] = generate_script(sd)
    APPDATA["servers"].append(sd)
    updateappdata()
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to configure your server's settings now?"]):
        with open(S_INSTALL_DIR+"/server.properties","w+") as f:
            f.write(PropertiesParse.dump(configure_bedrock_server(stdscr,S_INSTALL_DIR,PropertiesParse.load(__BEDROCK_DEFAULT_SERVER_PROPERTIES__))))
    popd()
    p.done()
    bedrock_manage_server(stdscr,servername,APPDATA["servers"].index(sd)+1)

def bedrock_do_update(stdscr,chosenserver,availablelinks):
    l2d = availablelinks[crss_custom_ad_menu(stdscr,["Latest Version","Latest Preview Version"],"Please select a version")]
    #Remember: Don't overwrite server.properties or allowlist.json
    p = cursesplus.ProgressBar(stdscr,5)
    cursesplus.displaymsg(stdscr,["Updating server","Please be patient."],False)
    p.step("Making backup")
    safetydir = generate_temp_dir()
    safefiles = ["server.properties","allowlist.json"]
    safemap = {}
    for sf in safefiles:
        if not os.path.isfile(sf):
            continue
        shutil.copyfile(sf,safetydir+"/"+file_get_md5(sf))
        safemap[sf] = file_get_md5(sf)
    S_INSTALL_DIR = APPDATA["servers"][chosenserver-1]["dir"]
    p.step("Downloading new server")
    #p.step("Downloading server file")
    urllib.request.urlretrieve(l2d,S_INSTALL_DIR+"/server.zip")
    #p.step("Extracting server file")
    pushd(S_INSTALL_DIR)#Make install easier
    p.step("Extracting new server")
    zf = zipfile.ZipFile(S_INSTALL_DIR+"/server.zip")
    zf.extractall(S_INSTALL_DIR)
    zf.close()
    #p.step("Removing excess files")
    os.remove(S_INSTALL_DIR+"/server.zip")
    #p.step("Preparing exec")
    if not WINDOWS:
        os.chmod(S_INSTALL_DIR+"/bedrock_server",0o777)
    p.step("Restoring properties")
    APPDATA["servers"][chosenserver-1]["ispreview"] = l2d == availablelinks[1]
    APPDATA["servers"][chosenserver-1]["version"] = l2d.split("-")[-1].replace(".zip","")
    APPDATA["servers"][chosenserver-1]["linkused"] = l2d
    for sf in safefiles:
        try:
            if os.path.isfile(sf):
                os.remove(sf)
            shutil.copyfile(safetydir+"/"+safemap[sf],sf)
        except:
            pass
    p.done()
    updateappdata()

def bedrock_manage_server(stdscr,servername,chosenserver):
    curver = APPDATA["servers"][chosenserver-1]["linkused"]
    cursesplus.displaymsg(stdscr,["Checking for Bedrock updates"],False)
    availablelinks = [g for g in extract_links_from_page(requests.get("https://www.minecraft.net/en-us/download/server/bedrock",headers={"User-Agent":MODRINTH_USER_AGENT}).text) if "bedrock" in g]
    link_win_normal = get_by_list_contains(availablelinks,"win/")
    link_lx_normal = get_by_list_contains(availablelinks,"linux/")
    link_win_preview = get_by_list_contains(availablelinks,"win-preview/")
    link_lx_preview = get_by_list_contains(availablelinks,"linux-preview/")
    if WINDOWS:
        availablelinks = [link_win_normal,link_win_preview]
    else:
        availablelinks = [link_lx_normal,link_lx_preview]
    
    if APPDATA["servers"][chosenserver-1]["ispreview"]:
        sel = 1
    else:
        sel = 0
        
    latestlink = availablelinks[sel]
    if curver != latestlink:
        if cursesplus.messagebox.askyesno(stdscr,["A bedrock update has been detected.","If you don't install it, devices can't connect.","Do you want to install this update?"]):
            bedrock_do_update(stdscr,chosenserver,availablelinks)
            
    svrd = APPDATA["servers"][chosenserver-1]["dir"]       
    while True:
        wtd = crss_custom_ad_menu(stdscr,["RETURN TO MAIN MENU","Start Server","Server Settings","Delete Server","Configure Allowlist","Export Server","World Settings","Re/change install","FILE MANAGER"],f"Managing {servername}")
        if wtd == 0:
            os.chdir("/")
            return
        elif wtd == 2:
            bedrock_config_server(stdscr,chosenserver)
        elif wtd == 3:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER"],default=cursesplus.messagebox.MessageBoxStates.NO):
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER","THIS IS YOUR LAST CHANCE"],default=cursesplus.messagebox.MessageBoxStates.NO):
                    os.chdir(SERVERSDIR)
                    shutil.rmtree(svrd)
                    del APPDATA["servers"][chosenserver-1]
                    cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                    stdscr.clear()
                    break
            stdscr.erase()
        elif wtd == 8:
            file_manager(stdscr,APPDATA["servers"][chosenserver-1]["dir"],f"Managing files for {servername}")
        elif wtd == 7:
            bedrock_do_update(stdscr,chosenserver,availablelinks)
        elif wtd == 6:
            try:
                with open(svrd+"/server.properties") as f:
                    r = f.read()
                data = PropertiesParse.load(r)
                data = bedrock_world_settings(stdscr,svrd,data)
                with open(svrd+"/server.properties","w+") as f:
                    f.write(PropertiesParse.dump(data))
            except Exception as e:
                cursesplus.messagebox.showerror(stdscr,["There was an error managing worlds.",str(e),"A world may be corrupt."])
        elif wtd == 5:
            package_server(stdscr,svrd,chosenserver-1)
        elif wtd == 4:
            bedrock_whitelist(stdscr,svrd)
        elif wtd == 1:
            os.system(";".join(APPDATA["servers"][chosenserver-1]["settings"]["launchcommands"]))
            os.chdir(APPDATA["servers"][chosenserver-1]["dir"])           
            stdscr.clear()
            stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}\n\r")
            stdscr.refresh()
            if not WINDOWS:
                curses.curs_set(1)
                curses.reset_shell_mode()
                lretr = os.system(APPDATA["servers"][chosenserver-1]["script"])
                #child = pexpect.spawn(APPDATA["servers"][chosenserver-1]["script"])
                #child.expect("Finished")
                curses.reset_prog_mode()
                curses.curs_set(0)
            else:
                curses.curs_set(1)
                curses.reset_shell_mode()
                #COLOURS_ACTIVE = False
                lretr = os.system("cmd /c ("+APPDATA["servers"][chosenserver-1]["script"]+")")
                curses.reset_prog_mode()
                curses.curs_set(0)
                #restart_colour()
            os.system(";".join(APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
            if lretr != 0 and lretr != 127 and lretr != 128 and lretr != 130:
                cursesplus.messagebox.showwarning(stdscr,["Oh No! Your server crashed"])
            stdscr.clear()
            stdscr.refresh()

def setupnewserver(stdscr):
    stdscr.erase()
    
    wtd = crss_custom_ad_menu(stdscr,["Cancel","Create a new server","Import a server from this computer"],"What would you like to do?")
    if wtd == 0:
        return
    elif wtd == 2:
        import_server(stdscr)
        return
    bigserverblock = crss_custom_ad_menu(stdscr,["Cancel","Java (Computer, PC)","Bedrock (Console, Tablet, etc)"],"Choose Minecraft kind to install")
    if bigserverblock == 0:
        return
    elif bigserverblock == 2:
        setup_bedrock_server(stdscr)
        return
        
    while True:
        
        serversoftware = crss_custom_ad_menu(stdscr,["Cancel","Help me choose","Vanilla","Spigot","Paper","Purpur"],"Please choose your server software")
        if serversoftware != 1:
            break
        else:
            cursesplus.textview(stdscr,text="""
                                
Help on choosing a server software
                                
Vanilla                                
This is the normal Minecraft server software. It is the only software that Mojang officially supports. It can't do any plugins.

Spigot
This is an optimized version of Bukkit. It supports plugins but can become memory heavy

Paper
This is an optimized version of Spigot and is very popular. It also supports plugins

Purpur
This is apparently even more optimized. It also supports plugins. It can configure a lot of things in your server
""")
    serversoftware -= 1
    if serversoftware == -1:
        return
    while True:
        curses.curs_set(1)
        servername = crssinput(stdscr,"Please choose a name for your server").strip()
        curses.curs_set(0)
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
    cursesplus.displaymsg(stdscr,["Please wait while your server is set up"],False)
    njavapath = choose_java_install(stdscr)
    if serversoftware == 1:
        PACKAGEDATA = download_vanilla_software(stdscr,S_INSTALL_DIR)
    elif serversoftware == 2:
        PACKAGEDATA = download_spigot_software(stdscr,S_INSTALL_DIR,njavapath)
    elif serversoftware == 3:
        PACKAGEDATA = download_paper_software(stdscr,S_INSTALL_DIR)
    elif serversoftware == 4:
        PACKAGEDATA = download_purpur_software(stdscr,S_INSTALL_DIR)
    cursesplus.displaymsg(stdscr,["Setting up server"],False)
    setupeula = cursesplus.messagebox.askyesno(stdscr,["To proceed, you must agree","To Mojang's EULA","","Do you agree?"])
    if setupeula:
        with open(S_INSTALL_DIR+"/eula.txt","w+") as f:
            f.write("eula=true")# Agree
    stdscr.clear()
    stdscr.erase()
    memorytoall = choose_server_memory_amount(stdscr)

    njavapath = njavapath.replace("//","/")
    serverid = random.randint(1111,9999)
    sd = {"name":servername,"javapath":njavapath,"memory":memorytoall,"dir":S_INSTALL_DIR,"version":PACKAGEDATA["id"],"moddable":serversoftware!=1,"software":serversoftware,"id":serverid,"settings":{"legacy":True,"launchcommands":[],"exitcommands":[]}}
    #_space = "\\ "
    #__SCRIPT__ = f"{njavapath.replace(' ',_space)} -jar -Xms{memorytoall} -Xmx{memorytoall} \"{S_INSTALL_DIR}/server.jar\" nogui"
    __SCRIPT__ = generate_script(sd)
    sd["script"] = __SCRIPT__
    
    APPDATA["servers"].append(sd)
    updateappdata()
    bdir = os.getcwd()
    os.chdir(S_INSTALL_DIR)
    with open("exdata.json","w+") as f:
        f.write(json.dumps(sd)) #Create backup
    advancedsetup = cursesplus.messagebox.askyesno(stdscr,["Would you like to set up your server configuration now?"])
    if not advancedsetup:
        cursesplus.messagebox.showinfo(stdscr,["Default configuration will be generated when you start your server"])
    else:
        data = setup_server_properties(stdscr)
        with open("server.properties","w+") as f:
            f.write(PropertiesParse.dump(data))
    try:
        shutil.copyfile(ASSETSDIR+"/defaulticon.png",S_INSTALL_DIR+"/server-icon.png")
    except:
        pass
    os.chdir(bdir)
    manage_server(stdscr,S_INSTALL_DIR,APPDATA["servers"].index(sd)+1)

def get_player_uuid(username:str):
    req = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    r = requests.get(req).json()
    uuid = r["id"]
    uuidl = list(uuid)
    uuidl.insert(8,"-")
    uuidl.insert(13,"-")
    uuidl.insert(18,"-")
    uuidl.insert(23,"-")
    return "".join(uuidl)

def setup_new_world(stdscr,dpp:dict,serverdir=os.getcwd(),initialconfig=True) -> dict:
    if not initialconfig:
        if not cursesplus.messagebox.askyesno(stdscr,["This will modify your world settings. Are you sure you wish to proceed?"]):
            return
    while True:
        dpp["level-name"] = crssinput(stdscr,"What should your world be called")
        if os.path.isdir(serverdir+"/"+dpp["level-name"]):
            if cursesplus.messagebox.showwarning(stdscr,["This world may already exist.","Are you sure you want to edit its settings?"]):
                break
        else:
            break
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to use a custom seed?","Answer no for a random seed"]):
        dpp["level-seed"] = crssinput(stdscr,"What should the seed be?")
    wtype = crss_custom_ad_menu(stdscr,["Normal","Flat","Large Biome","Amplified","Single Biome","Buffet (1.15 and before)","Customized (1.12 and before)","Other (custom namespace)"],"Please choose the type of world.")
    if wtype == 7:
        wname = crssinput(stdscr,"Please type the full name of the custom world type")
    elif wtype == 0:
        wname = "minecraft:normal"
    elif wtype == 1:
        wname = "minecraft:flat"
    elif wtype == 2:
        wname = "minecraft:large_biomes"
    elif wtype == 3:
        wname = "minecraft:amplified"
    elif wtype == 4:
        wname = "minecraft:single_biome_surface"
    elif wtype == 5:
        wname = "minecraft:buffet"
    elif wtype == 6:
        wname = "minecraft:customized"
    dpp["level-type"] = wname
    if wtype == 1 or wtype == 4 or wtype == 5 or wtype == 6:
        if wtype == 1:
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to customize the flat world?"]):
               dpp["generator-settings"] = crssinput(stdscr,f"Please type generator settings for {wname}") 
        else:
            dpp["generator-settings"] = crssinput(stdscr,f"Please type generator settings for {wname}")

    if not initialconfig:
        #Provide more settings
        #dpp["allow-flight"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable flight for non-admins on this world?"])
        #dpp["allow-nether"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable the nether on this world?"])
        #dpp["generate-structures"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable structure generation on this world?"])
        #dpp["hardcore"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable hardcore mode on this world?"])
        dpp["difficulty"] = str(crss_custom_ad_menu(stdscr,["Peaceful","Easy","Normal","Hard"],"Please select the difficulty of your world"))
        dpp["gamemode"] = str(crss_custom_ad_menu(stdscr,["survival","creative","adventure","spectator"],"Please select the gamemode of this world"))
        #dpp["enable-command-block"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable command blocks on this world?"])
        #dpp["pvp"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to allow PVP?"])
        #dpp["spawn-animals"] = cursesplus.messagebox.askyesno(stdscr,["Spawn animals?"])
        #dpp["spawn-monsters"] = cursesplus.messagebox.askyesno(stdscr,["Spawn monsters?"])
        #dpp["spawn-npcs"] = cursesplus.messagebox.askyesno(stdscr,["Spawn villagers?"])
        sslxdd = cursesplus.checkboxlist(stdscr,[
            CheckBoxItem("allow-flight","Allow Flight for all players",False),
            CheckBoxItem("allow-nether","Allow the nether",True),
            CheckBoxItem("generate-structures","Generate structures such as villages",True),
            CheckBoxItem("hardcore","Enable Hardcore mode",False),
            CheckBoxItem("enable-command-block","Allow command block usage",True),
            CheckBoxItem("pvp","Allow PVP",True),
            CheckBoxItem("spawn-animals","Spawn Passive animals",True),
            CheckBoxItem("spawn-monsters","Spawn monsters",True),
            CheckBoxItem("spawn-npcs","Spawn Villagers",True)
        ],"Please choose configuration for your server")
        dpp = merge_dicts(dpp,sslxdd)

    return dpp
def setup_server_properties(stdscr,data=PropertiesParse.load(___DEFAULT_SERVER_PROPERTIES___)) -> dict:
    dpp = data
    cursesplus.utils.showcursor()
    while True:
        lssl = crss_custom_ad_menu(stdscr,["Basic Settings","World Settings","Advanced Settings","Network Settings","FINISH","Setup Resource pack"],"Server Configuration Setup")
        #Go through all of the properties 1 by 1...
        if lssl == 4:
            cursesplus.utils.hidecursor()
            return dpp
        elif lssl == 3:
            #Network Settings

            #dpp["enable-rcon"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable Remote CONtrol on this server?","WARNING: This could be dangerous"])
            #dpp["enable-status"] = not cursesplus.messagebox.askyesno(stdscr,["Would you like to hide this server's status?"])
            #dpp["enable-query"] = not cursesplus.messagebox.askyesno(stdscr,["Would you like to hide this server's player count?"])
            #dpp["hide-online-players"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to hide the player list?"])
            #dpp["prevent-proxy-connection"] = not cursesplus.messagebox.askyesno(stdscr,["Do you want to allow proxy connections?"])
            iiodd = cursesplus.checkboxlist(stdscr,[
                CheckBoxItem("enable-rcon","Enable remote control (Advanced users only!)",False),
                CheckBoxItem("enable-status","Show server online status",True),
                CheckBoxItem("enable-query","Show server player count",True),
                CheckBoxItem("hide-online-players","Show list of online players",True),
                CheckBoxItem("prevent-proxy-connection","Permit proxy connections",True)
            ],'Please choose configuration for your server')
            dpp = merge_dicts(dpp,iiodd)
            dpp["query.port"] = cursesplus.numericinput(stdscr,"Please input the query port: (default 25565)",False,False,1,65535,25565)        
            dpp["server-port"] = cursesplus.numericinput(stdscr,"Please input the port that this server listens on: (default 25565)",False,False,1,65535,25565)  


            if dpp["enable-rcon"]:
                dpp["broadcast-rcon-to-ops"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable RCON (Remote CONtrol) output to operators?"])
                dpp["rcon.password"] = crssinput(stdscr,"Please input RCON password",passwordchar="*")
                dpp["rcon.port"] = cursesplus.numericinput(stdscr,"Please input the RCON port: (default 25575)",False,False,1,65535,25575)

        elif lssl == 2:
            #Advanced settings
            dpp["broadcast-console-to-ops"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable verbose output to operators?"])
            dpp["entity-broadcast-range-percentage"] = cursesplus.numericinput(stdscr,"What distance percentage should entities be sent to the client?",minimum=10,maximum=1000,prefillnumber=100)
            #dpp["enforce-secure-profile"] = not cursesplus.messagebox.askyesno(stdscr,["Do you want to allow cracked accounts to join?"])
            seclevel = crss_custom_ad_menu(stdscr,["Maximum (reccommended) - Secure profile and valid account","Moderate - Valid account, secure profile not required","Minimum - Cracked / illegal accounts permitted"],"Please choose a security option")
            if seclevel == 0:
                dpp["enforce-secure-profile"] = True
                dpp["online-mode"] = True
            elif seclevel == 1:
                dpp["enforce-secure-profile"] = False
            else:
                dpp["enforce-secure-profile"] = False
                dpp["online-mode"] = False
            dpp["white-list"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to enable whitelist on this server?"])
            if dpp["white-list"]:
                if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up a whitelist now?"]):
                    manage_whitelist(stdscr,os.getcwd()+"/whitelist.json")
                if cursesplus.messagebox.askyesno(stdscr,["Do you want to enfore the white list?"]):
                    dpp["enforce-whitelist"] = True
            dpp["force-gamemode"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to force players to use the default game mode?"])
            dpp["function-permission-level"] = crss_custom_ad_menu(stdscr,["1 (Bypass spawn protection)","2 (Singleplayer commands)","3 (Player management (ban/kick))","4 (Manage server)"],"Please choose the default op admin level") + 1
            dpp["max-chained-neighbor-updates"] = cursesplus.numericinput(stdscr,"Please input maximum chained neighboue updates",allownegatives=True,minimum=-1,prefillnumber=1000000)
            dpp["max-tick-time"] = cursesplus.numericinput(stdscr,"How many milliseconds should watchdog wait?",False,True,-1,2**32,60000)
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to enable anti-afk?"]):
                dpp["player-idle-timeout"] = cursesplus.numericinput(stdscr,"Minutes of AFK before player is kicked:",False,False,0,1000000)
            else:
                dpp["player-idle-timeout"] = 0
            dpp["accept-transfers"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to allow people to automatically transfer to this server?"])
            dpp["region-file-compression"] = ["deflate","lz4","none"][crss_custom_ad_menu(
                stdscr,
                ["Deflate (old algorithm, small size, high cpu)","LZ4 (more space, low cpu)","No compression (slow, huge space, no cpu)"],
                "What compression should the world files use?"
            )]
            
        elif lssl == 0:
            #basic
            dpp["difficulty"] = str(crss_custom_ad_menu(stdscr,["Peaceful","Easy","Normal","Hard"],"Please select the difficulty of your server"))
            dpp["gamemode"] = str(crss_custom_ad_menu(stdscr,["survival","creative","adventure","spectator"],"Please select the gamemode of your server"))
            #dpp["enable-command-block"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable command blocks on your server?"])
            dpp["max-players"] = cursesplus.numericinput(stdscr,"How many players should be allowed? (max players)",minimum=1,maximum=1000000,prefillnumber=20)
            dpp["motd"] = "\\n".join(crssinput(stdscr,"What should your server message say?",2,59).splitlines())
            #dpp["pvp"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to allow PVP?"])
            dpp["simulation-distance"] = cursesplus.numericinput(stdscr,"What should the maximum simulation distance on the server be?",False,False,2,32,10)
            dpp["view-distance"] = cursesplus.numericinput(stdscr,"What should the maximum view distance on the server be?",False,False,2,32,10)
            sslxdd = cursesplus.checkboxlist(stdscr,[
            CheckBoxItem("allow-flight","Allow Flight for all players",False),
            CheckBoxItem("allow-nether","Allow the nether",True),
            CheckBoxItem("generate-structures","Generate structures such as villages",True),
            CheckBoxItem("hardcore","Enable Hardcore mode",False),
            CheckBoxItem("enable-command-block","Allow command block usage",True),
            CheckBoxItem("pvp","Allow PVP",True),
            CheckBoxItem("spawn-animals","Spawn Passive animals",True),
            CheckBoxItem("spawn-monsters","Spawn monsters",True),
            CheckBoxItem("spawn-npcs","Spawn Villagers",True)
            ],"Please choose configuration for your server")
            dpp = merge_dicts(dpp,sslxdd)
            
        elif lssl == 1:
            #world
            dpp = setup_new_world(stdscr,dpp)
            cursesplus.messagebox.showinfo(stdscr,["World created successfully"])
        elif lssl == 5:
            dpp = resource_pack_setup(stdscr,dpp)

def resource_pack_setup(stdscr,dpp:dict) -> dict:
    while True:
        z = crss_custom_ad_menu(stdscr,["Done","Set Resource pack URL","Change resource pack settings","Disable resource pack"])
        if z == 0:
            return dpp
        elif z == 1:
            uurl = crssinput(stdscr,"Input the URI to your resource pack (Direct download link)")
            cursesplus.displaymsg(stdscr,["Testing link"],False)
            try:
                lzdir = TEMPDIR+"/rp"+str(random.randint(11111,99999))
                os.mkdir(lzdir)
                urllib.request.urlretrieve(uurl,lzdir+"pack.zip")
                with open(lzdir+"pack.zip",'rb') as pack:
                    p = pack.read()
                packsha = hashlib.sha1(p).hexdigest()
                dpp["resource-pack"] = uurl
                dpp["resource-pack-sha1"] = packsha
            except:
                cursesplus.messagebox.showerror(stdscr,["There was an error while verifying the resource pack.","Make sure you have inputted it correctly."])
        elif z == 2:
            dpp["require-resource-pack"] = cursesplus.messagebox.askyesno(stdscr,["Do you want this pack to be required?"])
        elif z == 3:
            dpp["resource-pack"] = ""
            dpp["require-resource-pack"] = "false"
            dpp["resource-pack-sha1"] = ""

def prune_servers():
    global APPDATA
    pushd(SERVERSDIR)
    APPDATA["servers"] = [a for a in APPDATA["servers"] if os.path.isdir(a["dir"])]
    #Look for unregistered directories
    serverdirs = [f for f in os.listdir(SERVERSDIR) if os.path.isdir(f)]
    registereddirs = [a["dir"] for a in APPDATA["servers"]]
    for serverdir in serverdirs:
        if not serverdir in registereddirs:
            if not os.path.isfile(serverdir+"/exdata.json") and not os.path.isfile(serverdir+"/server.properties"):
                shutil.rmtree(serverdir)
    popd()
    updateappdata()

def servermgrmenu(stdscr):
    prune_servers()
    stdscr.clear()
    global APPDATA
    chosenserver = crss_custom_ad_menu(stdscr,["Back"]+[a["name"] for a in APPDATA["servers"]],"Please choose a server")
    if chosenserver == 0:
        return
    else:
        _sname = [a["dir"] for a in APPDATA["servers"]][chosenserver-1]
        if os.path.isdir(_sname):
            manage_server(stdscr,_sname,chosenserver)
            updateappdata()

        else:
            cursesplus.messagebox.showerror(stdscr,["This server does not exist"])
            
            del APPDATA["servers"][chosenserver-1]#Unregister bad server
            updateappdata()

def jar_get_bukkit_plugin_name(file: str) -> dict:
    zf = zipfile.ZipFile(file)
    tmpxhash = hashlib.md5(zf.read("plugin.yml")).hexdigest()
    tmpxfl = TEMPDIR + "/" + tmpxhash
    if not os.path.isdir(tmpxfl):
        zf.extract("plugin.yml",tmpxfl)
    zf.close()
    with open(tmpxfl+"/plugin.yml") as f:
        plugdata = f.read()
    pdoc = yaml.load(plugdata,yaml.BaseLoader)#NOTE: add dump if this does not return dict
    return {"version":pdoc["version"],"name":pdoc["name"],"mcversion":str(pdoc["api-version"]),"path":file}

def retr_jplug(path: str) -> list[dict]:
    ltk = []
    for fob in os.listdir(path):
        if os.path.isfile(path+"/"+fob):
            ltk.append(os.path.join(path,fob))
    ltk = sorted(ltk,key=str.casefold)
    final = []
    for jf in ltk:
        try:
            final.append(jar_get_bukkit_plugin_name(jf))
        except Exception as e:
            #pass #This isn't a mod file [OLD]
            #New version: now return ???
            final.append({"version":"Unknown version","name":os.path.split(jf)[1],"mcversion":"Unknown","path":jf})
    return final

def file_get_md5(path: str) -> str:
    with open(path,'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()

def process_modrinth_api_return_with_config(responses:list,settings:dict) -> list:
    final = []
    #inres = [i for i in inres if i["project_type"] == "mod" and serverversion in i["versions"] and "bukkit" in i["categories"]]
    for response in responses:
        if settings["enforce-version"]:
            if not settings["serverversion"] in response["versions"]:
                continue#FAIL
        if settings["enforce-software"]:
            if not "bukkit" in response["categories"]:
                continue #FAIL
        if settings["enforce-type"]:
            if response["project_type"] != "mod":
                continue #FAIL #FAIL #FAIL
        final.append(response)
    return final

def modrinth_api_seach_and_download(stdscr,modfolder,serverversion,searchq,limit=1000):
    api_base = "https://api.modrinth.com/v2"
    headers = {"User-Agent":MODRINTH_USER_AGENT,"content-type":"application/json"}
    noffset = 0
    lenset = {
        "enforce-version" : True,
        "enforce-software" : True,
        "enforce-type" : True,
        "serverversion" : serverversion#Easy passing to function
    }
    inres = []
    npage = 1
    while True:
        cursesplus.displaymsg(stdscr,["Searching...",f"Page {npage}"],False)
        try:
            inress = requests.get(api_base+f"/search?query={searchq.strip()}&offset={noffset}",headers=headers)
            inres += inress.json()["hits"]
        except Exception as uuuu:
            cursesplus.messagebox.showwarning(stdscr,["API Limit exceeded","Search results will be limited",str(uuuu)])
            break #We have likely exceeded out limit
        
        noffset += inress.json()["limit"]
        npage += 1
        if inress.json()["offset"] > inress.json()["total_hits"] - inress.json()["limit"] or len(inres) > limit or npage > 200:#Limit to 100
            break
    oldinres = copy.deepcopy(inres)
    inres = process_modrinth_api_return_with_config(inres,lenset)
    while True:
        modch = crss_custom_ad_menu(stdscr,["Cancel","Leniency Settings","Help I can't find what I'm looking for"]+[ikl["title"] for ikl in inres],f"Search results for {searchq}")
        if modch == 0:
            break
        elif modch == 1:
            tl = cursesplus.checkboxlist(stdscr,[
                cursesplus.CheckBoxItem("enforce-version","Enforce Version",lenset["enforce-version"]),
                cursesplus.CheckBoxItem("enforce-software","Enforce Software Type",lenset["enforce-software"]),
                cursesplus.CheckBoxItem("enforce-type","Enforce Type",lenset["enforce-type"])
            ],"Please configure leniencey settings")
            lenset = merge_dicts(lenset,tl)#Merge dicts
            inres = process_modrinth_api_return_with_config(oldinres,lenset)
        elif modch == 2:
            cursesplus.textview(stdscr,text=PLUGIN_HELP,message="Help")
        else:
            chmod = inres[modch-3]
            while True:
                mocho = crss_custom_ad_menu(stdscr,["Cancel","Plugin Info","Download"])
                if mocho == 0:
                    break
                elif mocho == 1:
                    stdscr.clear()
                    stdscr.addstr(0,0,"PLUGIN INFO (press any key to continue)")
                    stdscr.addstr(2,0,"Name")
                    stdscr.addstr(3,0,"Author")
                    stdscr.addstr(4,0,"Date created")
                    stdscr.addstr(5,0,"Last modified")
                    stdscr.addstr(6,0,"Downloads")
                    stdscr.addstr(7,0,"Followers")
                    stdscr.addstr(8,0,"Latest MC ver")
                    stdscr.addstr(2,20,chmod["title"])
                    stdscr.addstr(3,20,chmod["author"])
                    stdscr.addstr(4,20,chmod["date_created"])
                    stdscr.addstr(5,20,chmod["date_modified"])
                    stdscr.addstr(6,20,str(chmod["downloads"]))
                    stdscr.addstr(7,20,str(chmod["follows"]))
                    stdscr.addstr(8,20,chmod["latest_version"])
                    stdscr.addstr(10,0,chmod["description"])#Meant to wrap around
                    stdscr.getch()
                elif mocho == 2:
                    #Download
                    cursesplus.displaymsg(stdscr,["Resolving download address"],False)
                    r6 = requests.get(api_base+"/project/"+chmod["project_id"]+"/version").json()
                    finald = []
                    final = []
                    for item in r6:
                        if serverversion in item["game_versions"] or not lenset["enforce-version"]:
                            finald.append(item)
                            final.append(f"{item['name']} ({item['version_type']})")
                    filed = cursesplus.coloured_option_menu(stdscr,["Cancel"]+final,"Please choose a version to download")
                    if filed == 0:
                        continue
                    primad = [d for d in finald[filed-1]["files"] if d["primary"]][0]
                    cursesplus.displaymsg(stdscr,["Downloading plugin file"],False)
                    urllib.request.urlretrieve(primad["url"],modfolder+"/"+primad["filename"])
                    cursesplus.messagebox.showinfo(stdscr,["Download successful"])
                    break

def chop_str_with_limit(ins:str,limit:int) -> str:
    #Limit ins to limit length
    if len(ins) > limit:
        return ins[0:limit-3]+"..."
    else:
        return ins

def modrinth_api_download_system(stdscr,modfolder,serverversion):
    api_base = "https://api.modrinth.com/v2"
    headers = {"User-Agent":MODRINTH_USER_AGENT,"content-type":"application/json"}
    while True:
        wtd = crss_custom_ad_menu(stdscr,["FINISH","Search for plugins","View most popular plugins"])
        if wtd == 0:
            break
        elif wtd == 1:
            searchq = crssinput(stdscr,"What is the name of the mod you are looking for?")
            modrinth_api_seach_and_download(stdscr,modfolder,serverversion,searchq)
        elif wtd == 2:
            modrinth_api_seach_and_download(stdscr,modfolder,serverversion,"",100)

def process_spigot_api_entries(haystack:list,needle:str) -> list:# Hehe PHP style
    return [z for z in haystack if needle.lower() in z["name"].lower()]

def is_package_file_old_or_dead(stdscr,serverdir) -> bool:
    
    if not os.path.isfile(assemble_package_file_path(serverdir)) :
        return False
    else:
        try:
            with open(assemble_package_file_path(serverdir)) as f:
                data = json.load(f)
            if (datetime.datetime.now() - datetime.datetime.strptime(data["date"],"%Y%m%d")).days > 5:
                if cursesplus.messagebox.askyesno(stdscr,["Your packages list is old.","Would you like to update it?"]):
                    return False
        except:
            return False
        else:
            return True

def write_package_file(packages:list,serverdir:str):
    with open(assemble_package_file_path(serverdir),"w+") as f:
        f.write(json.dumps({"date":datetime.datetime.now().strftime("%Y%m%d"),"packages":[{"name":z["name"],"id":z["id"]} for z in packages]},indent=2))

def spigot_api_manager(stdscr,modfolder:str,serverversion:str,serverdir:str):
    final = []
    headers = {
                "User-Agent" : MODRINTH_USER_AGENT
            }
    if not is_package_file_old_or_dead(stdscr,serverdir):
        px = 1
        
        
        shiftedversion = ".".join(serverversion.split(".")[0:2])
        while True:
            cursesplus.displaymsg(stdscr,["Downloading package list",f"Page {px}"],False)
            rq = f"https://api.spiget.org/v2/resources/for/{shiftedversion}"
            r = requests.get(rq,headers=headers,params={"size":1000,"page":px}).json()
            #cursesplus.textview(stdscr,text=json.dumps(r))
            px += 1
            final += r["match"]
            if len(r["match"]) ==0:
                break
        if len(final) == 0:
            cursesplus.messagebox.showerror(stdscr,["No plugins are available for your server version."])
        write_package_file(final,serverdir)
    else:
        with open(assemble_package_file_path(serverdir)) as f:
            data = json.load(f)
            final = data["packages"]
    final.sort(key=lambda x: x["name"])
    
    activesearch = ""
    display = process_spigot_api_entries(final,activesearch)
    while True:
        wtd = crss_custom_ad_menu(stdscr,["FINISH","New Search"]+[chop_str_with_limit(z["name"],40) for z in display],f"Searching for {activesearch} from Spigot")
        if wtd == 0:
            break
        elif wtd == 1:
            activesearch = crssinput(stdscr,"What do you want to search for?")
            display = process_spigot_api_entries(final,activesearch)
        else:
            chosenplugin = display[wtd-2]
            cursesplus.displaymsg(stdscr,["Fetching plugin info"],False)
            pldat = requests.get(f"https://api.spiget.org/v2/resources/{chosenplugin['id']}",headers=headers).json()
            if pldat["premium"]:
                cursesplus.messagebox.showerror(stdscr,["This is a paid plugin","it can't be downloaded by CRSS.","Please purchase and download","manually."])
                continue
            stdscr.clear()
            cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
            stdscr.addstr(0,0,f"Plugin info for {chosenplugin['name']}",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
            stdscr.addstr(1,0,"Press D to download. Press any other key to go back")
            stdscr.addstr(3,0,"Name")
            stdscr.addstr(4,0,"Downloads")
            stdscr.addstr(5,0,"Description:")
            stdscr.addstr(3,20,pldat["name"])
            stdscr.addstr(4,20,str(pldat["downloads"]))
            stdscr.addstr(6,10,pldat["tag"])
            stdscr.refresh()
            ch = stdscr.getch()
            if ch == 100:
                cursesplus.displaymsg(stdscr,["Downloading"],False)
                _dloc = pldat["file"]["url"].split("/")
                _dloc[1] = _dloc[1].split(".")[1]
                dloc = "/".join(_dloc)
                try:
                    urllib.request.urlretrieve(f"https://api.spiget.org/v2/{dloc}",modfolder+"/"+pldat["name"]+".jar")
                except:
                    cursesplus.messagebox.showerror(stdscr,["There was an error downloading","the plugin. You may have to download it manually."])
    
def svr_mod_mgr(stdscr,SERVERDIRECTORY: str,serverversion,servertype):
    modsforlder = SERVERDIRECTORY + "/plugins"
    if not os.path.isdir(modsforlder):
        os.mkdir(modsforlder)
    while True:
        PLUGSLIST = retr_jplug(modsforlder)
        spldi = crss_custom_ad_menu(stdscr,["BACK","ADD PLUGIN"]+[f["name"]+" (v"+f["version"]+")" for f in PLUGSLIST],"Choose a plugin to manage")
        if spldi == 0:
            return
        elif spldi == 1:
            #add mod
            minstype = cursesplus.coloured_option_menu(stdscr,["Back","Install from file on this computer","Download from Modrinth","Download from Spigot"])
            if minstype == 1:
                modfiles = cursesplus.filedialog.openfilesdialog(stdscr,"Please choose the plugins you would like to add",[["*.jar","JAR Executables"],["*","All files"]])
                for modfile in modfiles:
                    if os.path.isfile(modfile):
                        stdscr.clear()
                        cursesplus.displaymsg(stdscr,["loading plugin",modfile],False)
                        mf_name = os.path.split(modfile)[1]
                        if servertype > 0:
                            try:
                                jar_get_bukkit_plugin_name(modfile)
                            except:
                                
                                if not cursesplus.messagebox.askyesno(stdscr,[f"file {modfile} may not be a Minecraft plugin.","Are you sure you want to add it to your server?"]):
                                    continue
                        shutil.copyfile(modfile,modsforlder+"/"+mf_name)
                stdscr.erase()
            elif minstype == 2:
                modrinth_api_download_system(stdscr,modsforlder,serverversion)
            elif minstype == 3:
                spigot_api_manager(stdscr,modsforlder,serverversion,SERVERDIRECTORY)
        else:
            chosenplug = spldi - 2

            while True:
                wtd = crss_custom_ad_menu(stdscr,["BACK","View Plugin Info","Delete Plugin","Reset Plugin","Edit config.yml"])
                if wtd == 0:
                    break
                elif wtd == 1:
                    stdscr.erase()
                    activeplug = PLUGSLIST[chosenplug]
                    stdscr.addstr(0,0,"PLUGIN INFO")
                    stdscr.addstr(2,0,"Plugin Name")
                    stdscr.addstr(3,0,"Plugin Version")
                    stdscr.addstr(4,0,"Minimum MC Version")
                    stdscr.addstr(5,0,"File path")
                    stdscr.addstr(6,0,"File size")
                    stdscr.addstr(7,0,"MD5 sum")
                    stdscr.addstr(8,0,"AppData size")
                    stdscr.addstr(2,20,activeplug["name"])
                    stdscr.addstr(3,20,activeplug["version"])
                    stdscr.addstr(4,20,activeplug["mcversion"])
                    stdscr.addstr(5,20,activeplug["path"])
                    stdscr.addstr(6,20,parse_size(os.path.getsize(activeplug["path"])))
                    stdscr.addstr(7,20,file_get_md5(activeplug["path"]))
                    if os.path.isdir(SERVERDIRECTORY+"/plugins/"+activeplug["name"]):
                        fsize = parse_size(get_tree_size(SERVERDIRECTORY+"/plugins/"+activeplug["name"]))
                    else:
                        fsize = "0 bytes"
                    stdscr.addstr(8,20,fsize)
                    stdscr.addstr(10,0,"Press any key to proceed",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
                    stdscr.getch()
                elif wtd == 2:
                    if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this plugin from your server?"]):
                        activeplug = PLUGSLIST[chosenplug]
                        os.remove(activeplug["path"])
                        break
                elif wtd == 3:
                    activeplug = PLUGSLIST[chosenplug]
                    if os.path.isdir(SERVERDIRECTORY+"/plugins/"+activeplug["name"]):
                        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you would like to reset this plugin?"]):
                            shutil.rmtree(SERVERDIRECTORY+"/plugins/"+activeplug["name"])
                    else:
                        cursesplus.messagebox.showwarning(stdscr,["This plugin has no AppData so nothing was deleted"])
                elif wtd == 4:
                    activeplug = PLUGSLIST[chosenplug]
                    if os.path.isfile(SERVERDIRECTORY+"/plugins/"+activeplug["name"]+"/config.yml"):
                        ef = SERVERDIRECTORY+"/plugins/"+activeplug["name"]+"/config.yml"
                        with open(ef) as f:
                            data = yaml.load(f,yaml.FullLoader)
                        data = dictedit(stdscr,data,f"{activeplug['name']} config")
                        with open(ef,"w+") as f:
                            f.write(yaml.dump(data,default_flow_style=False))

                    else:
                        cursesplus.messagebox.showerror(stdscr,["This plugin does not have a config file"])

def generate_script(svrdict: dict) -> str:
    if svrdict["software"] == 0:
        if WINDOWS:
            __SCRIPT__ = svrdict["dir"]+"/bedrock_server.exe"
        else:
            __SCRIPT__ = svrdict["dir"]+"/bedrock_server"
    else:
        _space = "\\ "
        _bs = "\\"
        if not WINDOWS:
            __SCRIPT__ = f"{svrdict['javapath'].replace(' ',_space)} -jar -Xms{svrdict['memory']} -Xmx{svrdict['memory']} \"{svrdict['dir']}/server.jar\" nogui"
        else:
            __SCRIPT__ = f"\"{svrdict['javapath']}\" -jar -Xms{svrdict['memory']} -Xmx{svrdict['memory']} \"{svrdict['dir'].replace(_bs,'/')}/server.jar\" nogui"
    return __SCRIPT__

def update_s_software_preinit(serverdir:str):
    pushd(serverdir)

def rm_server_jar():
    if os.path.isfile("server.jar"):
        os.remove("server.jar")

def update_s_software_postinit(PACKAGEDATA:dict,chosenserver:int):
    APPDATA["servers"][chosenserver-1]["version"] = PACKAGEDATA["id"]#Update new version
    generate_script(APPDATA["servers"][chosenserver-1])
    updateappdata()
    popd()

def update_vanilla_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit(serverdir)
    stdscr.erase()
    downloadversion = crss_custom_ad_menu(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
    if downloadversion == 0:
        return
    else:
        stdscr.clear()
        cursesplus.displaymsg(stdscr,["Getting version manifest..."],False)
        PACKAGEDATA = requests.get(VERSION_MANIFEST_DATA["versions"][downloadversion-1]["url"]).json()
        cursesplus.displaymsg(stdscr,["Preparing new server"],False)
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to change the java installation","associated with this server?"]):
        njavapath = choose_java_install(stdscr)
        APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
    S_DOWNLOAD_data = PACKAGEDATA["downloads"]["server"]
    stdscr.clear()
    stdscr.addstr(0,0,"Downloading new server file...")
    stdscr.refresh()
    rm_server_jar()
    urllib.request.urlretrieve(S_DOWNLOAD_data["url"],serverdir+"/server.jar")
    update_s_software_postinit(PACKAGEDATA,chosenserver)
    cursesplus.messagebox.showinfo(stdscr,["Server is updated"])

def update_spigot_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit(serverdir)
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to change the java installation","associated with this server?","WARNING! Make sure you use java 17 or newer"]):
        njavapath = choose_java_install(stdscr)
        APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
    p = cursesplus.ProgressBar(stdscr,2,cursesplus.ProgressBarTypes.FullScreenProgressBar,show_log=True,show_percent=True,message="Updating spigot")
    p.update()
    rm_server_jar()
    urllib.request.urlretrieve("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar","BuildTools.jar")
    p.step()
    while True:
        build_lver = cursesplus.messagebox.askyesno(stdscr,["Do you want to build the latest version of Spigot?","YES: Latest version","NO: different version"])
        if not build_lver:
            curses.curs_set(1)
            xver = crssinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
            curses.curs_set(0)
        else:
            xver = "latest"
        PACKAGEDATA = {"id":xver}
        proc = subprocess.Popen([APPDATA["servers"][chosenserver-1]["javapath"],"-jar","BuildTools.jar","--rev",xver],shell=False,stdout=subprocess.PIPE)
        while True:
            output = proc.stdout.readline()
            if proc.poll() is not None:
                break
            if output:
                for l in output.decode().strip().splitlines():
                    p.appendlog(l.strip().replace("\n","").replace("\r",""))
        rc = proc.poll()
        if rc == 0:
            PACKAGEDATA["id"] = glob.glob("spigot*.jar")[0].split("-")[1].replace(".jar","")#Update version value as "latest" is very ambiguous. UPDATE: Fix bug where version is "1.19.4.jar"
            os.rename(glob.glob("spigot*.jar")[0],"server.jar")
            break
        else:
            cursesplus.messagebox.showerror(stdscr,["Build Failed","Please view the log for more info"])
    
    
    update_s_software_postinit(PACKAGEDATA,chosenserver)

def update_paper_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit(serverdir)
    stdscr.erase()
    VMAN = requests.get("https://api.papermc.io/v2/projects/paper").json()
    stdscr.erase()
    pxver = list(reversed(VMAN["versions"]))[crss_custom_ad_menu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
    BMAN = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds").json()
    buildslist = list(reversed(BMAN["builds"]))
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to update to the latest build of Paper","It is highly recommended to do so"]):
        builddat = buildslist[0]
    else:
        stdscr.erase()
        builddat = buildslist[crss_custom_ad_menu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
    bdownload = f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'
    #cursesplus.displaymsg(stdscr,[f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'])
    stdscr.clear()
    stdscr.addstr(0,0,"Downloading file...")
    stdscr.refresh()
    rm_server_jar()
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id":VMAN["versions"][VMAN["versions"].index(pxver)]}
    update_s_software_postinit(PACKAGEDATA,chosenserver)
    cursesplus.messagebox.showinfo(stdscr,["Server is updated"])

def update_purpur_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit(serverdir)
    verlist = list(reversed(requests.get("https://api.purpurmc.org/v2/purpur").json()["versions"]))
    verdn = verlist[crss_custom_ad_menu(stdscr,verlist,"Choose a version")]
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to install the latest build?","This is highly recommended"]):
        bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/latest/download"
    else:
        dz = list(reversed(requests.get(f"https://api.purpurmc.org/v2/purpur/{verdn}").json()["builds"]["all"]))
        builddn = crss_custom_ad_menu(stdscr,dz)
        bdownload = bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/{dz[builddn]}/download"
    cursesplus.displaymsg(stdscr,["Downloading file..."],False)
    rm_server_jar()
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id" : verlist[verlist.index(verdn)]}
    update_s_software_postinit(PACKAGEDATA,chosenserver)


def view_server_logs(stdscr,server_dir:str):
    logsdir = server_dir+"/logs"
    
    if not os.path.isdir(logsdir):
        cursesplus.messagebox.showwarning(stdscr,["This server has no logs."])
        return
    pushd(logsdir)
    while True:
        availablelogs = list(reversed(sorted([l for l in os.listdir(logsdir) if os.path.isfile(l)])))
        chosenlog = crss_custom_ad_menu(stdscr,["BACK"]+availablelogs,"Please choose a log to view")
        if chosenlog == 0:
            popd()
            return
        else:
            cl = availablelogs[chosenlog-1]
            if cl.endswith(".gz"):
                with open(cl,'rb') as f:
                    data = gzip.decompress(f.read()).decode()
            else:
                with open(cl) as f:
                    data = f.read()
            wtd = crss_custom_ad_menu(stdscr,["Cancel","View all of log","Chat logs only","Chat Utilities"])
            if wtd == 1:
                cursesplus.textview(stdscr,text=data,message=f"Viewing {cl}")
            elif wtd == 3:
                who_said_what(stdscr,server_dir)
            else:
                cursesplus.textview(stdscr,text="\n".join([d for d in data.splitlines() if is_log_line_a_chat_line(d)]))
                
def init_idata(stdscr):
    global APPDATA
    idata = requests.get("https://pastebin.com/raw/GLSGkysJ").json()
    APPDATA["idata"] = idata
    if idata["dead"]["active"]:
        cursesplus.messagebox.showerror(stdscr,["This computer program has been locked.",f"REASON: {idata['dead']['message']}"])
        sys.exit(3)

def find_world_folders(directory) -> list[str]:
    final = []
    drs = os.listdir(directory)
    for fx in drs:
        if os.path.isdir(directory+"/"+fx):
            if os.path.isfile(directory+"/"+fx+"/"+"level.dat"):
                final.append( fx )
    return final

def xdg_open_file(file:str) -> int:
    if not WINDOWS:
        return os.system(f"xdg-open {file}")
    else:
        return os.startfile(file)

def manage_server_icon(stdscr):
    while True:
        ssx = crss_custom_ad_menu(stdscr,["BACK","Change icon","Reset icon","Delete icon","View icon"])
        if ssx == 0:
            break
        elif ssx == 4:
            if os.path.isfile("server-icon.png"):
                xdg_open_file("server-icon.png")
                stdscr.erase()
            else:
                cursesplus.messagebox.showerror(stdscr,["This server does not have an icon."])
        elif ssx == 1:
            fl = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a server icon",[["*.png","PNG Image Files"],["*","All Files"]])
            try:
                d = pngdim.load(fl)
                if not d.is_valid_minecraft_server_image():
                    cursesplus.messagebox.showerror(stdscr,["Minecraft Server icons must be 64x64"])
                    continue
                shutil.copyfile(fl,"server-icon.png")
            except:
                cursesplus.messagebox.showerror(stdscr,["That is not a valid PNG file"])
        elif ssx == 2:
            if cursesplus.messagebox.askyesno(stdscr,["This will change the server icon to the CRSS default. Are you sure you want to proceed?"]):
                try:
                    os.remove("server-icon.png")
                except:
                    pass
                shutil.copyfile(ASSETSDIR+"/defaulticon.png","server-icon.png")
        elif ssx == 3:
            if cursesplus.messagebox.askyesno(stdscr,["This will delete your server icon. Are you sure you want to proceed?"]):
                try:
                    os.remove("server-icon.png")
                except:
                    pass

def config_server(stdscr,chosenserver):
    __l = crss_custom_ad_menu(stdscr,["Cancel","Modify server.properties","Modify CRSS Server options","Reset server configuration","Extra configuration","Rename Server","Change Server Memory","Startup Options"])#Todo rename server, memory
    if __l == 0:
        updateappdata()
        return
    elif __l == 1:
        if not os.path.isfile("server.properties"):
            cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
        else:
            with open("server.properties") as f:
                config = PropertiesParse.load(f.read())

            config = dictedit(stdscr,config,"Editing Server Properties",True)
            with open("server.properties","w+") as f:
                f.write(PropertiesParse.dump(config))
    elif __l == 2:
        dt = APPDATA["servers"][chosenserver-1]
        dt = dictedit(stdscr,dt,"More Server Properties")
        APPDATA["servers"][chosenserver-1] = dt
        APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 3:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to reset your server configuration","You won't delete any worlds"]):
            if os.path.isfile("server.properties"):
                os.remove("server.properties")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up some more server configuration"]):
                sd = setup_server_properties(stdscr)
                with open("server.properties","w+") as f:
                    f.write(PropertiesParse.dump(sd))
    elif __l == 4:
        dt = APPDATA["servers"][chosenserver-1]
        if not dt["moddable"]:
            cursesplus.messagebox.showwarning(stdscr,["There are no extra config options for this type of server"])
        else:
            while True:
                lkz = [os.path.split(z)[1] for z in glob.glob(dt["dir"]+"/*.yml")]
                dz = crss_custom_ad_menu(stdscr,["Quit"]+lkz)
                if dz == 0:
                    break
                else:
                    with open(lkz[dz-1]) as f:
                        data = yaml.load(f,yaml.FullLoader)
                    data = dictedit(stdscr,data,os.path.split(lkz[dz-1])[1])
                    with open(lkz[dz-1],"w+") as f:
                        f.write(yaml.dump(data,default_flow_style=False))
    elif __l == 5:
        newname = crssinput(stdscr,"Choose a new name for this server")
        APPDATA["servers"][chosenserver-1]["name"] = newname
        #APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 6:
        newmem = choose_server_memory_amount(stdscr)
        APPDATA["servers"][chosenserver-1]["memory"] = newmem
        APPDATA["servers"][chosenserver-1]["script"]=generate_script(APPDATA["servers"][chosenserver-1])#Regen script
    elif __l == 7:
        APPDATA["servers"][chosenserver-1] = startup_options(stdscr,APPDATA["servers"][chosenserver-1])

def change_software(stdscr,directory,data) -> dict:
    zxc = crss_custom_ad_menu(stdscr,["Cancel","Vanilla","Spigot","Paper","Purpur"],"Please choose the new software for the server")
    if zxc == 0:
        return data
    elif zxc == 1:
        if data["software"] != 1:
            if not cursesplus.messagebox.askyesno(stdscr,["Danger!","You are downgrading a server","Plugins will no longer work and you may lose data","Are you sure you want to continue?"]):
                return data
        ppr = download_vanilla_software(stdscr,directory)
        if ppr is None:
            return data
        ppx = {"id":ppr["id"]}
        ppx["software"] = 1
        ppx["moddable"] = False
        ndata = merge_dicts(data,ppx)
    elif zxc == 2:
        ppr = download_spigot_software(stdscr,directory,data["javapath"])
        if ppr is None:
            return data
        ppr["software"] = 2
        ppr["moddable"] = True
        ndata = merge_dicts(data,ppr)
    elif zxc == 3:
        ppr = download_paper_software(stdscr,directory)
        if ppr is None:
            return data
        ppr["software"] = 3
        ppr["moddable"] = True
        ndata = merge_dicts(data,ppr)
    elif zxc == 4:
        ppr = download_purpur_software(stdscr,directory)
        if ppr is None:
            return data
        ppr["software"] = 4
        ppr["moddable"] = True
        ndata = merge_dicts(data,ppr)
    return ndata

def text_editor(text:str,headmessage="edit") -> str:
    tmpdir = generate_temp_dir()
    pushd(tmpdir)
    with open(tmpdir+"/"+headmessage,"w+") as f:
        f.write(text)
    editcmd = (APPDATA["settings"]["editor"]["value"] % "\""+headmessage+"\"")
    curses.reset_shell_mode()
    os.system(editcmd)#Wait for finish
    curses.reset_prog_mode()
    with open(tmpdir+"/"+headmessage) as f:
        newdata = f.read()
    cursesplus.utils.hidecursor()
    popd()
    return newdata


def startup_options(stdscr,serverdata:dict):
    while True:
        wtd = crss_custom_ad_menu(stdscr,["Back","Edit startup commands","Edit shutdown commands","Set startup mode"])
        if wtd == 0:
            return serverdata
        elif wtd == 1:
            serverdata["settings"]["launchcommands"] = text_editor("\n".join(serverdata["settings"]["launchcommands"]),"Edit Launch Commands").splitlines()
        elif wtd == 2:
            serverdata["settings"]["exitcommands"] = text_editor("\n".join(serverdata["settings"]["exitcommands"]),"Edit Exit Commands").splitlines()
        elif wtd == 3:
            serverdata["settings"]["legacy"] = crss_custom_ad_menu(stdscr,["New Startups (fancy)","Old Startups (legacy)"],"Choose startup mode") == 1

def strict_word_search(haystack:str,needle:str) -> bool:
    #PHP
    words = haystack.split(" ")
    return needle in words

def load_server_logs(stdscr,serverdir) -> list[LogEntry]:
    cursesplus.displaymsg(stdscr,["Loading Logs, Please wait..."],False)
    logfile = serverdir + "/logs"
    if not os.path.isdir(logfile):
        cursesplus.messagebox.showerror(stdscr,["No logs could be found."])
        return []
    pushd(logfile)
    logs:list[str] = [l for l in os.listdir(logfile) if l.endswith(".gz") or l.endswith(".log")]
    #cursesplus.messagebox.showinfo(stdscr,[f"F {len(logs)}"])
    p = cursesplus.ProgressBar(stdscr,len(logs),cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Loading logs")
    allentries:list[LogEntry] = []
    for lf in logs:
        p.step(lf)
        if lf.endswith(".gz"):
            with open(lf,'rb') as f:
                allentries.extend(load_log_entries_from_raw_data(gzip.decompress(f.read()).decode(),lf))
        else:
            with open(lf) as f:
                allentries.extend(load_log_entries_from_raw_data(f.read(),lf))
    
    #allentries.reverse()
    
    #p.done()
    return allentries

def who_said_what(stdscr,serverdir):
    allentries = load_server_logs(stdscr,serverdir)
    allentries:list[LogEntry] = [a for a in allentries if is_log_entry_a_chat_line(a)]
    allentries.sort(key=lambda x: x.logdate,reverse=False)
    #allentries.reverse()
    while True:
        wtd = crss_custom_ad_menu(stdscr,["Back","Find by what was said","Find by player","View chat history of server","View Chat Bar Graph"])
        if wtd == 0:
            break
        elif wtd == 1:
            wws = crssinput(stdscr,"What message would you like to search for?")
            strict = cursesplus.messagebox.askyesno(stdscr,["Do you want to search strictly?","(Full words only)"])
            cassen = cursesplus.messagebox.askyesno(stdscr,["Do you want to be case sensitive?"])
            if not strict and cassen:
                ft = "\n".join([f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries if wws in a.data])
            elif not strict and not cassen:
                ft = "\n".join([f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries if wws.lower() in a.data.lower()])
            elif strict and cassen:
                ft = "\n".join([f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries if strict_word_search(a.data,wws)])
            elif strict and not cassen:
                ft = "\n".join([f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries if strict_word_search(a.data.lower(),wws.lower())])
            cursesplus.textview(stdscr,text=ft,message="Search Results")
        elif wtd == 2:
            wws = crssinput(stdscr,"What player would you like to search for?")
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                [
                                    f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries if wws in a.playername
                                ]),message="Search Results")
        elif wtd == 3:
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                [
                                    f"{a.logdate} {a.data.split(' ')[0][1:].replace(']','')} {a.playername}: {a.data.split(a.playername)[1][1:]}" for a in allentries
                                ]),message="Search Results")
        elif wtd == 4:
            sdata = {}
            for entry in allentries:
                if entry.playername in sdata:
                    sdata[entry.playername] += 1
                else:
                    sdata[entry.playername] = 1
            bargraph(stdscr,sdata,"Most Talkative Players","Messages")
    popd()

class FormattedIP:
    def __init__(self,a,c,p,d=datetime.datetime.now()):
        self.address:str = a
        self.country:str = c
        self.players:list[str] = p
        self.dateupdated = d
    def todict(self):
        return {
            "players" : self.players,
            "ip" : self.address,
            "country" : self.country,
            "date" : self.dateupdated.strftime("%Y-%m-%d %H:%M:%S")
        }
    def fromdict(id):
        return FormattedIP(id["ip"],id["country"],id["players"],datetime.datetime.strptime(id["date"],"%Y-%m-%d %H:%M:%S"))

def formattediplist_getindexbyip(search:str,haystack:list[FormattedIP]):
    """Look for an ip in a formatted ip list. Returns none if not found"""
    i = 0
    for needle in haystack:
        if needle.address == search:
            return i
        i += 1
    return None

def ip_lookup(stdscr,serverdir):
    ipdir = serverdir+"/.ipindex.json.gz"
    allentries = load_server_logs(stdscr,serverdir)
                
    IPS:dict[str,list] = {}
    formattedips:list[FormattedIP] = []
    if os.path.isfile(ipdir):
        try:
            with open(ipdir,'rb') as f:
                formattedips = [FormattedIP.fromdict(d) for d in json.loads(gzip.decompress(f.read()).decode())]
        except Exception as e:
            +cursesplus.messagebox.showerror(stdscr,["Error loading cache",str(e)])
            os.remove(ipdir)
            
    bigfatstring = "\n".join(l.data for l in allentries)
    
    for ip in re.findall(r"\s[A-Za-z]+\s[\[|\(]/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:",bigfatstring) + re.findall(r"\s[A-Za-z0-9]+\[/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:",bigfatstring):
        #Look for IP addresses
        n = ip.strip().replace("[","").replace("(","").replace(":","")
        name = n.split("/")[0].strip()
        ipaddress = n.split("/")[1].strip()
        if ipaddress in IPS:
            if not name in IPS[ipaddress]:
                IPS[ipaddress].append(name)
        else:
            IPS[ipaddress] = [name]
    p = cursesplus.ProgressBar(stdscr,len(IPS.keys())+10,cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.BOTTOM,message="Researching IPs")

    for uniqueip in list(IPS.keys()):
        p.step(uniqueip)
        if formattediplist_getindexbyip(uniqueip,formattedips) is not None:
            ind = formattediplist_getindexbyip(uniqueip,formattedips)
            if (datetime.datetime.now() - formattedips[ind].dateupdated).days >= 100 or (formattedips[ind].country == "Unknown Country" and not formattedips[ind].address.startswith("192.168")):
                #Do it again
                if uniqueip.startswith("192.168"):
                    formattedips[ind].country = "Local Network"
                    continue
                sleep(0.5)
                try:
                    r = requests.get(f"https://reallyfreegeoip.org/json/{uniqueip}").json()
                    country = r["country_name"]
                    if country.strip() == "":
                        raise Exception()#On local network
                except:
                    
                    country = "Unknown Country"
                #formattedips.append(FormattedIP(uniqueip,country,IPS[uniqueip]))
                formattedips[ind].dateupdated = datetime.datetime.now()
                if country != "Unknown Country":
                    formattedips[ind].country = country
            for pname in IPS[uniqueip]:
                if not pname in formattedips[ind].players:
                    formattedips[ind].players.append(pname)#If the IP has been looked at already
        else:
            if uniqueip.startswith("192.168"):
                    formattedips.append(FormattedIP(uniqueip,"Local Network",IPS[uniqueip]))
            time.sleep(0.5)#Am I getting blocked??
            try:
                r = requests.get(f"https://reallyfreegeoip.org/json/{uniqueip}").json()
                
                country = r["country_name"]
                if country.strip() == "":
                    raise Exception()#On local network
            except:
                
                country = "Unknown Country"
            formattedips.append(FormattedIP(uniqueip,country,IPS[uniqueip]))
    with open(ipdir,'wb+') as f:
        f.write(gzip.compress(json.dumps([f.todict() for f in formattedips]).encode()))
    p.done()
    while True:
        wtd = crss_custom_ad_menu(stdscr,["BACK","View All","Lookup by Player","Lookup by IP","Lookup by Country","Show bar graph","Reset Cache"])
        if wtd == 0:
            break
        elif wtd == 1:
            sorting = crss_custom_ad_menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message="All IPs")
        elif wtd == 2:
            sorting = crss_custom_ad_menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = crssinput(stdscr,"What player do you want to search for?")
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                if psearch in fi.players:
                    final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message=f"Searching for {psearch}")
    
        elif wtd == 3:
            sorting = crss_custom_ad_menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = crssinput(stdscr,"What IP do you want to look for?")
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                if psearch in fi.address:
                    final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message=f"Searching for {psearch}")
            
        elif wtd == 4:
            sorting = crss_custom_ad_menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = crssinput(stdscr,"What country do you want to look for?")
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                if psearch.lower() in fi.country.lower():
                    final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message=f"Searching for {psearch}")
            
        elif wtd == 5:
            fdata = {}
            for fip in formattedips:
                if fip.country in fdata:
                    fdata[fip.country] += 1
                else:
                    fdata[fip.country] = 1
            bargraph(stdscr,fdata,"Player Country Statistics","unique IPs")
        elif wtd == 6:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you wish to delete the cache?","This will result in slow loading times."],default=cursesplus.messagebox.MessageBoxStates.NO):
                os.remove(ipdir)
                return

def friendly_positions(ins:int) -> str:
    conv = str(ins)
    if conv.endswith("1"):
        conv += "st"
    elif conv.endswith("2"):
        conv += "nd"
    elif conv.endswith("3"):
        conv += "rd"
    else:
        conv += "th"
    return conv

def bargraph(stdscr,data:dict[str,int],message:str,unit="",sort=True,adjusty=False):
    if len(data) == 0:
        cursesplus.messagebox.showerror(stdscr,["No data"])
        return
    xoffset = 0
    footerl = 1
    selected = 0
    if sort:
        data = dict(sorted(data.items(), key=lambda x: x[1], reverse=True))
    while True:
        stdscr.clear()
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(0,0,message+" | Press Q to quit",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        maxval = max(list(data.values()))
        if adjusty:
            minval = min(list(data.values()))
        else:
            minval = 0
        if maxval-minval == 0:
            minval = maxval-1
        my,mx = stdscr.getmaxyx()
        my -= 1 #Strange bug
        graphspace = my - 1 - footerl #Remove head and foot
        ti = 4
        #Add numbers]
        for i in range(graphspace):
            stdscr.addstr(my-(i+footerl),0,str(round(i/graphspace*(maxval-minval))+minval))
        for pset in list(data.items())[xoffset:xoffset+mx-5]:
            ti += 1
            pval = pset[1]
            trueoffset = round(((pval-minval)/(maxval-minval))*graphspace)+1
            
            for i in range(trueoffset):             
                if ti-5+xoffset == selected:
                    try:
                        stdscr.addstr(my-(i+footerl),ti,"█",cursesplus.set_colour(cursesplus.CYAN,cursesplus.CYAN))
                    except:
                        pass
                else:
                    try:
                        stdscr.addstr(my-(i+footerl),ti,"█")
                    except:
                        pass
        dnsel = list(data.keys())[selected]
        stdscr.addstr(my,0,f"{dnsel} ({list(data.values())[selected]} {unit}) - {friendly_positions(sorted(list(data.values()),reverse=True).index(list(data.values())[selected])+1)} place")
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_LEFT:
            if selected > 0:
                selected -= 1
        elif ch == curses.KEY_RIGHT:
            if selected < len(data)-1:
                selected += 1
        elif ch == curses.KEY_SRIGHT:
            xoffset += 1
        elif ch == curses.KEY_SLEFT:
            if xoffset > 0:
                xoffset -= 1
        elif ch == 113:
            return
            
def get_minute_id_from_datetime(d:datetime.datetime) -> int:
    return int(d.timestamp()/60//1)

def get_datetime_from_minute_id(t:int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(t*60)

class JLLogFrame:
    data:str
    ext:datetime.datetime
    def __init__(self,lowerdata:LogEntry):
        rtime = lowerdata.data.split(" ")[0].strip()
        rdate = lowerdata.logdate
        
        self.ext = datetime.datetime.strptime(f"{rdate.year}-{rdate.month}-{rdate.day} {rtime[1:-1]}","%Y-%m-%d %H:%M:%S")
        self.data = lowerdata.data

class ServerMinuteFrame:
    minuteid:int
    onlineplayers:list[str] = []
    
    def __init__(self,minuteid):
        self.minuteid = minuteid
    def wasonline(self,name) -> bool:
        return name in self.onlineplayers
    def todatetime(self) -> datetime:
        return datetime.datetime.fromtimestamp(self.minuteid*60)
    def howmanyonline(self) -> int:
        return len(self.onlineplayers)

def serverminuteframe_uf(smf:ServerMinuteFrame):
    return f"{smf.minuteid} ({smf.todatetime()}) - {smf.onlineplayers}"

def strip_datetime(d:datetime.datetime) -> str:
    return d.strftime("%Y-%m-%d %H:%M:%S")

def count_unique_values(l:list) -> int:
    return len(set(l))

def remove_duplicates_from_list(l:list) -> list:
    return list(set(l))

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

def comingsoon(stdscr):
    cursesplus.messagebox.showerror(stdscr,["Sorry, this feature is coming soon"])

def split_list_into_chunks(l, n):
    for i in range(0, len(l), n): 
        yield l[i:i + n]

class AnalyticsExplorerZoomLevels(enum.Enum):
    MINUTE = 0
    HOUR = 60
    DAY = 1440
    MONTH = 43200
    
class AnalyticsExplorerDataTypes(enum.Enum):
    TOTALPLAYERMINUTES = 0
    MAXPLAYERCOUNT = 1
    AVERAGEPLAYERCOUNT = 2

def sort_dict_by_key(d:dict) -> dict:
    return dict(sorted(list(d.items())))

def server_analytics_explorer(stdscr,data:dict[int,ServerMinuteFrame]):
    
    #This function allows users to explore their analytics
    offset = 0
    datasize = len(data)-1
    currentzoomlevel = AnalyticsExplorerZoomLevels.MINUTE#Also passively the list chunk size
    currentdatatype = AnalyticsExplorerDataTypes.MAXPLAYERCOUNT
    ldata = list(data.values())#List representation of data to prevent performance issues?
    maxval = max([len(p.onlineplayers) for p in list(data.values())])
    while True:
        my,mx = stdscr.getmaxyx()
        xspace = mx-1
        yspace = my-4#Top Bottom, and weird bug
        stdscr.erase()
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.BLUE))
        stdscr.addstr(0,0,"Analytics Explorer - Press Q to quit and H for help",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        
        if currentdatatype == AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            maxval = maxval*currentzoomlevel
        
        ti = 0
        for i in range(offset-xspace//2,offset+xspace//2):
            if i < 0 or i > datasize:
                #Write red bar
                #print("w")
                for dy in range(1,yspace+1):
                    stdscr.addstr(dy,ti,"█",cursesplus.set_colour(cursesplus.RED,cursesplus.RED))
            else:
                seldata = ldata[i]
                scale = int(seldata.howmanyonline()/maxval*yspace)
                
                if i == offset:
                    for p in range(1,yspace+2):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.GREEN,cursesplus.GREEN))#Central marker
                    for p in range(yspace+1,yspace+1-scale,-1):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.CYAN,cursesplus.CYAN))
                else:
                    for p in range(yspace+1,yspace+1-scale,-1):
                        stdscr.addstr(p,ti,"█",cursesplus.set_colour(cursesplus.WHITE,cursesplus.WHITE))
            
            ti += 1
            
        seldata = ldata[offset]
        stdscr.addstr(my-2,0,f"{strip_datetime(get_datetime_from_minute_id(seldata.minuteid))} || {seldata.howmanyonline()} players online - {seldata.onlineplayers}")
        
        ch = curses.keyname(stdscr.getch()).decode()
        if ch == "q":
            break
        elif ch == "h":
            cursesplus.displaymsg(stdscr,["KEYBINDS","q - Quit","h - Help","<- -> Scroll","END - Go to end","HOME - Go to beginning","j - Jump to time","SHIFT <-- --> - Jump hour","Ctrl <-- --> - Jump day"])
        elif ch == "KEY_LEFT":
            if offset > 0:
                offset -= 1
        elif ch == "KEY_RIGHT":
            offset += 1
        elif ch == "KEY_SLEFT":
            if offset > 60:
                offset -= 60
            else:
                offset = 0
        elif ch == "KEY_SRIGHT":#Jump around by an hour
            offset += 60 
        elif ch == "kRIT5":
            offset += 1440
        elif ch == "kLFT5":
            if offset > 1440:
                offset -= 1440
            else:
                offset = 0
        elif ch == "KEY_END":
            offset = datasize - 1
        elif ch == "KEY_HOME":
            offset = 0
        elif ch == "j":
            ndate = cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a date and time to jump to",True,False,get_datetime_from_minute_id(ldata[offset].minuteid))
            nmid = get_minute_id_from_datetime(ndate)
            if not nmid in data:
                cursesplus.messagebox.showerror(stdscr,["Records do not exist for the selected date."])
            else:
                offset = list(data.keys()).index(nmid)
        if offset > datasize:
            offset = datasize - 1
            
def average_list(l:list[int|float]) -> float:
    return sum(l)/len(l)
            
def recursive_average(l:list[list[int|float]]) -> list[float]:
    return [average_list(z) for z in l]

def sanalytics(stdscr,serverdir):
    
    allentries:list[LogEntry] = load_server_logs(stdscr,serverdir)
    earliestentrydt:datetime.date = allentries[0].logdate
    cursesplus.displaymsg(stdscr,["Parsing Data","Please Wait"],wait_for_keypress=False)
    eventslist:list[JLLogFrame] = []
    joins:dict[int,list[str]] = {}
    leavs:dict[int,list[str]] = {}
    #Both of these lists will be [minuteid] -> [list of players].
    if len(allentries) == 0:
        cursesplus.messagebox.showwarning(stdscr,["No logs, so no info!"])
        return
    
    for entry in allentries:
        
        lz = re.findall(r' \S* joined the game| \S* left the game',entry.data)
        
        #print(entry.data)
        if len(lz) > 0:
            if entry.logdate < earliestentrydt:
                earliestentrydt = entry.logdate
            #print(lz)
            eventslist.append(JLLogFrame(entry))
            rs:str = lz[0].strip()
            plname = rs.split(" ")[0]
            action = rs.split(" ")[1]
            
            mid = get_minute_id_from_datetime(eventslist[-1].ext)
            if "joined" in action:
                if not mid in joins:
                    joins[mid] = [plname]
                else:
                    joins[mid].append(plname)
            if "left" in action:
                if not mid in leavs:
                    leavs[mid] = [plname]
                else:
                    leavs[mid].append(plname)
    cursesplus.displaymsg(stdscr,["Sorting Data","Please Wait"],wait_for_keypress=False)
    joins = sort_dict_by_key(joins)
    leavs = sort_dict_by_key(leavs)
    firstentrymid = get_minute_id_from_datetime(datetime.datetime.combine(earliestentrydt,datetime.time(0,0,0)))
    cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],wait_for_keypress=False)
    currentmid = get_minute_id_from_datetime(datetime.datetime.now())
    #Take leavs and joins and assemble minuteframe
    final:dict[int,ServerMinuteFrame] = {
        firstentrymid-1:ServerMinuteFrame(firstentrymid-1)#Keep template incase no action in first minute
    }
    lastrealjoin:dict[str,int] = {}#keep track of the last registered join of a player. If they stay on for longer than 6 hours without a real join, they get removed.
    for m in range(firstentrymid,currentmid+1):
        #M is minute id
        if m not in joins and not m in leavs:
            prev = copy.deepcopy(final[m-1])
            prev.minuteid = m
            final[m] = prev
        else:
            phj = []
            phl = []
            if m in joins:
                phj = joins[m]
            if m in leavs:
                phl = leavs[m]
            
            frame = copy.deepcopy(final[m-1])#Deep copy!?!?!? THEN WHY WERENT YOU COPYING !?!??!
            #frame = ServerMinuteFrame(0)
            frame.minuteid = m 
            frame.onlineplayers = frame.onlineplayers.copy()
            for player in phj:
                lastrealjoin[player] = m
                if player in phl:
                    phl.remove(player)
                    continue#This should solve the quick joinleave problem
                frame.onlineplayers.append(player)
            for player in phl:
                try:
                    frame.onlineplayers = remove_values_from_list(frame.onlineplayers,player)
                except:
                    pass
            for op in frame.onlineplayers:
                try:
                    if (m - lastrealjoin[op]) > 360:
                        #print("REM")
                        frame.onlineplayers = remove_values_from_list(frame.onlineplayers,op)
                except:
                    pass#If player inspects analytics starting from when players were online, this could crash
            final[m] = frame
            
    cursesplus.displaymsg(stdscr,["Cleaning Data","Please Wait"],wait_for_keypress=False)
    
    for k in final:
        final[k].onlineplayers = remove_duplicates_from_list(final[k].onlineplayers)
       
    #with open("/tmp/cwf.txt","w+") as f:
    #    f.write("\n".join([serverminuteframe_uf(x) for x in list(final.values())]))
    cursesplus.displaymsg(stdscr,["Done"],False)
    
    minminid = firstentrymid      
    maxminid = get_minute_id_from_datetime(datetime.datetime.now())
    while True:
        cursesplus.displaymsg(stdscr,["Applying filters..."],False)
        workingdata:dict[str,ServerMinuteFrame] = {}
        for k in list(final.keys()):
            if k >= minminid and k <= maxminid:
                workingdata[k] = final[k]
        wtd = crss_custom_ad_menu(stdscr,["Back","Analytics Explorer","Playtime","Total Player Count","Time of Day",f"FILTER MIN: {strip_datetime(get_datetime_from_minute_id(minminid))}",f"FILTER MAX: {strip_datetime(get_datetime_from_minute_id(maxminid))}","RESET FILTERS","Export to CSV","Server Popularity Over Time"],"Server Analytics Manager")
        if wtd == 0:
            return
        elif  wtd == 1:
            server_analytics_explorer(stdscr,workingdata)
        elif wtd == 2:
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            playminutes:dict[str,int] = {}
            for entry in list(workingdata.values()):
                for p in entry.onlineplayers:
                    if not p in playminutes:
                        playminutes[p] = 0
                    playminutes[p] += 1
            while True:
                swtd = crss_custom_ad_menu(stdscr,["Back","VIEW GRAPH"]+list(playminutes.keys()),"Choose a player to view their playtime information")
                if swtd == 0:
                    break
                elif swtd == 1:
                    bargraph(stdscr,playminutes,"Player Minute Information","minutes")
                else:
                    plstudy = list(playminutes.keys())[swtd-2]
                    zwtd = crss_custom_ad_menu(stdscr,["Total Playtime Minutes","Playtime History","Time of Day analyzers"])
                    match zwtd:
                        case 0:
                            cursesplus.messagebox.showinfo(stdscr,["Playtime Minutes: "+str(playminutes[list(playminutes.keys())[swtd-2]])])
                        case 1:
                            cursesplus.displaymsg(stdscr,["Analyzing Data","Please wait"],False)
                            dzl = {}#yearmonth:data
                            for entry in list(workingdata.values()):
                                if plstudy in entry.onlineplayers:
                                    nd = get_datetime_from_minute_id(entry.minuteid)
                                    nk = f"{nd.year}-{str(nd.month).zfill(2)}"
                                    if not nk in dzl:
                                        dzl[nk] = 1
                                    else:
                                        dzl[nk] += 1
                                        
                            bargraph(stdscr,dzl,f"How has {plstudy} played over the months?","minutes spend",False,True)
                        case 2:
                            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
                            dataset:list[int] = [0 for _ in range(24)]#0:00 to 23:00

                            for entry in list(workingdata.values()):
                                hr = get_datetime_from_minute_id(entry.minuteid).hour
                                if plstudy in entry.onlineplayers:
                                    dataset[hr] += 1
                                
                            dataset_ps = {}
                            i = 0
                            for ex in dataset:
                                dataset_ps[f"{i}:00 - {i}:59"] = ex
                                i += 1
                                
                            bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
                            
        elif wtd == 3:
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            allplayers = []
            for entry in list(workingdata.values()):
                allplayers += entry.onlineplayers
            cursesplus.messagebox.showinfo(stdscr,["During the time selected,",str(count_unique_values(allplayers)),"unique players have joined this server"])
            cursesplus.messagebox.showinfo(stdscr,["The maximum number of players at once was ",str(max([s.howmanyonline() for s in list(workingdata.values())]))])
        elif wtd == 4:
            cursesplus.messagebox.showinfo(stdscr,["This graph is shown in player-minutes","It is one for each minute a player spends"])
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            dataset:list[int] = [0 for _ in range(24)]#0:00 to 23:00

            for entry in list(workingdata.values()):
                hr = get_datetime_from_minute_id(entry.minuteid).hour
                dataset[hr] += entry.howmanyonline()
                
            dataset_ps = {}
            i = 0
            for ex in dataset:
                dataset_ps[f"{i}:00 - {i}:59"] = ex
                i += 1
                
            bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
            
        elif wtd == 5:
            minminid = get_minute_id_from_datetime(cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a new minimum filter time",True,False,get_datetime_from_minute_id(minminid)))
        elif wtd == 6:
            maxminid = get_minute_id_from_datetime(cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a new minimum filter time",True,False,get_datetime_from_minute_id(maxminid)))
        elif wtd == 7:
            minminid = firstentrymid      
            maxminid = get_minute_id_from_datetime(datetime.datetime.now())
        elif wtd == 8:
            od = cursesplus.filedialog.openfolderdialog(stdscr,"Select output folder")
            if od is not None:
                cursesplus.displaymsg(stdscr,["Please wait..."],False)
                finalstr = "Minute ID,Local Time,Player Count,Online Players\n"
                for entry in list(workingdata.values()):
                    finalstr += f"{entry.minuteid},{get_datetime_from_minute_id(entry.minuteid)},{entry.howmanyonline()},{', '.join(entry.onlineplayers)}\n"
                with open(od+"/serverplayers.csv","w+") as f:
                    f.write(finalstr)
                cursesplus.messagebox.showinfo(stdscr,["Exported successfully"])
        elif wtd == 9:
            tan = crss_custom_ad_menu(stdscr,["Total Player-minutes","Unique Players","Average Online Players","Average Online Players (active time)"],"Select Data to examine",footer="(active time) shows only data that is not zero")
            gd:dict[str,object] = {}
            unit = "player-minutes"
            cursesplus.displaymsg(stdscr,["Analyzing Data","Please Wait"],False)
            match tan:
                case 0:
                    for entry in list(workingdata.values()):
                        gkey = f"{get_datetime_from_minute_id(entry.minuteid).year}-{get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in gd:
                            gd[gkey] += entry.howmanyonline()
                        else:
                            gd[gkey] = entry.howmanyonline()
                case 1:
                    for entry in list(workingdata.values()):
                        gkey = f"{get_datetime_from_minute_id(entry.minuteid).year}-{get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in gd:
                            for pl in entry.onlineplayers:
                                if pl not in gd[gkey]:
                                    gd[gkey].append(pl)
                        else:
                            gd[gkey] = entry.onlineplayers
                    for dkey in gd:
                        gd[dkey] = len(gd[dkey])#Convert lists of players into lens
                    unit = "unique players"
                case 2 | 3:
                    for entry in list(workingdata.values()):
                        gkey = f"{get_datetime_from_minute_id(entry.minuteid).year}-{get_datetime_from_minute_id(entry.minuteid).month.__str__().zfill(2)}"
                        if gkey in gd:
                            if entry.howmanyonline() > 0 or tan == 2:
                                gd[gkey].append(entry.howmanyonline())
                            
                        else:
                            gd[gkey] = [entry.howmanyonline()]
                    for dkey in gd:
                        gd[dkey] = average_list(gd[dkey])
                    unit = "online players"
                
            bargraph(stdscr,gd,"Popularity Results",unit,False,False)

def manage_server(stdscr,_sname: str,chosenserver: int):
    global APPDATA
    global COLOURS_ACTIVE
    
    SERVER_DIR = _sname
    _ODIR = os.getcwd()
    
    if APPDATA["settings"]["transitions"]["value"]:
        cursesplus.transitions.vertical_bars(stdscr)
    if APPDATA["servers"][chosenserver-1]["software"] == 0:
        bedrock_manage_server(stdscr,_sname,chosenserver)
        return
    #Manager server
    while True:
        os.chdir(APPDATA["servers"][chosenserver-1]["dir"])#Fix bug where running a sub-option that changes dir would screw with future operations
        x__ops = ["RETURN TO MAIN MENU","Start Server","Change MOTD","Advanced configuration >>","Delete server","Manage worlds","Update Server software","Manage Content >>"]
        x__ops += ["View logs","Export server","View server info","Administration and Backups >>","Manage server icon"]
        x__ops += ["Change server software","More Utilities >>","FILE MANAGER"]
        if _sname in SERVER_INITS and not APPDATA["servers"][chosenserver-1]["settings"]["legacy"]:
            x__ops[1] = "Server is running >>"
        #w = crss_custom_ad_menu(stdscr,x__ops)
        w = crss_custom_ad_menu(stdscr,x__ops,"Please choose a server management option")
        if w == 0:
            stdscr.erase()
            os.chdir(_ODIR)
            if APPDATA["settings"]["transitions"]["value"]:
                cursesplus.transitions.random_blocks(stdscr)
            break
        
        elif w == 1:
            if sys.version_info[1] < 11:
                cursesplus.messagebox.showerror(stdscr,["Unfortunately, the new startups can only be used with Python 3.11 or newer.",f"You are running {sys.version}.","Your server will be started in legacy mode (pre 1.43)"])
                APPDATA["servers"][chosenserver-1]["settings"]["legacy"] = True
            os.system(";".join(APPDATA["servers"][chosenserver-1]["settings"]["launchcommands"]))
            if APPDATA["servers"][chosenserver-1]["settings"]["legacy"]:
                os.chdir(APPDATA["servers"][chosenserver-1]["dir"])           
                stdscr.clear()
                stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}\n\r")
                stdscr.refresh()
                if not WINDOWS:
                    curses.curs_set(1)
                    curses.reset_shell_mode()
                    lretr = os.system(APPDATA["servers"][chosenserver-1]["script"])
                    #child = pexpect.spawn(APPDATA["servers"][chosenserver-1]["script"])
                    #child.expect("Finished")
                    curses.reset_prog_mode()
                    curses.curs_set(0)
                else:
                    curses.curs_set(1)
                    curses.reset_shell_mode()
                    #COLOURS_ACTIVE = False
                    lretr = os.system("cmd /c ("+APPDATA["servers"][chosenserver-1]["script"]+")")
                    curses.reset_prog_mode()
                    curses.curs_set(0)
                    #restart_colour()
                os.system(";".join(APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
                if lretr != 0 and lretr != 127 and lretr != 128 and lretr != 130:
                    displog = cursesplus.messagebox.askyesno(stdscr,["Oh No! Your server crashed","Would you like to view the logs?"])
                    if displog:
                        view_server_logs(stdscr,SERVER_DIR)
                stdscr.clear()
                stdscr.refresh()
            else:
                if not _sname in SERVER_INITS:
                    truecommand = APPDATA["servers"][chosenserver-1]["script"]
                    if WINDOWS:
                        truecommand = "cmd /c ("+APPDATA["servers"][chosenserver-1]["script"]+")"
                    SERVER_INITS[_sname] = ServerRunWrapper(truecommand)
                    SERVER_INITS[_sname].launch()
                    cursesplus.messagebox.showinfo(stdscr,["The server has been started.","It will be ready for use in a few minutes"])
                latestlogfile = SERVER_DIR+"/logs/latest.log"
                #pos = 0
                obuffer = ["Getting logs. Please wait...","The log may take some time to appear.","Don't worry, your server is still running."]
                ooffset = 0
                oxoffset = 0
                tick = 0
                #lfsize = os.path.getsize(latestlogfile)
                stdscr.nodelay(1)
                
                redraw = True
                while True:
                    
                    tick += 1
                    if tick % 30 == 0:
                        tick = 0
                        #SERVER_INITS[_sname].datastream.seek(0,0)
                        #obuffer = SERVER_INITS[_sname].datastream.readlines()
                        if os.path.isfile(latestlogfile):
                            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(latestlogfile))
                            if mtime < SERVER_INITS[_sname].runtime:
                                pass
                            else:
                            
                                with open(latestlogfile) as f:
                                    obc = f.readlines()
                                    if obc != obuffer:
                                        obuffer = obc
                                        ooffset = len(obuffer)-my+headeroverhead
                                        if ooffset < 0:
                                            ooffset = 0
                                        redraw = True
                        
                    #Visual part
                    mx,my = os.get_terminal_size()
                    mx -= 1
                    my -= 1
                    headeroverhead = 5
                    if redraw:
                        stdscr.clear()
                        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
                        stdscr.addstr(0,0,f"Live options for {_sname}",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
                        stdscr.addstr(1,0,"Press B to go back to the options")
                        stdscr.addstr(2,0,"Press C to run a command | Press K to kill the server")
                        stdscr.addstr(3,0,"Press S to stop the server")
                        stdscr.addstr(4,0,cursesplus.constants.THIN_HORIZ_LINE*mx)
                        oi = 5
                        for line in obuffer[ooffset:]:
                            try:
                                stdscr.addstr(oi,0,line[oxoffset:oxoffset+mx-1])
                            except:
                                break
                            oi += 1
                        
                    svrstat = SERVER_INITS[_sname]
                    if not svrstat.isprocessrunning():
                        
                        stdscr.nodelay(0)
                        os.system(";".join(APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
                        if svrstat.hascrashed():
                            displog = cursesplus.messagebox.askyesno(stdscr,["Oh No! Your server crashed","Would you like to view the logs?"])
                            if displog:
                                view_server_logs(stdscr,SERVER_DIR)
                        else:
                            cursesplus.messagebox.showinfo(stdscr,["The server has been stopped safely."])
                        del SERVER_INITS[_sname]
                        break
                    #stdscr.addstr(0,0,f"Y: {ooffset} X: {oxoffset}")
                    if redraw:    
                        stdscr.refresh()
                    redraw = False
                    ch = stdscr.getch()
                    if ch == curses.KEY_UP and ooffset > 0:
                        ooffset -= 1
                        redraw = True
                    elif ch == curses.KEY_DOWN:
                        ooffset += 1
                        redraw = True
                    elif ch == curses.KEY_LEFT and oxoffset > 0:
                        oxoffset -= 1
                        redraw = True
                    elif ch == curses.KEY_RIGHT:
                        oxoffset += 1
                        redraw = True
                        
                    elif ch == 98:
                        break
                    elif ch == 99:
                        stdscr.nodelay(0)
                        svrstat.send(crssinput(stdscr,"Enter a command to run"))
                        stdscr.nodelay(1)
                    elif ch == 115:
                        svrstat.send("stop")
                        pass
                    elif ch == 107:
                        stdscr.nodelay(0)
                        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to kill the server?","This can corrupt data.","Only do this if you believe the server to be frozen"]):
                            svrstat.fullhalt()
                        stdscr.nodelay(1)
                        
                    sleep(1/30)
                    
                stdscr.nodelay(0)
        elif w == 2:
            if not os.path.isfile("server.properties"):
                cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
            else:
                with open("server.properties") as f:
                    config = PropertiesParse.load(f.read())
                if not "motd" in config:
                    cursesplus.messagebox.showwarning(stdscr,["For some reason, an old motd could not be found.","You will be prompted to choose one anyway."])
                    config["motd"] = ""
                else:
                    cursesplus.displaymsg(stdscr,["Current Message Is",config["motd"]])
                curses.curs_set(1)
                newmotd = crssinput(stdscr,"Please input a new MOTD",2,59,prefiltext=config["motd"].replace("\\n","\n"))
                curses.curs_set(0)
                config["motd"] = newmotd.replace("\n","\\n")
                with open("server.properties","w+") as f:
                    f.write(PropertiesParse.dump(config))
        elif w == 3:
            
            config_server(stdscr,chosenserver)
        elif w == 4:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER"],default=cursesplus.messagebox.MessageBoxStates.NO):
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER","THIS IS YOUR LAST CHANCE"],default=cursesplus.messagebox.MessageBoxStates.NO):
                    os.chdir(SERVERSDIR)
                    shutil.rmtree(SERVER_DIR)
                    del APPDATA["servers"][chosenserver-1]
                    cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                    stdscr.clear()
                    break
            stdscr.erase()
        elif w == 5:
            if not os.path.isfile("server.properties"):
                cursesplus.messagebox.showerror(stdscr,["Please start your server to generate","server.properties"])
                continue
            with open("server.properties") as f:

                dpp = PropertiesParse.load(f.read())

            while True:
                po = find_world_folders(SERVER_DIR)
                n = crss_custom_ad_menu(stdscr,["BACK","CREATE NEW WORLD"]+po)
                if n == 0:
                    with open("server.properties","w+") as f:
                        f.write(PropertiesParse.dump(dpp))   
                    break
                elif n == 1:
                    dppx = setup_new_world(stdscr,dpp,SERVER_DIR,False)
                    if dppx is not None:
                        dpp = dppx#Fix bug
                else:
                    manage_a_world(stdscr,SERVER_DIR,po[n-2])
            
        elif w == 6:
            if not APPDATA["servers"][chosenserver-1]["moddable"]:
                update_vanilla_software(stdscr,os.getcwd(),chosenserver)
            elif APPDATA["servers"][chosenserver-1]["software"] == 3:
                update_paper_software(stdscr,os.getcwd(),chosenserver)
            elif APPDATA["servers"][chosenserver-1]["software"] == 2:
                update_spigot_software(stdscr,os.getcwd(),chosenserver)
            elif APPDATA["servers"][chosenserver-1]["software"] == 4:
                update_purpur_software(stdscr,os.getcwd(),chosenserver)
            else:
                cursesplus.messagebox.showwarning(stdscr,["This type of server can't be upgraded."])
        elif w == 7:
            while True:
                mmwtd = crss_custom_ad_menu(stdscr,["Back","Plugins and Mods","Datapacks","Resource Pack"],"CONTENT MANAGER | What would you like to edit?")
                if mmwtd == 0:
                    break
                elif mmwtd == 1:
                    if APPDATA["servers"][chosenserver-1]["software"] == 1:
                        cursesplus.messagebox.showerror(stdscr,["Vanilla servers cannot have plugins."])
                        continue
                    svr_mod_mgr(stdscr,SERVER_DIR,APPDATA["servers"][chosenserver-1]["version"],APPDATA["servers"][chosenserver-1]["software"])
                elif mmwtd == 2:
                    world = crss_custom_ad_menu(stdscr,find_world_folders(SERVER_DIR),"Choose a world to apply datapacks to")
                    manage_datapacks(stdscr,find_world_folders(SERVER_DIR)[world]+"/datapacks")
                elif mmwtd == 3:
                    if not os.path.isfile("server.properties"):
                        cursesplus.messagebox.showerror(stdscr,["Please start your server to generate","server.properties"])
                        continue
                    with open("server.properties") as f:

                        dpp = PropertiesParse.load(f.read())
                    
                    dpp = resource_pack_setup(stdscr,dpp)
                    with open("server.properties","w+") as f:
                        f.write(PropertiesParse.dump(dpp))
        elif w == 8:
            view_server_logs(stdscr,SERVER_DIR)
        elif w == 9:
            package_server(stdscr,SERVER_DIR,chosenserver-1)
        elif w == 10:
            stdscr.erase()
            stdscr.refresh()
            stdscr.addstr(0,0,"Name ")
            stdscr.addstr(1,0,"MC Version")
            stdscr.addstr(2,0,"Directory")
            stdscr.addstr(3,0,"Allocated Memory")
            stdscr.addstr(4,0,"Server Size")
            stdscr.addstr(5,0,"Moddable server?")
            stdscr.refresh()
            sdat = APPDATA["servers"][chosenserver-1]
            stdscr.addstr(0,20,sdat["name"])
            stdscr.addstr(1,20,sdat["version"])
            stdscr.addstr(2,20,sdat["dir"][0:os.get_terminal_size()[0]])
            stdscr.addstr(3,20,sdat["memory"])
            stdscr.refresh()
            stdscr.addstr(4,20,parse_size(get_tree_size(sdat["dir"])))
            stdscr.refresh()
            stdscr.addstr(5,20,["Yes" if sdat["moddable"] else "No"][0])
            stdscr.addstr(6,0,"Press any key to continue",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
            stdscr.refresh()
            stdscr.getch()
        elif w == 11:
            while True:
                abkwtd = crss_custom_ad_menu(stdscr,["Back","Whitelist","Backups","Admins","Banned Players"],"ADMIN MENU | What do you want to edit?")
                if abkwtd == 0:
                    break
                elif abkwtd == 1:
                    manage_whitelist(stdscr,SERVER_DIR+"/whitelist.json")
                elif abkwtd == 2:
                    server_backups(stdscr,SERVER_DIR,APPDATA["servers"][chosenserver-1])
                elif abkwtd == 3:
                    manage_ops(stdscr,SERVER_DIR)
                elif abkwtd == 4:
                    manage_bans(stdscr,SERVER_DIR)
        # elif w == 11:
        #     manage_whitelist(stdscr,SERVER_DIR+"/whitelist.json")
        # elif w == 12:
        #     server_backups(stdscr,SERVER_DIR,APPDATA["servers"][chosenserver-1])
        # elif w == 13:
        #     manage_ops(stdscr,SERVER_DIR)
        # elif w == 14:
        #     manage_bans(stdscr,SERVER_DIR)
        elif w == 12:
            manage_server_icon(stdscr)
        elif w == 13:
            APPDATA["servers"][chosenserver-1] = change_software(stdscr,SERVER_DIR,APPDATA["servers"][chosenserver-1])
            updateappdata()
        elif w == 14:
            w2 = crss_custom_ad_menu(stdscr,["Back","Chat Utilities","IP Lookups","Server Analytics"],"Additional Utilities")
            if w2 == 1:
                who_said_what(stdscr,SERVER_DIR)
            elif w2 == 2:
                ip_lookup(stdscr,SERVER_DIR)
            elif w2 == 3:
                #cursesplus.messagebox.showerror(stdscr,["This feature is coming soon.","Sorry"])
                #continue
                sanalytics(stdscr,SERVER_DIR)
        elif w == 15:
            file_manager(stdscr,SERVER_DIR,f"Files of {APPDATA['servers'][chosenserver-1]['name']}")
_SCREEN = None

def handle_file_editing(stdscr,path:str):
    
    if (is_file_binary(path)):
        cursesplus.messagebox.showerror(stdscr,["This type of file can't be edited."])
    elif is_file_dicteditable(path) or path.endswith(".properties"):
        with open(path) as f:
            data = f.read()
        try:
            ndict = json.loads(data)
        except:
            try:
                ndict = yaml.load(data,yaml.FullLoader)
            except:
                pass
        try:
            ndict = dictedit(stdscr,ndict,os.path.split(path)[1])
            with open(path,"w+") as f:
                if path.endswith("json"):
                    json.dump(ndict,f)
                else:
                    yaml.dump(ndict,f,default_flow_style=False)
        except:
            if WINDOWS:
                os.system(f"notepad \"{path}\"")
            else:
                curses.reset_shell_mode()
                os.system(APPDATA["settings"]["editor"]["value"].replace("%s",path))
                curses.reset_prog_mode()
    else:
        if WINDOWS:
            os.system(f"notepad \"{path}\"")
        else:
            curses.reset_shell_mode()
            os.system(APPDATA["settings"]["editor"]["value"].replace("%s",path))
            curses.reset_prog_mode()

def is_file_binary(path:str):
    return path.endswith("exe") or path.endswith("jar")
    
def is_file_dicteditable(path:str):
    return path.endswith("json") or path.endswith("yml") or path.endswith("yaml")

def file_manager(stdscr,directory:str,header:str):
    #Manage file
    
    basedir = directory
    axt = "/"
    adir = basedir+axt
    yoffset = 0
    xoffset = 0
    selected = 0
    os.chdir(directory)
    cursesplus.displaymsg(stdscr,["Please wait while","files are indexed"],False)
    #Load allfile into activefile
    
    while True:
        activefile:list[cursesplus.filedialog.Fileobj] = []
        filssx = os.listdir(adir)
        for smx in filssx:
            activefile.append(cursesplus.filedialog.Fileobj(adir+"/"+smx))
        activefile.sort(key=lambda x: x.path)
        stdscr.clear()
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(0,0,header,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        
        mx,my = os.get_terminal_size()
        my -= 1
        mx -= 1

        sidebarboundary = mx-20
        stdscr.vline(1, sidebarboundary, curses.ACS_VLINE, my-1)
        cursesplus.utils.fill_line(stdscr,my,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(0,mx-17,"Keybinds: ",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(my,0,f"{len(activefile)} files ",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        cursesplus.utils.fill_line(stdscr,1,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(1,0,"Name".ljust(sidebarboundary-30)+"Size".ljust(15)+"Last Modified".ljust(15),cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(2,sidebarboundary+1,"[ALT-Q] Quit")
        stdscr.addstr(3,sidebarboundary+1,"[DOWN] Move down")
        stdscr.addstr(4,sidebarboundary+1,"[UP] Move up")
        stdscr.addstr(5,sidebarboundary+1,"[Ctrl-R] Go up dir")
        stdscr.addstr(7,sidebarboundary+1,"[N] New ...")
        stdscr.addstr(8,sidebarboundary+1,"[DEL] Delete")
        stdscr.addstr(9,sidebarboundary+1,"[M] Rename")

        fi = 0
        for file in activefile[yoffset:yoffset+(my-2)]:
            if os.path.isdir(file.path) and fi+yoffset == selected:
                cl = cursesplus.GREEN
                stdscr.addstr(my-5,sidebarboundary+1,"[ENTER] Open")
            elif os.path.isdir(file.path):
                cl = cursesplus.YELLOW
            elif fi+yoffset == selected and not os.path.isdir(file.path):
                cl = cursesplus.CYAN
                #stdscr.addstr(my-5,sidebarboundary+1,"[Ctrl-X] Execute")
                stdscr.addstr(my-5,sidebarboundary+1,"[ENTER] Edit")
            elif is_file_binary(file.path):
                cl = cursesplus.MAGENTA

                
            elif is_file_dicteditable(file.path):
                cl = cursesplus.RED
                
            else:
                cl = cursesplus.WHITE
            stdscr.addstr(fi+2,0,os.path.split(file.path)[1][xoffset:sidebarboundary+xoffset],cursesplus.set_colour(cursesplus.BLACK,cl))
            stdscr.addstr(fi+2,sidebarboundary-30,parse_size(file.size),cursesplus.set_colour(cursesplus.BLACK,cl))
            stdscr.addstr(fi+2,sidebarboundary-19,str(file.date),cursesplus.set_colour(cursesplus.BLACK,cl))
            fi += 1

        stdscr.refresh()
        ch = stdscr.getch()

        if ch == curses.KEY_NPAGE and yoffset+my-3 < len(activefile):
            yoffset += 1
        elif ch == curses.KEY_PPAGE and yoffset > 0:
            yoffset -= 1
        elif ch == curses.KEY_LEFT and xoffset > 0:
            xoffset -= 1
        elif ch == curses.KEY_RIGHT:
            xoffset += 1
        elif ch == curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < yoffset:
                yoffset -= 1
        elif ch == curses.KEY_DOWN and selected < len(activefile)-1:
            selected += 1
            if selected > yoffset+my-3:
                yoffset += 1
        elif ch == curses.KEY_ENTER or ch == 10 or ch == 13:
            if (os.path.isdir(activefile[selected].path)):
                adir = activefile[selected].path
                yoffset = 0
                selected = 0
                
            else:
                handle_file_editing(stdscr,activefile[selected].path)
        elif ch == curses.KEY_DC:
            if os.path.isfile(activefile[selected].path):
                os.remove(activefile[selected].path)
            elif os.path.isdir(activefile[selected].path):
                shutil.rmtree(activefile[selected].path)
        kkx = curses.keyname(ch).decode()
        if kkx.lower().endswith("q"):
            return
        elif kkx == "^R":
            if adir == basedir+axt:
                cursesplus.messagebox.showerror(stdscr,["You may not move back further."])
            else:
                adir = os.path.split(adir)[0]
                yoffset = 0
                selected = 0
        elif kkx == "n":
            whattpmake = crss_custom_ad_menu(stdscr,["Cancel","New File","New Directory"])
            if whattpmake == 1:
                newname = crssinput(stdscr,"Name of new file")
                try:
                    with open(adir+"/"+newname,"x") as f:
                        f.write("")
                except:
                    cursesplus.messagebox.showerror(stdscr,["Failed to create file"])
            elif whattpmake == 2:
                newname = crssinput(stdscr,"Name of new directory")
                try:
                    os.mkdir(adir+"/"+newname)
                except:
                    cursesplus.messagebox.showerror(stdscr,["Failed to create directory"])
            elif whattpmake == 2:
                pass
        elif kkx == "m":
            newname = crssinput(stdscr,"New name?")
            try:
                os.rename(activefile[selected].path,adir+"/"+newname)
            except:
                cursesplus.messagebox.showerror(stdscr,["Failed to move data"])

def collapse_datapack_description(desc):
    if type(desc) == str:
        return desc.splitlines()[0]
    elif type(desc) == list:
        return desc[0]["translate"].splitlines()[0]
    elif type(desc) == dict:
        return desc["translate"].splitlines()[0]

def datapack_is_valid(datapackfile):
    tmpx = generate_temp_dir()
    try:
        with zipfile.ZipFile(datapackfile) as zf:
            zf.extract("pack.mcmeta",tmpx)
        with open(tmpx+"/pack.mcmeta") as f:
            json.load(f)
    except:
        return False
    else:
        return True

def generate_temp_dir() -> str:
    flx = f"{TEMPDIR}/{hex(round(random.random()*2**64))[2:]}"
    os.mkdir(flx)
    return flx#Random int between 0 and 2^64

def find_world_datapacks(datadir) -> list[list[str,str]]:
    #datadir = worlddir+"/datapacks"
    tmpx = generate_temp_dir()
    final = []
    if not os.path.isdir(datadir):
        os.mkdir(datadir)
        return []
    else:
        try:
            
            for file in glob.glob(datadir+"/*.zip"):
                with zipfile.ZipFile(file) as zf:
                    zf.extract("pack.mcmeta",tmpx)
                with open(tmpx+"/pack.mcmeta") as f:
                    data = json.load(f)
                    final.append([data["pack"]["description"],file])
        except:
            pass
        return final

def manage_datapacks(stdscr,datapackdir:str):
    while True:
        fz = find_world_datapacks(datapackdir)
        wtd = crss_custom_ad_menu(stdscr,["Back","Add Datapack"]+[collapse_datapack_description(f[0]) for f in fz])
        
        if wtd == 0:
            return
        chx = fz[wtd-2]
        if wtd == 1:
            
            datatoadd = cursesplus.filedialog.openfiledialog(stdscr,"Choose a datapack to import",[["*.zip","ZIP Archives"]],os.path.expanduser("~"))
            if datatoadd is not None:
                if datapack_is_valid(datatoadd):
                    shutil.copyfile(datatoadd,datapackdir+"/"+os.path.split(datatoadd)[1])#Copy datapack
                else:
                    cursesplus.messagebox.showwarning(stdscr,["The selected file is not a valid Minecraft data pack"])
        else:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you wish to delete this?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                os.remove(chx[1])

def manage_a_world(stdscr,SERVER_DIR,svrx:str):
    while True:
        wtd = crss_custom_ad_menu(stdscr,["Back","Manage datapacks","View world info"])
        if wtd == 0:
            return
        elif wtd == 1:
            manage_datapacks(stdscr,svrx+"/datapacks")
        if wtd == 2:
            cursesplus.displaymsg(stdscr,["Calculating world size"],False)
            #svrx = po[n-2]
            svrd = SERVER_DIR+"/"+svrx
            os.chdir(SERVER_DIR)
            svrs = get_tree_size(svrd)
            stdscr.clear()
            stdscr.addstr(0,0,"World Name:")
            stdscr.addstr(1,0,"World Size:")
            stdscr.addstr(3,0,"PRESS D TO DELETE. PRESS ANY OTHER KEY TO GO BACK")
            stdscr.addstr(0,20,svrx)
            stdscr.addstr(1,20,parse_size(svrs))
            stdscr.refresh()
            ch = stdscr.getch()
            if ch == 100:
                cursesplus.displaymsg(stdscr,["Removing world"],False)
                shutil.rmtree(svrd)

def manage_ops(stdscr,serverdir):
    opdir = serverdir + "/ops.json"
    if not os.path.isfile(opdir):
        cursesplus.messagebox.showerror(stdscr,["Please start your server to generate ops.json"])
    else:
        with open(opdir) as f:
            data = json.load(f)
        
        while True:
            dz = crss_custom_ad_menu(stdscr,["BACK","ADD ADMIN"]+[d["name"] for d in data])
            if dz == 0:
                with open(opdir,"w+") as f:
                    f.write(json.dumps(data))
                break
            elif dz == 1:
                player = crssinput(stdscr,"Please input the player's name")
                try:
                    uuid = get_player_uuid(player)
                except:
                    cursesplus.messagebox.showerror(stdscr,["This player does not exist."])
                else:
                    bypass = cursesplus.messagebox.askyesno(stdscr,["Should this player be able","to bypass player limits?"])
                    oplevel = crss_custom_ad_menu(stdscr,["Bypass spawn protection only","Singleplayer commands","Moderation (kick/ban)","All commands (/stop)"])+1
                    data.append(
                        {
                            "name" : player,
                            "uuid" : uuid,
                            "level" : oplevel,
                            "bypassesPlayerLimit" : bypass
                        }
                    )
            else:
                activel = data[dz-2]
                while True:
                    stdscr.clear()
                    stdscr.refresh()
                    stdscr.addstr(0,0,"Name:")
                    stdscr.addstr(1,0,"UUID:")
                    stdscr.addstr(2,0,"Admin Level:")
                    stdscr.addstr(3,0,"Bypasses Limit?")
                    stdscr.addstr(0,20,activel["name"])
                    stdscr.addstr(1,20,activel["uuid"])
                    stdscr.addstr(2,20,str(activel["level"]))
                    stdscr.addstr(3,20,str(activel["bypassesPlayerLimit"]))
                    stdscr.addstr(5,0,"PRESS R TO REMOVE. PRESS C TO CHANGE PERMISSIONS. PRESS ENTER TO RETURN.",cursesplus.set_color(cursesplus.WHITE,cursesplus.BLACK))
                    stdscr.refresh()
                    ch = stdscr.getch()
                    if ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
                        break
                    elif ch == 114:
                        del data[dz-2]
                        break
                    elif ch == 99:
                        bypass = cursesplus.messagebox.askyesno(stdscr,["Should this player be able","to bypass player limits?"])
                        oplevel = crss_custom_ad_menu(stdscr,["Bypass spawn protection only","Singleplayer commands","Moderation (kick/ban)","All commands (/stop)"])+1
                        activel["level"] = oplevel
                        activel["bypassesPlayerLimit"] = bypass
                        data[dz-2] = activel
                        break

def get_mc_valid_timezone() -> str:
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    nzoffset = int((offset / 60 / 60 * -1)*100)
    if str(nzoffset).startswith("-"):
        isnegative = True
        nzoffset = -nzoffset
    else:
        isnegative = False

    szstr = str(nzoffset).zfill(4)
    if isnegative:
        finaloffset = "-"+szstr
    else:
        finaloffset = "+"+szstr
    return finaloffset

def get_mc_valid_timestamp(d:datetime.datetime) -> str: 
    return str(d)[0:-7] + " " + get_mc_valid_timezone()

def manage_bans(stdscr,serverdir):
    opdir = serverdir + "/banned-players.json"
    if not os.path.isfile(opdir):
        cursesplus.messagebox.showerror(stdscr,["Please start your server to generate ops.json"])
    else:
        with open(opdir) as f:
            data = json.load(f)
        
        while True:
            dz = crss_custom_ad_menu(stdscr,["BACK","ADD BAN"]+[d["name"] for d in data])
            if dz == 0:
                with open(opdir,"w+") as f:
                    f.write(json.dumps(data))
                break
            elif dz  == 1:
                player = crssinput(stdscr,"Please input the player's name")
                try:
                    uuid = get_player_uuid(player)
                except:
                    cursesplus.messagebox.showerror(stdscr,["This player does not exist."])
                else:
                    ctime = get_mc_valid_timestamp(datetime.datetime.now())
                    source = "CraftServerSetup"
                    if cursesplus.messagebox.askyesno(stdscr,["Should this ban be forever?"]):
                        dend = "forever"
                    else:
                        ddate = crssinput(stdscr,"What date should the ban end? (example: 2023-09-22)",maxlen=10)
                        dtime = crssinput(stdscr,"What time should the ban end? (example: 10:00:00)",maxlen=8)
                        dend =  ddate + " " + dtime + " " + get_mc_valid_timezone()
                    reason = crssinput(stdscr,"What is the reason for this ban?")
                    data.append(
                        {
                            "name" : player,
                            "uuid" : uuid,
                            "created" : ctime,
                            "source" : source,
                            "expires" : dend,
                            "reason" : reason
                        }
                    )
            else:
                active = data[dz-2]
                while True:
                    stdscr.clear()
                    stdscr.refresh()
                    stdscr.addstr(0,0,"Player:")
                    stdscr.addstr(1,0,"UUID:")
                    stdscr.addstr(2,0,"Time Created:")
                    stdscr.addstr(3,0,"Created by:")
                    stdscr.addstr(4,0,"Ban Expires:")
                    stdscr.addstr(5,0,"Reason:")
                    stdscr.addstr(0,20,active["name"])
                    stdscr.addstr(1,20,active["uuid"])
                    stdscr.addstr(2,20,active["created"])
                    stdscr.addstr(3,20,active["source"])
                    stdscr.addstr(4,20,active["expires"])
                    stdscr.addstr(5,20,active["reason"])
                    stdscr.addstr(7,0,"PRESS C TO CHANGE BAN END TIME. PRESS R TO REMOVE BAN. PRESS ENTER TO RETURN.",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
                    ch = stdscr.getch()
                    if ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
                        break
                    elif ch == 114:
                        del data[dz-2]
                        break
                    elif ch == 99:
                        ddate = crssinput(stdscr,"What date should the ban end? (example: 2023-09-22)",maxlen=10)
                        dtime = crssinput(stdscr,"What time should the ban end? (example: 10:00:00)",maxlen=8)
                        dend =  ddate + " " + dtime + " " + get_mc_valid_timezone()
                        active["expires"] = dend
                        data[dz-2] = active
                        
def server_backups(stdscr,serverdir:str,serverdata:dict):
    LBKDIR = serverdata["backupdir"]
    pushd(serverdir)#Just in case some super weird bug
    #if not os.path.isdir(LBKDIR):
    #    os.mkdir(LBKDIR)
    while True:
        z = crss_custom_ad_menu(stdscr,["Back","Create a Backup","Load a Backup",f"Choose backup directory ({LBKDIR})","Delete all backups"])
        if z == 0:
            popd()
            break
        elif z == 1:
            with open(serverdir+"/crss.json","w+") as f:
                f.write(json.dumps(serverdata))
            useprofile = APPDATA["backupprofiles"][list(APPDATA["backupprofiles"].keys())[crss_custom_ad_menu(stdscr,list(APPDATA["backupprofiles"].keys()),"Select which backup profile to use")]]
            cursesplus.displaymsg(stdscr,["Calculating backup size..."],False)
            totalbackupsize = 0
            filestoindex = []
            for irule in useprofile["include"]:
                filestoindex += glob.glob(irule.replace("#SD",serverdir),recursive=True)
            for includefile in filestoindex:
                if os.path.isdir(includefile):
                    continue
                totalbackupsize += os.path.getsize(includefile)
                
            filetoremove = []
            for erule in useprofile["exclude"]:
                filetoremove += glob.glob(erule.replace("#SD",serverdir),recursive=True)
            for excludefile in filetoremove:
                
                try:
                    filestoindex.remove(excludefile)
                    totalbackupsize -= os.path.getsize(excludefile)
                except:
                    pass
            
            
            if cursesplus.messagebox.askyesno(stdscr,["The backup will take up",parse_size(totalbackupsize),"Do you want to continue?"]):
                dstsname = str(datetime.datetime.now())[0:-7].replace(" ","_").replace(":","")
                p = cursesplus.ProgressBar(stdscr,totalbackupsize+1,bar_location=cursesplus.ProgressBarLocations.CENTER,message="Creating backup")
                for file in filestoindex:
                    if os.path.isdir(file):
                        continue
                    p.value += os.path.getsize(file) - 1
                    p.step(file)
                    
                    dst = LBKDIR + f'/{dstsname}/' + file.replace(serverdir,"")
                    os.makedirs(os.path.dirname(dst),exist_ok=True)
                    try:
                        shutil.copyfile(file,dst)
                    except:
                        pass#Fix bug - temp files crash
                p.done()
                cursesplus.messagebox.showinfo(stdscr,["Completed backup"])
                
        elif z == 2:
            if len(os.listdir(LBKDIR)) == 0:
                cursesplus.messagebox.showwarning(stdscr,["You do not have any backups"])
                continue
            if cursesplus.messagebox.askyesno(stdscr,["This will completely overwrite your server directory","Are you sure you wish to proceed"]):
                selbk = cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a backup dir",directory=LBKDIR)
                #cursesplus.displaymsg(stdscr,["Restoring Backup"],False)
                w = cursesplus.PleaseWaitScreen(stdscr,["Restoring Backup"])
                w.start()
                os.chdir("/")
                shutil.rmtree(serverdir)
                shutil.copytree(selbk,serverdir)
                try:
                    with open(serverdir+"/crss.json") as f:
                        nd = json.load(f)
                        locateid = nd["id"]
                        tom_index = next((index for (index, d) in enumerate(APPDATA["servers"]) if d["id"] == locateid), None)
                        APPDATA["servers"][tom_index] = nd
                except:
                    pass
                w.stop()
                cursesplus.messagebox.showinfo(stdscr,["Restore completed"])
                os.chdir(serverdir)       
        elif z == 3:
            serverdata["backupdir"] = cursesplus.filedialog.openfolderdialog(stdscr,"Choose a new backup directory")
            LBKDIR = serverdata["backupdir"]
            updateappdata()       
        elif z == 4:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete all backups?"]):
                shutil.rmtree(LBKDIR,True)
                os.mkdir(LBKDIR)

def get_tree_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size
def updateappdata():
    global APPDATA
    global APPDATAFILE
    with open(APPDATAFILE,"w+") as f:
        f.write(json.dumps(APPDATA,indent=2))

def choose_java_install(stdscr) -> str:

    #Return path of selected java- Smart java?
    while True:
        stdscr.erase()
        jsl = crss_custom_ad_menu(stdscr,["ADD NEW INSTALLATION"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in APPDATA["javainstalls"]],"Please choose a Java installation from the list")
        if jsl == 0:
            managejavainstalls(stdscr)
        else:
            break
    return APPDATA["javainstalls"][jsl-1]["path"]
def managejavainstalls(stdscr):
    global APPDATA
    if "java" in [j["path"] for j in APPDATA["javainstalls"]]:
        pass
    else:
        if os.system("java --help") == 0 or os.system("java /?") == 0 or os.system("java -help") == 0:
        
            APPDATA["javainstalls"].append({"path":"java","ver":get_java_version()})
        stdscr.clear()
    while True:
        stdscr.erase()
        jmg = crss_custom_ad_menu(stdscr,["ADD INSTALLATION","FINISH"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in APPDATA["javainstalls"]])
        if jmg == 0:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a java executable",directory=os.path.expanduser("~"))
            if os.system(njavapath.replace("\\","/")+" -help") != 0:
                if not cursesplus.messagebox.askyesno(stdscr,["You may have selected an invalid java file.","Are you sure you would like to add it"]):
                    continue
                else:
                    stdscr.erase()
                    ndict = {"path":njavapath.replace("\\","/"),"ver":"Unknown"}
                    if cursesplus.messagebox.askyesno(stdscr,["Do you know what java version this is?"]):
                        ndict["ver"] = crssinput(stdscr,"Java version?",maxlen=10)
                        APPDATA["javainstalls"].append(ndict)
            else:
                fver = get_java_version(njavapath.replace("\\","/"))
                ndict = {"path":njavapath.replace("\\","/"),"ver":fver}
                APPDATA["javainstalls"].append(ndict)
        elif jmg == 1:
            return
        else:
            
            jdl = APPDATA["javainstalls"][jmg-2]
            stdscr.clear()
            stdscr.addstr(0,0,"MANAGING JAVA INSTALLATION")
            stdscr.addstr(2,0,"Path")
            stdscr.addstr(3,0,"Version")
            stdscr.addstr(5,0,"Press V to verify installation | Press D to delete | Press any other key to return",cursesplus.cp.set_colour(cursesplus.WHITE,cursesplus.BLACK))
            stdscr.addstr(2,10,jdl["path"])
            stdscr.addstr(3,10,jdl["ver"])
            k = stdscr.getch()
            if k == curses.KEY_DC or k == 100:
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to remove the java installation",jdl["path"]],default=cursesplus.messagebox.MessageBoxStates.NO):
                    del APPDATA["javainstalls"][jmg-2]
            elif k == 118:
                jdl["ver"] = get_java_version(jdl["path"])
                if jdl["ver"] == "Error":
                    cursesplus.messagebox.showwarning(stdscr,["Java installaion is corrupt"])
                    del APPDATA["javainstalls"][jmg-2]
                else:
                    cursesplus.messagebox.showinfo(stdscr,["Java installation is safe"])

        updateappdata()

def compare_versions(version1, version2):
    """0: Same, -1: 1 < 2. 1: 1 > 2"""
    version1_parts = tuple(map(int, version1.split('.')))
    version2_parts = tuple(map(int, version2.split('.')))

    for v1, v2 in zip(version1_parts, version2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    if len(version1_parts) < len(version2_parts):
        return -1
    elif len(version1_parts) > len(version2_parts):
        return 1

    return 0

def windows_update_software(stdscr,interactive=True):
    if interactive:
        cursesplus.displaymsg(stdscr,["Checking for updates"],False)
    td = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/update.txt").text
    tdz = td.split("|")
    svr = tdz[1]
    url = tdz[0]
    if compare_versions(svr,APP_UF_VERSION) == 1:
        #NUA
        if cursesplus.messagebox.askyesno(stdscr,["There is a new update available.",f"{svr} over {APP_UF_VERSION}","Would you like to install it?"]):
            cursesplus.displaymsg(stdscr,["Downloading new update..."],False)
            urllib.request.urlretrieve(url,os.path.expandvars("%TEMP%/crssupdate.exe"))
            os.startfile(os.path.expandvars("%TEMP%/crssupdate.exe"))
            sys.exit()
    else:
        if interactive:
            cursesplus.messagebox.showinfo(stdscr,["No new updates are available"])

def show_changelog_info(stdscr):
    """Display the latest changelog info"""
    cursesplus.displaymsg(stdscr,["Getting Info"],wait_for_keypress=False)
    changeloginfo = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/refs/heads/main/changelog").text
    final = []
    for ln in changeloginfo.splitlines():
        if ln.replace(" ","") == "":
            continue
        if ln.startswith("-") or ln.startswith(" "):
            #Info
            final.append(ln)
        else:
            final.append("")
            final.append("")
            final.append(f"Added in {ln}")
            
    cursesplus.textview(stdscr,text="\n".join(final),message="Changelog Info")

def import_amc_server(stdscr,chlx):
    nwait = cursesplus.PleaseWaitScreen(stdscr,["Unpacking Server"])
    nwait.start()
    smd5 = file_get_md5(chlx)
    if os.path.isdir(f"{TEMPDIR}/{smd5}"):
        shutil.rmtree(f"{TEMPDIR}/{smd5}")
    s = unpackage_server(chlx,f"{TEMPDIR}/{smd5}")
    nwait.stop()
    if s != 0:
        cursesplus.messagebox.showerror(stdscr,["An error occured unpacking your server"])
        return
    try:
        smtmpfile = f"{TEMPDIR}/{smd5}/exdata.json"
        with open(smtmpfile) as f:
            xdat = json.load(f)
        nname = xdat["name"]
        while True:
            if nname in [l["name"] for l in APPDATA["servers"]]:
                #cursesplus.utils.showcursor()
                
                nname = crssinput(stdscr,"The name already exists. Please input a new name",prefiltext=xdat["name"])
                #cursesplus.utils.hidecursor()
            else:
                xdat["name"] = nname
                break
        nwait.start()
        #os.mkdir(SERVERSDIR+"/"+nname)
        shutil.copytree(f"{TEMPDIR}/{smd5}",SERVERSDIR+"/"+nname)
        xdat["dir"] = SERVERSDIR+"/"+nname
        bri = False
        if xdat["software"] != 0:
            xdat["javapath"] = choose_java_install(stdscr)
        else:
            if (os.path.isfile(xdat["dir"]+"/bedrock_server.exe") and not WINDOWS) or (not os.path.isfile(xdat["dir"]+"/bedrock_server.exe") and WINDOWS):
                bri = True
                nwait.stop()
                cursesplus.messagebox.showinfo(stdscr,["This server was packaged on a different OS.","The new file will be downloaded on the next screen."])
                nwait.start()
        xdat["script"] = generate_script(xdat)
        APPDATA["servers"].append(xdat)
        chosensrver = len(APPDATA["servers"])
        if bri:
            availablelinks = [g for g in extract_links_from_page(requests.get("https://www.minecraft.net/en-us/download/server/bedrock",headers={"User-Agent":MODRINTH_USER_AGENT}).text) if "azureedge" in g]
            link_win_normal = get_by_list_contains(availablelinks,"win/")
            link_lx_normal = get_by_list_contains(availablelinks,"linux/")
            link_win_preview = get_by_list_contains(availablelinks,"win-preview/")
            link_lx_preview = get_by_list_contains(availablelinks,"linux-preview/")
            if WINDOWS:
                availablelinks = [link_win_normal,link_win_preview]
            else:
                availablelinks = [link_lx_normal,link_lx_preview]
            nwait.stop()
            bedrock_do_update(stdscr,chosensrver,availablelinks)
            
        nwait.stop()
        nwait.destroy()
        cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
    except Exception as e:
        raise e
        cursesplus.messagebox.showerror(stdscr,["An error occured importing your server."])

def str_contains_word(s:str,string:str) -> bool:
    d = s.lower().split(" ")
    return string in d

def list_get_maxlen(l:list) -> int:
    return max([len(s) for s in l])

def crssinput(stdscr,
    prompt: str,
    lines: int = 1,
    maxlen: int = 0,
    passwordchar: str = None,
    retremptylines: bool = False,
    prefiltext: str = "",
    bannedcharacters: str = "") -> str:
    cursesplus.utils.showcursor()
    r = cursesplus.cursesinput(stdscr,prompt,lines,maxlen,passwordchar,retremptylines,prefiltext,bannedcharacters)
    cursesplus.utils.hidecursor()
    return r

def crss_custom_ad_menu(stdscr,options:list[str],title="Please choose an option from the list below",show_ad=False,footer="") -> int:
    """An alternate optionmenu that will be used in primary areas. has an ad. footer will only be shown if no ad (so no problems after 1.40.5)"""
    try:
        uselegacy = APPDATA["settings"]["oldmenu"]["value"]
    except:
        uselegacy = True
    
    if uselegacy:
        return cursesplus.optionmenu(stdscr,options,title)
    selected = 0
    offset = 0
    if ads_available():
        chosenad = random.choice(ADS)
    else:
        show_ad = False
    maxl = list_get_maxlen(options)
    while True:
        stdscr.clear()
        mx,my = os.get_terminal_size()
        
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        cursesplus.utils.fill_line(stdscr,1,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(0,0,title,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(1,0,"Use the up and down arrow keys to navigate and enter to select",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        oi = 0
        for op in options[offset:offset+my-7]:
            if str_contains_word(op,"back") or str_contains_word(op,"quit") or str_contains_word(op,"cancel") or str_contains_word(op,"delete") or str_contains_word(op,"disable") or str_contains_word(op,"reset") or str_contains_word(op,"-"):
                col = cursesplus.RED
            elif str_contains_word(op,"start") or str_contains_word(op,"new") or str_contains_word(op,"add") or str_contains_word(op,"enable") or str_contains_word(op,"create") or str_contains_word(op,"-"):
                col = cursesplus.GREEN
            elif op.upper() == op:
                col = cursesplus.CYAN
            elif str_contains_word(op,"update") or str_contains_word(op,"help"):
                col = cursesplus.MAGENTA
            else:
                col = cursesplus.WHITE
            if not oi == selected-offset:
                stdscr.addstr(oi+3,7,op,cursesplus.set_colour(cursesplus.BLACK,col))
            else:
                stdscr.addstr(oi+3,7,op,cursesplus.set_colour(cursesplus.BLACK,col) | curses.A_UNDERLINE | curses.A_BOLD)
            oi += 1
        stdscr.addstr(selected+3-offset,1,"-->")
        stdscr.addstr(selected+3-offset,maxl+9,"<--")
        stdscr.addstr(oi+3,0,"━"*(mx-1))
        if offset > 0:
            stdscr.addstr(3,maxl+15,f"{offset} options above")
        if len(options) > offset+my-7:
            stdscr.addstr(oi+2,maxl+15,f"{len(options)-offset-my+7} options below")
        if ads_available() and show_ad:
            adx = oi + 5
            stdscr.addstr(adx-1,0,"ADVERTISEMENT (Insert product key to remove)")
            adl = textwrap.wrap(chosenad.message,mx-1)
            li = 0
            for l in adl:
                stdscr.addstr(adx+li,0,l,curses.A_BOLD)
                li += 1
            stdscr.addstr(adx+li,0,"Press A to check it out in your web browser!",cursesplus.set_colour(cursesplus.BLACK,cursesplus.MAGENTA)|curses.A_BOLD)
        else:
            stdscr.addstr(oi+4,0,footer)#Add footer if no add
        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_DOWN and selected < len(options)-1:
            
            selected += 1
            if selected > my-8:
                offset += 1
        elif ch == curses.KEY_UP and selected > 0:
            
            selected -= 1
            if selected < offset:
                offset -= 1
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return selected
        elif ch == 97 and show_ad:
            webbrowser.open(chosenad.url)
            stdscr.erase()
            stdscr.clear()
        elif ch == curses.KEY_HOME:
            selected = 0
            offset = 0
        elif ch == curses.KEY_END:
            selected = len(options)-1
            if selected > my-8+offset:
                offset = selected-my+8

def choose_server_memory_amount(stdscr) -> str:
    chop = cursesplus.coloured_option_menu(
        stdscr,
        [
            "1024 Megabytes (1 GB) - This is minimum for vanilla servers only",
            "2 GB - This the minimum safe amount for modded servers",
            "4 GB - This is good for most small servers",
            "8 GB - This is good for small servers with high render distance and high player counts",
            "Custom Amount - Choose a custom amount of memory"
        ],"Please choose the amount of memory your server should recieve"
    )
    if chop == 0:
        return "1024M"
    elif chop == 1:
        return "2G"
    elif chop == 2:
        return "4G"
    elif chop == 3:
        return "8G"
    elif chop == 4:
        while True:
            mtoal = crssinput(stdscr,"How much memory should your server get? (for example 1024M or 5G)")
            if not (mtoal.endswith("M") or mtoal.endswith("G")):
                cursesplus.messagebox.showerror(stdscr,["Memory strings must end with M for megabytes","or G for gigabytes,","For example 3G or 1600M"])
                continue
            try:
                int(mtoal[0:-1])
            except:
                cursesplus.messagebox.showerror(stdscr,["Invalid memory string.","EXAMPLE: 5G, 1465M"])
                continue
            if mtoal.endswith("M") and int(mtoal[0:-1]) < 1000:
                if cursesplus.messagebox.askyesno(stdscr,["You have alocated a dangerously low amount of memory.","Low memory will harm your server","Are you sure you want to allocate this much?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                    return mtoal
                else:
                    continue
            return mtoal

def import_server(stdscr):
    umethod = crss_custom_ad_menu(stdscr,["Import from .amc file","Import from folder","Cancel (Go Back)"])
    if umethod == 0:
        chlx = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a file",filter=[["*.amc","Minecraft Server file"],["*.xz","xz archive"],["*.tar","tar archive"]])
        import_amc_server(stdscr,chlx)
    elif umethod == 1:
        try:
            xdat = {}#Dict of server data
            cursesplus.messagebox.showinfo(stdscr,["First, select the folder that your server is in"])
            ddir = cursesplus.filedialog.openfolderdialog(stdscr,"Choose the folder of the server you want to import")
            cursesplus.messagebox.showinfo(stdscr,["Next, please select the main JAR file. This is usually named server.jar"])
            ffile = cursesplus.filedialog.openfiledialog(stdscr,"Please choose the server JAR file",[["*.jar","Java Archive files"],["*","All Files"]],ddir)
            fpl = os.path.split(ffile)[1]
            delaftercomplete = cursesplus.messagebox.askyesno(stdscr,["Delete original folder after import?"])
            nname = crssinput(stdscr,"Please enter the name of this server")
            while True:
                if nname in [l["name"] for l in APPDATA["servers"]]:
                    cursesplus.utils.showcursor()
                    nname = crssinput(stdscr,"The name already exists. Please input a new name",prefiltext=nname)
                    cursesplus.utils.hidecursor()
                else:
                    xdat["name"] = nname
                    break
            p = cursesplus.PleaseWaitScreen(stdscr,["Copying","Depending on the size of the server, this could take a few minutes"])
            p.start()
            shutil.copytree(ddir,SERVERSDIR+"/"+nname)
            if delaftercomplete:
                try:
                    shutil.rmtree(ddir)
                except:
                    pass
            p.stop()
            p.destroy()
            xdat["dir"] = SERVERSDIR+"/"+nname
            xdat["javapath"] = choose_java_install(stdscr)
            memorytoall = choose_server_memory_amount(stdscr)
            xdat["memory"] = memorytoall
            xdat["version"] = crssinput(stdscr,"What version is your server?")
            xdat["moddable"] = cursesplus.messagebox.askyesno(stdscr,["Is this server moddable?","That is, Can it be changed with plugins/mods"])
            xdat["software"] = crss_custom_ad_menu(stdscr,["Other/Unknown","Vanilla","Spigot","Paper","Purpur"],"What software is this server running")
            xdat["script"] = generate_script(xdat)
            
            APPDATA["servers"].append(xdat)
            pushd(xdat["dir"])
            with open("exdata.json","w+") as f:
                f.write(json.dumps(xdat))
            os.rename(fpl,"server.jar")#Fix problem if someone is not using server.jar as their executable jar file
            cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
        except:
            cursesplus.messagebox.showerror(stdscr,["An error occured importing your server."])
    else: return

def ads_available() -> bool:
    if len(ADS) == 0:
        return False
    else:
        return SHOW_ADVERT

def parse_bp_ielist(data:dict) -> list[str]:
    final = []
    for include in data["include"]:
        final.append("+ include "+include)
    for exclude in data["exclude"]:
        final.append("- exclude "+exclude)
    return final

def edit_backup_profile(stdscr,backupname: str) :
    bdata = APPDATA["backupprofiles"][backupname]
    bname = backupname
    while True:
        lditems = parse_bp_ielist(bdata)
        m = crss_custom_ad_menu(stdscr,["FINISH","CHANGE PROFILE NAME","Delete Profile","Create Rule"]+lditems,f"Editing backup profile {bname}")
        if m == 0:
            del APPDATA["backupprofiles"][backupname]
            APPDATA["backupprofiles"][bname] = bdata
            return
        elif m == 1:
            while True:
                bname = crssinput(stdscr,"Name the backup profile")
                if bname in APPDATA["backupprofiles"] and bname != backupname:
                    #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
                    if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Do you want to over-write it?"]):
                        break
                else:
                    break
        elif m == 2:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this","backup profile?"]):
                del APPDATA["backupprofiles"][bname]
                return
        elif m == 3:
            wtype = crss_custom_ad_menu(stdscr,["Cancel","Include (files to include)","Exclude (files to not include)"],"What type of rule should this be?")
            if wtype == 0:
                continue
            isexclude = wtype == 2
            imethod = crss_custom_ad_menu(stdscr,["Handwrite a Glob pattern","Select Files/Folders"],"How would you like to input this rule?")
            pattern = [""]
            if imethod == 0:
                cursesplus.displaymsg(stdscr,[
                    "Notes for writing Glob statements",
                    "Use * for wildcard, ** for recursive wildcard",
                    "Do not end with a / for a folder, use /* or /** instead."
                ])
                pattern[0] = crssinput(stdscr,"Write the GLOB pattern to match. Use #SD/ for the server directory.")
            else:
                itype = crss_custom_ad_menu(stdscr,["Choose a directory","Choose file(s)"])
                if itype == 0:
                    idir = cursesplus.filedialog.openfolderdialog(stdscr,"Choose a directory to match.")
                    pattern[0] = idir + "/**"
                else:
                    ifiles = cursesplus.filedialog.openfilesdialog(stdscr,"Choose files to match")
                    pattern = ifiles
                    
            if isexclude:
                bdata["exclude"] += pattern
            else:
                bdata["include"] += pattern
            
        else:
            isexclude = lditems[m-4].startswith("-")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to delete this rule?"]):
                relname = lditems[m-4].replace("+ include ","").replace("- exclude ","")
                if isexclude:
                    bdata["exclude"].remove(relname)
                else:
                    bdata["include"].remove(relname)
            

def new_backup_profile(stdscr) -> str:
    while True:
        name = crssinput(stdscr,"Name the backup profile")
        if name in APPDATA["backupprofiles"]:
            if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Would you like to over-write it?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                return name
            #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
        else:
            #Add to dict
            APPDATA["backupprofiles"][name] = {
                "include" : ["#SD/*"],
                "exclude" : []
            }
            return name
    
def backup_manager(stdscr):
    while True:
        co = crss_custom_ad_menu(stdscr,["Quit","Create backup profile"]+list(APPDATA["backupprofiles"].keys()),"Backup Profile Manager")
        if co == 0:
            updateappdata()
            return
        elif co == 1:
            edit_backup_profile(stdscr,new_backup_profile(stdscr))
        else:
            edit_backup_profile(stdscr,list(APPDATA["backupprofiles"].keys())[co-2])

def settings_mgr(stdscr):
    global COLOURS_ACTIVE
    global APPDATA
    while True:
        m = crss_custom_ad_menu(stdscr,["BACK","ADVANCED OPTIONS","MANAGE JAVA INSTALLATIONS","CHANGE LANGUAGE","BACKUP PROFILES"]+[d["display"] + " : " + str(d["value"]) for d in list(APPDATA["settings"].values())],"Please choose a setting to modify")
        if m == 0:
            updateappdata()
            return
        elif m == 1:
            while True:
                n = crss_custom_ad_menu(stdscr,["BACK","Reset settings","Reset all app data","De-register product key","Clear temporary directory"])
                if n == 0:
                    break
                elif n == 1:
                    del APPDATA["settings"]
                    APPDATA = compatibilize_appdata(APPDATA)
                    updateappdata()
                elif n == 2:
                    if cursesplus.messagebox.askyesno(stdscr,["DANGER","This will destroy all of the data this app has stored!","This includes ALL servers!","This will restore this program to default","Are you sure you wish to continue?"]):
                        if not cursesplus.messagebox.askyesno(stdscr,["THIS IS YOUR LAST CHANCE!","To make sure that you actually intend to reset,","SELECT NO TO WIPE"]):
                            if cursesplus.messagebox.askyesno(stdscr,["Last chance. For real this time","Are you sure you want to reset?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                                os.chdir("/")
                                shutil.rmtree(APPDATADIR)
                                cursesplus.messagebox.showinfo(stdscr,["Program reset."])
                                sys.exit()
                    updateappdata()
                elif n == 3:
                    APPDATA["productKey"] = ""
                    verifykey("")
                    updateappdata()
                elif n == 4:
                    shutil.rmtree(TEMPDIR)
        elif m == 2:
            managejavainstalls(stdscr)
        elif m == 3:
            eptranslate.prompt(stdscr,"Welcome to CraftServerSetup! Please choose a language to begin.")
            APPDATA["language"] = eptranslate.Config.choice
            cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        elif m == 4:
            backup_manager(stdscr)
        else:
            selm = list(APPDATA["settings"].values())[m-5]
            selk = list(APPDATA["settings"].keys())[m-5]
            if selm["type"] == "bool":
                selm["value"] = crss_custom_ad_menu(stdscr,["True (Yes)","False (No)"],f"New value for {selm['display']}") == 0
            elif selm["type"] == "int":
                selm["value"] = cursesplus.numericinput(stdscr,f"Please choose a new value for {selm['display']}")
            elif selm["type"] == "str":
                selm["value"] = crssinput(stdscr,f"Please choose a new value for {selm['display']}",prefiltext=selm["value"])
            APPDATA["settings"][selk] = selm

def doc_system(stdscr):
    while True:
        z = crss_custom_ad_menu(stdscr,["BACK","View documentation","Help on using text-based software","CONTACT SUPPORT"])
        if z == 0:
            break
        elif z == 1:
            cursesplus.displaymsg(stdscr,["Downloading Documentation"],False)
            urllib.request.urlretrieve(DOCFILE,DOCDOWNLOAD)
            efile: epdoc.EPDocfile = epdoc.load_from_file(DOCDOWNLOAD,"Craft Server Setup")
            efile.load()
            efile.show_documentation(stdscr)
        elif z == 2:
            usertutorial(stdscr)
        elif z == 3:
            source = crss_custom_ad_menu(stdscr,["Cancel","Via E-mail","Via Discord"],"How do you wish to contact support?")
            if source == 1:
                webbrowser.open("mailto:?to=enderbyte09@gmail.com&subject=Craft Server Setup Support", new=1)
            elif source == 2:
                cursesplus.messagebox.showinfo(stdscr,["Contact @enderbyte09 on Discord"])

def license(stdscr):
    global APPDATA
    if not APPDATA["license"] and not WINDOWS:
        if not os.path.isfile(ASSETSDIR+"/license"):
            urllib.request.urlretrieve("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/LICENSE",ASSETSDIR+"/license")
        with open(ASSETSDIR+"/license") as f:
            dat = f.read()
        cursesplus.textview(stdscr,text=dat,requireyes=True,isagreement=True,message="Please agree to the CraftServerSetup license to proceed.")
        APPDATA["license"] = True

def oobe(stdscr):
    global APPDATA
    if not APPDATA["hasCompletedOOBE"]:       
        stdscr.clear()
        cursesplus.displaymsg(stdscr,[t("oobe.welcome.0"),"",t("oobe.welcome.1"),t("oobe.welcome.2")])
        if not cursesplus.messagebox.askyesno(stdscr,["Do you know how to use a text-based program like this?"]):
            usertutorial(stdscr)
        if not bool(APPDATA["javainstalls"]):
            if cursesplus.messagebox.askyesno(stdscr,["You have no java installations set up","Would you like to set some up now?"]):
                managejavainstalls(stdscr)
            else:
                cursesplus.messagebox.showinfo(stdscr,["You can manage your","Java installations from the","settings menu"])
        
        if cursesplus.messagebox.askyesno(stdscr,["Would you like to change your default text editor?","YES: Choose a custom command","NO: use the default editor (usually nano)"],default=cursesplus.messagebox.MessageBoxStates.NO):
            APPDATA["settings"]["editor"]["value"] = crssinput(stdscr,"Please type a custom command: use %s to represent the file name")
        APPDATA["hasCompletedOOBE"] = True
        updateappdata()

def usertutorial(stdscr):
    cursesplus.messagebox.showinfo(stdscr,["This is a messagebox","Press enter to dismiss it"])
    cursesplus.messagebox.showinfo(stdscr,["This software has no mouse","You will never have to use your mouse, only your keyboard"])
    cursesplus.messagebox.askyesno(stdscr,["This is a question","Use the right and left arrows to change the highlighted options","or use Y and N on your keyboard.","Choose NO"])
    crss_custom_ad_menu(stdscr,["Don't choose this","Don't Choose this","Choose this!"],"This is a vertical option menu. Choose the third option using the up and down arrow keys!")
    cursesplus.messagebox.showinfo(stdscr,["Hit Ctrl-C to open up the quit menu"])

def stats_and_credits(stdscr):
    cursesplus.textview(stdscr,text="""
CRAFT SERVER SETUP CREDITS

=== DEVELOPERS ===
Enderbyte09

=== ART ===
Enderbyte09
Finn Komuniecki

=== BUG TESTERS ===
MangyCat (2 bugs)
kbence (2 bugs)
StephenR18 (1 bug)

Thank you very much, beta testers

=== UI TESTERS ===
Finn Komuniecki
Jim Westwell
                        

Software used in the making of this program:

-Visual Studio Code
-Python
-Pyinstaller
-Inno Setup
-Github

    """,message="CREDITS")

def do_linux_update(stdscr,interactive=True) -> bool:
    if os.path.isfile("/usr/lib/craftserversetup/updateblock"):
        cursesplus.messagebox.showerror(stdscr,["You are using a debian or arch install setup","Please download the latest version from GitHub"])
        return False
    try:
        if interactive:
            cursesplus.displaymsg(stdscr,["Querrying updates"],False)
        r = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/releases/latest")
        mostrecentreleasedversion = r.url.split("/")[-1][1:]
        if compare_versions(mostrecentreleasedversion,APP_UF_VERSION) == 1:
            #New update
            if cursesplus.messagebox.askyesno(stdscr,["There is a new update available.",f"{mostrecentreleasedversion} over {APP_UF_VERSION}","Would you like to install it?"]):
                if not os.path.isfile("/usr/lib/craftserversetup/deb"):
                    cursesplus.displaymsg(stdscr,["Downloading new update"],False)
                    downloadurl = f"https://github.com/Enderbyte-Programs/CraftServerSetup/releases/download/v{mostrecentreleasedversion}/craftserversetup.tar.xz"
                    if os.path.isdir("/tmp/crssupdate"):
                        shutil.rmtree("/tmp/crssupdate")
                    os.mkdir("/tmp/crssupdate")
                    urllib.request.urlretrieve(downloadurl,"/tmp/crssupdate/craftserversetup.tar.xz")
                    cursesplus.displaymsg(stdscr,["Installing update"],False)
                    if unpackage_server("/tmp/crssupdate/craftserversetup.tar.xz","/tmp/crssupdate") == 1:
                        cursesplus.messagebox.showerror(stdscr,["There was an error unpacking the update"])
                        return False
                    pushd("/tmp/crssupdate")
                    if os.path.isfile("/usr/bin/craftserversetup"):
                        #admin
                        spassword = crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(f"echo -e \"{spassword}\" | sudo -S -k python3 /tmp/crssupdate/installer install",stdout=std0,stderr=std0,shell=True)
                    else:
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(["python3","/tmp/crssupdate/installer","install"],stdout=std0,stderr=std0)
                    popd()
                    if r == 0:
                        return True
                    else:
                        cursesplus.messagebox.showwarning(stdscr,["Update failed.","Check /tmp/crssupdate/UPDATELOG.txt"])
                    
                    # Equivilant of tar -xf
                else:
                    #Attempt deb install
                    cursesplus.displaymsg(stdscr,["Downloading new update"],False)
                    downloadurl = f"https://github.com/Enderbyte-Programs/CraftServerSetup/releases/download/v{mostrecentreleasedversion}/craftserversetup.deb"
                    if os.path.isdir("/tmp/crssupdate"):
                        shutil.rmtree("/tmp/crssupdate")
                    os.mkdir("/tmp/crssupdate")
                    urllib.request.urlretrieve(downloadurl,"/tmp/crssupdate/craftserversetup.deb")
                    cursesplus.displaymsg(stdscr,["Installing update"],False)
                    spassword = crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
                    with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                        r = subprocess.call(f"echo -e \"{spassword}\n\" | sudo -S -k dpkg -i /tmp/crssupdate/craftserversetup.deb",stdout=std0,stderr=std0,shell=True)

            else:
                return False#Quit by user preference
        else:
            if interactive:
                cursesplus.messagebox.showinfo(stdscr,["No new updates are available"])
            return False#Quit because no update
    except:
        cursesplus.messagebox.showerror(stdscr,["There was an error applying an update"])
        return False#Quit because errpr

def devtools(stdscr):
    global APPDATA
    while True:
        m = crss_custom_ad_menu(stdscr,["BACK","Python debug prompt","Test exception handling","Global variable dump","Appdata editor"])
        if m == 0:
            return
        elif m == 1:
            stdscr.clear()
            stdscr.erase()
            stdscr.refresh()
            curses.reset_shell_mode()
            print("Run exit to return")
            cursesplus.utils.showcursor()
            while True:
                
                epp = input("Python >")
                if epp == "exit":
                    break
                try:
                    exec(epp)
                except Exception as ex:    
                    print(f"ER {type(ex)}\nMSG {str(ex)}")
            curses.reset_prog_mode()
            cursesplus.utils.hidecursor()
        elif m == 2:
            raise RuntimeError("Manually triggered exception")
        elif m == 3:
            final = ""
            glv = globals()
            for g in list(glv.items()):
                final += f"NAME: {g[0]} VAL: {str(g[1])}\n"
            cursesplus.textview(stdscr,text=final)
        elif m == 4:
            APPDATA = dictedit(stdscr,APPDATA,"CRSS config")
            updateappdata()

def internet_thread(stdscr):
    global ADS
    global SHOW_ADVERT
    global VERSION_MANIFEST_DATA
    VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
    init_idata(stdscr)
    gen_adverts("Upgrade with a product key to remove ads")
    epprodkey.load_data("https://pastebin.com/raw/8CejUxsY")
    SHOW_ADVERT = not verifykey(APPDATA["productKey"])

def update_menu(stdscr):
    global UPDATEINSTALLED
    while True:
        m = crss_custom_ad_menu(stdscr,["Back","Check for Updates","View Changelog"])
        if m == 0:
            break
        elif m == 1:
            if WINDOWS:
                windows_update_software(stdscr)
                return
            #OLD UPDATE MAY BE REMOVED IN 0.18.3
            if do_linux_update(stdscr):
                UPDATEINSTALLED = True
                return
        elif m == 2:
            show_changelog_info(stdscr)

def main(stdscr):
    global VERSION_MANIFEST
    global VERSION_MANIFEST_DATA
    global COLOURS_ACTIVE
    global APPDATAFILE
    global UPDATEINSTALLED
    global _SCREEN
    global SHOW_ADVERT
    global ADS
    _SCREEN = stdscr
    global DEBUG
    
    restart_colour()
    curses.curs_set(0)
    try:
        cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        stdscr.addstr(0,0,"Waiting for internet connection...")
        stdscr.refresh()
        cursesplus.utils.hidecursor()
        issue = False
        if not internet_on():
            cursesplus.messagebox.showerror(stdscr,["No internet connection could be found.","An internet connection is required to run this program."],colour=True)
        #cursesplus.messagebox.showerror(stdscr,[str(_transndt)])
        ADS.append(Advertisement("https://ko-fi.com/s/f44efdb343","Support Enderbyte Programs by Buying A CraftServerSetup Product Key"))#Ads are now empty
        if _transndt:
            urllib.request.urlretrieve("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/src/translations.toml",APPDATADIR+"/translations.toml")
            eptranslate.load(APPDATADIR+"/translations.toml")
        
        if DEBUG:
            stdscr.addstr(0,0,"WARNING: This program is running from its source tree!",cursesplus.set_colour(cursesplus.BLACK,cursesplus.YELLOW))
            stdscr.refresh()
            issue = True
        if os.path.isdir("/usr/lib/craftserversetup") and os.path.isdir(os.path.expanduser("~/.local/lib/craftserversetup")):
            stdscr.addstr(1,0,"ERROR: Conflicting installations of crss were found! Some issues may occur",cursesplus.set_colour(cursesplus.BLACK,cursesplus.RED))
            stdscr.refresh()
            issue = True
        if issue:
            sleep(3)
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        global APPDATA
        stdscr.addstr(0,0,"Initializing application data...                 ")
        stdscr.refresh()
        cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        signal.signal(signal.SIGINT,sigint)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', MODRINTH_USER_AGENT)]
        urllib.request.install_opener(opener)
        
        threading.Thread(target=internet_thread,args=(stdscr,)).start()
        APPDATAFILE = APPDATADIR+"/config.json"
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
        APPDATA = compatibilize_appdata(APPDATA)
        #send_telemetry()
        if APPDATA["language"] is None:
            eptranslate.prompt(stdscr,"Welcome to CraftServerSetup! Please choose a language to begin.")
            APPDATA["language"] = eptranslate.Config.choice
            cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        license(stdscr)
        oobe(stdscr)
        if len(sys.argv) > 1:
            if os.path.isfile(sys.argv[1]):
                import_amc_server(stdscr,sys.argv[1])        
        
        if not APPDATA["pkd"]:
            if cursesplus.messagebox.askyesno(stdscr,["Have you purchased a product key?","If so, press yes and you will be prompted to enter it."],default=cursesplus.messagebox.MessageBoxStates.NO):
                
                product_key_page(stdscr,True)
        APPDATA["pkd"] = True
        updateappdata()
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        introsuffix = ""
        if DEBUG:
            introsuffix=" | SRC DEBUG"
        threading.Thread(target=send_telemetry).start()
        if APPDATA["settings"]["showprog"]["value"]:
            mx = stdscr.getmaxyx()[1]-1
            md = round(mx//20)
            for i in range(0,20):
                stdscr.addstr(stdscr.getmaxyx()[0]-1,i*md," "*md,cursesplus.set_colour(cursesplus.GREEN,cursesplus.WHITE))
                stdscr.refresh()
                time.sleep(1/40)
        if APPDATA["settings"]["autoupdate"]["value"]:
            if WINDOWS:
                windows_update_software(stdscr,False)
            #OLD UPDATE MAY BE REMOVED IN 0.18.3
            else:
                if do_linux_update(stdscr,False):
                    UPDATEINSTALLED = True
                    return
        while True:
            try:
                stdscr.erase()
                #lz = ["Set up new server","Manage servers","Quit Craft Server Setup","Manage java installations","Import Server","Update CraftServerSetup","Manage global backups","Report a bug","Settings","Help","Stats and Credits"]
                lz = ["New server","My servers","Settings","Help","Report a bug","Update CraftServerSetup","Credits","Quit","OTHER ENDERBYTE PROGRAMS SOFTWARE"]
                if APPDATA["productKey"] == "" or not prodkeycheck(APPDATA["productKey"]):
                    lz += ["Buy/Insert a Product Key"]
                if DEVELOPER:
                    lz += ["Debug Tools"]
                m = crss_custom_ad_menu(stdscr,lz,f"{t('title.welcome')} | Version {APP_UF_VERSION}{introsuffix} | {APPDATA['idata']['MOTD']}",True)
                if m == 7:
                    cursesplus.displaymsg(stdscr,["Shutting down..."],False)
                    if len(SERVER_INITS.items()):
                        if not cursesplus.messagebox.askyesno(stdscr,["Are you sure you wish to quit?",f"{len(SERVER_INITS.items())} servers are still running!","They will be stopped."]):
                            continue
                    safe_exit(0)
                    break
                elif m == 0:

                    setupnewserver(stdscr)
                elif m == 1:
                    servermgrmenu(stdscr)
                #elif m == 3:
                #    managejavainstalls(stdscr)
                elif m == 5:
                    if PORTABLE:
                        cursesplus.messagebox.showerror(stdscr,["You may not update in portable mode"])
                        continue
                    else:
                        update_menu(stdscr)
                elif m == 4:
                    webbrowser.open("https://github.com/Enderbyte-Programs/CraftServerSetup/issues")
                    cursesplus.messagebox.showinfo(stdscr,["Please check your web browser"])     
                elif m == 2:
                    settings_mgr(stdscr)
                elif m == 3:
                    doc_system(stdscr)
                elif m == 6:
                    stats_and_credits(stdscr)
                elif DEVELOPER and lz[m] == "Debug Tools":
                    devtools(stdscr)
                elif m == 8:
                    webbrowser.open("https://enderbyteprograms.net")
                elif m == 9:
                    product_key_page(stdscr)
            except Exception as e2:
                safe_error_handling(e2)
        if APPDATA["settings"]["transitions"]["value"]:
            cursesplus.transitions.horizontal_bars(stdscr)
    except Exception as e:
        error_handling(e,"A serious error has occured")

if __name__ == "__main__":
    curses.wrapper(main)
    if UPDATEINSTALLED:
        print("""
=============================
Update installed successfully
=============================""")