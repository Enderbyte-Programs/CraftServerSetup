#!/usr/bin/python3

print("Auto Minecraft Server by Enderbyte Programs (c) 2023")

VERSION_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
APP_VERSION = 1#The API Version.
APP_UF_VERSION = "0.8"#The semver version

print("Loading libraries:")
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
import traceback                #Get information about errors
import hashlib                  #Calculate file hashes

### SET UP SYS.PATH TO ONLY USE my special library directory
if "bin" in sys.argv[0]:
    sys.path = [s for s in sys.path if not "site-packages" in s]#Removing conflicting dirs
    sys.path.insert(1,os.path.expanduser("~/.local/lib/automcserver"))
    sys.path.insert(1,"/usr/lib/automcserver")
    DEBUG=False
    if os.path.isdir("/usr/lib/automcserver"):
        UTILDIR="/usr/lib/automcserver/utils"
    else:
        UTILDIR = os.path.expanduser("~/.local/lib/automcserver/utils")
else:
    DEBUG=True
    UTILDIR="src/utils"

#Third party libraries below here
import cursesplus               #Terminal Display Control
import cursesplus.messagebox
import cursesplus.filedialog
import requests                 #Networking Utilities
import urllib.request
import urllib.error
import yaml                     #Parse YML Files
print("Checking internet connection")

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
APPDATADIR = os.path.expanduser("~/.local/share/mcserver")
SERVERSDIR = APPDATADIR + "/servers"
TEMPDIR = APPDATADIR + "/temp"
if not os.path.isdir(APPDATADIR):
    os.mkdir(APPDATADIR)
if not os.path.isdir(SERVERSDIR):
    os.mkdir(SERVERSDIR)
if not os.path.isdir(TEMPDIR):
    os.mkdir(TEMPDIR)
__DEFAULTAPPDATA__ = {
    "servers" : [

    ],
    "hasCompletedOOBE" : False,
    "version" : APP_VERSION,
    "javainstalls" : [

    ]
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
def get_java_version(file="java") -> str:
    try:
        return subprocess.check_output(fr"{file} -version 2>&1 | grep -Eow '[0-9]+\.[0-9]+' | head -1",shell=True).decode().strip()
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

def package_server(stdscr,serverdir:str,chosenserver:int):
    sdata = APPDATA["servers"][chosenserver]
    with open(serverdir+"/exdata.json","w+") as f:
        f.write(json.dumps(sdata))
        #Write server data into a temporary file
    wdir=cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a folder for the output server file")
    wxfileout=wdir+"/"+sdata["name"]+".amc"
    cursesplus.displaymsgnodelay(stdscr,["Packaging server","please wait..."])
    pr = os.system(f"bash {UTILDIR}/package_server.sh {serverdir} {wxfileout}")
    if pr != 0:
        cursesplus.messagebox.showerror(stdscr,["An error occured packaging your server"])
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
    __SCRIPT__ = f"#!/usr/bin/sh\n{njavapath.replace(' ',_space)} -jar -Xms{memorytoall} -Xmx{memorytoall} \"{S_INSTALL_DIR}/server.jar\" nogui"
    p.step("All done!",True)
    startnow = cursesplus.messagebox.askyesno(stdscr,["Do you want to start your server now","to generate remaining config files","and to generate a default world?"])
    APPDATA["servers"].append({"name":servername,"javapath":njavapath,"memory":memorytoall,"dir":S_INSTALL_DIR,"version":PACKAGEDATA["id"],"moddable":serversoftware!=1,"software":serversoftware,"script":__SCRIPT__})
    updateappdata()
    if not startnow:
        return
    curses.curs_set(1)
    curses.reset_shell_mode()
    _OLDDIR = os.getcwd()
    os.chdir(S_INSTALL_DIR)
    os.system(__SCRIPT__)
    
    curses.reset_prog_mode()
    os.chdir(_OLDDIR)
    curses.curs_set(0)
    stdscr.clear()
    
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
    os.chdir(serverdir)
    if os.path.isfile("server.jar"):
        os.remove("server.jar")
def update_s_software_postinit(PACKAGEDATA:dict,chosenserver:int):
    APPDATA["servers"][chosenserver-1]["version"] = PACKAGEDATA["id"]#Update new version
    generate_script(APPDATA["servers"][chosenserver-1])
    updateappdata()

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

def update_spigot_software(stdscr,serverdir:str,chosenserver:int):
    update_s_software_preinit()
    stdscr.erase()
    
    update_s_software_postinit()

def textview(stdscr,file:str):# NOTE: This function may be moved to cursesplus library
    if not os.path.isfile(file):
        cursesplus.messagebox.showwarning(stdscr,["Specified file does not exist"])
        return
    else:
        with open(file) as f:
            data = f.readlines()
    xoffset = 0
    yoffset = 0
    mx,my = os.get_terminal_size()
    ERROR = ""
    while True:
        stdscr.clear()
        cursesplus.filline(stdscr,my-1,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        cursesplus.filline(stdscr,0,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(0,0,f"Viewing file {file}. PRESS Q TO QUIT"[xoffset:xoffset+mx-2],cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        if ERROR != "":
            stdscr.addstr(my-1,0,ERROR,cursesplus.set_colour(cursesplus.WHITE,cursesplus.RED))
            ERROR = ""
        stdscr.addstr(my-1,mx-7,f"({xoffset},{yoffset})",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        for p in range(yoffset,len(data)):
            try:
                stdscr.addstr(yoffset+1,0,data[p][xoffset:xoffset+mx-2])
            except:
                continue

        stdscr.refresh()
        ch = stdscr.getch()
        if ch == 113:
            return
        elif ch == curses.KEY_UP:
            if yoffset == 0:
                curses.beep()
                ERROR = "You are already at the top of the page"
            else:
                yoffset -= 1
        elif ch == curses.KEY_DOWN:
            if yoffset < len(data)-mx-3:
                yoffset += 1
            else:
                curses.beep()
                ERROR = "You are already at the bottom of the page"
        elif ch == curses.KEY_RIGHT:
            xoffset += 1
        elif ch == curses.KEY_LEFT:
            if xoffset == 0:
                curses.beep()
                ERROR = "You are already at the left"
            else:
                xoffset -= 1


def view_server_logs(stdscr,server_dir:str):
    
    logsdir = server_dir+"/logs"
    if not os.path.isdir(logsdir):
        cursesplus.messagebox.showwarning(stdscr,["This server has no logs."])
        return
    #if not cursesplus.messagebox.askyesno(stdscr,["Do you want to view that latest log?"]):#TODO Finish all log feature
    #    pass
    else:
        textview(stdscr,logsdir+"/latest.log")

def manage_server(stdscr,_sname: str,chosenserver: int):
    global APPDATA
    SERVER_DIR = _sname
    _ODIR = os.getcwd()
    os.chdir(SERVER_DIR)

    #Manager server
    while True:
        x__ops = ["Back","Start Server","Change MOTD","Advanced configuration","Delete server","Set up new world","Update Server software"]
        if APPDATA["servers"][chosenserver-1]["moddable"]:
            x__ops += ["Manage mods/plgins"]
        else:
            x__ops += ["Convert server to moddable"]
        x__ops += ["View logs","Export server","View server info"]
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
            __l = cursesplus.displayops(stdscr,["Cancel","Modify server properties","Modify AMCS Server options"])
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
            else:
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
_SCREEN = None
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
        if os.system("java -help > /dev/null 2>&1") == 0:
        
            APPDATA["javainstalls"].append({"path":"java","ver":get_java_version()})
    while True:
        stdscr.erase()
        jmg = cursesplus.optionmenu(stdscr,["ADD INSTALLATION","FINISH"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in APPDATA["javainstalls"]])
        if jmg == 0:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a java executable",directory="/")
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
                try:
                    jdl["ver"] = get_java_version(njavapath)
                except:
                    cursesplus.messagebox.showwarning(stdscr,["Java installaion is corrupt"])
                    del APPDATA["javainstalls"][jmg-2]
                else:
                    cursesplus.messagebox.showinfo(stdscr,["Java installation is safe"])

        updateappdata()

def import_server(stdscr):
    chlx = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a file",filter=[["*.amc","Minecraft Server file"],["*.xz","xz archive"],["*.tar","tar archive"]])
    cursesplus.displaymsgnodelay(stdscr,["Unpacking server...","please wait"])
    smd5 = file_get_md5(chlx)
    if os.path.isdir(f"{TEMPDIR}/{smd5}"):
        shutil.rmtree(f"{TEMPDIR}/{smd5}")
    s = os.system(f"bash {UTILDIR}/unpackage_server.sh \"{chlx}\" \"{TEMPDIR}/{smd5}\"")
    if s != 0:
        cursesplus.messagebox.showerror(stdscr,["An error occured unpacking your server"])
        return
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
    cursesplus.displaymsgnodelay(stdscr,["Unpacking server...","please wait"])
    #os.mkdir(SERVERSDIR+"/"+nname)
    shutil.copytree(f"{TEMPDIR}/{smd5}",SERVERSDIR+"/"+nname)
    xdat["dir"] = SERVERSDIR+"/"+nname
    xdat["javapath"] = choose_java_install(stdscr)
    xdat["script"] = generate_script(xdat)
    APPDATA["servers"].append(xdat)
    cursesplus.messagebox.showinfo(stdscr,["Server is imported"])

def main(stdscr):
    global VERSION_MANIFEST
    global VERSION_MANIFEST_DATA
    global APPDATAFILE
    global _SCREEN
    _SCREEN = stdscr
    global DEBUG
    try:
        curses.start_color()
        curses.curs_set(0)
        
        cursesplus.displaymsgnodelay(stdscr,["Auto Minecraft Server","Starting..."])
        issue = False
        if DEBUG:
            stdscr.addstr(0,0,"WARNING: This program is running from its source tree!",cursesplus.set_colour(cursesplus.BLACK,cursesplus.YELLOW))
            stdscr.refresh()
            issue = True
        if os.path.isdir("/usr/lib/automcserver") and os.path.isdir(os.path.expanduser("~/.local/lib/automcserver")):
            stdscr.addstr(1,0,"ERROR: Conflicting installations of AMCS were found! Some issues may occur",cursesplus.set_colour(cursesplus.BLACK,cursesplus.RED))
            stdscr.refresh()
            issue = True
        if issue:
            sleep(5)

        global APPDATA
        signal.signal(signal.SIGINT,sigint)
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
        APPDATA = compatibilize_appdata(APPDATA)

        #Graphics support loading
        if not internet_on():
            if not cursesplus.messagebox.askyesno(stdscr,["WARNING","No internet connection could be found!","You may run in to errors","Are you sure you want to continue?"]):
                return
        VERSION_MANIFEST_DATA = requests.get(VERSION_MANIFEST).json()
        
        if not APPDATA["hasCompletedOOBE"]:
            stdscr.clear()
            cursesplus.displaymsg(stdscr,["AMCS OOBE","","Welcome to AutoMinecraftServer: The best way to make a Minecraft server","This guide will help you set up your first Minecraft Server"])
            if not bool(APPDATA["javainstalls"]):
                if cursesplus.messagebox.askyesno(stdscr,["You have no java installations set up","Would you like to set some up now?"]):
                    managejavainstalls(stdscr)
                else:
                    cursesplus.messagebox.showinfo(stdscr,["You can manage your","Java installations from the","Main menu"])
            setupservernow = False
            setupservernow = cursesplus.messagebox.askyesno(stdscr,["AMCS OOBE","","Would you like to set up a server now?"])
            stdscr.clear()
            if setupservernow:
                
                setupnewserver(stdscr)
        

        APPDATA["hasCompletedOOBE"] = True
        updateappdata()
        mx,my = os.get_terminal_size()
        if DEBUG:
            introsuffix=" | SRC DEBUG"
        else:
            introsuffix = ""
#        if mx < 120 or my < 20:
#            cursesplus.messagebox.showwarning(stdscr,["Your terminal size may be too small","Some instability may occur","For best results, set size to","at least 120x20"])
        while True:
            stdscr.erase()
            m = cursesplus.displayops(stdscr,["Set up new server","View list of servers","Quit","Manage java installations","Import Server"],f"AutoMcServer by Enderbyte Programs | VER {APP_UF_VERSION}{introsuffix}")
            if m == 2:

                return
            elif m == 0:

                setupnewserver(stdscr)
            elif m == 1:
                servermgrmenu(stdscr)
            elif m == 3:
                managejavainstalls(stdscr)
            elif m == 4:
                import_server(stdscr)
        
    except Exception as e:
        cursesplus.displaymsg(stdscr,["An error occured"]+traceback.format_exc().splitlines())


curses.wrapper(main)