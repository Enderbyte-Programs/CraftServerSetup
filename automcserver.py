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
import signal
import datetime
import subprocess
import glob
import zipfile
import hashlib
print("Checking for cursesplus")
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
print("Checking for requests")
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
print("Checking for pyyaml")
try:
    import yaml
except:
    lop = os.system("pip3 install --quiet pyyaml")
    if lop != 0:
        print("Failed to install pyyaml")
        sys.exit(1)
    import yaml
print("Checking internet connection")

def sigint(signal,frame):
    if cursesplus.messagebox.askyesno(_SCREEN,["Are you sure you want to quit?"]):
        updateappdata()
        sys.exit()

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
    usecustomjavaversion = cursesplus.messagebox.askyesno(stdscr,["Do you want to use the default java install (program java)?",f"Version {get_java_version()}"])
    stdscr.clear()
    stdscr.erase()
    p.step("Loading java",True)
    if not usecustomjavaversion:
        while True:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a new java executable",directory="/")
            if os.system(njavapath+" -version &> /dev/null") != 0:
                cursesplus.displaymsg(stdscr,["Bad java file"])
            else:
                break
    else:
        njavapath = "java"
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
                xver = cursesplus.cursesinput(stdscr,"Please type the version you want to build (eg: 1.19.2)")
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
    else:
        if serversoftware == 1:
            #Vanilla
            memorytoall = "1024M"
        else:
            memorytoall = "2G"#Bukkit
    njavapath = njavapath.replace("//","/")
    _space = "\\ "
    __SCRIPT__ = f"#!/usr/bin/sh\n{njavapath.replace(' ',_space)} -jar -Xms{memorytoall} -Xmx{memorytoall} \"{S_INSTALL_DIR}/server.jar\" nogui"
    with open(S_INSTALL_DIR+"/start","w+") as f:
        f.write(__SCRIPT__)
    os.system(f"chmod +x '{S_INSTALL_DIR+'/start'}'")
    p.step("All done!",True)
    startnow = cursesplus.messagebox.askyesno(stdscr,["Do you want to start your server now","to generate remaining config files","and to generate a default world?"])
    APPDATA["servers"].append({"name":servername,"javapath":njavapath,"memory":memorytoall,"dir":S_INSTALL_DIR,"version":PACKAGEDATA["id"],"moddable":serversoftware!=1})
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
    

def manage_server(stdscr,_sname: str,chosenserver: int):
    global APPDATA
    SERVER_DIR = SERVERSDIR+"/"+_sname
    _ODIR = os.getcwd()
    os.chdir(SERVER_DIR)

    #Manager server
    while True:
        x__ops = ["Back","Start Server","Change MOTD","Advanced config","Delete server","Set up new world"]
        if APPDATA["servers"][chosenserver-1]["moddable"]:
            x__ops += ["Manage mods/plgins"]
        w = cursesplus.displayops(stdscr,x__ops)
        if w == 0:
            stdscr.erase()
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
            stdscr.erase()
        elif w == 6:
            svr_mod_mgr(stdscr,SERVER_DIR)
        else:
            nyi(stdscr)
_SCREEN = None
def updateappdata():
    global APPDATA
    global APPDATAFILE
    with open(APPDATAFILE,"w+") as f:
        f.write(json.dumps(APPDATA))
def nyi(stdscr):
    cursesplus.messagebox.showerror(stdscr,["Not Yet Implemented"],colour=True)
    stdscr.erase()
def main(stdscr):
    global VERSION_MANIFEST
    global VERSION_MANIFEST_DATA
    global APPDATAFILE
    global _SCREEN
    _SCREEN = stdscr
    try:
        curses.start_color()

        cursesplus.displaymsgnodelay(stdscr,["Auto Minecraft Server","Starting..."])
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
    
        
    except Exception as e:
        cursesplus.displaymsg(stdscr,["An error occured",str(e)])


curses.wrapper(main)