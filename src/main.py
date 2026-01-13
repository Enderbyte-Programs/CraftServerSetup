#!/usr/bin/python3
#type: ignore
#Early load variables
APP_VERSION = 1#The API Version.
APP_UF_VERSION = "1.54.7"
#The semver version
print(f"CraftServerSetup by Enderbyte Programs v{APP_UF_VERSION} (c) 2023-2026, some rights reserved")

### Standard Library Imports ###

import shutil                   #File utilities
import sys                      #C Utilities
import os                       #OS System Utilities
import curses                   #NCurses Terminal Library
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
import webbrowser               #Open links like the bug link
import tarfile                  #Create archives
import gzip                     #Compression utilities
import time                     #Timezone data
import copy                     #Object copies
import enum                     #Improve readability
import io                       #File streams
import shlex                    #Data parsing
import re                       #Pattern matching
import typing                   #HArd types
import itertools                #Useful things for working with lists

WINDOWS = platform.system() == "Windows"
DEBUG = False#Some constants need to be loaded before library startup... It's a bad system, but this is what is needed to split up this 7000 line file

if sys.version_info < (3,10):
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!!! Serious Error !!!!!!!")
    print("!! Python version  too old !!")
    print("! Use version 3.10 or newer !")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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
import yaml                     #Parse YML Files

#Modularized inputs (1.53 refactoring +)
import epdoc                    #Documentations library (BY ME)
import pngdim                   #Calculate dimensions of a PNG file
import eptranslate              #Translations
from eptranslate import t       #Shorthand
import staticflags              #Constants and urls
import arguments                #CLI arguments

#Setup static flags
staticflags.setup_ua(APP_UF_VERSION,APP_VERSION)
staticflags.setup_early_load(WINDOWS,DEBUG)


from staticflags import *       #Static flags are locked at this time
import utils                    #Textural utilities
import appdata                  #Application data
import autorestart              #Server auto restart
import timedexec                #Cursesplus timeout
import uicomponents             #Custom UI components
import propertiesfiles          #Tools for .properties files
import codeofconduct            #Tools for code of conduct
import tempdir                  #Temp dir maker
import dirstack                 #pushd/popd
import renaminghandler          #MC rename namdler
import texteditor               #Text editor handler
import logutils                 #Load logs
import bedrocklinks             #Load bedrock files

del WINDOWS
del DEBUG

_transndt = False
try:
    eptranslate.load("translations.toml")
except:
    try:
        eptranslate.load(APPDATADIR+"/translations.toml")
    except:
        print("WARN: Can't find translations file.")
        _transndt = True

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

def assemble_package_file_path(serverdir:str):
    return TEMPDIR+"/packages-spigot-"+serverdir.replace("\\","/").split("/")[-1]+".json"

def is_uuidindex_loaded():
    return len(appdata.UUID_INDEX) != 0

def get_name_from_uuid(uuid:str) -> str:
    if uuid in appdata.UUID_INDEX:
        if uuid is None:
            return uuid#Failed all attemps. I know it's a bad idea to be using this both internally and from the user side, but I am a bad developer
        return appdata.UUID_INDEX[uuid]
    else:
        r = requests.get("https://api.minetools.eu/uuid/"+uuid)
        try:
            name = r.json()["name"]
            appdata.UUID_INDEX[uuid] = name
            sleep(1)#Prevent crash from rate spamming
            return name
        except:
            return uuid#If all fails, just return to sender

def extract_links_from_page(data: str) -> list[str]:
    dl = data.split("href=")
    final = []
    for dm in dl[1:]:
        final.append(dm.split("\"")[1])
    return final

class ServerRunWrapper:
    process:typing.Any
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
    def getexitcode(self) -> None|int:
        if not self.isprocessrunning() :
            return self.process.returncode
        else:
            return None
    def hascrashed(self):
        code = self.getexitcode()
        if code is None:
            return None
        else:
            if code != 0:
                if code < 128 or code > 130:
                    return True
                else:
                    return False
            else:
                return False

SERVER_INITS:dict[str,ServerRunWrapper] = {}

def package_server_script(indir:str,outfile:str) -> int:
    try:
        dirstack.pushd(indir)
        with tarfile.open(outfile,"w:xz") as tar:
            tar.add(".")
        dirstack.popd()
    except:
        return 1
    return 0

def unpackage_server(infile:str,outdir:str) -> int:
    try:
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        dirstack.pushd(outdir)
        with tarfile.open(infile,"r:xz") as tar:
            tar.extractall(".")
        dirstack.popd()
    except:
        return 1
    return 0

### END UTILS

def safe_exit(code):
    appdata.updateappdata()
    for server in list(SERVER_INITS.values()):
        server.safestop()
    sys.exit(code)

def send_telemetry():
    pass#This feature has been disabled

def parse_size(data: int) -> str:
    result:str = ""
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
            if ON_WINDOWS:
                cursesplus.messagebox.showerror(_SCREEN,["This feature is not yet available on Windows"])
                continue
            if cursesplus.messagebox.askyesno(_SCREEN,["Do you want to update the most recent App data?","If you suspect your appdata is corrupt, do not say yes"]):
                appdata.updateappdata()
            _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLACK,cursesplus.WHITE))
            main(_SCREEN)
        elif erz == 3:
            while True:
                aerz = cursesplus.optionmenu(_SCREEN,["Back","Repair CraftServerSetup","Reset CraftServerSetup"],"Please choose an advanced option")
                if aerz == 0:
                    break
                elif aerz == 1:
                    if ON_WINDOWS:
                        cursesplus.messagebox.showerror(_SCREEN,["This feature is not available on Windows"])
                        continue
                    if cursesplus.messagebox.askyesno(_SCREEN,["This will re-install CraftServerSetup and restore any lost files.","You will need to have a release downloaded"]):
                        flz = cursesplus.filedialog.openfiledialog(_SCREEN,"Please choose the release file",[["*.xz","crss XZ Release"],["*","All files"]]) # type: ignore
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
        
def get_java_version(file="java") -> str:
    try:
        if not ON_WINDOWS:
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
        dop = uicomponents.menu(stdscr,["ADD PLAYER","FINISH"]+[p["name"] for p in dat],"Choose a player to remove or choose bolded options")
        if dop == 1:
            with open(whitefile,"w+") as f:
                f.write(json.dumps(dat))
            return
        elif dop == 0:
            cursesplus.utils.showcursor()
            name = uicomponents.crssinput(stdscr,"Name(s) of players allowed: (Seperate with commas)")
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

def trail(ind,maxlen:int):
    if maxlen < 1:
        return ""
    ind = str(ind)
    if len(ind) > maxlen:
        return ind[0:maxlen-4]+"..."
    else:
        return ind

def package_server(stdscr,serverdir:str,chosenserver:int):
    sdata = appdata.APPDATA["servers"][chosenserver]
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

def download_vanilla_software(stdscr,serverdir) -> dict|None:
    cursesplus.displaymsg(stdscr,["Getting version information"],False)
    VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
    stdscr.clear()
    stdscr.erase()
    downloadversion = uicomponents.menu(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
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
            xver = uicomponents.crssinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
            curses.curs_set(0)
        else:
            xver = "latest"
        PACKAGEDATA = {"id":xver}
        mx = os.get_terminal_size()[0]-4
        proc = subprocess.Popen([javapath,"-jar","BuildTools.jar","--rev",xver],shell=False,stdout=subprocess.PIPE)
        tick = 0
        while True:
            if proc.stdout is None:
                continue
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
    pxver = list(reversed(VMAN["versions"]))[uicomponents.menu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
    BMAN = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds").json()
    buildslist = list(reversed(BMAN["builds"]))
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to install the latest build of Paper","It is highly recommended to do so"]):
        builddat = buildslist[0]
    else:
        stdscr.erase()
        builddat = buildslist[uicomponents.menu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
    bdownload = f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'
    #cursesplus.displaymsg(stdscr,[f'https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'])
    cursesplus.displaymsg(stdscr,["Downloading server file"],False)
    
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id":VMAN["versions"][VMAN["versions"].index(pxver)]}
    return PACKAGEDATA

def download_purpur_software(stdscr,serverdir) -> dict:
    verlist = list(reversed(requests.get("https://api.purpurmc.org/v2/purpur").json()["versions"]))
    verdn = verlist[uicomponents.menu(stdscr,verlist,"Choose a version")]
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to install the latest build?","This is highly recommended"]):
        bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/latest/download"
    else:
        dz = list(reversed(requests.get(f"https://api.purpurmc.org/v2/purpur/{verdn}").json()["builds"]["all"]))
        builddn = uicomponents.menu(stdscr,dz)
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

def list_recursive_contains_inverse(s:str,searches:list[str]) -> bool:
    for sr in searches:
        if sr in s:
            return True
    return False

def get_by_list_contains(lst: list,item:str):
    return lst[list_recursive_contains(lst,item)]

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
        pdata = propertiesfiles.load(r)
        with open(allowfile) as f:
            data:list = json.load(f)
        while True:
            wtd = uicomponents.menu(stdscr,["FINISH","Add new player",f"{uf_toggle_conv(pdata['allow-list'])} Allowlist"]+["[-] "+d["name"] for d in data],"Managing allowlist",footer="Add a player or delete an existing player from the allowlist.")
            if wtd == 0:
                break
            elif wtd == 1:
                plname = uicomponents.crssinput(stdscr,"What is the player's Xbox/Minecraft username?")
                plxuid = uicomponents.crssinput(stdscr,"If you know it, what is the user's XUID? (Press enter if unknown)")
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
            f.write(propertiesfiles.dump(pdata))

def bedrock_world_settings(stdscr,serverdir:str,data:dict) -> dict:

    while True:
        availableworlds = bedrock_enum_worlds(serverdir)
        op = uicomponents.menu(stdscr,["FINISH","Create New World"]+[a.name for a in availableworlds],footer="Choose a world to select or delete, or create a world",title=f"Current world: {data['level-name']}")
        if op == 0:
            break
        elif op == 1:
            levelname = uicomponents.crssinput(stdscr,"Choose a name for the world")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to choose a custom seed?","If you answer no, a random seed will be chosen."],default=cursesplus.messagebox.MessageBoxStates.NO):
                newseed = uicomponents.crssinput(stdscr,"Choose a seed")
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
        wtd = uicomponents.menu(stdscr,["FINISH","Basic options","World settings","Advanced options"])
        if wtd == 0:
            return data
        elif wtd == 1:
            data["server-name"] = uicomponents.crssinput(stdscr,"What is the public name of the server?")
            data["gamemode"] = ["survival","creative","adventure"][uicomponents.menu(stdscr,["Survival","Creative","Adventure"],"Choose gamemode for server")]
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
            data["default-player-permission-level"] = ["visitor","member","operator"][uicomponents.menu(stdscr,["Visitor (very limited access)","Member (Normal player)","Operator (Admin)"],"Select default permissions")]
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
            data["compression-algorithm"] = ["zlib","snappy"][uicomponents.menu(stdscr,["zlib","snappy"],"Choose compression algorith")]
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
    return options[uicomponents.menu(stdscr,options,header)].split(" - ")[0]

def bedrock_config_server(stdscr,chosenserver):
    __l = uicomponents.menu(stdscr,["Cancel","Modify server.properties","Modify CRSS Server options","Reset server configuration","Rename Server","Startup Options"])#Todo rename server, memory
    if __l == 0:
        return
    elif __l == 1:
        if not os.path.isfile("server.properties"):
            cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
        else:
            with open("server.properties") as f:
                config = propertiesfiles.load(f.read())

            config = cursesplus.dictedit(stdscr,config,"Editing Server Properties",True)
            with open("server.properties","w+") as f:
                f.write(propertiesfiles.dump(config))
    elif __l == 2:
        dt = appdata.APPDATA["servers"][chosenserver-1]
        dt = cursesplus.dictedit(stdscr,dt,"More Server Properties")
        appdata.APPDATA["servers"][chosenserver-1] = dt
        appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 3:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to reset your server configuration","You won't delete any worlds"]):
            os.remove("server.properties")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up some more server configuration"]):
                sd = setup_server_properties(stdscr)
                with open("server.properties","w+") as f:
                    f.write(propertiesfiles.dump(sd))
    elif __l == 4:
        newname = uicomponents.crssinput(stdscr,"Choose a new name for this server")
        appdata.APPDATA["servers"][chosenserver-1]["name"] = newname
        #appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 5:
        appdata.APPDATA["servers"][chosenserver-1] = startup_options(stdscr,appdata.APPDATA["servers"][chosenserver-1])

def setup_bedrock_server(stdscr):
    while True:
        servername = uicomponents.crssinput(stdscr,"Please choose a name for your server").strip()
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
    dlinfo = bedrocklinks.ui_download_bedrock_software(stdscr,p,S_INSTALL_DIR)
    
    l2d:str = dlinfo[0]

    sd = {
        "name" : servername,
        "javapath" : "",
        "memory" : "",
        "dir" : S_INSTALL_DIR,
        "version" : l2d.split("-")[-1].replace(".zip",""),
        "moddable" : False,
        "software" : 5,
        "id" : random.randint(1111,9999),
        "settings": {
            "launchcommands": [],
            "exitcommands": [],
            "safeexitcommands": []
        },
        "script" : S_INSTALL_DIR+"/bedrock_server",
        "linkused" : l2d,
        "ispreview" : dlinfo[1]
    }
    try:
        shutil.copyfile(ASSETSDIR+"/defaulticon.png",S_INSTALL_DIR+"/server-icon.png")
    except:
        pass
    sd["script"] = generate_script(sd)
    appdata.APPDATA["servers"].append(sd)
    appdata.updateappdata()
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to configure your server's settings now?"]):
        with open(S_INSTALL_DIR+"/server.properties","w+") as f:
            f.write(propertiesfiles.dump(configure_bedrock_server(stdscr,S_INSTALL_DIR,propertiesfiles.load(BEDROCK_DEFAULT_SERVER_PROPERTIES))))
    dirstack.popd()
    p.done()
    bedrock_manage_server(stdscr,servername,appdata.APPDATA["servers"].index(sd)+1)

def bedrock_do_update(stdscr,chosenserver,availablelinks):
    l2d = bedrocklinks.get_links()[uicomponents.menu(stdscr,["Latest Version","Latest Preview Version"],"Please select a version")]
    #Remember: Don't overwrite server.properties or allowlist.json
    p = cursesplus.ProgressBar(stdscr,5)
    cursesplus.displaymsg(stdscr,["Updating server","Please be patient."],False)
    p.step("Making backup")
    safetydir = tempdir.generate_temp_dir()
    safefiles = ["server.properties","allowlist.json"]
    safemap = {}
    for sf in safefiles:
        if not os.path.isfile(sf):
            continue
        shutil.copyfile(sf,safetydir+"/"+file_get_md5(sf))
        safemap[sf] = file_get_md5(sf)
    S_INSTALL_DIR = appdata.APPDATA["servers"][chosenserver-1]["dir"]
    p.step("Downloading new server")
    #p.step("Downloading server file")
    urllib.request.urlretrieve(l2d,S_INSTALL_DIR+"/server.zip")
    #p.step("Extracting server file")
    dirstack.pushd(S_INSTALL_DIR)#Make install easier
    p.step("Extracting new server")
    zf = zipfile.ZipFile(S_INSTALL_DIR+"/server.zip")
    zf.extractall(S_INSTALL_DIR)
    zf.close()
    #p.step("Removing excess files")
    os.remove(S_INSTALL_DIR+"/server.zip")
    #p.step("Preparing exec")
    if not ON_WINDOWS:
        os.chmod(S_INSTALL_DIR+"/bedrock_server",0o777)
    p.step("Restoring properties")
    appdata.APPDATA["servers"][chosenserver-1]["ispreview"] = l2d == availablelinks[1]
    appdata.APPDATA["servers"][chosenserver-1]["version"] = l2d.split("-")[-1].replace(".zip","")
    appdata.APPDATA["servers"][chosenserver-1]["linkused"] = l2d
    for sf in safefiles:
        try:
            if os.path.isfile(sf):
                os.remove(sf)
            shutil.copyfile(safetydir+"/"+safemap[sf],sf)
        except:
            pass
    p.done()
    appdata.updateappdata()

def bedrock_manage_server(stdscr,servername,chosenserver):
    curver = appdata.APPDATA["servers"][chosenserver-1]["linkused"]
    cursesplus.displaymsg(stdscr,["Checking for Bedrock updates"],False)
    
    availablelinks = bedrocklinks.get_links()
    
    if appdata.APPDATA["servers"][chosenserver-1]["ispreview"]:
        sel = 1
    else:
        sel = 0
        
    latestlink = availablelinks[sel]
    #cursesplus.messagebox.showinfo(stdscr,[latestlink,curver])
    if curver != latestlink:
        if cursesplus.messagebox.askyesno(stdscr,["A bedrock update has been detected.","If you don't install it, devices can't connect.","Do you want to install this update?"]):
            bedrock_do_update(stdscr,chosenserver,availablelinks)
            
    svrd = appdata.APPDATA["servers"][chosenserver-1]["dir"]       
    while True:
        wtd = uicomponents.menu(stdscr,["RETURN TO MAIN MENU","Start Server","Server Settings","Delete Server","Configure Allowlist","Export Server","World Settings","Re/change install","FILE MANAGER"],f"Managing {servername}")
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
                    del appdata.APPDATA["servers"][chosenserver-1]
                    cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                    stdscr.clear()
                    break
            stdscr.erase()
        elif wtd == 8:
            file_manager(stdscr,appdata.APPDATA["servers"][chosenserver-1]["dir"],f"Managing files for {servername}")
        elif wtd == 7:
            bedrock_do_update(stdscr,chosenserver,availablelinks)
        elif wtd == 6:
            try:
                with open(svrd+"/server.properties") as f:
                    r = f.read()
                data = propertiesfiles.load(r)
                data = bedrock_world_settings(stdscr,svrd,data)
                with open(svrd+"/server.properties","w+") as f:
                    f.write(propertiesfiles.dump(data))
            except Exception as e:
                cursesplus.messagebox.showerror(stdscr,["There was an error managing worlds.",str(e),"A world may be corrupt."])
        elif wtd == 5:
            package_server(stdscr,svrd,chosenserver-1)
        elif wtd == 4:
            bedrock_whitelist(stdscr,svrd)
        elif wtd == 1:
            while True:
                os.system(";".join(appdata.APPDATA["servers"][chosenserver-1]["settings"]["launchcommands"]))
                os.chdir(appdata.APPDATA["servers"][chosenserver-1]["dir"])           
                stdscr.clear()
                stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}\n\r")
                stdscr.refresh()
                if not ON_WINDOWS:
                    curses.curs_set(1)
                    curses.reset_shell_mode()
                    lretr = os.system(appdata.APPDATA["servers"][chosenserver-1]["script"])
                    #child = pexpect.spawn(appdata.APPDATA["servers"][chosenserver-1]["script"])
                    #child.expect("Finished")
                    curses.reset_prog_mode()
                    curses.curs_set(0)
                else:
                    curses.curs_set(1)
                    curses.reset_shell_mode()
                    #COLOURS_ACTIVE = False
                    lretr = os.system("cmd /c ("+appdata.APPDATA["servers"][chosenserver-1]["script"]+")")
                    curses.reset_prog_mode()
                    curses.curs_set(0)
                    #restart_colour()
                os.system(";".join(appdata.APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
                hascrashed = lretr != 0 and lretr != 127 and lretr != 128 and lretr != 130
                willgoagain = False
                #Handle autorestart
                recommended_action = autorestart.get_recommended_action(appdata.APPDATA["servers"][chosenserver-1],True)
                match recommended_action:
                    case autorestart.AutoRestartOptions.ALWAYS:
                        willgoagain = True
                    case autorestart.AutoRestartOptions.SAFEEXIT:
                        if not hascrashed:
                            willgoagain = True
                    
                if willgoagain:
                    execagain = timedexec.timeout_askyesno(stdscr,["Unless you interrupt by saying no","This server will auto-restart when","the timer runs out"],True,appdata.get_setting_value("autorestarttimeout"))
                    if execagain:
                        continue

                if hascrashed:
                    cursesplus.messagebox.showwarning(stdscr,["Oh no!","Your server has crashed."])

                stdscr.clear()
                stdscr.refresh()
                break

def choose_server_name(stdscr) -> str:
    """Prompt the user to create new name, not allowing duplicates found in SERVERSDIR"""
    while True:
        curses.curs_set(1)
        servername = uicomponents.crssinput(stdscr,"Please choose a name for your server").strip()
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
    return servername

def setup_proxy_server(stdscr):
    cursesplus.messagebox.showerror(stdscr,["Not Yet Implemented"])
    if not cursesplus.messagebox.askokcancel(stdscr,["Proxy servers are DIFFERENT from normal servers!","A proxy server connects to existing normal servers to distribute them.","Proxy servers are more difficult to configure.","Be sure you know what server type you are making"]):
        return
    
    proxytype = uicomponents.menu(stdscr,["Cancel","Bungeecord (by spigot)"])
    if proxytype == 0:
        return
    else:
        servername = choose_server_name(stdscr)
        S_INSTALL_DIR = SERVERSDIR+"/"+servername
        cursesplus.displaymsg(stdscr,["Please wait while your server is set up"],False)
        urllib.request.urlretrieve(BUNGEECORD_DOWNLOAD_URL,S_INSTALL_DIR+"/server.jar")
        njavapath = choose_java_install(stdscr)
        

def setupnewserver(stdscr):
    stdscr.erase()
    
    wtd = uicomponents.menu(stdscr,["Cancel","Create a new server","Import a server from this computer"],"What would you like to do?")
    if wtd == 0:
        return
    elif wtd == 2:
        import_server(stdscr)
        return
    bigserverblock = uicomponents.menu(stdscr,["Cancel","Java (Computer, PC)","Bedrock (Console, Tablet, etc)","Java Proxy"],"Choose Minecraft kind to install")
    if bigserverblock == 0:
        return
    elif bigserverblock == 2:
        setup_bedrock_server(stdscr)
        return
    elif bigserverblock == 3:
        setup_proxy_server(stdscr)
        return
        
    while True:
        
        serversoftware = uicomponents.menu(stdscr,["Cancel","Help me choose","Vanilla","Spigot","Paper","Purpur"],"Please choose your server software")
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
    servername = choose_server_name(stdscr)
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
    sd = {
        "name":servername,
        "javapath":njavapath,
        "memory":memorytoall,
        "dir":S_INSTALL_DIR,
        "version":PACKAGEDATA["id"],
        "moddable":serversoftware!=1,
        "software":serversoftware,
        "id":serverid,
        "settings":{
            "legacy":True,
            "launchcommands":[],
            "exitcommands":[],
            "flags" : "",
            "restartsource" : 0,
            "autorestart" : 0
        }
        }
    #_space = "\\ "
    #__SCRIPT__ = f"{njavapath.replace(' ',_space)} -jar -Xms{memorytoall} -Xmx{memorytoall} \"{S_INSTALL_DIR}/server.jar\" nogui"
    __SCRIPT__ = generate_script(sd)
    sd["script"] = __SCRIPT__
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to enable automatic restarts?"]):
        sd["settings"]["restartsource"] = 1#Allow file, but fall through to CRSS
        sd["settings"]["autorestart"] = 1#Only auto restart if the server has not crashed
        cursesplus.messagebox.showinfo(stdscr,["You may change this at any time by going to","Advanced configuration -> Startup Options -> Autorestart options"])

    appdata.APPDATA["servers"].append(sd)
    appdata.updateappdata()
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
            f.write(propertiesfiles.dump(data))

    try:
        shutil.copyfile(ASSETSDIR+"/defaulticon.png",S_INSTALL_DIR+"/server-icon.png")
    except:
        pass
    os.chdir(bdir)
    manage_server(stdscr,S_INSTALL_DIR,appdata.APPDATA["servers"].index(sd)+1)

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
        dpp["level-name"] = uicomponents.crssinput(stdscr,"What should your world be called")
        if os.path.isdir(serverdir+"/"+dpp["level-name"]):
            if cursesplus.messagebox.showwarning(stdscr,["This world may already exist.","Are you sure you want to edit its settings?"]):
                break
        else:
            break
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to use a custom seed?","Answer no for a random seed"]):
        dpp["level-seed"] = uicomponents.crssinput(stdscr,"What should the seed be?")
    wtype = uicomponents.menu(stdscr,["Normal","Flat","Large Biome","Amplified","Single Biome","Buffet (1.15 and before)","Customized (1.12 and before)","Other (custom namespace)"],"Please choose the type of world.")
    if wtype == 7:
        wname = uicomponents.crssinput(stdscr,"Please type the full name of the custom world type")
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
               dpp["generator-settings"] = uicomponents.crssinput(stdscr,f"Please type generator settings for {wname}") 
        else:
            dpp["generator-settings"] = uicomponents.crssinput(stdscr,f"Please type generator settings for {wname}")

    if not initialconfig:
        #Provide more settings
        #dpp["allow-flight"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable flight for non-admins on this world?"])
        #dpp["allow-nether"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable the nether on this world?"])
        #dpp["generate-structures"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable structure generation on this world?"])
        #dpp["hardcore"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable hardcore mode on this world?"])
        dpp["difficulty"] = str(uicomponents.menu(stdscr,["Peaceful","Easy","Normal","Hard"],"Please select the difficulty of your world"))
        dpp["gamemode"] = str(uicomponents.menu(stdscr,["survival","creative","adventure","spectator"],"Please select the gamemode of this world"))
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
def setup_server_properties(stdscr,data=propertiesfiles.load(DEFAULT_SERVER_PROPERTIES)) -> dict:
    dpp = data
    cursesplus.utils.showcursor()
    while True:
        lssl = uicomponents.menu(stdscr,["Basic Settings","World Settings","Advanced Settings","Network Settings","FINISH","Setup Resource pack"],"Server Configuration Setup")
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
                dpp["rcon.password"] = uicomponents.crssinput(stdscr,"Please input RCON password",passwordchar="*")
                dpp["rcon.port"] = cursesplus.numericinput(stdscr,"Please input the RCON port: (default 25575)",False,False,1,65535,25575)

        elif lssl == 2:
            #Advanced settings
            dpp["broadcast-console-to-ops"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable verbose output to operators?"])
            dpp["entity-broadcast-range-percentage"] = cursesplus.numericinput(stdscr,"What distance percentage should entities be sent to the client?",minimum=10,maximum=1000,prefillnumber=100)
            #dpp["enforce-secure-profile"] = not cursesplus.messagebox.askyesno(stdscr,["Do you want to allow cracked accounts to join?"])
            seclevel = uicomponents.menu(stdscr,["Maximum (reccommended) - Secure profile and valid account","Moderate - Valid account, secure profile not required","Minimum - Cracked / illegal accounts permitted"],"Please choose a security option")
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
            dpp["function-permission-level"] = uicomponents.menu(stdscr,["1 (Bypass spawn protection)","2 (Singleplayer commands)","3 (Player management (ban/kick))","4 (Manage server)"],"Please choose the default op admin level") + 1
            dpp["max-chained-neighbor-updates"] = cursesplus.numericinput(stdscr,"Please input maximum chained neighboue updates",allownegatives=True,minimum=-1,prefillnumber=1000000)
            dpp["max-tick-time"] = cursesplus.numericinput(stdscr,"How many milliseconds should watchdog wait?",False,True,-1,2**32,60000)
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to enable anti-afk?"]):
                dpp["player-idle-timeout"] = cursesplus.numericinput(stdscr,"Minutes of AFK before player is kicked:",False,False,0,1000000)
            else:
                dpp["player-idle-timeout"] = 0
            dpp["accept-transfers"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to allow people to automatically transfer to this server?"])
            dpp["region-file-compression"] = ["deflate","lz4","none"][uicomponents.menu(
                stdscr,
                ["Deflate (old algorithm, small size, high cpu)","LZ4 (more space, low cpu)","No compression (slow, huge space, no cpu)"],
                "What compression should the world files use?"
            )]
            
        elif lssl == 0:
            #basic
            dpp["difficulty"] = str(uicomponents.menu(stdscr,["Peaceful","Easy","Normal","Hard"],"Please select the difficulty of your server"))
            dpp["gamemode"] = str(uicomponents.menu(stdscr,["survival","creative","adventure","spectator"],"Please select the gamemode of your server"))
            #dpp["enable-command-block"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable command blocks on your server?"])
            dpp["max-players"] = cursesplus.numericinput(stdscr,"How many players should be allowed? (max players)",minimum=1,maximum=1000000,prefillnumber=20)
            dpp["motd"] = "\\n".join(uicomponents.crssinput(stdscr,"What should your server message say?",2,59).splitlines())
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
        z = uicomponents.menu(stdscr,["Done","Set Resource pack URL","Change resource pack settings","Disable resource pack"])
        if z == 0:
            return dpp
        elif z == 1:
            uurl = uicomponents.crssinput(stdscr,"Input the URI to your resource pack (Direct download link)")
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
    
    dirstack.pushd(SERVERSDIR)
    appdata.APPDATA["servers"] = [a for a in appdata.APPDATA["servers"] if os.path.isdir(a["dir"])]
    #Look for unregistered directories
    dirstack.popd()
    appdata.updateappdata()

def servermgrmenu(stdscr):
    prune_servers()
    stdscr.clear()
    
    chosenserver = uicomponents.menu(stdscr,["Back"]+[a["name"] for a in appdata.APPDATA["servers"]],"Please choose a server")
    if chosenserver == 0:
        return
    else:
        _sname = [a["dir"] for a in appdata.APPDATA["servers"]][chosenserver-1]
        if os.path.isdir(_sname):
            manage_server(stdscr,_sname,chosenserver)
            appdata.updateappdata()

        else:
            cursesplus.messagebox.showerror(stdscr,["This server does not exist"])
            
            del appdata.APPDATA["servers"][chosenserver-1]#Unregister bad server
            appdata.updateappdata()

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
        modch = uicomponents.menu(stdscr,["Cancel","Leniency Settings","Help I can't find what I'm looking for"]+[ikl["title"] for ikl in inres],f"Search results for {searchq}")
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
                mocho = uicomponents.menu(stdscr,["Cancel","Plugin Info","Download"])
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
                    filed = uicomponents.menu(stdscr,["Cancel"]+final,"Please choose a version to download")
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
        wtd = uicomponents.menu(stdscr,["FINISH","Search for plugins","View most popular plugins"])
        if wtd == 0:
            break
        elif wtd == 1:
            searchq = uicomponents.crssinput(stdscr,"What is the name of the mod you are looking for?")
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

def clean_file_name(name:str) -> str:
    ALLOWED_CHARACTERS = list("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-")
    fn_name = ""
    for ch in name:
        if ch in ALLOWED_CHARACTERS:
            fn_name += ch

    return fn_name

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
        #wtd = uicomponents.menu(stdscr,["FINISH","New Search"]+[chop_str_with_limit(z["name"],40) for z in display],f"Searching for {activesearch} from Spigot")
        wtd = cursesplus.searchable_option_menu(stdscr,[d["name"] for d in display],"Choose a plugin",["Finish"])
        if wtd == 0:
            break
        else:
            chosenplugin = display[wtd-1]
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
                    urllib.request.urlretrieve(f"https://api.spiget.org/v2/{dloc}",modfolder+"/"+clean_file_name(pldat["name"])+".jar")
                except:
                    cursesplus.messagebox.showerror(stdscr,["There was an error downloading","the plugin. You may have to download it manually."])
    
def svr_mod_mgr(stdscr,SERVERDIRECTORY: str,serverversion,servertype):
    modsforlder = SERVERDIRECTORY + "/plugins"
    if not os.path.isdir(modsforlder):
        os.mkdir(modsforlder)
    while True:
        PLUGSLIST = retr_jplug(modsforlder)
        spldi = uicomponents.menu(stdscr,["BACK","ADD PLUGIN"]+[f["name"]+" (v"+f["version"]+")" for f in PLUGSLIST],"Choose a plugin to manage")
        if spldi == 0:
            return
        elif spldi == 1:
            #add mod
            minstype = uicomponents.menu(stdscr,["Back","Install from file on this computer","Download from Modrinth","Download from Spigot"])
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
                wtd = uicomponents.menu(stdscr,["BACK","View Plugin Info","Delete Plugin","Reset Plugin","Edit config.yml"])
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
                        data = cursesplus.dictedit(stdscr,data,f"{activeplug['name']} config")
                        with open(ef,"w+") as f:
                            f.write(yaml.dump(data,default_flow_style=False))

                    else:
                        cursesplus.messagebox.showerror(stdscr,["This plugin does not have a config file"])

def generate_script(svrdict: dict) -> str:
    if svrdict["software"] == 5:
        if ON_WINDOWS:
            __SCRIPT__ = svrdict["dir"]+"/bedrock_server.exe"
        else:
            __SCRIPT__ = svrdict["dir"]+"/bedrock_server"
    else:
        _space = "\\ "
        _bs = "\\"
        if not ON_WINDOWS:
            __SCRIPT__ = f"{svrdict['javapath'].replace(' ',_space)} -jar -Xms{svrdict['memory']} -Xmx{svrdict['memory']} {svrdict['settings']['flags']} \"{svrdict['dir']}/server.jar\" nogui"
        else:
            __SCRIPT__ = f"\"{svrdict['javapath']}\" -jar -Xms{svrdict['memory']} -Xmx{svrdict['memory']} {svrdict['settings']['flags']} \"{svrdict['dir'].replace(_bs,'/')}/server.jar\" nogui"
    return __SCRIPT__

def update_s_software_preinit(serverdir:str):
    dirstack.pushd(serverdir)

def rm_server_jar():
    if os.path.isfile("server.jar"):
        os.remove("server.jar")

def update_s_software_postinit(PACKAGEDATA:dict,chosenserver:int):
    appdata.APPDATA["servers"][chosenserver-1]["version"] = PACKAGEDATA["id"]#Update new version
    generate_script(appdata.APPDATA["servers"][chosenserver-1])
    appdata.updateappdata()
    dirstack.popd()

def update_vanilla_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit(serverdir)
    stdscr.erase()
    VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
    downloadversion = uicomponents.menu(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
    if downloadversion == 0:
        return
    else:
        stdscr.clear()
        cursesplus.displaymsg(stdscr,["Getting version manifest..."],False)
        PACKAGEDATA = requests.get(VERSION_MANIFEST_DATA["versions"][downloadversion-1]["url"]).json()
        cursesplus.displaymsg(stdscr,["Preparing new server"],False)
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to change the java installation","associated with this server?"]):
        njavapath = choose_java_install(stdscr)
        appdata.APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
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
        appdata.APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
    p = cursesplus.ProgressBar(stdscr,2,cursesplus.ProgressBarTypes.FullScreenProgressBar,show_log=True,show_percent=True,message="Updating spigot")
    p.update()
    rm_server_jar()
    urllib.request.urlretrieve("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar","BuildTools.jar")
    p.step()
    while True:
        build_lver = cursesplus.messagebox.askyesno(stdscr,["Do you want to build the latest version of Spigot?","YES: Latest version","NO: different version"])
        if not build_lver:
            curses.curs_set(1)
            xver = uicomponents.crssinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
            curses.curs_set(0)
        else:
            xver = "latest"
        PACKAGEDATA = {"id":xver}
        proc = subprocess.Popen([appdata.APPDATA["servers"][chosenserver-1]["javapath"],"-jar","BuildTools.jar","--rev",xver],shell=False,stdout=subprocess.PIPE)
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
    pxver = list(reversed(VMAN["versions"]))[uicomponents.menu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
    BMAN = requests.get(f"https://api.papermc.io/v2/projects/paper/versions/{pxver}/builds").json()
    buildslist = list(reversed(BMAN["builds"]))
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to update to the latest build of Paper","It is highly recommended to do so"]):
        builddat = buildslist[0]
    else:
        stdscr.erase()
        builddat = buildslist[uicomponents.menu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
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
    verdn = verlist[uicomponents.menu(stdscr,verlist,"Choose a version")]
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to install the latest build?","This is highly recommended"]):
        bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/latest/download"
    else:
        dz = list(reversed(requests.get(f"https://api.purpurmc.org/v2/purpur/{verdn}").json()["builds"]["all"]))
        builddn = uicomponents.menu(stdscr,dz)
        bdownload = bdownload = f"https://api.purpurmc.org/v2/purpur/{verdn}/{dz[builddn]}/download"
    cursesplus.displaymsg(stdscr,["Downloading file..."],False)
    rm_server_jar()
    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id" : verlist[verlist.index(verdn)]}
    update_s_software_postinit(PACKAGEDATA,chosenserver)

class CommandExecution:
    issuer:str
    when:datetime.datetime
    commandstr: str
    def __init__(self,i,w,c):
        self.issuer = i
        self.when = w
        self.commandstr = c
    def fromraw(line:logutils.LogEntry):
        selsection = re.findall(r"[a-zA-Z0-9_]+\sissued server command: .*",line.data)[0]
        i = selsection.split(" ")[0]
        w = line.get_full_log_time()
        c = selsection.split("issued server command")[1][2:]
        return CommandExecution(i,w,c)
    def __str__(self):
        return f"{self.when} {self.issuer}{' '*(16-len(self.issuer))} {self.commandstr}"
    
def is_logentry_a_command(l:logutils.LogEntry) -> bool:
    return len(re.findall(r"[a-zA-Z0-9_]+\sissued server command: .*",l.data)) > 0

def recursive_list_startswith(searcher:str,items:list[str]) -> bool:
    for s in items:
        if s in searcher:
            return True
    return False

def command_execution_auditing(stdscr,serverdir:str):
    if resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    
    orderedlogs = logutils.load_server_logs(stdscr,serverdir)
    finalcmds:list[CommandExecution] = []
    cursesplus.displaymsg(stdscr,["Finding Commands"],False)
    for entry in orderedlogs:
        if is_logentry_a_command(entry):
            finalcmds.append(CommandExecution.fromraw(entry))
            
    while True:
        wtd = uicomponents.menu(stdscr,["BACK","View Command History","Commands by Player","Commands by Text","Find command discrepancies","Graph by Player","Graph by command","Player command profile"])
        match wtd:
            case 0:
                break
            case 1:
                cursesplus.textview(stdscr,text="\n".join([str(s) for s in finalcmds]),message="Every command ever executed")
            case 2:
                whatplayer = uicomponents.crssinput(stdscr,"What player do you want to audit?")
                cursesplus.textview(stdscr,text="\n".join(
                    list(itertools.chain.from_iterable([[str(s) for s in finalcmds if whatplayer_indiv in s.issuer.lower()] for whatplayer_indiv in renaminghandler.get_aliases_of(whatplayer)]))),message=f"Commands from {whatplayer}")
            case 3:
                whatplayer = uicomponents.crssinput(stdscr,"What commands do you want to find?")
                cursesplus.textview(stdscr,text="\n".join([str(s) for s in finalcmds if whatplayer in s.commandstr]),message=f"Commands including {whatplayer}")
            case 4:
                cursesplus.messagebox.showinfo(stdscr,["This will show when","Players have been running commands","on other players."])
                cursesplus.displaymsg(stdscr,["searching"],False)
                abusable_prefixes = ["/give","/gamemode","/tp","/teleport"]
                excluder_prefixes = ["/tpa","/tpr","/msg","/w","/tpc"]
                other_players = remove_duplicates_from_list([s.issuer for s in finalcmds])
                final = ""
                for cmd in finalcmds:
                    if recursive_list_startswith(cmd.commandstr,abusable_prefixes) and not recursive_list_startswith(cmd.commandstr,excluder_prefixes):
                        other_players.remove(cmd.issuer)
                        if list_recursive_contains_inverse(cmd.commandstr,other_players):
                            final += str(cmd) + "\n"
                        other_players.append(cmd.issuer)
                
                cursesplus.textview(stdscr,text=final,message="Potential Command Abuse")
                
            case 5:
                dat = {}
                for entry in finalcmds:
                    if entry.issuer in dat:
                        dat[entry.issuer] += 1
                    else:
                        dat[entry.issuer] = 1
                        
                cursesplus.bargraph(stdscr,dat,"Commands issued by player","commands")
            case 6:
                dat = {}
                for entry in finalcmds:
                    commandhead = entry.commandstr.split(" ")[0]
                    if commandhead in dat:
                        dat[commandhead] += 1
                    else:
                        dat[commandhead] = 1
                        
                cursesplus.bargraph(stdscr,dat,"Commands issued by type","times")
                
            case 7:
                forwhichplayer = uicomponents.crssinput(stdscr,"Player name?")
                commands = {}
                totalcommands = 0
                for cmd in finalcmds:
                    if cmd.issuer.lower() == forwhichplayer.lower():
                        chead = cmd.commandstr.split(" ")[0]
                        if chead in commands:
                            commands[chead] += 1
                        else:
                            commands[chead] = 1
                        totalcommands += 1
                
                final = f"You have run {totalcommands} commands\n\n"
                for cset in sorted(list(commands.items()),key=lambda x:x[1],reverse=True):
                    final += f"{cset[0]} - {cset[1]} times ({round(cset[1]/totalcommands*100,2)}%)\n"
                cursesplus.textview(stdscr,text=final)
                
def view_server_logs(stdscr,server_dir:str):
    logsdir = server_dir+"/logs"
    
    if not os.path.isdir(logsdir):
        cursesplus.messagebox.showwarning(stdscr,["This server has no logs."])
        return
    dirstack.pushd(logsdir)
    
    while True:
        wtd = uicomponents.menu(stdscr,["BACK","View whole log history","View by file","Chat History & Utilities","Command Execution Audits"])
        if wtd == 0:
            dirstack.popd()
            return
        elif wtd == 1:
            logs = logutils.load_server_logs(stdscr,server_dir)
            
            finaltext = ""
            for entry in logs:
                finaltext += f"{entry.logdate} {entry.data}\n"
            cursesplus.textview(stdscr,text=finaltext,message="Every Log Ever")
        elif wtd == 2:
            while True:
                availablelogs = list(reversed(sorted([l for l in os.listdir(logsdir) if os.path.isfile(l)])))
                chosenlog = uicomponents.menu(stdscr,["BACK"]+availablelogs,"Please choose a log to view")
                if chosenlog == 0:
                    break
                else:
                    cl = availablelogs[chosenlog-1]
                    if cl.endswith(".gz"):
                        with open(cl,'rb') as f:
                            data = gzip.decompress(f.read()).decode()
                    else:
                        with open(cl) as f:
                            data = f.read()
                    wtd = uicomponents.menu(stdscr,["Cancel","View all of log","Chat logs only"])
                    if wtd == 1:
                        cursesplus.textview(stdscr,text=data,message=f"Viewing {cl}")
                    elif wtd == 3:
                        who_said_what(stdscr,server_dir)
                    else:
                        cursesplus.textview(stdscr,text="\n".join([d for d in data.splitlines() if logutils.is_log_line_a_chat_line(d)]))
        elif wtd == 3:
            who_said_what(stdscr,server_dir)
        elif wtd == 4:
            command_execution_auditing(stdscr,server_dir)
                
def init_idata(stdscr):
    
    idata = requests.get("https://pastebin.com/raw/GLSGkysJ").json()
    appdata.APPDATA["idata"] = idata
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
    if not ON_WINDOWS:
        return os.system(f"xdg-open {file}")
    else:
        return os.startfile(file)

def manage_server_icon(stdscr):
    while True:
        ssx = uicomponents.menu(stdscr,["BACK","Change icon","Reset icon","Delete icon","View icon"])
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
    __l = uicomponents.menu(stdscr,["Cancel","Modify server.properties (raw)","Modify CRSS Server options (raw)","Reset server configuration","Extra configuration","Rename Server","Change Server Memory","Startup Options","Change Java Installation","Change server software"])#Todo rename server, memory
    if __l == 0:
        appdata.updateappdata()
        return
    elif __l == 1:
        if not os.path.isfile("server.properties"):
            cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
        else:
            with open("server.properties") as f:
                config = propertiesfiles.load(f.read())

            config = cursesplus.dictedit(stdscr,config,"Editing Server Properties",True)
            with open("server.properties","w+") as f:
                f.write(propertiesfiles.dump(config))
    elif __l == 2:
        dt = appdata.APPDATA["servers"][chosenserver-1]
        dt = cursesplus.dictedit(stdscr,dt,"More Server Properties")
        appdata.APPDATA["servers"][chosenserver-1] = dt
        appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 3:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to reset your server configuration","You won't delete any worlds"]):
            if os.path.isfile("server.properties"):
                os.remove("server.properties")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up some more server configuration"]):
                sd = setup_server_properties(stdscr)
                with open("server.properties","w+") as f:
                    f.write(propertiesfiles.dump(sd))
    elif __l == 4:
        dt = appdata.APPDATA["servers"][chosenserver-1]
        if not dt["moddable"]:
            cursesplus.messagebox.showwarning(stdscr,["There are no extra config options for this type of server"])
        else:
            while True:
                lkz = [os.path.split(z)[1] for z in glob.glob(dt["dir"]+"/*.yml")]
                dz = uicomponents.menu(stdscr,["Quit"]+lkz)
                if dz == 0:
                    break
                else:
                    with open(lkz[dz-1]) as f:
                        data = yaml.load(f,yaml.FullLoader)
                    data = cursesplus.dictedit(stdscr,data,os.path.split(lkz[dz-1])[1])
                    with open(lkz[dz-1],"w+") as f:
                        f.write(yaml.dump(data,default_flow_style=False))
    elif __l == 5:
        newname = uicomponents.crssinput(stdscr,"Choose a new name for this server")
        appdata.APPDATA["servers"][chosenserver-1]["name"] = newname
        #appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
    elif __l == 6:
        newmem = choose_server_memory_amount(stdscr)
        appdata.APPDATA["servers"][chosenserver-1]["memory"] = newmem
        appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(appdata.APPDATA["servers"][chosenserver-1])#Regen script
    elif __l == 7:
        appdata.APPDATA["servers"][chosenserver-1] = startup_options(stdscr,appdata.APPDATA["servers"][chosenserver-1])
        appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(appdata.APPDATA["servers"][chosenserver-1])#Regen script

    elif __l == 8:
        njavapath = choose_java_install(stdscr)
        appdata.APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
        appdata.APPDATA["servers"][chosenserver-1]["script"]=generate_script(appdata.APPDATA["servers"][chosenserver-1])#Regen script

    elif __l == 9:
        appdata.APPDATA["servers"][chosenserver-1] = change_software(stdscr,appdata.APPDATA["servers"][chosenserver-1]["dir"],appdata.APPDATA["servers"][chosenserver-1])
        appdata.updateappdata()


def change_software(stdscr,directory,data) -> dict:
    zxc = uicomponents.menu(stdscr,["Cancel","Vanilla","Spigot","Paper","Purpur"],"Please choose the new software for the server")
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

def startup_options(stdscr,serverdata:dict):
    while True:
        wtd = uicomponents.menu(stdscr,["Back","Edit startup commands","Edit shutdown commands","Set startup mode","Command Line Arguments","View server script","Autorestart options"])
        if wtd == 0:
            return serverdata
        elif wtd == 1:
            serverdata["settings"]["launchcommands"] = texteditor.text_editor("\n".join(serverdata["settings"]["launchcommands"]),"Edit Launch Commands").splitlines()
        elif wtd == 2:
            serverdata["settings"]["exitcommands"] = text_editor("\n".join(serverdata["settings"]["exitcommands"]),"Edit Exit Commands").splitlines()
        elif wtd == 3:
            serverdata["settings"]["legacy"] = uicomponents.menu(stdscr,["New Startups (fancy)","Old Startups (legacy)"],"Choose startup mode") == 1
        elif wtd == 4:
            serverdata["settings"]["flags"] = uicomponents.crssinput(stdscr,"Custom flags for your server",prefiltext=serverdata['settings']["flags"])
        elif wtd == 5:
            cursesplus.textview(stdscr,text=serverdata["script"],message="Server startup script")
        elif wtd == 6:
            serverdata = autorestart.autorestart_settings(stdscr,serverdata)
            

def strict_word_search(haystack:str,needle:str) -> bool:
    #PHP
    words = haystack.split(" ")
    return needle in words

def load_server_logs_and_find(stdscr,serverdir:str,tofind:str) -> list[str]:
    cursesplus.displaymsg(stdscr,["Loading Logs, Please wait..."],False)
    logfile = serverdir + "/logs"
    if not os.path.isdir(logfile):
        return []
    dirstack.pushd(logfile)
    logs:list[str] = [l for l in os.listdir(logfile) if l.endswith(".gz") or l.endswith(".log")]
    p = cursesplus.ProgressBar(stdscr,len(logs),cursesplus.ProgressBarTypes.SmallProgressBar,cursesplus.ProgressBarLocations.TOP,message="Loading logs")
    final:list[str] = []
    for lf in logs:
        p.step(lf)
        if lf.endswith(".gz"):
            with open(lf,'rb') as f:
                final.extend(re.findall(tofind,gzip.decompress(f.read()).decode()))
        else:
            with open(lf) as f:
                final.extend(re.findall(tofind,f.read()))
    return final



class ChatEntry:
    logtime:datetime.datetime
    playername:str
    destination:str|None = None#Only used if targetted message
    message:str

    def __init__(self):
        pass

    @staticmethod
    def from_logentry(l:logutils.LogEntry):
        r = ChatEntry()
        r.logtime = l.get_full_log_time()
        r.playername = l.playername.lower()
        rawmessage:str = l.data

        is_targetted = "issued server command" in rawmessage.lower()#Spigot/paper servers only
        if not is_targetted:
            r.message = rawmessage.split(l.playername)[1][1:]
        else:
            try:
                cmdsection = rawmessage.split("issued server command: ")[1]
                target = cmdsection.split(" ")[1]
                r.destination = target
                r.message = f"--> {r.destination}  "+" ".join(cmdsection.split(" ")[2:])
                pass
            except:
                r.message = rawmessage#If it fails, use the raw data
                
        return r
    
    def get_parsed_date(self) -> str:
        #Return a friendly date
        return self.logtime.strftime("%Y-%m-%d %H:%M:%S")

def who_said_what(stdscr,serverdir):
    if resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    allentries = logutils.load_server_logs(stdscr,serverdir)
    allentries:list[ChatEntry] = [ChatEntry.from_logentry(a) for a in allentries if logutils.is_log_entry_a_chat_line(a)]
    #allentries.sort(key=lambda x: x.logdate,reverse=False)
    #Not needed after LSL does sorting
    #allentries.reverse()
    while True:
        wtd = uicomponents.menu(stdscr,["Back","Find by what was said","Find by player","View chat history of server","View Chat Bar Graph"])
        if wtd == 0:
            break
        elif wtd == 1:
            wws = uicomponents.crssinput(stdscr,"What message would you like to search for?")
            strict = cursesplus.messagebox.askyesno(stdscr,["Do you want to search strictly?","(Full words only)"])
            cassen = cursesplus.messagebox.askyesno(stdscr,["Do you want to be case sensitive?"])
            if not strict and cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws in a.message])
            elif not strict and not cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws.lower() in a.message.lower()])
            elif strict and cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if strict_word_search(a.message,wws)])
            elif strict and not cassen:
                ft = "\n".join([f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if strict_word_search(a.message.lower(),wws.lower())])
            cursesplus.textview(stdscr,text=ft,message="Search Results")
        elif wtd == 2:
            wws = uicomponents.crssinput(stdscr,"What player would you like to search for?").lower()
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                list(
                                    itertools.chain.from_iterable([
                                            [
                                            f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries if wws_indiv in a.playername
                                            ] for wws_indiv in renaminghandler.get_aliases_of(wws)
                                        ]
                                            
                                        )
                                    )
                                ),message="Search Results")
        elif wtd == 3:
            cursesplus.textview(stdscr,text=
                                "\n".join(
                                [
                                    f"{a.get_parsed_date()} {a.playername}: {a.message}" for a in allentries
                                ]),message="Search Results")
        elif wtd == 4:
            sdata = {}
            for entry in allentries:
                if entry.playername in sdata:
                    sdata[entry.playername] += 1
                else:
                    sdata[entry.playername] = 1
            cursesplus.bargraph(stdscr,sdata,"Most Talkative Players","Messages")
    dirstack.popd()

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
    if resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    
    ipdir = serverdir+"/.ipindex.json.gz"
    allentries = logutils.load_server_logs(stdscr,serverdir,False)
                
    IPS:dict[str,list] = {}
    formattedips:list[FormattedIP] = []
    if os.path.isfile(ipdir):
        try:
            with open(ipdir,'rb') as f:
                formattedips = [FormattedIP.fromdict(d) for d in json.loads(gzip.decompress(f.read()).decode())]
        except Exception as e:
            cursesplus.messagebox.showerror(stdscr,["Error loading cache",str(e)])
            os.remove(ipdir)
            
    bigfatstring = "\n".join(l.data for l in allentries)
    
    for ip in re.findall(r"\s[A-Za-z]+\s[\[|\(]\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:|\s[A-Za-z0-9_]+\[\/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+:",bigfatstring):
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

    cursesplus.displaymsg(stdscr,["Fixing player names..."],False)
    ki = 0
    for k in formattedips:
        new_ls = []
        for pl in k.players:
            new_ls += renaminghandler.get_aliases_of(pl)
        formattedips[ki].players = remove_duplicates_from_list(new_ls)

        ki += 1

    with open(ipdir,'wb+') as f:
        f.write(gzip.compress(json.dumps([f.todict() for f in formattedips]).encode()))
    p.done()
    while True:
        wtd = uicomponents.menu(stdscr,["BACK","View All","Lookup by Player","Lookup by IP","Lookup by Country","Show bar graph","Reset Cache"])
        if wtd == 0:
            break
        elif wtd == 1:
            sorting = uicomponents.menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
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
            sorting = uicomponents.menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = uicomponents.crssinput(stdscr,"What player do you want to search for?")
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                if psearch in fi.players:
                    final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message=f"Searching for {psearch}")
    
        elif wtd == 3:
            sorting = uicomponents.menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = uicomponents.crssinput(stdscr,"What IP do you want to look for?")
            final = "IP ADDRESS       COUNTRY                  PLAYERS\n"
            for fi in formattedips:
                if psearch in fi.address:
                    final += f"{fi.address.rjust(16)} ({fi.country.rjust(20)}) - {' '.join(fi.players)}\n"
            cursesplus.textview(stdscr,text=final,message=f"Searching for {psearch}")
            
        elif wtd == 4:
            sorting = uicomponents.menu(stdscr,["No Sorting","IP Address 1 -> 9","IP Address 9 -> 1","Country A -> Z","Country Z -> A","Players A -> Z","Players Z -> A"],"How do you wish to sort the results?")
            if sorting == 1 or sorting == 2:
                formattedips.sort(key= lambda x:x.address)
            elif sorting == 3 or sorting == 4:
                formattedips.sort(key=lambda x:x.country)
            elif sorting == 5 or sorting == 6:
                formattedips.sort(key=lambda x: [l.lower() for l in x.players])
            if sorting == 2 or sorting == 4 or sorting == 6:
                formattedips.reverse()#You have selected Z->A, which reverses sorting
            psearch = uicomponents.crssinput(stdscr,"What country do you want to look for?")
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
            cursesplus.bargraph(stdscr,fdata,"Player Country Statistics","unique IPs")
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
            
def get_minute_id_from_datetime(d:datetime.datetime) -> int:
    return int(d.timestamp()/60//1)

def get_datetime_from_minute_id(t:int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(t*60)

class JLLogFrame:
    data:str
    ext:datetime.datetime
    def __init__(self,lowerdata:logutils.LogEntry):
        rtime = lowerdata.data.split(" ")[0].strip()
        rdate = lowerdata.logdate
        
        self.ext = datetime.datetime.strptime(f"{rdate.year}-{rdate.month}-{rdate.day} {rtime[1:-1]}","%Y-%m-%d %H:%M:%S")
        self.data = lowerdata.data

class ServerMinuteFrame:
    minuteid:int
    onlineplayers:list[str] = []
    playerminutes:int = None
    
    def __init__(self,minuteid):
        self.minuteid = minuteid
    def wasonline(self,name) -> bool:
        return name in self.onlineplayers
    def todatetime(self) -> datetime:
        return datetime.datetime.fromtimestamp(self.minuteid*60)
    def howmanyonline(self) -> int:
        return len(self.onlineplayers)
    def getplayerminutes(self) -> int:
        if self.playerminutes is None:
            return self.howmanyonline()
        else:
            return self.playerminutes
    def get_data(self,setting):
        if setting == AnalyticsExplorerDataTypes.PLAYERCOUNT:
            return self.howmanyonline()
        else:
            return self.getplayerminutes()

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
    MINUTE = 1
    HOUR = 60
    DAY = 1440
    WEEK = 1440*7
    
class AnalyticsExplorerDataTypes(enum.Enum):
    TOTALPLAYERMINUTES = 0
    PLAYERCOUNT = 1

def sort_dict_by_key(d:dict) -> dict:
    return dict(sorted(list(d.items())))

def get_chunk_size_from_aezl(s:AnalyticsExplorerZoomLevels):
    return {
        AnalyticsExplorerZoomLevels.MINUTE:1,
        AnalyticsExplorerZoomLevels.HOUR:60,
        AnalyticsExplorerZoomLevels.DAY:1440,
        AnalyticsExplorerZoomLevels.WEEK:1440*7
        }[s]

def serialize_smf(s:ServerMinuteFrame) -> dict:
    return {
        "id" : s.minuteid,
        "playerminutes" : s.playerminutes,
        "onlineplayers" : s.onlineplayers
    }

def deserialize_smf(s:dict) -> ServerMinuteFrame:
    d = ServerMinuteFrame(s["id"])
    d.onlineplayers = s["onlineplayers"]
    d.playerminutes = s["playerminutes"]
    return d

def server_analytics_explorer(stdscr,data:dict[int,ServerMinuteFrame]):
    cursesplus.displaymsg(stdscr,["Analytics Explorer","Initializing..."],False)
    #This function allows users to explore their analytics
    offset = 0
    datasize = len(data)-1
    currentzoomlevel = AnalyticsExplorerZoomLevels.MINUTE#Also passively the list chunk size
    currentdatatype = AnalyticsExplorerDataTypes.PLAYERCOUNT
    zoomlevels = {
        AnalyticsExplorerZoomLevels.MINUTE: "Minute (default)",
        AnalyticsExplorerZoomLevels.HOUR: "Hour",
        AnalyticsExplorerZoomLevels.DAY: "Day",
        AnalyticsExplorerZoomLevels.WEEK: "Week"
    }
    datatypes = {
        AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES: "Player Minutes Spent",
        AnalyticsExplorerDataTypes.PLAYERCOUNT: "Online Players (default)"
    }
    ldata = list(data.values())#List representation of data to prevent performance issues?

    td = tempdir.generate_temp_dir()

    #ogdata = copy.deepcopy(data)
    #ogldata = copy.deepcopy(ldata)#For use later
    JsonGz.write(td+"/data.json.gz",{k:serialize_smf(v) for k,v in list(data.items())})
    maxval = max([len(p.onlineplayers) for p in ldata])
    while True:
        my,mx = stdscr.getmaxyx()
        xspace = mx-1
        yspace = my-4#Top Bottom, and weird bug
        stdscr.erase()
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.BLUE))
        stdscr.addstr(0,0,"Analytics Explorer - Press Q to quit and H for help",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        
        
        ti = 0
        for i in range(offset-xspace//2,offset+xspace//2):
            if i < 0 or i > datasize:
                #Write red bar
                #print("w")
                for dy in range(1,yspace+1):
                    stdscr.addstr(dy,ti,"█",cursesplus.set_colour(cursesplus.RED,cursesplus.RED))
            else:
                seldata = ldata[i]
                if currentdatatype == AnalyticsExplorerDataTypes.PLAYERCOUNT:
                    scale = int(seldata.howmanyonline()/maxval*yspace)
                else:
                    scale = int(seldata.getplayerminutes()/maxval*yspace)
                
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
        if currentdatatype == AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            stdscr.addstr(my-2,0,f"{strip_datetime(get_datetime_from_minute_id(seldata.minuteid))} || {seldata.getplayerminutes()} player-minutes")
        else:
            try:
                stdscr.addstr(my-2,0,f"{strip_datetime(get_datetime_from_minute_id(seldata.minuteid))} || {seldata.howmanyonline()} players online - {seldata.onlineplayers}")
            except:
                stdscr.addstr(my-2,0,f"{strip_datetime(get_datetime_from_minute_id(seldata.minuteid))} || {seldata.howmanyonline()} players online")#Too long for list
        
        ch = curses.keyname(stdscr.getch()).decode()
        if ch == "q":
            break
        elif ch == "h":
            cursesplus.displaymsg(stdscr,["KEYBINDS","q - Quit","h - Help","<- -> Scroll","END - Go to end","HOME - Go to beginning","j - Jump to time","SHIFT <-- --> - Jump hour","Ctrl <-- --> - Jump day","T - Select time unit","D - Select data type"])
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
        elif ch == "kRIT5":#ctrl left
            offset += 1440
        elif ch == "kLFT5":#ctrl right
            if offset > 1440:
                offset -= 1440
            else:
                offset = 0
        elif ch == "KEY_END":
            offset = datasize - 1
        elif ch == "KEY_HOME":
            offset = 0
        elif ch == "j":
            stdscr.clear()
            ndate = cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a date and time to jump to",True,False,get_datetime_from_minute_id(ldata[offset].minuteid))
            if currentzoomlevel == AnalyticsExplorerZoomLevels.HOUR:
                ndate = ndate.replace(second=0,minute=0)
            if currentzoomlevel == AnalyticsExplorerZoomLevels.DAY or currentzoomlevel == AnalyticsExplorerZoomLevels.WEEK:
                ndate = ndate.replace(hour=0)
            nmid = get_minute_id_from_datetime(ndate)
            if not nmid in data:
                cursesplus.messagebox.showerror(stdscr,["Records do not exist for the selected date."])
            else:
                offset = list(data.keys()).index(nmid)
        elif ch == "t":
            currentzoomlevel = list(zoomlevels.keys())[uicomponents.menu(stdscr,list(zoomlevels.values()),"Choose a zoom level")]
            cursesplus.displaymsg(stdscr,["Generating Data"],False)
            #This will use ogdat because data may have been used for hour or day, which will screw it up
            offset = 0
            if currentzoomlevel == AnalyticsExplorerZoomLevels.MINUTE:
                data = {k:deserialize_smf(v) for k,v in list(JsonGz.read(td+"/data.json.gz").items())}
                ldata = list(data.values())
            else:
                chunked_data:list[list[ServerMinuteFrame]] = split_list_into_chunks(list({k:deserialize_smf(v) for k,v in list(JsonGz.read(td+"/data.json.gz").items())}.values()),get_chunk_size_from_aezl(currentzoomlevel))
                final_data:dict[int,ServerMinuteFrame] = {}
                for chunk in chunked_data:
                    s:ServerMinuteFrame = ServerMinuteFrame(chunk[0].minuteid)
                    #Append all unique players, and set playerminutes
                    total_playerminutes = 0
                    unique_players = []
                    for minute in chunk:
                        total_playerminutes += minute.howmanyonline()
                        for onlineplayer in minute.onlineplayers:
                            if onlineplayer not in unique_players:
                                unique_players.append(onlineplayer)
                    s.playerminutes = total_playerminutes
                    s.onlineplayers = unique_players
                    final_data[s.minuteid] = s
                data = final_data
                del chunked_data
                del final_data
                ldata = list(data.values())
            maxval = max([p.get_data(currentdatatype) for p in list(data.values())])
            #if currentdatatype == AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            #    maxval = maxval*get_chunk_size_from_aezl(currentzoomlevel)
            datasize = len(data)-1
                
        elif ch == "d":
            currentdatatype = list(datatypes.keys())[uicomponents.menu(stdscr,list(datatypes.values()),"Choose a data type")]
            maxval = max([p.get_data(currentdatatype) for p in ldata])
            #if currentdatatype == AnalyticsExplorerDataTypes.TOTALPLAYERMINUTES:
            #    maxval = maxval*get_chunk_size_from_aezl(currentzoomlevel)
        if offset > datasize:
            offset = datasize - 1
            
def average_list(l:list[int|float]) -> float:
    return sum(l)/len(l)
            
def recursive_average(l:list[list[int|float]]) -> list[float]:
    return [average_list(z) for z in l]

class JsonGz:
    def read(path:str) -> dict:
        with open(path,'rb') as f:
            rd = f.read()
        return json.loads(gzip.decompress(rd).decode())
    def write(path:str,data:dict) -> None:
        with open(path,'wb+') as f:
            f.write(gzip.compress(json.dumps(data).encode()))

def sanalytics(stdscr,serverdir):
    
    if resource_warning(stdscr):
        return
    renaminghandler.autoupdate_cache(stdscr,serverdir)
    analytics_file_path = serverdir + os.sep + "anacache.json.gz"
    cursesplus.displaymsg(stdscr,["Loading from cache..."],False)
    readfrom = None
    cachefile = {"end":None,"minutes":{}}
    if os.path.isfile(analytics_file_path):
        cachefile = JsonGz.read(analytics_file_path)
        if cachefile["end"] is not None:
            readfrom = get_datetime_from_minute_id(cachefile["end"])#Stores the last minuteid that it successfully processed.
    
    allentries:list[logutils.LogEntry] = logutils.load_server_logs(stdscr,serverdir,False,readfrom)
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
            plname = rs.split(" ")[0].lower()
            action = rs.split(" ")[1]
            #Remove special characters from plname
            plname = plname.replace("(","").replace(")","")
            plname = renaminghandler.get_current_name_of(plname)
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
    if len(cachefile["minutes"]) > 0:
        firstentrymid = int(list(cachefile["minutes"].keys())[0])+1
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
    for cachedentry in list(cachefile["minutes"].items()):
        final[int(cachedentry[0])] = ServerMinuteFrame(int(cachedentry[0]))
        final[int(cachedentry[0])].onlineplayers = cachedentry[1]
        #This should overwrite any nasty data.
    cursesplus.displaymsg(stdscr,["Cleaning Data","Please Wait"],wait_for_keypress=False)
    
    for k in final:
        final[k].onlineplayers = remove_duplicates_from_list(final[k].onlineplayers)
        
    #Find last zeroed time to store in cache
    for mre in list(final.values()).__reversed__():
        if mre.howmanyonline() == 0:
            storeto = mre.minuteid
            break
    cursesplus.displaymsg(stdscr,["Saving Data","Please Wait"],False)
    newcache = {"end":int(storeto),"minutes":{}}
    for line in list(final.items()):
        if int(line[0]) <= int(storeto):
            newcache["minutes"][int(line[0])] = line[1].onlineplayers
    JsonGz.write(analytics_file_path,newcache)
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
        wtd = uicomponents.menu(stdscr,["Back","Analytics Explorer","Playtime","Total Player Count","Time of Day",f"FILTER MIN: {strip_datetime(get_datetime_from_minute_id(minminid))}",f"FILTER MAX: {strip_datetime(get_datetime_from_minute_id(maxminid))}","RESET FILTERS","Export to CSV","Server Popularity Over Time","Last Seen","First Join","Reset Cache"],"Server Analytics Manager")
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
                #swtd = uicomponents.menu(stdscr,["Back","VIEW GRAPH"]+list(playminutes.keys()),"Choose a player to view their playtime information")
                swtd = cursesplus.searchable_option_menu(stdscr,list(playminutes.keys()),"Choose a player to view their playtime information",["Back","View Total Graph"])
                if swtd == 0:
                    break
                elif swtd == 1:
                    
                    cursesplus.bargraph(stdscr,playminutes,"Player Minute Information","minutes")
                else:
                    plstudy = list(playminutes.keys())[swtd-2]
                    zwtd = uicomponents.menu(stdscr,["Total Playtime Minutes","Playtime History","Time of Day analyzers"])
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
                                        
                            cursesplus.bargraph(stdscr,dzl,f"How has {plstudy} played over the months?","minutes spend",False,True)
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
                                
                            cursesplus.bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
                            
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
                
            cursesplus.bargraph(stdscr,dataset_ps,"Player minutes spent per hour of day","player-minutes",False,True)
            
        elif wtd == 5:
            stdscr.clear()
            minminid = get_minute_id_from_datetime(cursesplus.date_time_selector(stdscr,cursesplus.DateTimeSelectorTypes.DATEANDTIME,"Choose a new minimum filter time",True,False,get_datetime_from_minute_id(minminid)))
        elif wtd == 6:
            stdscr.clear()
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
            tan = uicomponents.menu(stdscr,["Total Player-minutes","Unique Players","Average Online Players","Average Online Players (active time)"],"Select Data to examine",footer="(active time) shows only data that is not zero")
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
                
            cursesplus.bargraph(stdscr,gd,"Popularity Results",unit,False,False)
        elif wtd == 10:
            plf = 0
            cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)
            sortop = uicomponents.menu(stdscr,["Alphabetically","Recent -> Old"],"Choose search option")
            fjblock:dict[str,datetime.datetime] = {}
            for line in reversed(list(workingdata.values())):
                for pl in line.onlineplayers:
                    if not pl in fjblock.keys():
                        fjblock[pl] = get_datetime_from_minute_id(line.minuteid)
                        plf += 1
                        cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)

            if sortop == 0:
                fjblock = dict(sorted(fjblock.items()))#Sort A-Z

            #Assemble text
            finals = "PLAYER NAME".ljust(16)+" "+"LAST SEEN"+"\n"
            for blk in fjblock.items():
                finals += blk[0].ljust(16) + " " + strip_datetime(blk[1]) + "\n"

            cursesplus.textview(stdscr,text=finals,message="Results")
        elif wtd == 11:
            plf = 0
            cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)
            sortop = uicomponents.menu(stdscr,["Alphabetically","Oldest to newest"],"Choose search option")
            fjblock:dict[str,datetime.datetime] = {}
            for line in list(workingdata.values()):
                for pl in line.onlineplayers:
                    if not pl in fjblock.keys():
                        fjblock[pl] = get_datetime_from_minute_id(line.minuteid)
                        plf += 1
                        cursesplus.displaymsg(stdscr,["Analyzing data",f"{plf} players found"],False)

            if sortop == 0:
                fjblock = dict(sorted(fjblock.items()))#Sort A-Z

            #Assemble text
            finals = "PLAYER NAME".ljust(16)+" "+"JOIN DATE"+"\n"
            for blk in fjblock.items():
                finals += blk[0].ljust(16) + " " + strip_datetime(blk[1]) + "\n"

            cursesplus.textview(stdscr,text=finals,message="Results")
            
        elif wtd == 12:
            os.remove(analytics_file_path)
            return

def resource_warning(stdscr) -> bool:
    if appdata.APPDATA["settings"]["reswarn"]:
        return not cursesplus.messagebox.askyesno(stdscr,["What you just selected is a high resource operation.","Continuing may affect the performance of other apps running on this device.","Are you sure you wish to proceed?"])
    else:
        return False

def start_server(stdscr,_sname,chosenserver,SERVER_DIR):
    if sys.version_info[1] < 11:
        cursesplus.messagebox.showerror(stdscr,["Unfortunately, the new startups can only be used with Python 3.11 or newer.",f"You are running {sys.version}.","Your server will be started in legacy mode (pre 1.43)"])
        appdata.APPDATA["servers"][chosenserver-1]["settings"]["legacy"] = True
    os.system(";".join(appdata.APPDATA["servers"][chosenserver-1]["settings"]["launchcommands"]))
    if appdata.APPDATA["servers"][chosenserver-1]["settings"]["legacy"]:
        while True:
            os.chdir(appdata.APPDATA["servers"][chosenserver-1]["dir"])           
            stdscr.clear()
            stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}\n\r")
            stdscr.refresh()
            if not ON_WINDOWS:
                curses.curs_set(1)
                curses.reset_shell_mode()
                lretr = os.system(appdata.APPDATA["servers"][chosenserver-1]["script"])
                #child = pexpect.spawn(appdata.APPDATA["servers"][chosenserver-1]["script"])
                #child.expect("Finished")
                curses.reset_prog_mode()
                curses.curs_set(0)
            else:
                curses.curs_set(1)
                curses.reset_shell_mode()
                #COLOURS_ACTIVE = False
                lretr = os.system("cmd /c ("+appdata.APPDATA["servers"][chosenserver-1]["script"]+")")
                curses.reset_prog_mode()
                curses.curs_set(0)
                #restart_colour()
            os.system(";".join(appdata.APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
            hascrashed = lretr != 0 and lretr != 127 and lretr != 128 and lretr != 130
            willgoagain = False
            #Handle autorestart

            recommended_action = autorestart.get_recommended_action(appdata.APPDATA["servers"][chosenserver-1],True)

            match recommended_action:
                case autorestart.AutoRestartOptions.ALWAYS:
                    willgoagain = True
                case autorestart.AutoRestartOptions.SAFEEXIT:
                    if not hascrashed:
                        willgoagain = True
                
            if willgoagain:
                execagain = timedexec.timeout_askyesno(stdscr,["Unless you interrupt by saying no","This server will auto-restart when","the timer runs out"],True,appdata.get_setting_value("autorestarttimeout"))
                if execagain:
                    continue

            if hascrashed:
                displog = cursesplus.messagebox.askyesno(stdscr,["Oh No! Your server crashed","Would you like to view the logs?"])
                if displog:
                    view_server_logs(stdscr,SERVER_DIR)

            stdscr.clear()
            stdscr.refresh()
            break
    else:
        if not _sname in SERVER_INITS:
            truecommand = appdata.APPDATA["servers"][chosenserver-1]["script"]
            if ON_WINDOWS:
                truecommand = "cmd /c ("+appdata.APPDATA["servers"][chosenserver-1]["script"]+")"
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
                os.system(";".join(appdata.APPDATA["servers"][chosenserver-1]["settings"]["exitcommands"]))
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
                svrstat.send(uicomponents.crssinput(stdscr,"Enter a command to run"))
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

def light_config_server(stdscr,chosenserver:int) -> None:
    while True:
        wtd = uicomponents.menu(stdscr,["Back","Change MOTD","Manage server icon","Code of Conduct"])
        if wtd == 0:
            break
        elif wtd == 1:
            if not os.path.isfile("server.properties"):
                cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
            else:
                with open("server.properties") as f:
                    config = propertiesfiles.load(f.read())
                if not "motd" in config:
                    cursesplus.messagebox.showwarning(stdscr,["For some reason, an old motd could not be found.","You will be prompted to choose one anyway."])
                    config["motd"] = ""
                else:
                    cursesplus.displaymsg(stdscr,["Current Message Is",config["motd"]])
                curses.curs_set(1)
                newmotd = uicomponents.crssinput(stdscr,"Please input a new MOTD",2,59,prefiltext=config["motd"].replace("\\n","\n"))
                curses.curs_set(0)
                config["motd"] = newmotd.replace("\n","\\n")
                with open("server.properties","w+") as f:
                    f.write(propertiesfiles.dump(config))
        elif wtd == 2:
            manage_server_icon(stdscr)
        elif wtd == 3:
            codeofconduct.codeofconductmenu(stdscr,appdata.APPDATA["servers"][chosenserver - 1]["dir"])

def manage_server(stdscr,_sname: str,chosenserver: int):
    
    global COLOURS_ACTIVE
    
    SERVER_DIR = _sname
    _ODIR = os.getcwd()
    
    if appdata.APPDATA["settings"]["transitions"]["value"]:
        cursesplus.transitions.vertical_bars(stdscr)
    if appdata.APPDATA["servers"][chosenserver-1]["software"] == 5:
        bedrock_manage_server(stdscr,_sname,chosenserver)
        return
    #Manager server
    while True:

        #TODO - Make new: Server configuration. Inside put server icon and change MOTD. Put change server software in advanced configuration

        os.chdir(appdata.APPDATA["servers"][chosenserver-1]["dir"])#Fix bug where running a sub-option that changes dir would screw with future operations
        x__ops = ["RETURN TO MAIN MENU","Start Server","Configuration >>","Advanced configuration >>","Delete server","Manage worlds","Update Server software","Manage Content >>"]
        x__ops += ["Server Logs >>","Export server","View server info","Administration and Backups >>"]
        x__ops += ["Utilities >>","FILE MANAGER"]
        if _sname in SERVER_INITS and not appdata.APPDATA["servers"][chosenserver-1]["settings"]["legacy"]:
            x__ops[1] = "Server is running >>"
        #w = uicomponents.menu(stdscr,x__ops)
        w = uicomponents.menu(stdscr,x__ops,"Please choose a server management option")
        if w == 0:
            stdscr.erase()
            os.chdir(_ODIR)
            if appdata.APPDATA["settings"]["transitions"]["value"]:
                cursesplus.transitions.random_blocks(stdscr)
            break
        
        elif w == 1:
            start_server(stdscr,_sname,chosenserver,SERVER_DIR)
        elif w == 2:
            light_config_server(stdscr,chosenserver)
        elif w == 3:
            
            config_server(stdscr,chosenserver)
        elif w == 4:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER"],default=cursesplus.messagebox.MessageBoxStates.NO):
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER","THIS IS YOUR LAST CHANCE"],default=cursesplus.messagebox.MessageBoxStates.NO):
                    os.chdir(SERVERSDIR)
                    shutil.rmtree(SERVER_DIR)
                    del appdata.APPDATA["servers"][chosenserver-1]
                    cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                    stdscr.clear()
                    break
            stdscr.erase()
        elif w == 5:
            if not os.path.isfile("server.properties"):
                cursesplus.messagebox.showerror(stdscr,["Please start your server to generate","server.properties"])
                continue
            with open("server.properties") as f:

                dpp = propertiesfiles.load(f.read())

            while True:
                po = find_world_folders(SERVER_DIR)
                n = uicomponents.menu(stdscr,["BACK","CREATE NEW WORLD"]+po)
                if n == 0:
                    with open("server.properties","w+") as f:
                        f.write(propertiesfiles.dump(dpp))   
                    break
                elif n == 1:
                    dppx = setup_new_world(stdscr,dpp,SERVER_DIR,False)
                    if dppx is not None:
                        dpp = dppx#Fix bug
                else:
                    manage_a_world(stdscr,SERVER_DIR,po[n-2])
            
        elif w == 6:
            if not appdata.APPDATA["servers"][chosenserver-1]["moddable"]:
                update_vanilla_software(stdscr,os.getcwd(),chosenserver)
            elif appdata.APPDATA["servers"][chosenserver-1]["software"] == 3:
                update_paper_software(stdscr,os.getcwd(),chosenserver)
            elif appdata.APPDATA["servers"][chosenserver-1]["software"] == 2:
                update_spigot_software(stdscr,os.getcwd(),chosenserver)
            elif appdata.APPDATA["servers"][chosenserver-1]["software"] == 4:
                update_purpur_software(stdscr,os.getcwd(),chosenserver)
            else:
                cursesplus.messagebox.showwarning(stdscr,["This type of server can't be upgraded."])
        elif w == 7:
            while True:
                mmwtd = uicomponents.menu(stdscr,["Back","Plugins and Mods","Datapacks","Resource Pack"],"CONTENT MANAGER | What would you like to edit?")
                if mmwtd == 0:
                    break
                elif mmwtd == 1:
                    if appdata.APPDATA["servers"][chosenserver-1]["software"] == 1:
                        cursesplus.messagebox.showerror(stdscr,["Vanilla servers cannot have plugins."])
                        continue
                    svr_mod_mgr(stdscr,SERVER_DIR,appdata.APPDATA["servers"][chosenserver-1]["version"],appdata.APPDATA["servers"][chosenserver-1]["software"])
                elif mmwtd == 2:
                    world = uicomponents.menu(stdscr,find_world_folders(SERVER_DIR),"Choose a world to apply datapacks to")
                    manage_datapacks(stdscr,find_world_folders(SERVER_DIR)[world]+"/datapacks")
                elif mmwtd == 3:
                    if not os.path.isfile("server.properties"):
                        cursesplus.messagebox.showerror(stdscr,["Please start your server to generate","server.properties"])
                        continue
                    with open("server.properties") as f:

                        dpp = propertiesfiles.load(f.read())
                    
                    dpp = resource_pack_setup(stdscr,dpp)
                    with open("server.properties","w+") as f:
                        f.write(propertiesfiles.dump(dpp))
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
            stdscr.addstr(6,0,"Number of Plugins")
            stdscr.addstr(7,0,"Server ID")
            stdscr.refresh()
            sdat = appdata.APPDATA["servers"][chosenserver-1]
            stdscr.addstr(0,20,sdat["name"])
            stdscr.addstr(1,20,sdat["version"])
            stdscr.addstr(2,20,sdat["dir"][0:os.get_terminal_size()[0]])
            stdscr.addstr(3,20,sdat["memory"])
            stdscr.addstr(4,20,"...")
            stdscr.refresh()
            stdscr.addstr(4,20,parse_size(get_tree_size(sdat["dir"])))
            stdscr.refresh()
            stdscr.addstr(5,20,["Yes" if sdat["moddable"] else "No"][0])
            stdscr.addstr(6,20,str(len(glob.glob(SERVER_DIR+"/plugins/*.jar")) if os.path.isdir(SERVER_DIR+"/plugins") else "N/A"))
            stdscr.addstr(7,20,str(sdat["id"]))
            stdscr.addstr(8,0,"Press any key to continue",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
            stdscr.refresh()
            stdscr.getch()
        elif w == 11:
            while True:
                abkwtd = uicomponents.menu(stdscr,["Back","Whitelist","Backups","Admins","Banned Players"],"ADMIN MENU | What do you want to edit?")
                if abkwtd == 0:
                    break
                elif abkwtd == 1:
                    manage_whitelist(stdscr,SERVER_DIR+"/whitelist.json")
                elif abkwtd == 2:
                    server_backups(stdscr,SERVER_DIR,appdata.APPDATA["servers"][chosenserver-1])
                elif abkwtd == 3:
                    manage_ops(stdscr,SERVER_DIR)
                elif abkwtd == 4:
                    manage_bans(stdscr,SERVER_DIR)
        #elif w == 12:
        #    appdata.APPDATA["servers"][chosenserver-1] = change_software(stdscr,SERVER_DIR,appdata.APPDATA["servers"][chosenserver-1])
        #    appdata.updateappdata()
        elif w == 12:
            w2 = uicomponents.menu(stdscr,["Back","Chat Utilities","IP Lookups","Server Analytics","Player Statistics","Player name history"],"Additional Utilities")
            if w2 == 1:
                who_said_what(stdscr,SERVER_DIR)
            elif w2 == 2:
                ip_lookup(stdscr,SERVER_DIR)
            elif w2 == 3:
                #cursesplus.messagebox.showerror(stdscr,["This feature is coming soon.","Sorry"])
                #continue
                sanalytics(stdscr,SERVER_DIR)
            elif w2 == 4:
                playerstat(stdscr,SERVER_DIR)
            elif w2 == 5:
                renaminghandler.player_naming_history(stdscr)
        elif w == 13:
            file_manager(stdscr,SERVER_DIR,f"Files of {appdata.APPDATA['servers'][chosenserver-1]['name']}")
_SCREEN:typing.Any = None

def get_nested_keys(d, parent_key=''):
    keys = []#COPIED
    for k, v in d.items():
        full_key = f"{parent_key}.{k}" if parent_key else k
        
        if isinstance(v, dict):
            keys.extend(get_nested_keys(v, full_key))
        else:
            keys.append(full_key)
    return keys

def dictpath(inputd:dict,path:str):
    """Select path from inputd where path is seperated by /"""
    if path == ".":
        return inputd
    final = inputd
    for axx in path.split("."):
        if axx == "":
            continue
        if type(final) == list:
            final = final[int(axx)]
        else:
            final = final[axx]
    return final

def push_uuids_for_searching(uuids:list[str]) -> None:
    """Adds a list of uuids to the list. It is a good idea to call create_uuid_index after this"""
    for uuid in uuids:
        if not uuid in appdata.UUID_INDEX:
            appdata.UUID_INDEX[uuid] = None
    appdata.updateappdata()

def collapse_tuple(l) -> str:
    if isinstance(l,tuple) or isinstance(l,list):
        best = ""
        bestn = 0
        for i in l:
            if len(i) > bestn:
                best = i
                bestn = len(i)
        return best
    else:
        return l

def create_uuid_index(stdscr) -> None:
    """Loads logs from all servers and attempts to fill in as many uuids as it can"""
    #First, check if UUID index actually needs to be updated.
    if not None in list(appdata.UUID_INDEX.values()):
        return#Doesn't need updating
    cursesplus.displaymsg(stdscr,["Finding missing UUIDs"],False)
    missinguuids = []
    for entry in list(appdata.UUID_INDEX.items()):
        if entry[1] is None:
            missinguuids.append(entry[0])
    matches = []
    s1knowledgebase = {}
    for server in appdata.APPDATA["servers"]:
        matches.extend(load_server_logs_and_find(stdscr,server['dir'],r'(UUID of player \S+ is [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})|(logged in as \S+ joined \(UUID: [0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'))
        #Load servers
    
    cursesplus.displaymsg(stdscr,["Parsing data..."],False)
    for match in matches:
        s = collapse_tuple(match).split(" ")
        s1knowledgebase[s[3]] = s[-1]#Match player name to UUID
    saveduuids = 0
    faileduuids = 0
    cursesplus.displaymsg(stdscr,["Saving UUIDS..."],False)
    #Attempt to match UUID-less matches
    #cursesplus.textview(stdscr,text=str(missinguuids))
    for missinuuid in missinguuids:
        if missinuuid in s1knowledgebase:
            appdata.UUID_INDEX[missinuuid] = s1knowledgebase[missinuuid]
            saveduuids += 1
            missinguuids.remove(missinuuid)
            
    #cursesplus.messagebox.showinfo(stdscr,[str(saveduuids),str(faileduuids)])
    #Use webrequests for remaining UUIDS
    tofindpbar = cursesplus.ProgressBar(stdscr,len(missinguuids),message="Finding UUIDs")
    for missinuuid in missinguuids:
        tofindpbar.step(f"{saveduuids} found; {faileduuids} failed || {missinuuid}")
        if missinuuid.startswith("0000"):
            faileduuids += 1
            continue
        webresult = get_name_from_uuid(missinuuid)
        if webresult is None or webresult == missinuuid:
            faileduuids += 1
            continue
        appdata.UUID_INDEX[missinuuid] = webresult
        saveduuids += 1
        missinguuids.remove(missinuuid)
        sleep(1)
       
    appdata.updateappdata() 

def playerstat(stdscr,serverdir):
    worlds = find_world_folders(serverdir)
    selworld = uicomponents.menu(stdscr,["Cancel"]+worlds,"Choose a world to search statistics for")
    if selworld == 0:
        return
    else:
        cursesplus.displaymsg(stdscr,["Loading data"],False)
        playerdatafolder = serverdir+"/"+worlds[selworld-1]+"/stats/"
        uuids = []
        filemaps = {}
        playerdatafiles = glob.glob(playerdatafolder+"*.json")
        for datafile in playerdatafiles:
            b = os.path.basename(datafile)
            uuid = b.split(".")[0]
            if len(uuid) == 36:
                uuids.append(uuid)
                filemaps[datafile] = uuid
        
        #cursesplus.textview(stdscr,text="\n".join(uuids))
                
        #Attempt to load UUID to playernames
        localmappings = {k:k for k in uuids}
        p = cursesplus.ProgressBar(stdscr,len(uuids),message="Converting UUIDs")
        push_uuids_for_searching(uuids)
        create_uuid_index(stdscr)
        for uuid in uuids:
            p.step(f"{p.max - p.value} remaining - {uuid}")
            localmappings[uuid] = get_name_from_uuid(uuid)
        localmappings = {k:v for k,v in list(localmappings.items()) if k is not None and v is not None }
        #localmappings = {k:v for k,v in list(localmappings.items()) if os.path.isfile(playerdatafolder+k+".json")}
        
        while True:
            pl = cursesplus.searchable_option_menu(stdscr,list(localmappings.values()),"Select an option or a player to view their statistics",["FINISH","COMPETITION GRAPHS"])
            if pl == 0:
                break
            elif pl == 1:
                bigdata = {}
                allkeys = []
                for file in playerdatafiles:
                    with open(file) as f:
                        d = json.load(f)["stats"]
                        allkeys += get_nested_keys(d)
                        bigdata[get_name_from_uuid(filemaps[file])] = d
                
                allkeys = remove_duplicates_from_list(allkeys)
                while True:
                    compe = cursesplus.searchable_option_menu(stdscr,allkeys,"Choose a statistic to compare",["FINISH"])
                    if compe == 0:
                        break
                    else:
                        ktg = allkeys[compe-1]
                        final = {}
                        for person in bigdata:
                            try:
                                final[person] = dictpath(bigdata[person],ktg)
                            except:
                                pass
                        cursesplus.bargraph(stdscr,final,f"Competition for {ktg}")
                
            else:
                assocuuid = uuids[pl-2]
                assocfile = playerdatafolder + assocuuid + ".json"
                with open(assocfile) as f:
                    data = json.load(f)['stats']
                    options = get_nested_keys(data)
                    while True:
                        to_look = cursesplus.searchable_option_menu(stdscr,options,"Choose a statistic",["FINISH","Graph"])
                        if to_look == 0:
                            break
                        elif to_look == 1:
                            final = {}
                            for o in options:
                                final[o] = dictpath(data,o)
                            cursesplus.bargraph(stdscr,final,"All statistics")
                        else:
                            res = dictpath(data,options[to_look-2])
                            cursesplus.messagebox.showinfo(stdscr,[options[to_look-1],str(res)])

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
            ndict = cursesplus.dictedit(stdscr,ndict,os.path.split(path)[1])
            with open(path,"w+") as f:
                if path.endswith("json"):
                    json.dump(ndict,f)
                else:
                    yaml.dump(ndict,f,default_flow_style=False)
        except:
            if ON_WINDOWS:
                os.system(f"notepad \"{path}\"")
            else:
                curses.reset_shell_mode()
                os.system(appdata.APPDATA["settings"]["editor"]["value"].replace("%s",path))
                curses.reset_prog_mode()
    else:
        if ON_WINDOWS:
            os.system(f"notepad \"{path}\"")
        else:
            curses.reset_shell_mode()
            os.system(appdata.APPDATA["settings"]["editor"]["value"].replace("%s",path))
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
            whattpmake = uicomponents.menu(stdscr,["Cancel","New File","New Directory"])
            if whattpmake == 1:
                newname = uicomponents.crssinput(stdscr,"Name of new file")
                try:
                    with open(adir+"/"+newname,"x") as f:
                        f.write("")
                except:
                    cursesplus.messagebox.showerror(stdscr,["Failed to create file"])
            elif whattpmake == 2:
                newname = uicomponents.crssinput(stdscr,"Name of new directory")
                try:
                    os.mkdir(adir+"/"+newname)
                except:
                    cursesplus.messagebox.showerror(stdscr,["Failed to create directory"])
            elif whattpmake == 2:
                pass
        elif kkx == "m":
            newname = uicomponents.crssinput(stdscr,"New name?")
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
    tmpx = tempdir.generate_temp_dir()
    try:
        with zipfile.ZipFile(datapackfile) as zf:
            zf.extract("pack.mcmeta",tmpx)
        with open(tmpx+"/pack.mcmeta") as f:
            json.load(f)
    except:
        return False
    else:
        return True

def find_world_datapacks(datadir) -> list[list[str,str]]:
    #datadir = worlddir+"/datapacks"
    tmpx = tempdir.generate_temp_dir()
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
        wtd = uicomponents.menu(stdscr,["Back","Add Datapack"]+[collapse_datapack_description(f[0]) for f in fz])
        
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
        wtd = uicomponents.menu(stdscr,["Back","Manage datapacks","View world info"])
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
            dz = uicomponents.menu(stdscr,["BACK","ADD ADMIN"]+[d["name"] for d in data])
            if dz == 0:
                with open(opdir,"w+") as f:
                    f.write(json.dumps(data))
                break
            elif dz == 1:
                player = uicomponents.crssinput(stdscr,"Please input the player's name")
                try:
                    uuid = get_player_uuid(player)
                except:
                    cursesplus.messagebox.showerror(stdscr,["This player does not exist."])
                else:
                    bypass = cursesplus.messagebox.askyesno(stdscr,["Should this player be able","to bypass player limits?"])
                    oplevel = uicomponents.menu(stdscr,["Bypass spawn protection only","Singleplayer commands","Moderation (kick/ban)","All commands (/stop)"])+1
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
                        oplevel = uicomponents.menu(stdscr,["Bypass spawn protection only","Singleplayer commands","Moderation (kick/ban)","All commands (/stop)"])+1
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
            dz = uicomponents.menu(stdscr,["BACK","ADD BAN"]+[d["name"] for d in data])
            if dz == 0:
                with open(opdir,"w+") as f:
                    f.write(json.dumps(data))
                break
            elif dz  == 1:
                player = uicomponents.crssinput(stdscr,"Please input the player's name")
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
                        ddate = uicomponents.crssinput(stdscr,"What date should the ban end? (example: 2023-09-22)",maxlen=10)
                        dtime = uicomponents.crssinput(stdscr,"What time should the ban end? (example: 10:00:00)",maxlen=8)
                        dend =  ddate + " " + dtime + " " + get_mc_valid_timezone()
                    reason = uicomponents.crssinput(stdscr,"What is the reason for this ban?")
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
                        ddate = uicomponents.crssinput(stdscr,"What date should the ban end? (example: 2023-09-22)",maxlen=10)
                        dtime = uicomponents.crssinput(stdscr,"What time should the ban end? (example: 10:00:00)",maxlen=8)
                        dend =  ddate + " " + dtime + " " + get_mc_valid_timezone()
                        active["expires"] = dend
                        data[dz-2] = active
                        
def server_backups(stdscr,serverdir:str,serverdata:dict):
    LBKDIR = serverdata["backupdir"]
    dirstack.pushd(serverdir)#Just in case some super weird bug
    #if not os.path.isdir(LBKDIR):
    #    os.mkdir(LBKDIR)
    while True:
        z = uicomponents.menu(stdscr,["Back","Create a Backup","Load a Backup",f"Choose backup directory ({LBKDIR})","Delete all backups"])
        if z == 0:
            dirstack.popd()
            break
        elif z == 1:
            if resource_warning(stdscr):
                continue
            with open(serverdir+"/crss.json","w+") as f:
                f.write(json.dumps(serverdata))
            useprofile = appdata.APPDATA["backupprofiles"][list(appdata.APPDATA["backupprofiles"].keys())[uicomponents.menu(stdscr,list(appdata.APPDATA["backupprofiles"].keys()),"Select which backup profile to use")]]
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
                        tom_index = next((index for (index, d) in enumerate(appdata.APPDATA["servers"]) if d["id"] == locateid), None)
                        appdata.APPDATA["servers"][tom_index] = nd
                except:
                    pass
                w.stop()
                cursesplus.messagebox.showinfo(stdscr,["Restore completed"])
                os.chdir(serverdir)       
        elif z == 3:
            serverdata["backupdir"] = cursesplus.filedialog.openfolderdialog(stdscr,"Choose a new backup directory")
            LBKDIR = serverdata["backupdir"]
            appdata.updateappdata()       
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


def choose_java_install(stdscr) -> str:

    #Return path of selected java- Smart java?
    while True:
        stdscr.erase()
        jsl = uicomponents.menu(stdscr,["ADD NEW INSTALLATION"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in appdata.APPDATA["javainstalls"]],"Please choose a Java installation from the list")
        if jsl == 0:
            managejavainstalls(stdscr)
        else:
            break
    return appdata.APPDATA["javainstalls"][jsl-1]["path"]
def managejavainstalls(stdscr):
    
    if "java" in [j["path"] for j in appdata.APPDATA["javainstalls"]]:
        pass
    else:
        if os.system("java --help") == 0 or os.system("java /?") == 0 or os.system("java -help") == 0:
        
            appdata.APPDATA["javainstalls"].append({"path":"java","ver":get_java_version()})
        stdscr.clear()
    while True:
        stdscr.erase()
        jmg = uicomponents.menu(stdscr,["ADD INSTALLATION","FINISH"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in appdata.APPDATA["javainstalls"]])
        if jmg == 0:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a java executable",directory=os.path.expanduser("~"))
            if os.system(njavapath.replace("\\","/")+" -help") != 0:
                if not cursesplus.messagebox.askyesno(stdscr,["You may have selected an invalid java file.","Are you sure you would like to add it"]):
                    continue
                else:
                    stdscr.erase()
                    ndict = {"path":njavapath.replace("\\","/"),"ver":"Unknown"}
                    if cursesplus.messagebox.askyesno(stdscr,["Do you know what java version this is?"]):
                        ndict["ver"] = uicomponents.crssinput(stdscr,"Java version?",maxlen=10)
                        appdata.APPDATA["javainstalls"].append(ndict)
            else:
                fver = get_java_version(njavapath.replace("\\","/"))
                ndict = {"path":njavapath.replace("\\","/"),"ver":fver}
                appdata.APPDATA["javainstalls"].append(ndict)
        elif jmg == 1:
            return
        else:
            
            jdl = appdata.APPDATA["javainstalls"][jmg-2]
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
                    del appdata.APPDATA["javainstalls"][jmg-2]
            elif k == 118:
                jdl["ver"] = get_java_version(jdl["path"])
                if jdl["ver"] == "Error":
                    cursesplus.messagebox.showwarning(stdscr,["Java installaion is corrupt"])
                    del appdata.APPDATA["javainstalls"][jmg-2]
                else:
                    cursesplus.messagebox.showinfo(stdscr,["Java installation is safe"])

        appdata.updateappdata()

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
    
    lastreleaseinfo = requests.get("https://api.github.com/repos/Enderbyte-Programs/CraftServerSetup/releases/latest").json()
    foundurl = None
    ver = lastreleaseinfo["tag_name"]

    if compare_versions(ver.replace("v",""),APP_UF_VERSION.replace("v","")) == 1:

        for releaseasset in lastreleaseinfo["assets"]:

            url = releaseasset["browser_download_url"]
            if "installer" in url and url.endswith("exe"):
                foundurl = url

        if foundurl is not None:
            urllib.request.urlretrieve(foundurl,os.path.expandvars("%TEMP%/crssupdate.exe"))
            os.startfile(os.path.expandvars("%TEMP%/crssupdate.exe"))
        else:
            cursesplus.messagebox.showerror(stdscr,["No suitable release asset could be found.","Please report this to devs AT ONCE"])
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
            if nname in [l["name"] for l in appdata.APPDATA["servers"]]:
                #cursesplus.utils.showcursor()
                
                nname = uicomponents.crssinput(stdscr,"The name already exists. Please input a new name",prefiltext=xdat["name"])
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
            if (os.path.isfile(xdat["dir"]+"/bedrock_server.exe") and not ON_WINDOWS) or (not os.path.isfile(xdat["dir"]+"/bedrock_server.exe") and ON_WINDOWS):
                bri = True
                nwait.stop()
                cursesplus.messagebox.showinfo(stdscr,["This server was packaged on a different OS.","The new file will be downloaded on the next screen."])
                nwait.start()
        xdat["script"] = generate_script(xdat)
        appdata.APPDATA["servers"].append(xdat)
        chosensrver = len(appdata.APPDATA["servers"])
        if bri:
            availablelinks = [g for g in extract_links_from_page(requests.get("https://www.minecraft.net/en-us/download/server/bedrock",headers={"User-Agent":MODRINTH_USER_AGENT}).text) if "azureedge" in g]
            link_win_normal = get_by_list_contains(availablelinks,"win/")
            link_lx_normal = get_by_list_contains(availablelinks,"linux/")
            link_win_preview = get_by_list_contains(availablelinks,"win-preview/")
            link_lx_preview = get_by_list_contains(availablelinks,"linux-preview/")
            if ON_WINDOWS:
                availablelinks = [link_win_normal,link_win_preview]
            else:
                availablelinks = [link_lx_normal,link_lx_preview]
            nwait.stop()
            bedrock_do_update(stdscr,chosensrver,availablelinks)
            
        nwait.stop()
        nwait.destroy()

        #Make sure data is up to date
        appdata.self_compatibilize()

        cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
    except Exception as e:
        #raise e
        cursesplus.messagebox.showerror(stdscr,["An error occured importing your server.",str(e)])

def choose_server_memory_amount(stdscr) -> str:
    chop = uicomponents.menu(
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
            mtoal = uicomponents.crssinput(stdscr,"How much memory should your server get? (for example 1024M or 5G)")
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
    umethod = uicomponents.menu(stdscr,["Import from .amc file","Import from folder","Cancel (Go Back)"])
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
            nname = uicomponents.crssinput(stdscr,"Please enter the name of this server")
            while True:
                if nname in [l["name"] for l in appdata.APPDATA["servers"]]:
                    cursesplus.utils.showcursor()
                    nname = uicomponents.crssinput(stdscr,"The name already exists. Please input a new name",prefiltext=nname)
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
            xdat["version"] = uicomponents.crssinput(stdscr,"What version is your server?")
            xdat["moddable"] = cursesplus.messagebox.askyesno(stdscr,["Is this server moddable?","That is, Can it be changed with plugins/mods"])
            xdat["software"] = uicomponents.menu(stdscr,["Other/Unknown","Vanilla","Spigot","Paper","Purpur"],"What software is this server running")
            xdat["settings"] = {"legacy":True,"launchcommands":[],"exitcommands":[],"flags" : ""}
            xdat["id"] = random.randint(1111,9999)
            xdat["backupdir"] = SERVERS_BACKUP_DIR + os.sep + str(xdat["id"])
            xdat["script"] = generate_script(xdat)
            
            appdata.APPDATA["servers"].append(xdat)
            dirstack.pushd(xdat["dir"])
            with open("exdata.json","w+") as f:
                f.write(json.dumps(xdat))
            try:
                os.rename(fpl,"server.jar")#Fix problem if someone is not using server.jar as their executable jar file
            except:
                pass#Good Satan how did this bug stay in here for so long
            cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
        except Exception as e:
            cursesplus.messagebox.showerror(stdscr,["An error occured importing your server.",str(e)])
    else: return

def parse_bp_ielist(data:dict) -> list[str]:
    final = []
    for include in data["include"]:
        final.append("+ include "+include)
    for exclude in data["exclude"]:
        final.append("- exclude "+exclude)
    return final

def edit_backup_profile(stdscr,backupname: str) :
    bdata = appdata.APPDATA["backupprofiles"][backupname]
    bname = backupname
    while True:
        lditems = parse_bp_ielist(bdata)
        m = uicomponents.menu(stdscr,["FINISH","CHANGE PROFILE NAME","Delete Profile","Create Rule"]+lditems,f"Editing backup profile {bname}")
        if m == 0:
            del appdata.APPDATA["backupprofiles"][backupname]
            appdata.APPDATA["backupprofiles"][bname] = bdata
            return
        elif m == 1:
            while True:
                bname = uicomponents.crssinput(stdscr,"Name the backup profile")
                if bname in appdata.APPDATA["backupprofiles"] and bname != backupname:
                    #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
                    if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Do you want to over-write it?"]):
                        break
                else:
                    break
        elif m == 2:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this","backup profile?"]):
                del appdata.APPDATA["backupprofiles"][bname]
                return
        elif m == 3:
            wtype = uicomponents.menu(stdscr,["Cancel","Include (files to include)","Exclude (files to not include)"],"What type of rule should this be?")
            if wtype == 0:
                continue
            isexclude = wtype == 2
            imethod = uicomponents.menu(stdscr,["Handwrite a Glob pattern","Select Files/Folders"],"How would you like to input this rule?")
            pattern = [""]
            if imethod == 0:
                cursesplus.displaymsg(stdscr,[
                    "Notes for writing Glob statements",
                    "Use * for wildcard, ** for recursive wildcard",
                    "Do not end with a / for a folder, use /* or /** instead."
                ])
                pattern[0] = uicomponents.crssinput(stdscr,"Write the GLOB pattern to match. Use #SD/ for the server directory.")
            else:
                itype = uicomponents.menu(stdscr,["Choose a directory","Choose file(s)"])
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
        name = uicomponents.crssinput(stdscr,"Name the backup profile")
        if name in appdata.APPDATA["backupprofiles"]:
            if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Would you like to over-write it?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                return name
            #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
        else:
            #Add to dict
            appdata.APPDATA["backupprofiles"][name] = {
                "include" : ["#SD/*"],
                "exclude" : []
            }
            return name
    
def backup_manager(stdscr):
    while True:
        co = uicomponents.menu(stdscr,["Quit","Create backup profile"]+list(appdata.APPDATA["backupprofiles"].keys()),"Backup Profile Manager")
        if co == 0:
            appdata.updateappdata()
            return
        elif co == 1:
            edit_backup_profile(stdscr,new_backup_profile(stdscr))
        else:
            edit_backup_profile(stdscr,list(appdata.APPDATA["backupprofiles"].keys())[co-2])

def settings_mgr(stdscr):
    global COLOURS_ACTIVE
    
    while True:
        m = uicomponents.menu(stdscr,["BACK","ADVANCED OPTIONS","MANAGE JAVA INSTALLATIONS","CHANGE LANGUAGE","BACKUP PROFILES"]+[d["display"] + " : " + str(d["value"]) for d in list(appdata.APPDATA["settings"].values())],"Please choose a setting to modify")
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
                                shutil.rmtree(APPDATADIR)
                                cursesplus.messagebox.showinfo(stdscr,["Program reset."])
                                sys.exit()
                    appdata.updateappdata()
                elif n == 3:
                    shutil.rmtree(TEMPDIR)
        elif m == 2:
            managejavainstalls(stdscr)
        elif m == 3:
            eptranslate.prompt(stdscr,"Welcome to CraftServerSetup! Please choose a language to begin.")
            appdata.APPDATA["language"] = eptranslate.Config.choice
            cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        elif m == 4:
            backup_manager(stdscr)
        else:
            selm = list(appdata.APPDATA["settings"].values())[m-5]
            selk = list(appdata.APPDATA["settings"].keys())[m-5]
            if selm["type"] == "bool":
                selm["value"] = uicomponents.menu(stdscr,["True (Yes)","False (No)"],f"New value for {selm['display']}") == 0
            elif selm["type"] == "int":
                selm["value"] = cursesplus.numericinput(stdscr,f"Please choose a new value for {selm['display']}")
            elif selm["type"] == "str":
                selm["value"] = uicomponents.crssinput(stdscr,f"Please choose a new value for {selm['display']}",prefiltext=selm["value"])
            appdata.APPDATA["settings"][selk] = selm

def doc_system(stdscr):
    while True:
        z = uicomponents.menu(stdscr,["BACK","View documentation","Help on using text-based software","CONTACT SUPPORT"])
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
            source = uicomponents.menu(stdscr,["Cancel","Via E-mail","Via Discord"],"How do you wish to contact support?")
            if source == 1:
                webbrowser.open("mailto:?to=enderbyte09@gmail.com&subject=Craft Server Setup Support", new=1)
            elif source == 2:
                cursesplus.messagebox.showinfo(stdscr,["Contact @enderbyte09 on Discord"])

def license(stdscr):
    
    if not appdata.APPDATA["license"] and not ON_WINDOWS:
        if not os.path.isfile(ASSETSDIR+"/license"):
            urllib.request.urlretrieve("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/LICENSE",ASSETSDIR+"/license")
        with open(ASSETSDIR+"/license") as f:
            dat = f.read()
        cursesplus.textview(stdscr,text=dat,requireyes=True,isagreement=True,message="Please agree to the CraftServerSetup license to proceed.")
        appdata.APPDATA["license"] = True

def oobe(stdscr):
    
    if not appdata.APPDATA["hasCompletedOOBE"]:       
        stdscr.clear()
        cursesplus.displaymsg(stdscr,[t("oobe.welcome.0"),"",t("oobe.welcome.1"),t("oobe.welcome.2")])
        if not cursesplus.messagebox.askyesno(stdscr,["Do you know how to use a text-based program like this?"]):
            usertutorial(stdscr)
        if not bool(appdata.APPDATA["javainstalls"]):
            if cursesplus.messagebox.askyesno(stdscr,["You have no java installations set up","Would you like to set some up now?"]):
                managejavainstalls(stdscr)
            else:
                cursesplus.messagebox.showinfo(stdscr,["You can manage your","Java installations from the","settings menu"])
        
        if cursesplus.messagebox.askyesno(stdscr,["Would you like to change your default text editor?","YES: Choose a custom command","NO: use the default editor (usually nano)"],default=cursesplus.messagebox.MessageBoxStates.NO):
            appdata.APPDATA["settings"]["editor"]["value"] = uicomponents.crssinput(stdscr,"Please type a custom command: use %s to represent the file name")
        appdata.APPDATA["hasCompletedOOBE"] = True
        appdata.updateappdata()

def usertutorial(stdscr):
    cursesplus.messagebox.showinfo(stdscr,["This is a messagebox","Press enter to dismiss it"])
    cursesplus.messagebox.showinfo(stdscr,["This software has no mouse","You will never have to use your mouse, only your keyboard"])
    cursesplus.messagebox.askyesno(stdscr,["This is a question","Use the right and left arrows to change the highlighted options","or use Y and N on your keyboard.","Choose NO"])
    uicomponents.menu(stdscr,["Don't choose this","Don't Choose this","Choose this!"],"This is a vertical option menu. Choose the third option using the up and down arrow keys!")
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
                    dirstack.pushd("/tmp/crssupdate")
                    if os.path.isfile("/usr/bin/craftserversetup"):
                        #admin
                        spassword = uicomponents.crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(f"echo -e \"{spassword}\" | sudo -S -k python3 /tmp/crssupdate/installer install",stdout=std0,stderr=std0,shell=True)
                    else:
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(["python3","/tmp/crssupdate/installer","install"],stdout=std0,stderr=std0)
                    dirstack.popd()
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
                    spassword = uicomponents.crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
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
    
    while True:
        m = uicomponents.menu(stdscr,["BACK","Python debug prompt","Test exception handling","Global variable dump","Appdata editor"])
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
            appdata.APPDATA = cursesplus.dictedit(stdscr,appdata.APPDATA,"CRSS config")
            appdata.updateappdata()

def internet_thread(stdscr):
    init_idata(stdscr)

def update_menu(stdscr):
    global UPDATEINSTALLED
    while True:
        m = uicomponents.menu(stdscr,["Back","Check for Updates","View Changelog"])
        if m == 0:
            break
        elif m == 1:
            if ON_WINDOWS:
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
    global COLOURS_ACTIVE
    global UPDATEINSTALLED
    global _SCREEN
    global SHOW_ADVERT
    _SCREEN = stdscr
    global IN_SOURCE_TREE
    
    restart_colour()
    curses.curs_set(0)
    try:
        cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        cursesplus.utils.hidecursor()
        issue = False
        
        if _transndt:
            urllib.request.urlretrieve("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/src/translations.toml",APPDATADIR+"/translations.toml")
            eptranslate.load(APPDATADIR+"/translations.toml")
        
        if IN_SOURCE_TREE:
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
        
        stdscr.addstr(0,0,"Initializing application data...                 ")
        stdscr.refresh()
        cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        signal.signal(signal.SIGINT,sigint)
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', MODRINTH_USER_AGENT)]
        urllib.request.install_opener(opener)
        
        threading.Thread(target=internet_thread,args=(stdscr,)).start()
        appdata.setup_appdata()

        #Breakaway point for -m and -s tasks
        _scc = False
        if AUTOMANAGE_ID != 0:
            inc = 0
            for server in appdata.APPDATA["servers"]:
                if server["id"] == AUTOMANAGE_ID:
                    manage_server(stdscr,server["name"],inc+1)#chosenserver-1 used... sorry
                    _scc = True
                    break

                inc += 1
            if not _scc:
                cursesplus.messagebox.showerror(stdscr,["Unable to find requested","direct manage ID."])
        
        if AUTOSTART_ID != 0:
            inc = 0
            for server in appdata.APPDATA["servers"]:
                if server["id"] == AUTOSTART_ID:
                    os.chdir(server["dir"])
                    start_server(stdscr,server["name"],inc+1,server["dir"])
                    _scc = True
                    break

                inc += 1
            if not _scc:
                cursesplus.messagebox.showerror(stdscr,["Unable to find requested","direct start ID."])
        
        #send_telemetry()
        if appdata.APPDATA["language"] is None:
            eptranslate.prompt(stdscr,"Welcome to CraftServerSetup! Please choose a language to begin.")
            appdata.APPDATA["language"] = eptranslate.Config.choice
            cursesplus.displaymsg(stdscr,["Craft Server Setup"],False)
        license(stdscr)
        oobe(stdscr)
        if arguments.should_run_import_mode():
            import_amc_server(stdscr,arguments.get_file_to_import())      
        
        appdata.updateappdata()
        
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        introsuffix = ""
        if IN_SOURCE_TREE:
            introsuffix=" | SRC mode"
        threading.Thread(target=send_telemetry).start()

        if appdata.APPDATA["settings"]["autoupdate"]["value"]:
            if ON_WINDOWS:
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
                if DEVELOPER:
                    lz += ["Debug Tools"]
                m = uicomponents.menu(stdscr,lz,f"{t('title.welcome')} | {appdata.APPDATA['idata']['MOTD']}",f"Version {APP_UF_VERSION}{introsuffix} on {platform.system()} {platform.release()} (Python {platform.python_version()})")
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
            except Exception as e2:
                safe_error_handling(e2)
        if appdata.APPDATA["settings"]["transitions"]["value"]:
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