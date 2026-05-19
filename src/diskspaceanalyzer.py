"""An analyzer for disk space"""

import os
import utils
import copy
import datetime
import jsongz
import uicomponents

def get_parents(basedir:str,subfile:str) -> list[str]:
    """Get all relative parents as well as the file"""
    subfile = subfile.replace(basedir,"")
    result = [copy.copy(subfile)]
    while subfile != "/":
        subfile = os.path.dirname(subfile)
        result.append(copy.copy(subfile))

    return result

class DiskSpaceAnalysis:
    def __init__(self,serverdir,rd:dict[str,int]):
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
        stdscr.update()
        for file in files:
            purepath = basedir + "/" + file

            filesize = os.path.getsize(purepath)

            for availableparent in get_parents(of_dir,file):
                if availableparent not in rd:
                    rd[availableparent] = filesize
                else:
                    rd[availableparent] += filesize

    res = DiskSpaceAnalysis(of_dir,rd)
    res.write()
    return res

def dsa_ui(stdscr,base_dir:str) -> None:
    """UI analyzer of disk space"""
    stdscr.clear()
    
    while True:
        baseoption = uicomponents.menu(stdscr,["Finish","Scan right now","View old scan","Disk space history","Disk space projections"])
        if baseoption == 0:
            break
        

def get_server_dsa_history_folder(serverdir:str) -> str:
    os.makedirs(serverdir + "/dsahistory",exist_ok=True)
    return serverdir + "/dsahistory"