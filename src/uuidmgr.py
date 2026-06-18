"""A global index of UUIDs"""

import staticflags
import logloader
import os
import logfilters
import jsongz
import datetime
import re
import mojangapi
from time import sleep

uuidindex:dict = {}#UUID: Last known username
uuidindex_reversed:dict = {}

def init() -> None:
    global uuidindex
    global uuidindex_reversed
    if not os.path.isfile(staticflags.UUIDSTORAGEFILE):
        jsongz.write(staticflags.UUIDSTORAGEFILE,{
            "lastupdate" : 0,
            "data" : {}
        })

    uuidindex = jsongz.read(staticflags.UUIDSTORAGEFILE)
    uuidindex_reversed = {"lastupdate":0,"data" : {v:k for k,v in uuidindex["data"].items()}}

def writeuuidcache() -> None:
    jsongz.write(staticflags.UUIDSTORAGEFILE,uuidindex)

def clearcache() -> None:
    global uuidindex
    global uuidindex_reversed
    uuidindex = {}
    uuidindex_reversed = {}

    writeuuidcache()

def load_from_logs(stdscr,serverdir:str):
    allentries = logloader.load_logs(stdscr,serverdir,logfilters.get_uuid,datetime.datetime.fromtimestamp(uuidindex["lastupdate"]))

    for entry in allentries:
        try:
            uuidresult:str = re.findall(r": UUID of player \S+ is \S+$",entry.data)[0]
            uname = uuidresult.split(" ")[4]
            uname = uname.lower()
            uuid = uuidresult.split(" ")[6]
            uuidindex["data"][uuid] = uname
            uuidindex_reversed["data"][uname] = uuid
        except:
            uuidresult:str = re.findall(r"Floodgate player logged in as \S+ joined \(UUID: \S+\)",entry.data)[0]
            uname = uuidresult.split(" ")[5]
            uname = uname.lower()
            uuid = uuidresult.split(" ")[8].replace(")","")
            uuidindex["data"][uuid] = uname
            uuidindex_reversed["data"][uname] = uuid

    uuidindex["lastupdate"] = int(datetime.datetime.now().timestamp())
    writeuuidcache()

def get_uuid_from_name(name:str) -> str:
    name = name.lower()
    if name in uuidindex_reversed["data"]:
        return uuidindex_reversed["data"][name]
    else:
        try:
            sleep(1)
            res = str(mojangapi.get_player_uuid(name))
            uuidindex["data"][res] = name
            uuidindex_reversed["data"][name] = res
            return res
        except:
            return ""

def get_name_from_uuid(uuid:str) -> str:
    if uuid in uuidindex["data"]:
        return uuidindex["data"][uuid]
    else:
        try:
            sleep(1)
            res = mojangapi.get_player_name(uuid.replace("-",""))
            uuidindex["data"][uuid] = res
            uuidindex_reversed["data"][res] = uuid
            return res 
        except:
            return ""