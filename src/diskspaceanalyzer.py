"""An analyzer for disk space"""

import os
import utils
import copy
import datetime
import jsongz
import uicomponents
import cursesplus

def get_parents(basedir:str,subfile:str) -> list[str]:
    """Get all relative parents as well as the file"""
    result = [copy.copy(subfile)]
    while subfile.replace(basedir,"").strip() != "/":
        subfile = os.path.dirname(subfile)
        if subfile in basedir:
            break
        result.append(copy.copy(subfile))

    return result

class DiskSpaceAnalysis:
    def __init__(self,serverdir:str,rd:dict[str,int]):
        self.rawdata = rd
        self.calltime = datetime.datetime.now()
        self.serverdir = serverdir

    def write(self) -> None:
        """Write this to its file"""
        outdir = get_server_dsa_history_folder(self.serverdir)
        filepath = self.calltime.strftime("%Y-%m-%d %H:%M:%S.json.gz")
        jsongz.write(outdir + "/" + filepath,self.rawdata)
    

def do_analysis(stdscr,of_dir:str) -> DiskSpaceAnalysis:
    """Create an analysis dictionary"""
    
    of_dir = utils.clean_file_path(of_dir)
    rd:dict[str,int] = {}

    for basedir, subdir, files in os.walk(of_dir):
        stdscr.clear()
        stdscr.addstr(0,0,"Loading "+basedir+"...")
        stdscr.refresh()
        for file in files:
            purepath = basedir + "/" + file

            filesize = os.path.getsize(purepath)

            for availableparent in get_parents(of_dir,purepath):
                if availableparent not in rd:
                    rd[availableparent] = filesize
                else:
                    rd[availableparent] += filesize

    res = DiskSpaceAnalysis(of_dir,rd)
    res.write()
    return res

def view_scan(scan:DiskSpaceAnalysis) -> None:
    pass

def dsa_ui(stdscr,base_dir:str) -> None:
    """UI analyzer of disk space"""
    stdscr.clear()
    
    while True:
        baseoption = uicomponents.menu(stdscr,["Finish","Scan right now","View old scan","Disk space history","Disk space projections"],"What do you want to do about disk space analysis?")
        if baseoption == 0:
            break
        elif baseoption == 1:
            view_scan(do_analysis(stdscr,base_dir))
        elif baseoption == 2:
            availableoptions = get_all_dsa_scans(base_dir)
            if len(availableoptions) == 0:
                cursesplus.messagebox.showwarning(stdscr,["There are no scans","You can create one by selecting","scan right now."])
            else:
                wantedscan = uicomponents.menu(stdscr,["Cancel"]+[s.calltime.strftime("Scan from %Y-%m-%d %H:%M:%S") for s in availableoptions])
                if wantedscan != 0:
                    view_scan(availableoptions[wantedscan - 1])

def get_server_dsa_history_folder(serverdir:str) -> str:
    os.makedirs(serverdir + "/dsahistory",exist_ok=True)
    return serverdir + "/dsahistory"

def get_all_dsa_scans(serverdir:str) -> list[DiskSpaceAnalysis]:
    result = []
    for availablescan in sorted(os.listdir(get_server_dsa_history_folder(serverdir))):
        purefile = get_server_dsa_history_folder(serverdir) + "/" + availablescan
        current = DiskSpaceAnalysis(serverdir,jsongz.read(purefile))
        loadeddt = datetime.datetime.strptime(availablescan,"%Y-%m-%d %H:%M:%S.json.gz")
        current.calltime = loadeddt
        result.append(current)

    return result