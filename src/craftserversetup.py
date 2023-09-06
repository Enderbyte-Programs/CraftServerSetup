#!/usr/bin/python3
VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
APP_VERSION = 1#The API Version.
APP_UF_VERSION = "0.14.1"#The semver version
UPDATEINSTALLED = False

print(f"CraftServerSetup by Enderbyte Programs v{APP_UF_VERSION} (c) 2023")

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
import socket                   #Telemetry
import hashlib                  #Calculate file hashes
import platform                 #Get system information
import threading                #Start threads
import random                   #Random number generation
import traceback                #Error management
import webbrowser               #Advertisements
import tarfile                  #Create archives

WINDOWS = platform.system() == "Windows"

### SET UP SYS.PATH TO ONLY USE my special library directory
if not WINDOWS:#Windows edition will package libraries already
    if "bin" in sys.argv[0]:
        sys.path = [s for s in sys.path if not "site-packages" in s]#Removing conflicting dirs
        sys.path.insert(1,os.path.expanduser("~/.local/lib/craftserversetup"))
        sys.path.insert(1,"/usr/lib/craftserversetup")
        DEBUG=False
        if os.path.isdir("/usr/lib/craftserversetup"):
            UTILDIR="/usr/lib/craftserversetup/utils"
        else:
            UTILDIR = os.path.expanduser("~/.local/lib/craftserversetup/utils")
    else:
        DEBUG=True
        UTILDIR="src/utils"
else:
    DEBUG = False
#Third party libraries below here
import cursesplus               #Terminal Display Control
import cursesplus.messagebox
import cursesplus.filedialog
import requests                 #Networking Utilities
import urllib.request
import urllib.error
import yaml                     #Parse YML Files

___DEFAULT_SERVER_PROPERTIES___ = """
enable-jmx-monitoring=false
rcon.port=25575
level-seed=
gamemode=survival
enable-command-block=false
enable-query=false
generator-settings={}
enforce-secure-profile=true
level-name=world
motd=A Minecraft Server
query.port=25565
pvp=true
generate-structures=true
max-chained-neighbor-updates=1000000
difficulty=easy
network-compression-threshold=256
max-tick-time=60000
require-resource-pack=false
use-native-transport=true
max-players=20
online-mode=true
enable-status=true
allow-flight=false
initial-disabled-packs=
broadcast-rcon-to-ops=true
view-distance=10
server-ip=
resource-pack-prompt=
allow-nether=true
server-port=25565
enable-rcon=false
sync-chunk-writes=true
op-permission-level=4
prevent-proxy-connections=false
hide-online-players=false
resource-pack=
entity-broadcast-range-percentage=100
simulation-distance=10
rcon.password=
player-idle-timeout=0
debug=false
force-gamemode=false
rate-limit=0
hardcore=false
white-list=false
broadcast-console-to-ops=true
spawn-npcs=true
spawn-animals=true
function-permission-level=2
initial-enabled-packs=vanilla
level-type=minecraft\:normal
text-filtering-config=
spawn-monsters=true
enforce-whitelist=false
spawn-protection=16
resource-pack-sha1=
max-world-size=29999984
"""
REPAIR_SCRIPT = """cd ~/.local/share;mkdir crss-temp;cd crss-temp;tar -xf $1;bash scripts/install.sh;cd ~;rm -rf ~/.local/share/crss-temp"""#LINUX ONLY
def sigint(signal,frame):
    if cursesplus.messagebox.askyesno(_SCREEN,["Are you sure you want to quit?"]):
        updateappdata()
        sys.exit()

def compatibilize_appdata(data:dict) -> dict:
    try:
        cver = data["version"]
    except:
        data["version"] = APP_VERSION
    return data

def internet_on():
    try:
        urllib.request.urlopen('http://google.com', timeout=5)
        return True
    except urllib.error.URLError as err: 
        return False
if not WINDOWS:
    APPDATADIR = os.path.expanduser("~/.local/share/mcserver")
    SERVERSDIR = APPDATADIR + "/servers"
    SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
    TEMPDIR = APPDATADIR + "/temp"
    BACKUPDIR = os.path.expanduser("~/.local/share/crss_backup")
else:
    APPDATADIR = os.path.expandvars("%APPDATA%/mcserver")
    SERVERSDIR = APPDATADIR + "/servers"
    SERVERS_BACKUP_DIR = APPDATADIR + "/backups"
    TEMPDIR = APPDATADIR + "/temp"
    BACKUPDIR = os.path.expandvars("%APPDATA%/crss_backup")

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
__DEFAULTAPPDATA__ = {
    "servers" : [

    ],
    "hasCompletedOOBE" : False,
    "version" : APP_VERSION,
    "javainstalls" : [

    ],
    "productKey" : "",
    "pkd" : False
}

ADLIB_BASE = "https://pastebin.com/raw/Jm1NV9u6"#   I'm sorry I had to do this.
ADS = []

def gen_adverts():
    d = requests.get(ADLIB_BASE).text
    for ad in d.splitlines():
        if ad == "":
            continue
        ADS.append(Advertisement(ad.split("|")[0],ad.split("|")[1].replace("\\n","\n")))

def verify_product_key(key:str) -> bool:
    try:
        if len(key) < 8:
            return False
        else:
            if int(key) == 0:
                return False
            elif (int(key[0]) + int(key[2]) == int(key[3])) and (int(key[6]) - int(key[4]) == int(key[1])) and (int(key[7]) * int(key[5]) < 50):
                return True
            
            else:
                return False
    except:
        return False
def generate_product_key() -> str:
    while True:
        l1 = random.randint(0,5)
        
        l3 = random.randint(0,4)
        l4 = l1 + l3
        l5 = random.randint(0,5)
        l6 = random.randint(0,9)
        l7 = random.randint(0,9)
        l2 = l7 - l5
        if l2 < 0:
            continue
        l8 = random.randint(0,9)

        assembled = f"{l1}{l2}{l3}{l4}{l5}{l6}{l7}{l8}"
        if verify_product_key(assembled):
            return assembled

def product_key_page(stdscr):
    while True:
        o = cursesplus.displayops(stdscr,["Register Product key","How to register a product key","Use without product key :("],"You have not yet inserted a valid product key.")
        if o == 2:
            cursesplus.messagebox.showinfo(stdscr,["You can upgrade any time from the main menu"])
            return
        elif o == 1:
            stdscr.clear()
            stdscr.addstr(0,0,"1. Send $2 CAD or equivilant to @enderbyte09 on PayPal")
            stdscr.addstr(1,0,"2. Send an email to enderbyte09@gmail.com that includes your PayPal username")
            stdscr.addstr(2,0,"3. I will send you a return email with your product key as soon as I can")
            stdscr.addstr(4,0,"Press any key to proceed")
            stdscr.refresh()
            stdscr.getch()
        elif o == 0:
            npk = cursesplus.cursesinput(stdscr,"Please enter your productkey",1,8)
            #npk = str(cursesplus.numericinput(stdscr,""))
            if not verify_product_key(npk):
                cursesplus.messagebox.showwarning(stdscr,["Invalid key"])
            else:
                APPDATA["productKey"] = npk
                cursesplus.messagebox.showinfo(stdscr,["Registered!",":D"],"Success")
                updateappdata()
                return

### BEGIN UTILS ###

def create_global_backup(outpath:str) -> int:
    try:
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        pushd(APPDATADIR)
        with tarfile.open(outpath,"w:xz") as tar:
            tar.add(".")
        popd()
        return 0
    except:
        return 1


def restore_global_backup(backup_file:str) -> int:
    try:
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        if not os.path.isdir(BACKUPDIR+"/tempbk"):
            pass
        else:
            shutil.rmtree(BACKUPDIR+"/tempbk")
        shutil.copytree(APPDATADIR,BACKUPDIR+"/tempbk")
        try:
            shutil.rmtree(APPDATADIR)
            os.mkdir(APPDATADIR)
            with tarfile.open(backup_file,"r:xz") as tar:
                tar.extractall(path=APPDATADIR)
        except:
            os.mkdir(APPDATADIR)
            shutil.copytree(BACKUPDIR+"/tempbk",APPDATADIR)
            shutil.rmtree(BACKUPDIR+"/tempbk")
            return 1
            
        return 0
    except:
        return 1

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
        os.mkdir(outdir)
        pushd(outdir)
        with tarfile.open(infile,"r:xz") as tar:
            tar.extractall(".")
        popd()
    except:
        return 1
    return 0

### END UTILS

def send_telemetry():
    try:
        s = socket.socket()
        s.connect(('enderbyteprograms.ddnsfree.com',11111))
        s.sendall(f"GET /api/amcs/os={platform.platform()}&ver={APP_UF_VERSION} HTTP/1.1".encode())
        s.close()
    except:
        pass
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
    global _SCREEN
    _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
    
    while True:
        erz = cursesplus.displayops(_SCREEN,["Exit Program","View Error info","Return to main menu","Advanced options"],f"{message}. What do you want to do?")
        if erz == 0:
            sys.exit(1)
        elif erz == 1:
            _SCREEN.clear()
            _SCREEN.addstr(0,0,f"TYPE: {type(e)}")
            _SCREEN.addstr(1,0,f"MESSAGE: {str(e)[0:os.get_terminal_size()[0]-1]}")
            ztb = traceback.format_exc().splitlines()
            ex = 2
            for eline in ztb:
                try:
                    _SCREEN.addstr(ex,0,eline[0:os.get_terminal_size()[0]-1])
                except:
                    break
                ex += 1
            _SCREEN.addstr(os.get_terminal_size()[1]-1,0,"Press any key to return")
            _SCREEN.refresh()
            _SCREEN.getch()
        elif erz == 2:
            if cursesplus.messagebox.askyesno(_SCREEN,["Do you want to update the most recent App data?","If you suspect your appdata is corrupt, do not say yes"]):
                updateappdata()
            _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLACK,cursesplus.WHITE))
            main(_SCREEN)
        elif erz == 3:
            while True:
                aerz = cursesplus.displayops(_SCREEN,["Back","Restore a backup","Repair CraftServerSetup","Reset CraftServerSetup","Use emergency command prompt"],"Please choose an advanced option")
                if aerz == 0:
                    break
                elif aerz == 1:
                    load_backup(_SCREEN)
                elif aerz == 2:
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
                elif aerz == 3:
                    if cursesplus.messagebox.askyesno(_SCREEN,["This will delete all servers","Are you sure you wish to proceed?"]):
                        os.chdir(os.path.expanduser("~"))
                        try:
                            shutil.rmtree(APPDATADIR)
                            os.mkdir(APPDATADIR)
                            sys.exit(1)
                        except:
                            cursesplus.messagebox.showerror(_SCREEN,["Failed to wipe"])
                elif aerz == 4:
                    _SCREEN.clear()
                    _SCREEN.erase()
                    _SCREEN.bkgd(cursesplus.set_color(cursesplus.BLACK,cursesplus.WHITE))
                    _SCREEN.refresh()
                    curses.reset_shell_mode()
                    print("Run exit to return")
                    cursesplus.showcursor()
                    while True:
                        
                        epp = input("Python >")
                        if epp == "exit":
                            break
                        try:
                            exec(epp)
                        except Exception as ex:    
                            print(f"ER {type(ex)}\nMSG {str(ex)}")
                    curses.reset_prog_mode()
                    cursesplus.hidecursor()
                    _SCREEN.bkgd(cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
    
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
        return "Error"

def manage_whitelist(stdscr,whitefile:str):
    with open(whitefile) as f:
        dat = json.load(f)
    while True:
        dop = cursesplus.displayops(stdscr,["ADD PLAYER","FINISH"]+[p["name"] for p in dat],"Choose a player to remove")
        if dop == 1:
            with open(whitefile,"w+") as f:
                f.write(json.dumps(dat))
            return
        elif dop == 0:
            cursesplus.showcursor()
            name = cursesplus.cursesinput(stdscr,"Name(s) of players allowed: (Seperate with commas)")
            cursesplus.hidecursor()
            names = name.split(",")
            for player in names:
                cursesplus.displaymsgnodelay(stdscr,[player])
                try:
                    pluid = get_player_uuid(player)
                except:
                    pass
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
            final[key] = val
        return final
    @staticmethod
    def dump(d: dict) -> str:
        l = ""
        for f in d.items():
            lout = f[1]
            if isinstance(lout,bool):
                if lout:
                    lout = "true"
                else:
                    lout = "false"
            elif isinstance(lout,int) or isinstance(lout,float):
                lout = str(lout)
            l += f[0] + "=" + str(lout) + "\n"
        return l

def package_server(stdscr,serverdir:str,chosenserver:int):
    sdata = APPDATA["servers"][chosenserver]
    with open(serverdir+"/exdata.json","w+") as f:
        f.write(json.dumps(sdata))
        #Write server data into a temporary file
    wdir=cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a folder for the output server file")
    wxfileout=wdir+"/"+sdata["name"]+".amc"
    nwait = cursesplus.PleaseWaitScreen(stdscr,["Packaging Server"])
    nwait.start()
    package_server_script(wdir,wxfileout)
    nwait.stop()
    nwait.destroy()
    #if pr != 0:
    #    cursesplus.messagebox.showerror(stdscr,["An error occured packaging your server"])
    os.remove(serverdir+"/exdata.json")
    cursesplus.messagebox.showinfo(stdscr,["Server is packaged."])
    
def setupnewserver(stdscr):
    stdscr.erase()
    serversoftware = cursesplus.displayops(stdscr,["Cancel","Vanilla (Normal)","Spigot","Paper"],"Please choose your server software")
    if serversoftware == 0:
        return
    elif serversoftware == 1:
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
        curses.curs_set(1)
        servername = cursesplus.cursesinput(stdscr,"What is the name of your server?").strip()
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
    p = cursesplus.ProgressBar(stdscr,6,cursesplus.ProgressBarTypes.FullScreenProgressBar,message="Setting up server")
    p.step("Getting download data",True)
    njavapath = choose_java_install(stdscr)
    if serversoftware == 1:
        S_DOWNLOAD_data = PACKAGEDATA["downloads"]["server"]
        S_DOWNLOAD_size = parse_size(S_DOWNLOAD_data["size"])
        p.appendlog(f"SIZE: {S_DOWNLOAD_size}")
        p.appendlog(f"URL: {S_DOWNLOAD_data['url']}")
        p.step("Downloading",True)
        urllib.request.urlretrieve(S_DOWNLOAD_data["url"],S_INSTALL_DIR+"/server.jar")
    elif serversoftware == 2:
        
        p.max = 8
        p.step("Getting build file")
        urllib.request.urlretrieve("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar",S_INSTALL_DIR+"/BuildTools.jar")
        os.chdir(S_INSTALL_DIR)
        p.step("Building Spigot")
        while True:
            build_lver = cursesplus.messagebox.askyesno(stdscr,["Do you want to build the latest version of Spigot?","YES: Latest version","NO: different version"])
            if not build_lver:
                curses.curs_set(1)
                xver = cursesplus.cursesinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
                curses.curs_set(0)
            else:
                xver = "latest"
            PACKAGEDATA = {"id":xver}
            proc = subprocess.Popen([njavapath,"-jar","BuildTools.jar","--rev",xver],shell=False,stdout=subprocess.PIPE)
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
    elif serversoftware == 3:
        VMAN = requests.get("https://papermc.io/api/v2/projects/paper").json()
        stdscr.erase()
        pxver = list(reversed(VMAN["versions"]))[cursesplus.optionmenu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
        BMAN = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds").json()
        buildslist = list(reversed(BMAN["builds"]))
        
        if cursesplus.messagebox.askyesno(stdscr,["Would you like to install the latest build of Paper","It is highly recommended to do so"]):
            builddat = buildslist[0]
        else:
            stdscr.erase()
            builddat = buildslist[cursesplus.optionmenu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
        bdownload = f'https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'
        #cursesplus.displaymsg(stdscr,[f'https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'])
        p.step("Downloading",True)
        
        urllib.request.urlretrieve(bdownload,S_INSTALL_DIR+"/server.jar")
        PACKAGEDATA = {"id":VMAN["versions"][VMAN["versions"].index(pxver)]}


    p.step("Checking stuff",True)
    setupeula = cursesplus.messagebox.askyesno(stdscr,["To proceed, you must agree","To Mojang's EULA","","Do you agree?"])
    if setupeula:
        with open(S_INSTALL_DIR+"/eula.txt","w+") as f:
            f.write("eula=true")# Agree
    
    
    stdscr.clear()
    stdscr.erase()
    p.step("Preparing scripts",True)
    userecmem = cursesplus.messagebox.askyesno(stdscr,["Do you want to use the","default amount of memory","YES: Use default","NO: Set custom amount of memory"])
    if not userecmem:
        while True:
            curses.curs_set(1)
            memorytoall: str = cursesplus.cursesinput(stdscr,"How much memory should the server get? (EX: 1024M, 5G)")
            curses.curs_set(0)
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
    else:
        if serversoftware == 1:
            #Vanilla
            memorytoall = "1024M"
        else:
            memorytoall = "2G"#Bukkit
    njavapath = njavapath.replace("//","/")
    _space = "\\ "
    __SCRIPT__ = f"{njavapath.replace(' ',_space)} -jar -Xms{memorytoall} -Xmx{memorytoall} \"{S_INSTALL_DIR}/server.jar\" nogui"
    p.step("All done!",True)
    serverid = random.randint(1111,9999)
    APPDATA["servers"].append({"name":servername,"javapath":njavapath,"memory":memorytoall,"dir":S_INSTALL_DIR,"version":PACKAGEDATA["id"],"moddable":serversoftware!=1,"software":serversoftware,"script":__SCRIPT__,"id":serverid})
    updateappdata()
    bdir = os.getcwd()
    os.chdir(S_INSTALL_DIR)
    advancedsetup = cursesplus.messagebox.askyesno(stdscr,["Would you like to set up your server configuration now?"])
    if not advancedsetup:
        cursesplus.messagebox.showinfo(stdscr,["Default configuration will be generated when you start your server"])
    else:
        data = setup_server_properties(stdscr)
        with open("server.properties","w+") as f:
            f.write(PropertiesParse.dump(data))
    os.chdir(bdir)

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

def setup_new_world(stdscr,dpp:dict,serverdir=os.getcwd()) -> dict:

    while True:
        dpp["level-name"] = cursesplus.cursesinput(stdscr,"What should your world be called")
        if os.path.isdir(serverdir+"/"+dpp["level-name"]):
            if cursesplus.messagebox.showwarning(stdscr,["This world may already exist.","Are you sure you want to edit its settings?"]):
                break
        else:
            break
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to use a custom seed?","Answer no for a random seed"]):
        dpp["level-seed"] = cursesplus.cursesinput(stdscr,"What should the seed be?")
    wtype = cursesplus.displayops(stdscr,["Normal","Flat","Large Biome","Amplified","Single Biome","Buffet (1.15 and before)","Customized (1.12 and before)","Other (custom namespace)"],"Please choose the type of world.")
    if wtype == 7:
        wname = cursesplus.cursesinput(stdscr,"Please type the full name of the custom world type")
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
               dpp["generator-settings"] = cursesplus.cursesinput(stdscr,f"Please type generator settings for {wname}") 
        else:
            dpp["generator-settings"] = cursesplus.cursesinput(stdscr,f"Please type generator settings for {wname}")
    return dpp
def setup_server_properties(stdscr) -> dict:
    dpp = PropertiesParse.load(___DEFAULT_SERVER_PROPERTIES___)
    cursesplus.showcursor()
    while True:
        lssl = cursesplus.displayops(stdscr,["Basic Settings","World Settings","Advanced Settings","Network Settings","FINISH"],"Server Configuration Setup")
        #Go through all of the properties 1 by 1...
        if lssl == 4:
            cursesplus.hidecursor()
            return dpp
        elif lssl == 3:
            #Network Settings
            dpp["enable-rcon"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable Remote CONtrol on this server?","WARNING: This could be dangerous"])
            if dpp["enable-rcon"]:
                dpp["broadcast-rcon-to-ops"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable RCON (Remote CONtrol) output to operators?"])
                dpp["rcon.password"] = cursesplus.cursesinput(stdscr,"Please input RCON password",passwordchar="*")
                dpp["rcon.port"] = cursesplus.numericinput(stdscr,"Please input the RCON port: (default 25575)",False,False,1,65535,25575)

            dpp["enable-status"] = not cursesplus.messagebox.askyesno(stdscr,["Would you like to hide this server's status?"])
            dpp["enable-query"] = not cursesplus.messagebox.askyesno(stdscr,["Would you like to hide this server's player count?"])
            dpp["hide-online-players"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to hide the player list?"])
            dpp["prevent-proxy-connection"] = not cursesplus.messagebox.askyesno(stdscr,["Do you want to allow proxy connections?"])
            dpp["query.port"] = cursesplus.numericinput(stdscr,"Please input the query port: (default 25565)",False,False,1,65535,25565)        
            dpp["server-port"] = cursesplus.numericinput(stdscr,"Please input the port that this server listens on: (default 25565)",False,False,1,65535,25565)  

        elif lssl == 2:
            #Advanced settings
            dpp["broadcast-console-to-ops"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable verbose output to operators?"])
            dpp["entity-broadcast-range-percentage"] = cursesplus.numericinput(stdscr,"What distance percentage should entities be sent to the client?",minimum=10,maximum=1000,prefillnumber=100)
            #dpp["enforce-secure-profile"] = not cursesplus.messagebox.askyesno(stdscr,["Do you want to allow cracked accounts to join?"])
            seclevel = cursesplus.displayops(stdscr,["Maximum (reccommended) - Secure profile and valid account","Moderate - Valid account, secure profile not required","Minimum - Cracked / illegal accounts permitted"],"Please choose a security option")
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
                    #TODO Add whitelist manager
                    whitelist_manager(stdscr,os.getcwd())
                if cursesplus.messagebox.askyesno(stdscr,["Do you want to enfore the white list?"]):
                    dpp["enforce-whitelist"] = True
            dpp["force-gamemode"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to force players to use the default game mode?"])
            dpp["function-permission-level"] = cursesplus.displayops(stdscr,["1 (Bypass spawn protection)","2 (Singleplayer commands)","3 (Player management (ban/kick))","4 (Manage server)"],"Please choose the default op admin level") + 1
            dpp["max-chained-neighbor-updates"] = cursesplus.numericinput(stdscr,"Please input maximum chained neighboue updates",allownegatives=True,minimum=-1,prefillnumber=1000000)
            dpp["max-tick-time"] = cursesplus.numericinput(stdscr,"How many milliseconds should watchdog wait?",False,True,-1,2**32,60000)
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to enable anti-afk?"]):
                dpp["player-idle-timeout"] = cursesplus.numericinput(stdscr,"Minutes of AFK before player is kicked:",False,False,0,1000000)
            else:
                dpp["player-idle-timeout"] = 0
            
        elif lssl == 0:
            #basic
            dpp["allow-flight"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable flight for non-admins?"])
            dpp["allow-nether"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable the nether on this server?"])
            dpp["generate-structures"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable structure generation on this server?"])
            dpp["hardcore"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable hardcore mode on this server?"])
            dpp["difficulty"] = str(cursesplus.optionmenu(stdscr,["Peaceful","Easy","Normal","Hard"],"Please select the difficulty of your server"))
            dpp["gamemode"] = str(cursesplus.optionmenu(stdscr,["survival","creative","adventure","spectator"],"Please select the gamemode of your server"))
            dpp["enable-command-block"] = cursesplus.messagebox.askyesno(stdscr,["Would you like to enable command blocks on your server?"])
            dpp["max-players"] = cursesplus.numericinput(stdscr,"How many players should be allowed? (max players)",minimum=1,maximum=1000000,prefillnumber=20)
            dpp["motd"] = "\\n".join(cursesplus.cursesinput(stdscr,"What should your server message say?",2,59).splitlines())
            dpp["pvp"] = cursesplus.messagebox.askyesno(stdscr,["Do you want to allow PVP?"])
            dpp["simulation-distance"] = cursesplus.numericinput(stdscr,"What should the maximum simulation distance on the server be?",False,False,2,32,10)
            dpp["view-distance"] = cursesplus.numericinput(stdscr,"What should the maximum view distance on the server be?",False,False,2,32,10)
            dpp["spawn-animals"] = cursesplus.messagebox.askyesno(stdscr,["Spawn animals?"])
            dpp["spawn-monsters"] = cursesplus.messagebox.askyesno(stdscr,["Spawn monsters?"])
            dpp["spawn-npcs"] = cursesplus.messagebox.askyesno(stdscr,["Spawn villagers?"])
            
        elif lssl == 1:
            #world
            dpp = setup_new_world(stdscr,dpp)

def resource_pack_setup(stdscr,serverdata:dict) -> dict:
    nyi(stdscr)

def whitelist_manager(stdscr,serverdir:str):
    nyi(stdscr)

def servermgrmenu(stdscr):
    stdscr.clear()
    global APPDATA
    chosenserver = cursesplus.displayops(stdscr,["Back"]+[a["name"] for a in APPDATA["servers"]],"Please choose a server")
    if chosenserver == 0:
        return
    else:
        _sname = [a["dir"] for a in APPDATA["servers"]][chosenserver-1]
        if os.path.isdir(_sname):
            manage_server(stdscr,_sname,chosenserver)
            updateappdata()

        else:
            cursesplus.displaymsg(stdscr,["ERROR","Server not found"])
            
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
    final = []
    for jf in ltk:
        try:
            final.append(jar_get_bukkit_plugin_name(jf))
        except Exception as e:
            cursesplus.displayerror(_SCREEN,e,"er")
            final.append({"version":"???","name":fob,"mcversion":"","path":path})#There was a problem loading this plugin file
    return final

def file_get_md5(path: str) -> str:
    with open(path,'rb') as f:
        data = f.read()
    return hashlib.md5(data).hexdigest()

def svr_mod_mgr(stdscr,SERVERDIRECTORY: str):
    modsforlder = SERVERDIRECTORY + "/plugins"
    if not os.path.isdir(modsforlder):
        os.mkdir(modsforlder)
    while True:
        PLUGSLIST = retr_jplug(modsforlder)
        spldi = cursesplus.displayops(stdscr,["BACK","ADD PLUGIN"]+[f["name"]+" ("+f["version"]+")" for f in PLUGSLIST])
        if spldi == 0:
            return
        elif spldi == 1:
            #add mod
            modfiles = cursesplus.filedialog.openfilesdialog(stdscr,"Please choose the plugins you would like to add",[["*.jar","JAR Executables"],["*","All files"]])
            for modfile in modfiles:
                if os.path.isfile(modfile):
                    stdscr.clear()
                    cursesplus.displaymsgnodelay(stdscr,["loading plugin",modfile])
                    mf_name = os.path.split(modfile)[1]
                    try:
                        jar_get_bukkit_plugin_name(modfile)
                    except:
                        
                        if not cursesplus.messagebox.askyesno(stdscr,[f"file {modfile} may not be a Minecraft plugin.","Are you sure you want to add it to your server?"]):
                            continue
                    shutil.copyfile(modfile,modsforlder+"/"+mf_name)
            stdscr.erase()
        else:
            chosenplug = spldi - 2
            while True:
                stdscr.erase()
                activeplug = PLUGSLIST[chosenplug]
                stdscr.addstr(0,0,"PLUGIN INFO")
                stdscr.addstr(2,0,"Plugin Name")
                stdscr.addstr(3,0,"Plugin Version")
                stdscr.addstr(4,0,"Minecraft Version")
                stdscr.addstr(5,0,"File path")
                stdscr.addstr(6,0,"File size")
                stdscr.addstr(7,0,"MD5 sum")
                stdscr.addstr(2,20,activeplug["name"])
                stdscr.addstr(3,20,activeplug["version"])
                stdscr.addstr(4,20,activeplug["mcversion"])
                stdscr.addstr(5,20,activeplug["path"])
                stdscr.addstr(6,20,parse_size(os.path.getsize(activeplug["path"])))
                stdscr.addstr(7,20,file_get_md5(activeplug["path"]))
                stdscr.addstr(8,0,"PRESS D TO DELETE PLUGIN. PRESS ENTER TO GO BACK",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
                ch = stdscr.getch()
                if ch == curses.KEY_ENTER or ch == 10 or ch == 13:
                    break
                elif ch == 100 or ch == 68:
                    if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this plugin from your server?"]):
                        os.remove(activeplug["path"])
                        break
            stdscr.clear()

def generate_script(svrdict: dict) -> str:
    _space = "\\ "
    __SCRIPT__ = f"#!/usr/bin/sh\n{svrdict['javapath'].replace(' ',_space)} -jar -Xms{svrdict['memory']} -Xmx{svrdict['memory']} \"{svrdict['dir']}/server.jar\" nogui"
    return __SCRIPT__

def update_s_software_preinit(serverdir:str):
    pushd(serverdir)
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
    downloadversion = cursesplus.displayops(stdscr,["Cancel"]+[v["id"] for v in VERSION_MANIFEST_DATA["versions"]],"Please choose a version")
    if downloadversion == 0:
        return
    else:
        stdscr.clear()
        cursesplus.displaymsgnodelay(stdscr,["Getting version manifest..."])
        PACKAGEDATA = requests.get(VERSION_MANIFEST_DATA["versions"][downloadversion-1]["url"]).json()
        cursesplus.displaymsgnodelay(stdscr,["Preparing new server"])
    if cursesplus.messagebox.askyesno(stdscr,["Do you want to change the java installation","associated with this server?"]):
        njavapath = choose_java_install(stdscr)
        APPDATA["servers"][chosenserver-1]["javapath"] = njavapath
    S_DOWNLOAD_data = PACKAGEDATA["downloads"]["server"]
    stdscr.clear()
    stdscr.addstr(0,0,"Downloading new server file...")
    stdscr.refresh()
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
    urllib.request.urlretrieve("https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar","BuildTools.jar")
    p.step()
    while True:
        build_lver = cursesplus.messagebox.askyesno(stdscr,["Do you want to build the latest version of Spigot?","YES: Latest version","NO: different version"])
        if not build_lver:
            curses.curs_set(1)
            xver = cursesplus.cursesinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
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
    VMAN = requests.get("https://papermc.io/api/v2/projects/paper").json()
    stdscr.erase()
    pxver = list(reversed(VMAN["versions"]))[cursesplus.optionmenu(stdscr,list(reversed(list(VMAN["versions"]))),"Please choose a version")]
    BMAN = requests.get(f"https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds").json()
    buildslist = list(reversed(BMAN["builds"]))
    
    if cursesplus.messagebox.askyesno(stdscr,["Would you like to update to the latest build of Paper","It is highly recommended to do so"]):
        builddat = buildslist[0]
    else:
        stdscr.erase()
        builddat = buildslist[cursesplus.optionmenu(stdscr,[str(p["build"]) + " ("+p["time"]+")" for p in buildslist])]
    bdownload = f'https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'
    #cursesplus.displaymsg(stdscr,[f'https://papermc.io/api/v2/projects/paper/versions/{pxver}/builds/{builddat["build"]}/downloads/{builddat["downloads"]["application"]["name"]}'])
    stdscr.clear()
    stdscr.addstr(0,0,"Downloading file...")

    urllib.request.urlretrieve(bdownload,serverdir+"/server.jar")
    PACKAGEDATA = {"id":VMAN["versions"][VMAN["versions"].index(pxver)]}
    update_s_software_postinit(PACKAGEDATA,chosenserver)
    cursesplus.messagebox.showinfo(stdscr,["Server is updated"])

def view_server_logs(stdscr,server_dir:str):
    
    logsdir = server_dir+"/logs"
    if not os.path.isdir(logsdir):
        cursesplus.messagebox.showwarning(stdscr,["This server has no logs."])
        return
    #if not cursesplus.messagebox.askyesno(stdscr,["Do you want to view that latest log?"]):#TODO Finish all log feature
    #    pass
    else:
        #textview(stdscr,logsdir+"/latest.log")
        cursesplus.textview(stdscr,file=logsdir+"/latest.log")

def load_backup(stdscr):
    backup = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a backup file",[["*.xz","XZ Backup Files"],["*","All Files"]],BACKUPDIR)
    pw = cursesplus.PleaseWaitScreen(stdscr,["Restoring"])
    pw.start()
    p = restore_global_backup(backup)
    pw.stop()
    pw.destroy()
    if p != 0:
        cursesplus.messagebox.showerror(stdscr,["There was an error installing your backup","Your installation has not been modified"])
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

def manage_server(stdscr,_sname: str,chosenserver: int):
    global APPDATA
    SERVER_DIR = _sname
    _ODIR = os.getcwd()
    os.chdir(SERVER_DIR)

    #Manager server
    while True:
        show_ad(stdscr)
        x__ops = ["Back","Start Server","Change MOTD","Advanced configuration","Delete server","Set up new world","Update Server software"]
        if APPDATA["servers"][chosenserver-1]["moddable"]:
            x__ops += ["Manage plugins"]
        else:
            x__ops += ["Convert server to moddable"]
        x__ops += ["View logs","Export server","View server info","Manage Whitelist","Manage backups"]
        w = cursesplus.displayops(stdscr,x__ops)
        if w == 0:
            stdscr.erase()
            break
        elif w == 1:
            stdscr.clear()
            stdscr.addstr(0,0,f"STARTING {str(datetime.datetime.now())[0:-5]}\n\r")
            stdscr.refresh()
            curses.curs_set(1)
            curses.reset_shell_mode()
            lretr = os.system(APPDATA["servers"][chosenserver-1]["script"])
            curses.reset_prog_mode()
            curses.curs_set(0)
            if lretr != 0:
                displog = cursesplus.messagebox.askyesno(stdscr,["Oh No! Your server crashed","Would you like to view the logs?"])
                if displog:
                    view_server_logs(stdscr,SERVER_DIR)
            stdscr.clear()
            stdscr.refresh()
        elif w == 2:
            if not os.path.isfile("server.properties"):
                cursesplus.displaymsg(stdscr,["ERROR","server.properties could not be found","Try starting your sever to generate one"])
            else:
                with open("server.properties") as f:
                    config = PropertiesParse.load(f.read())
                cursesplus.displaymsg(stdscr,["Current Message Is",config["motd"]])
                curses.curs_set(1)
                newmotd = cursesplus.cursesinput(stdscr,"Please input a new MOTD",2,59,prefiltext=config["motd"].replace("\\n","\n"))
                curses.curs_set(0)
                config["motd"] = newmotd.replace("\n","\\n")
                with open("server.properties","w+") as f:
                    f.write(PropertiesParse.dump(config))
        elif w == 3:
            __l = cursesplus.displayops(stdscr,["Cancel","Modify server properties","Modify crss Server options","Reset server configuration"])
            if __l == 0:
                continue
            elif __l == 1:
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
                            cursesplus.displaymsg(stdscr,[f"Current value of {list(config.keys())[chc-1]} Is",list(config.values())[chc-1]])
                            if cursesplus.messagebox.askyesno(stdscr,["Do you want to change this value?"]):
                                curses.curs_set(1)
                                newval = cursesplus.cursesinput(stdscr,f"Please input a new value for {list(config.keys())[chc-1]}",prefiltext=str(list(config.values())[chc-1]))
                                curses.curs_set(0)
                                config[list(config.keys())[chc-1]] = newval
                    with open("server.properties","w+") as f:
                        f.write(PropertiesParse.dump(config))
            elif __l == 2:
                dt = APPDATA["servers"][chosenserver-1]
                while True:
                    dx = cursesplus.optionmenu(stdscr,["FINISH"]+[lmx for lmx in list(dt.keys())])
                    if dx == 0:
                        APPDATA["servers"][chosenserver-1] = dt
                        break
                    else:
                        cursesplus.displaymsg(stdscr,[f"Current value of {list(dt.keys())[dx-1]} is",str(list(dt.values())[dx-1])])
                        lname = list(dt.keys())[dx-1]
                        if cursesplus.messagebox.askyesno(stdscr,["Do you want to change this value?"]):
                            if lname == "software" or lname == "moddable":
                                cursesplus.messagebox.showerror(stdscr,["This value may not be changed"])
                                continue
                            curses.curs_set(1)
                            newval = cursesplus.cursesinput(stdscr,f"Please input a new value for {list(dt.keys())[dx-1]}",prefiltext=str(list(dt.values())[dx-1]))
                            curses.curs_set(0)
                            dt[list(dt.keys())[dx-1]] = newval
                APPDATA["servers"][chosenserver-1]["script"]=generate_script(dt)
            elif __l == 3:
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to reset your server configuration","You won't delete any worlds"]):
                    os.remove("server.properties")
                    if cursesplus.messagebox.askyesno(stdscr,["Do you want to set up some more server configuration"]):
                        sd = setup_server_properties(stdscr)
                        with open("server.properties","w+") as f:
                            f.write(PropertiesParse.dump(sd))
        elif w == 4:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER"]):
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure that you want to delete this server?","It will be GONE FOREVER","THIS IS YOUR LAST CHANCE"]):
                    os.chdir(SERVERSDIR)
                    shutil.rmtree(SERVER_DIR)
                    del APPDATA["servers"][chosenserver-1]
                    cursesplus.messagebox.showinfo(stdscr,["Deleted server"])
                    stdscr.clear()
                    break
            stdscr.erase()
        elif w == 6:
            if not APPDATA["servers"][chosenserver-1]["moddable"]:
                update_vanilla_software(stdscr,os.getcwd(),chosenserver)
            elif APPDATA["servers"][chosenserver-1]["software"] == 3:
                update_paper_software(stdscr,os.getcwd(),chosenserver)
            elif APPDATA["servers"][chosenserver-1]["software"] == 2:
                update_spigot_software(stdscr,os.getcwd(),chosenserver)
            else:
                nyi(stdscr)
        elif w == 7 and APPDATA["servers"][chosenserver-1]["moddable"]:
            svr_mod_mgr(stdscr,SERVER_DIR)
        elif w == 7 and not APPDATA["servers"][chosenserver-1]["moddable"]:
            nyi(stdscr)
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
            manage_whitelist(stdscr,SERVER_DIR+"/whitelist.json")
        elif w == 12:
            server_backups(stdscr,SERVER_DIR,APPDATA["servers"][chosenserver-1])
_SCREEN = None
def server_backups(stdscr,serverdir:str,serverdata:dict):
    LBKDIR = SERVERS_BACKUP_DIR + "/" + str(serverdata["id"])
    if not os.path.isdir(LBKDIR):
        os.mkdir(LBKDIR)
    while True:
        z = cursesplus.displayops(stdscr,["Back","Create a Backup","Load a Backup"])
        if z == 0:
            break
        elif z == 1:
            if cursesplus.messagebox.askyesno(stdscr,[f"This will take up {parse_size(get_tree_size(serverdir))}","of disk space","Do you want to proceed?"]):
                #os.mkdir(LBKDIR+"/"+str(datetime.datetime.now())[0:-7].replace(" ","_").replace(":",""))
                cursesplus.displaymsgnodelay(stdscr,["Creating Backup..."])
                shutil.copytree(serverdir,LBKDIR+"/"+str(datetime.datetime.now())[0:-7].replace(" ","_").replace(":",""))
                cursesplus.messagebox.showinfo(stdscr,["Backup completed"])
        elif z == 2:
            if len(os.listdir(LBKDIR)) == 0:
                cursesplus.messagebox.showwarning(stdscr,["You do not have any backups"])
                continue
            if cursesplus.messagebox.askyesno(stdscr,["This will completely overwrite your server directory","Are you sure you wish to proceed"]):
                selbk = cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a backup dir",directory=LBKDIR)
                cursesplus.displaymsgnodelay(stdscr,["Restore Backup"])
                os.chdir("/")
                shutil.rmtree(serverdir)
                shutil.copytree(selbk,serverdir)
                cursesplus.messagebox.showinfo(stdscr,["Restore completed"])              

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
        f.write(json.dumps(APPDATA))
def nyi(stdscr):
    cursesplus.messagebox.showerror(stdscr,["Not Yet Implemented"],colour=True)
    stdscr.erase()
def choose_java_install(stdscr) -> str:
    #Return path of selected java
    while True:
        stdscr.erase()
        jsl = cursesplus.optionmenu(stdscr,["ADD NEW INSTALLATION"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in APPDATA["javainstalls"]],"Please choose a Java installation from the list")
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
        if os.system("java --help") == 0:
        
            APPDATA["javainstalls"].append({"path":"java","ver":get_java_version()})
        stdscr.clear()
    while True:
        stdscr.erase()
        jmg = cursesplus.optionmenu(stdscr,["ADD INSTALLATION","FINISH"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in APPDATA["javainstalls"]])
        if jmg == 0:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a java executable",directory=os.path.expanduser("~"))
            if os.system(njavapath+" -version > /dev/null 2>&1") != 0:
                if not cursesplus.messagebox.askyesno(stdscr,["You have selected an invalid java file.","Would you like to try again?"]):
                    break
            else:
                fver = get_java_version(njavapath)
                ndict = {"path":njavapath,"ver":fver}
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
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to remove the java installation",jdl["path"]]):
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

def windows_update_software(stdscr):
    cursesplus.displaymsgnodelay(stdscr,["Checking for updates"])
    td = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/update.txt").text
    tdz = td.split("|")
    svr = tdz[1]
    url = tdz[0]
    msg = tdz[2]
    if compare_versions(svr,APP_UF_VERSION) == 1:
        #NUA
        if cursesplus.messagebox.askyesno(stdscr,["There is a new update available.",f"{svr} over {APP_UF_VERSION}",msg,"Would you like to install it?"]):
            cursesplus.displaymsgnodelay(stdscr,["Downloading new update..."])
            urllib.request.urlretrieve(url,os.path.expandvars("%TEMP%/crssupdate.exe"))
            os.startfile(os.path.expandvars("%TEMP%/crssupdate.exe"))
            sys.exit()
    else:
        cursesplus.messagebox.showinfo(stdscr,["No new updates are available"])

def import_server(stdscr):
    umethod = cursesplus.displayops(stdscr,["Import from .amc file","Import from folder"])
    if umethod == 0:
        chlx = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a file",filter=[["*.amc","Minecraft Server file"],["*.xz","xz archive"],["*.tar","tar archive"]])
        nwait = cursesplus.PleaseWaitScreen(stdscr,["Unpacking Server"])
        nwait.start()
        smd5 = file_get_md5(chlx)
        if os.path.isdir(f"{TEMPDIR}/{smd5}"):
            shutil.rmtree(f"{TEMPDIR}/{smd5}")
        #s = os.system(f"bash {UTILDIR}/unpackage_server.sh \"{chlx}\" \"{TEMPDIR}/{smd5}\"")
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
                    cursesplus.showcursor()
                    nname = cursesplus.cursesinput(stdscr,"The name already exists. Please input a new name",prefiltext=xdat["name"])
                    cursesplus.hidecursor()
                else:
                    xdat["name"] = nname
                    break
            nwait.start()
            #os.mkdir(SERVERSDIR+"/"+nname)
            shutil.copytree(f"{TEMPDIR}/{smd5}",SERVERSDIR+"/"+nname)
            xdat["dir"] = SERVERSDIR+"/"+nname
            xdat["javapath"] = choose_java_install(stdscr)
            xdat["script"] = generate_script(xdat)
            APPDATA["servers"].append(xdat)
            nwait.stop()
            nwait.destroy()
            cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
        except:
            cursesplus.messagebox.showerror(stdscr,["An error occured importing your server."])
    else:
        try:
            xdat = {}#Dict of server data
            ddir = cursesplus.filedialog.openfolderdialog(stdscr,"Choose the folder of the server you want to import")
            ffile = cursesplus.filedialog.openfiledialog(stdscr,"Please choose the server JAR file",[["*.jar","Java Archive files"],["*","All Files"]],ddir)
            fpl = os.path.split(ffile)[1]
            delaftercomplete = cursesplus.messagebox.askyesno(stdscr,["Delete original folder after import?"])
            nname = cursesplus.cursesinput(stdscr,"Please enter the name of this server")
            while True:
                if nname in [l["name"] for l in APPDATA["servers"]]:
                    cursesplus.showcursor()
                    nname = cursesplus.cursesinput(stdscr,"The name already exists. Please input a new name",prefiltext=nname)
                    cursesplus.hidecursor()
                else:
                    xdat["name"] = nname
                    break
            p = cursesplus.PleaseWaitScreen(stdscr,["Copying"])
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
            while True:
                curses.curs_set(1)
                memorytoall: str = cursesplus.cursesinput(stdscr,"How much memory should the server get? (EX: 1024M, 5G)")
                curses.curs_set(0)
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
            xdat["memory"] = memorytoall
            xdat["version"] = cursesplus.cursesinput(stdscr,"What version is your server?")
            xdat["moddable"] = cursesplus.messagebox.askyesno(stdscr,["Is this server moddable?"])
            xdat["software"] = cursesplus.displayops(stdscr,["Vanilla","Spigot","Paper"],"What software is this server running") + 1
            xdat["script"] = generate_script(xdat)
            APPDATA["servers"].append(xdat)
            cursesplus.messagebox.showinfo(stdscr,["Server is imported"])
        except:
            cursesplus.messagebox.showerror(stdscr,["An error occured importing your server."])

class Advertisement:
    def __init__(self,url:str,msg:str):
        self.url = url
        self.message = msg
    def show(self,stdscr):
        if cursesplus.messagebox.askyesno(stdscr,["Advertisement",""] + self.message.splitlines() + ["","Open website?","Upgrade with a product key to remove ads"]):
            webbrowser.open(self.url)

def show_ad(stdscr):
    if APPDATA["productKey"] == "" or not verify_product_key(APPDATA["productKey"]):

        if random.randint(0,5) == 3:
            ad = random.choice(ADS)
            ad.show(stdscr) 

def main(stdscr):
    global VERSION_MANIFEST
    global VERSION_MANIFEST_DATA
    global APPDATAFILE
    global UPDATEINSTALLED
    global _SCREEN
    _SCREEN = stdscr
    global DEBUG
    curses.start_color()
    curses.curs_set(0)
    try:
        cursesplus.displaymsgnodelay(stdscr,["Craft Server Setup","Starting..."])
        issue = False
        if DEBUG:
            stdscr.addstr(0,0,"WARNING: This program is running from its source tree!",cursesplus.set_colour(cursesplus.BLACK,cursesplus.YELLOW))
            stdscr.refresh()
            issue = True
        if os.path.isdir("/usr/lib/craftserversetup") and os.path.isdir(os.path.expanduser("~/.local/lib/craftserversetup")):
            stdscr.addstr(1,0,"ERROR: Conflicting installations of crss were found! Some issues may occur",cursesplus.set_colour(cursesplus.BLACK,cursesplus.RED))
            stdscr.refresh()
            issue = True
        if issue:
            sleep(5)
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        global APPDATA
        signal.signal(signal.SIGINT,sigint)
        gen_adverts()
        threading.Thread(target=send_telemetry).start()
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

        #Graphics support loading
        if not internet_on():
            if not cursesplus.messagebox.askyesno(stdscr,["WARNING","No internet connection could be found!","You may run in to errors","Are you sure you want to continue?"]):
                return
        VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
        
        if not APPDATA["hasCompletedOOBE"]:
            stdscr.clear()
            cursesplus.displaymsg(stdscr,["CraftServerSetup OOBE","","Welcome to Craft Server Setup: The best way to make a Minecraft server","This guide will help you set up your first Minecraft Server"])
            if not bool(APPDATA["javainstalls"]):
                if cursesplus.messagebox.askyesno(stdscr,["You have no java installations set up","Would you like to set some up now?"]):
                    managejavainstalls(stdscr)
                else:
                    cursesplus.messagebox.showinfo(stdscr,["You can manage your","Java installations from the","Main menu"])
            setupservernow = False
            setupservernow = cursesplus.messagebox.askyesno(stdscr,["crss OOBE","","Would you like to set up a server now?"])
            stdscr.clear()
            if setupservernow:
                
                setupnewserver(stdscr)
        

        APPDATA["hasCompletedOOBE"] = True
        updateappdata()
        mx,my = os.get_terminal_size()
        if not "productKey" in list(APPDATA.keys()):
            APPDATA["productKey"] = ""
        if not "pkd" in list(APPDATA.keys()):
            APPDATA["pkd"] = False
        if not APPDATA["pkd"]:
            product_key_page(stdscr)
        APPDATA["pkd"] = True

        #UPDATE APPDATA to 23.9.01 format
        svri = 0
        for svr in APPDATA["servers"]:
            if not "id" in svr:
                APPDATA["servers"][svri]["id"] = random.randint(1111,9999)
            svri += 1

        updateappdata()
        if not os.path.isdir(BACKUPDIR):
            os.mkdir(BACKUPDIR)
        introsuffix = ""
        if DEBUG:
            introsuffix=" | SRC DEBUG"

    #        if mx < 120 or my < 20:
    #            cursesplus.messagebox.showwarning(stdscr,["Your terminal size may be too small","Some instability may occur","For best results, set size to","at least 120x20"])
        while True:
            stdscr.erase()
            show_ad(stdscr)
            lz = ["Set up new server","Manage servers","Quit","Manage java installations","Import Server","Update CraftServerSetup","Manage global backups"]
            
            if APPDATA["productKey"] == "" or not verify_product_key(APPDATA["productKey"]):
                lz += ["Insert Product Key","Donate"]
            m = cursesplus.displayops(stdscr,lz,f"Craft Server Setup by Enderbyte Programs | VER {APP_UF_VERSION}{introsuffix}")
            if m == 2:

                sys.exit(0)
            elif m == 0:

                setupnewserver(stdscr)
            elif m == 1:
                servermgrmenu(stdscr)
            elif m == 3:
                managejavainstalls(stdscr)
            elif m == 4:
                import_server(stdscr)
            elif m == 5:

                if WINDOWS:
                    windows_update_software(stdscr)
                    continue
                if not os.path.isfile(UTILDIR+"/run_update.sh"):
                    cursesplus.messagebox.showerror(stdscr,["The update script could not be found.","Try reinstalling the program."])
                else:
                    stdscr.clear()
                    stdscr.refresh()
                    curses.reset_shell_mode()
                    r = subprocess.call(["bash",f"{UTILDIR}/run_update.sh"])
                    curses.reset_prog_mode()
                    if r == 0:
                        UPDATEINSTALLED = True
                        return#Exit for update
                    else:
                        cursesplus.messagebox.showwarning(stdscr,["Update failed."])
            elif m == 6:
                while True:
                    bkm = cursesplus.optionmenu(stdscr,["Back","Create backup","Load backup"])
                    if bkm == 1:
                        if cursesplus.messagebox.askyesno(stdscr,["This will create a backup of your entire crss installation including configuration","To create a backup of each server","Go to its management page"]):
                            cursesplus.displaymsgnodelay(stdscr,["Calculating..."])
                            mb = round(get_tree_size(APPDATADIR)/1000000,3)
                            if cursesplus.messagebox.askyesno(stdscr,[f"This will take up {mb} MB of space.","Are you sure you want to proceed?"]):
                                foln = str(datetime.datetime.now())[0:-7].replace(" ","_").replace(":","")
                                cursesplus.displaymsgnodelay(stdscr,["Creating..."])
                                p = create_global_backup(foln)
                                if p != 0:
                                    cursesplus.messagebox.showerror(stdscr,["There was an error creating your backup"])
                    elif bkm == 0:
                        break
                    elif bkm == 2:
                        load_backup(stdscr)        
            elif m == 7:
                product_key_page(stdscr)
            elif m == 8:
                cursesplus.messagebox.showinfo(stdscr,["Donate to @enderbyte09 on PayPal"])
    except Exception as e:
        error_handling(e,"A serious unspecified exception happened.")

if __name__ == "__main__":
    curses.wrapper(main)
    if UPDATEINSTALLED:
        print("""
    =============================
    Update installed successfully
    =============================""")