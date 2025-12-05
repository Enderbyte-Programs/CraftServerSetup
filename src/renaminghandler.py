import appdata
import os
import datetime
import json
import logutils
import re
import cursesplus
import uicomponents

NAMECHANGETRACKFILE = appdata.APPDATADIR + os.sep + "playeraliases.json"
nctf_template = {
    "aliases": [
        
    ],
    "last_updated" : 0
}
NC_DATA = nctf_template

if not os.path.isfile(NAMECHANGETRACKFILE):
    with open(NAMECHANGETRACKFILE,"w+") as f:
        json.dump(nctf_template,f)

with open(NAMECHANGETRACKFILE) as f:
    NC_DATA = json.load(f)

#Functions

def get_aliases_of(playername:str) -> list[str]:
    """Return aliases of playername. If they could not be found, return the playername"""
    playername = playername.lower()
    for group in NC_DATA["aliases"]:
        if playername.lower() in group:
            return group
    return [playername]

def get_current_name_of(playername:str) -> str:
    return get_aliases_of(playername)[-1]

def has_known_aliases(playername:str) -> bool:
    playername = playername.lower()

    for group in NC_DATA["aliases"]:
        if playername.lower() in group:
            return True
    return False

def get_alias_addr(playername:str) -> int:
    playername = playername.lower()

    ctr = 0
    for group in NC_DATA["aliases"]:
        if playername.lower() in group:
            return ctr
        ctr += 1
    return -1

def update_cache_custom(stdscr,rawentries:list[logutils.LogEntry]):
    if len(rawentries) == 0:
        return
    raw_lastupdated = 0
    cursesplus.displaymsg(stdscr,["Updating cache","Please wait"],False)
    rolling_str = ""
    for entry in rawentries:
        ttx = entry.get_full_log_time().timestamp()
        if ttx > raw_lastupdated:
            raw_lastupdated = ttx
        rolling_str += entry.data
    
    matches:list[str] = re.findall(r"\S+ \(formerly known as \S+\)",rolling_str)

    for rnentry in matches:
        newname = rnentry.split(" ")[0].strip().lower()
        oldname = rnentry.split(" ")[-1].replace(")","").lower()
        if has_known_aliases(oldname):
            addr = get_alias_addr(oldname)
            NC_DATA["aliases"][addr].append(newname)
        else:
            NC_DATA["aliases"].append([oldname,newname])

    NC_DATA["last_updated"] = raw_lastupdated

    with open(NAMECHANGETRACKFILE,"w+") as f:
        json.dump(NC_DATA,f)

def autoupdate_cache(stdscr,serverdir):

    lastupdatetime = datetime.datetime.fromtimestamp(NC_DATA["last_updated"])
    update_cache_custom(stdscr,logutils.load_server_logs(stdscr,serverdir,True,lastupdatetime,r"\S+ \(formerly known as \S+\)"))

def player_naming_history(stdscr):
    srch = uicomponents.crssinput(stdscr,"What player do you want to learn about?").lower()
    if not has_known_aliases(srch):
        cursesplus.messagebox.askyesno(stdscr,["This player has no known former names"])
    else:
        cursesplus.messagebox.showinfo(stdscr,["This player has gone by the following names:"]+get_aliases_of(srch))
        cursesplus.messagebox.showinfo(stdscr,["The newest name that this player has used is",get_current_name_of(srch)])