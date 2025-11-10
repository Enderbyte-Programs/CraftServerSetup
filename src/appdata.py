from staticflags import *
import random
import json
import gzip
import typing

def compatibilize_appdata(data:dict) -> dict:
    """This function ensures that appdata is brought up to the latest version. It is compatible to the beginning."""
    try:
        cver = data["version"]
    except:
        data["version"] = APP_APPDATA_VERSION

    if not "language" in data:
        data["language"] = None

    if not "settings" in data:
        data["settings"] = {

        "transitions":{
            "display" : "Show Transitions?",
            "type" : "bool",
            "value" : False
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
            data["servers"][svri]["settings"] = {"launchcommands":[],"exitcommands":[],"restartsource" : 0,"autorestart" : 0,"legacy" : True,"flags":""}#0 - disabled, 1 - file-controlled, 2 - crss-controlled. 
        if not "legacy" in data["servers"][svri]["settings"]:
            data['servers'][svri]["settings"]["legacy"] = True
        if not "backupdir" in svr:
            data['servers'][svri]["backupdir"] = SERVERS_BACKUP_DIR + os.sep + str(data['servers'][svri]["id"])
        if data["servers"][svri]["software"] == 0:
            data["servers"][svri]["software"] = 5#v1.48

        if not "autorestart" in data["servers"][svri]["settings"]:
            data["servers"][svri]["settings"]["autorestart"] = 0
            data["servers"][svri]["settings"]["restartsource"] = 0

        if not "flags" in data["servers"][svri]["settings"]:
            data["servers"][svri]["settings"]["flags"] = ""

            
        #1.49.1
        if not "flags" in svr["settings"]:
            data["servers"][svri]["settings"]["flags"] = ""
            
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
        
    #1.49
    if not "reswarn" in data["settings"]:
        data["settings"]["reswarn"] = {
            "name" :"reswarn",
            "display" : "Give warnings for high-resource operations",
            "type" : "bool",
            "value" : True
        }

    #1.53
    if "pkd" in data:
        del data["productKey"]
        del data["pkd"]

    if "showprog" in data["settings"]:
        del data["settings"]["showprog"]

    if not "autorestarttimeout" in data["settings"]:
        data["settings"]["autorestarttimeout"] = {
            "name" : "autorestarttimeout",
            "display" : "Autorestart timeout in seconds",
            "type" : "int",
            "value" : 30
        }

    return data

__DEFAULTAPPDATA__ = {
    "servers" : [

    ],
    "hasCompletedOOBE" : False,
    "version" : APP_APPDATA_VERSION,
    "javainstalls" : [

    ],

    "settings" : {
        "transitions":{
            "display" : "Show Transitions?",
            "type" : "bool",
            "value" : False
        },
        "oldmenu":{
            "name" : "oldmenu",
            "display" : "Use legacy style menus?",
            "type" : "bool",
            "value" : False
        },
        "reswarn" : {
            "name" :"reswarn",
            "display" : "Give warnings for high-resource operations?",
            "type" : "bool",
            "value" : True
        },
        "autorestarttimeout" : {
            "name" : "autorestarttimeout",
            "display" : "Autorestart timeout in seconds",
            "type" : "int",
            "value" : 30
        },
            "editor": {
            "name": "editor",
            "display": "Text Editor",
            "type": "str",
            "value": "/usr/bin/editor %s"
        },
            "autoupdate": {
            "name": "autoupdate",
            "display": "Update automatically",
            "type": "bool",
            "value": True
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

UUID_INDEX:dict = {}

def setup_appdata():
    """Load appdata from the file and populate the appdata.APPDATA variable."""
    global APPDATA
    global APPDATAFILE
    global UUIDFILE
    global UUID_INDEX
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

    UUIDFILE = APPDATADIR+"/uuidindex.json.gz"

    if not os.path.isfile(UUIDFILE):
        with open(UUIDFILE,"wb+") as f:
            f.write(gzip.compress(json.dumps({}).encode()))
    else:
        try:
            with open(UUIDFILE,"rb") as f:
                UUID_INDEX = json.loads(gzip.decompress(f.read()))
        except:
            with open(UUIDFILE,"wb+") as f:
                f.write(gzip.compress(json.dumps({}).encode()))

def self_compatibilize():
    """Execute a compatibilization and repair routine on appdata.APPDATA"""
    global APPDATA

    APPDATA = compatibilize_appdata(APPDATA)

def updateappdata():
    """Write in-memory appdata and UUID cache to the disk"""
    
    global APPDATAFILE
    global UUID_INDEX
    global UUIDFILE
    with open(APPDATAFILE,"w+") as f:
        f.write(json.dumps(APPDATA,indent=2))
    with open(UUIDFILE,"wb+") as f:
        f.write(gzip.compress(json.dumps(UUID_INDEX).encode()))#Write compressed file

def get_setting_value(key:str) -> typing.Any:
    return APPDATA["settings"][key]["value"]