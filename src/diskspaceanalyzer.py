"""An analyzer for disk space"""

import os
import utils
import copy
import datetime
import jsongz
import uicomponents
import cursesplus
import curses
import shutil

def get_parents(basedir:str,subfile:str) -> list[str]:
    """Get all relative parents as well as the file"""
    result = [copy.copy(subfile.replace(basedir,"").strip())]
    while subfile.replace(basedir,"").strip() != "/":
        subfile = os.path.dirname(subfile)
        if subfile in basedir:
            break
        result.append(copy.copy(subfile.replace(basedir,"").strip()))
    result.append("/")

    return result

class DiskSpaceAnalysis:
    def __init__(self,serverdir:str,rd:dict[str,int]):
        self.rawdata = rd
        self.calltime = datetime.datetime.now()
        self.serverdir = serverdir

    def write(self) -> None:
        """Write this to its file"""
        outdir = get_server_dsa_history_folder(self.serverdir)
        filepath = self.calltime.strftime("%Y-%m-%d %H-%M-%S.json.gz")
        jsongz.write(outdir + "/" + filepath,self.rawdata)

class DiskSpaceChild:
    def __init__(self,key:str,value:int):
        splitkey = key.split(":")
        self.name = ":".join(splitkey[1:])
        self.isdir = splitkey[0] == "d"
        self.size = value
        self.display_name = os.path.basename(self.name)

def do_analysis(stdscr,of_dir:str) -> DiskSpaceAnalysis:
    """Create an analysis dictionary"""
    
    of_dir = utils.clean_file_path(of_dir)
    rd:dict[str,int] = {"d:/":0}

    for basedir, subdir, files in os.walk(of_dir):
        stdscr.clear()
        stdscr.addstr(0,0,"Loading "+basedir+"...")
        stdscr.refresh()
        for file in files:
            purepath = basedir + "/" + file
            purepath = purepath.replace("\\","/")

            filesize = os.path.getsize(purepath)

            for availableparent in get_parents(of_dir,purepath):
                if os.path.isdir(of_dir+availableparent):
                    availableparent = "d:"+availableparent
                else:
                    availableparent = "f:"+availableparent
                if availableparent not in rd:
                    rd[availableparent] = filesize
                else:
                    rd[availableparent] += filesize

    #rd = {k:v for k,v in rd.items()}

    res = DiskSpaceAnalysis(of_dir,rd)
    res.write()
    return res

def view_scan(stdscr:curses.window,scan:DiskSpaceAnalysis) -> None:
    relative = "/"
    recompile = True
    activelist:list[DiskSpaceChild] = []
    all_options = [DiskSpaceChild(k,v) for k,v in scan.rawdata.items()]
    offset = 0
    scrolloffset = 0
    TOTAL_SIZE:int = scan.rawdata["d:/"]
    DIR_SIZE = 1

    if TOTAL_SIZE == 0:
        cursesplus.messagebox.showinfo(stdscr,["No files in your server","somehow..."])
        return

    while True:
        desname = os.path.basename(scan.serverdir)
        stdscr.clear()
        my,mx = stdscr.getmaxyx()
        my -= 1
        mx -= 1

        if recompile:
            activelist.clear()

            for option in all_options:
                #cursesplus.messagebox.showinfo(stdscr,[option.name.replace(relative,"")[1:]])
                if option.name.startswith(relative) and not "/" in option.name.replace(relative,"",1)[1:] and option.name != relative:
                    activelist.append(option)

            recompile = False
            activelist.sort(key=lambda x: x.size,reverse=True)
            DIR_SIZE = sum([x.size for x in activelist])

        SZ_START_X = mx - 30
        DIR_RELSIZE_START_X = mx - 16
        ALL_RELSIZE_START_X = mx - 8
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        cursesplus.utils.fill_line(stdscr,my,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(0,0,f"Disk Space Analysis - {desname} @ {scan.calltime.strftime('%Y-%m-%d %H:%M:%S')}",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(my,0,f"Total: {utils.parse_size(TOTAL_SIZE)} | {len(activelist)} in dir | {relative}",cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        cursesplus.utils.fill_line(stdscr,1,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(1,0,"Name",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(1,DIR_RELSIZE_START_X,"Dir. %",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(1,ALL_RELSIZE_START_X,"All %",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(1,SZ_START_X,"Size",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))

        

        rollingy = 2
        for activeitem in activelist[scrolloffset:scrolloffset + (my - 2)]:
            incoffset = rollingy - 2
            if incoffset + scrolloffset == offset:
                if activeitem.isdir:
                    colour = cursesplus.set_colour(cursesplus.WHITE,cursesplus.YELLOW)
                else:
                    colour = cursesplus.set_colour(cursesplus.WHITE,cursesplus.RED)
            else:
                if activeitem.isdir:
                    colour = cursesplus.set_colour(cursesplus.BLACK,cursesplus.GREEN)
                else:
                    colour = cursesplus.set_colour(cursesplus.BLACK,cursesplus.WHITE)
            cursesplus.utils.fill_line(stdscr,rollingy,colour)
            stdscr.addstr(rollingy,0,activeitem.display_name,colour)
            stdscr.addstr(rollingy,SZ_START_X,utils.parse_size(activeitem.size),colour)
            stdscr.addstr(rollingy,DIR_RELSIZE_START_X,f"{round(activeitem.size/DIR_SIZE*100,2)}%",colour)
            stdscr.addstr(rollingy,ALL_RELSIZE_START_X,f"{round(activeitem.size/TOTAL_SIZE*100,2)}%",colour)
            rollingy += 1

        stdscr.refresh()
        key = stdscr.getch()
        keyname = curses.keyname(key).decode()
        if keyname == "q":
            break
        elif key == curses.KEY_DOWN and offset < len(activelist)-1:
            offset += 1
            if (offset-scrolloffset) > (my - 3):
                scrolloffset += 1
        elif key == curses.KEY_UP and offset > 0:
            offset -= 1
            if offset < scrolloffset:
                scrolloffset -= 1
        elif key == curses.KEY_HOME:
            offset = 0
            scrolloffset = 0
        elif key == curses.KEY_END:
            if len(activelist) > (my - 2):
                offset = len(activelist) - 1
                scrolloffset = offset - (my - 3)
        elif keyname == "h":
            cursesplus.displaymsg(stdscr,[
                "Down: Move down",
                "Up: Move up",
                "Enter: Open folder",
                "R: Delete file/folder",
                "B: Go to parent folder"
                "Q: Quit"
            ])
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            selitem = activelist[offset]
            if selitem.isdir:
                relative = selitem.name
                recompile = True
                offset = 0
                scrolloffset = 0
            else:
                cursesplus.messagebox.showerror(stdscr,["That is a file"])
        elif keyname == "b":
            if relative == "/":
                cursesplus.messagebox.showerror(stdscr,["Already at the root"])
            else:
                relative = os.path.dirname(relative)
                recompile = True
                offset = 0
                scrolloffset = 0
        elif keyname == "r":
            selitem = activelist[offset]
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this?","It cannot be recovered!"]):
                truepath = scan.serverdir + selitem.name
                if os.path.isdir(truepath) or os.path.isfile(truepath):
                    try:
                        if selitem.isdir:
                            shutil.rmtree(truepath)
                        else:
                            os.remove(truepath)
                    except:
                        cursesplus.messagebox.showwarning(stdscr,["Failed to delete this file."])
                        continue
                else:
                    cursesplus.messagebox.showinfo(stdscr,["Couldn't find file/directory","Are you using an old scan?",truepath])
                activelist.remove(selitem)
                DIR_SIZE -= selitem.size
                TOTAL_SIZE -= selitem.size
                if DIR_SIZE == 0:
                    DIR_SIZE = 1
                if TOTAL_SIZE == 0:
                    TOTAL_SIZE = 1
                if offset > len(activelist) - 1:
                    offset -= 1
                #Stop division 0


def dsa_ui(stdscr,base_dir:str) -> None:
    """UI analyzer of disk space"""
    stdscr.clear()
    
    while True:
        baseoption = uicomponents.menu(stdscr,["Finish","Scan right now","View old scan","Disk space history","Disk space projections"],"What do you want to do about disk space analysis?")
        if baseoption == 0:
            break
        elif baseoption == 1:
            view_scan(stdscr,do_analysis(stdscr,base_dir))
        elif baseoption == 2:
            availableoptions = get_all_dsa_scans(base_dir)
            if len(availableoptions) == 0:
                cursesplus.messagebox.showwarning(stdscr,["There are no scans","You can create one by selecting","scan right now."])
            else:
                wantedscan = uicomponents.menu(stdscr,["Cancel"]+[s.calltime.strftime("Scan from %Y-%m-%d %H:%M:%S") for s in availableoptions])
                if wantedscan != 0:
                    view_scan(stdscr,availableoptions[wantedscan - 1])
        elif baseoption == 3:
            cursesplus.messagebox.showinfo(stdscr,["This feature is coming soon."])
        elif baseoption == 4:
            cursesplus.messagebox.showinfo(stdscr,["This feature is coming soon."])

def get_server_dsa_history_folder(serverdir:str) -> str:
    os.makedirs(serverdir + "/dsahistory",exist_ok=True)
    return serverdir + "/dsahistory"

def get_all_dsa_scans(serverdir:str) -> list[DiskSpaceAnalysis]:
    result = []
    for availablescan in sorted(os.listdir(get_server_dsa_history_folder(serverdir))):
        purefile = get_server_dsa_history_folder(serverdir) + "/" + availablescan
        current = DiskSpaceAnalysis(serverdir,jsongz.read(purefile))
        loadeddt = datetime.datetime.strptime(availablescan,"%Y-%m-%d %H-%M-%S.json.gz")
        current.calltime = loadeddt
        result.append(current)

    return result