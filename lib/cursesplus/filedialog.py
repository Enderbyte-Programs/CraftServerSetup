from . import cp, messagebox, utils
import os
import glob
from datetime import datetime
from platform import system as __system
import string

WINDOWS = __system() == "Windows"
if WINDOWS:
    from ctypes import windll
    d_move_l = "B"
else:
    d_move_l = "Shift-Left Arrow"
def __get_drives():
    if WINDOWS:
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1
        return drives
    else:
        return []
def parse_size(data: int) -> str:
    """Internal Function to change an int to a data string size ex 1000000 -> 1 MB"""
    result = "???"
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

class Fileobj:
    """Internal class for a single file for use with file dialogs."""
    def __init__(self,path: str) -> None:
        if not os.path.isfile(path) and not os.path.isdir(path):
            raise FileNotFoundError(f"No file found {path}")
        self.path = path
        if os.path.isfile(path):
            self.isdir = False
        elif os.path.isdir(path):
            self.isdir = True
        self.size = os.path.getsize(path)
        self.datestamp = os.path.getctime(path)
        self.date = str(datetime.fromtimestamp(self.datestamp))[0:-7]
        self.sizestr = parse_size(self.size)
        self.strippedpath = path.replace("\\","/").split("/")[-1]  

def openfiledialog(stdscr,title: str = "Please choose a file",filter: str = [["*","All Files"]],directory: str = os.getcwd(),allowcancel=True) -> str:
    """Start a filedialog to open a file. title is the prompt the use recieves. filter is the file filter. The filter syntax is the same as TK syntax. The first
    filter provided is the main filter. 
    Filter Syntax: 
    [[GLOB,NAME],[GLOB,NAME]]
    Glob is a pattern to match for files (like *.txt)
    Name is a file type like (Text Files)
    
    directory is the directory that the dialog opens to

    RETURNS the full file path chosen
    """
    xoffset: int = 0
    yoffset: int = 0
    activefilter: int = 0
    selected: int = 0
    refresh: bool = False
    directory = directory.replace("\\","/")
    masterlist: list = list[Fileobj]
    directories = [directory+"/"+l for l in os.listdir(directory) if os.path.isdir(directory+"/"+l)]
    if filter[activefilter][0].strip() == "*":
        files = [directory+"/"+l for l in os.listdir(directory) if os.path.isfile(directory+"/"+l)]
    else:
        files = glob.glob(directory+"/"+filter[activefilter][0])
    directories.sort()
    files.sort()
    #displaymsg(stdscr,directories+files)
    masterlist = [Fileobj(f) for f in (directories+files)]
    while True:
        
        mx,my = os.get_terminal_size()
        MAXNL = mx - 33
        stdscr.clear()
        if directory == "/" and WINDOWS:
            directory = "C:/"
            refresh = True
            yoffset = 0
            selected = 0
        elif directory.endswith(":") and WINDOWS:
            directory += "/"
            refresh = True
            yoffset = 0
            selected = 0
        directory = directory.replace("\\","/")
        cp.rectangle(stdscr,2,0,my-2,mx-1)
        utils.fill_line(stdscr,0,cp.set_colour(cp.BLUE,cp.WHITE))
        utils.fill_line(stdscr,1,cp.set_colour(cp.GREEN,cp.WHITE))
        utils.fill_line(stdscr,my-2,cp.set_colour(cp.WHITE,cp.BLACK))
        utils.fill_line(stdscr,my-1,cp.set_colour(cp.RED,cp.WHITE))
        topline = "Name"+" "*(MAXNL-4)+"|"+"Size     "+"|Date Modified"
        topline = topline+(mx-2-len(topline))*" "
        if refresh:
            masterlist: list = list[Fileobj]
            directories = [directory+"/"+l for l in os.listdir(directory) if os.path.isdir(directory+"/"+l)]
            if filter[activefilter][0].strip() == "*":
                files = [directory+"/"+l for l in os.listdir(directory) if os.path.isfile(directory+"/"+l)]
            else:
                files = glob.glob(directory+"/"+filter[activefilter][0])
            directories.sort()
            files.sort()
            #displaymsg(stdscr,directories+files)
            masterlist = [Fileobj(f) for f in (directories+files)]
        stdscr.addstr(0,0,title+f"|H for Help|Press {d_move_l} to move up directory"[0:mx],cp.set_colour(cp.BLUE,cp.WHITE))
        stdscr.addstr(1,0,directory[xoffset:xoffset+mx],cp.set_colour(cp.GREEN,cp.WHITE))
        stdscr.addstr(my-2,0,f"{filter[activefilter][1]} ({filter[activefilter][0]}) [{len(masterlist)} objects found]"[0:mx],cp.set_colour(cp.WHITE,cp.BLACK))
        stdscr.addstr(2,1,topline[0:mx-1])
        
        try:
            stdscr.addstr(my-1,0,masterlist[selected].path[xoffset:xoffset+mx],cp.set_colour(cp.RED,cp.WHITE))
        except:
            pass
        ind = yoffset#Track position in list
        indx = 0#track position in iter
        for fileobjects in masterlist[yoffset:yoffset+my-5]:
            wstr = fileobjects.strippedpath[xoffset:xoffset+MAXNL]
            wstr += " "*(MAXNL-len(wstr)+1)
            wstr += fileobjects.sizestr
            wstr += " "*(10-len(fileobjects.sizestr))
            wstr += fileobjects.date
            if selected == ind:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.GREEN))
            elif fileobjects.isdir:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.YELLOW))
            else:
                stdscr.addstr(3+indx,1,wstr)
            ind += 1
            indx += 1#Inc both

        
        stdscr.refresh()
        ch = stdscr.getch()
        refresh = False
        if ch == cp.curses.KEY_LEFT and xoffset > 0:
            xoffset -= 1
        elif ch == cp.curses.KEY_RIGHT:
            xoffset += 1
        elif ch == cp.curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < yoffset:
                yoffset -= 1
        elif ch == cp.curses.KEY_DOWN and selected < len(masterlist)-1:
            if selected - yoffset > my - 7:
                yoffset += 1
            selected += 1
        elif ch == 102:
            activefilter = cp.displayops(stdscr,[f"{f[1]} ({f[0]})" for f in filter],"Please choose a filter")
            selected = 0
            yoffset = 0
            refresh = True
        elif ch == cp.curses.KEY_ENTER or ch == 10 or ch == 13:
            if len(masterlist) == 0:
                messagebox.showwarning(stdscr,["This directory is empty"])
            else:
                if masterlist[selected].isdir:
                    try:
                        os.listdir(masterlist[selected].path)
                    except:
                        messagebox.showerror(stdscr,["Directory Access Forbidden"])
                    else:
                        directory = masterlist[selected].path
                        selected = 0
                        refresh = True
                        yoffset = 0
                        directory = directory.replace("\\","/").replace("//","/")
                else:
                    return masterlist[selected].path.replace("\\","/")
        elif ch == cp.curses.KEY_SLEFT or ch == 98:
            directory = "/".join(directory.split("/")[0:-1])
            selected = 0
            yoffset = 0
            refresh = True
            if directory == "":
                directory = "/"
            directory = directory.replace("\\","/").replace("//","/")
        elif ch == 114:
            refresh = True#Refresh files list
        elif ch == 99 or cp.curses.keyname(ch) == b"^C":
            if allowcancel:
                return None
            else:
                messagebox.showwarning(stdscr,["Cancel is not allowed."])
        elif ch == 108:
            npath = cp.cursesinput(stdscr,"Please enter new path").replace("\n","")
            if os.path.isdir(npath):
                directory = npath
                selected = 0
                yoffset = 0
                refresh = True
            else:
                messagebox.showwarning(stdscr,["Path does not exist"])
        elif ch == 104:
            cp.displaymsg(stdscr,["List of Keybinds","Down Arrow: Scroll down","Up Arrow: Scroll up","Left Arrow: Scroll left","Right Arrow: Scroll right","Shift-left arrow: Move up to parent Directory","Enter: Open/select","F: Change filter","L: Change location","Shift-D: Choose drive (WINDOWS ONLY)","Ctrl-C / C: Cancel"])
        elif ch == 68 and WINDOWS:
            #Drive letter select
            drives = __get_drives()
            ad = cp.optionmenu(stdscr,["Cancel"]+[drive+":\\" for drive in drives],"Please select a drive")
            if ad != 0:
                directory = drives[ad-1]+":/"
                refresh = True
                selected = 0 
                yoffset = 0
        #masterlist.clear()

def openfolderdialog(stdscr,title: str = "Please choose a folder",directory: str = os.getcwd(),allowcancel=True) -> str:
    """Start a filedialog to open a file. title is the prompt the use recieves. filter is the file filter. The filter syntax is the same as TK syntax. The first
    filter provided is the main filter. 
    Filter Syntax: 
    [[GLOB,NAME],[GLOB,NAME]]
    Glob is a pattern to match for files (like *.txt)
    Name is a file type like (Text Files)
    
    directory is the directory that the dialog opens to

    RETURNS the full file path chosen
    """
    xoffset: int = 0
    yoffset: int = 0
    selected: int = 0
    refresh: bool = False
    masterlist: list = list[Fileobj]
    directories = [directory+"/"+l for l in os.listdir(directory) if os.path.isdir(directory+"/"+l)]
    directories.sort()
    #displaymsg(stdscr,directories+files)
    masterlist = [Fileobj(f) for f in directories]
    while True:
        directory = directory.replace("\\","/")
        mx,my = os.get_terminal_size()
        MAXNL = mx - 33
        stdscr.clear()
        cp.rectangle(stdscr,2,0,my-2,mx-1)
        utils.fill_line(stdscr,0,cp.set_colour(cp.BLUE,cp.WHITE))
        utils.fill_line(stdscr,1,cp.set_colour(cp.GREEN,cp.WHITE))
        utils.fill_line(stdscr,my-2,cp.set_colour(cp.WHITE,cp.BLACK))
        utils.fill_line(stdscr,my-1,cp.set_colour(cp.RED,cp.WHITE))
        topline = "Name"+" "*(MAXNL-4)+"|"+"Size     "+"|Date Modified"
        topline = topline+(mx-2-len(topline))*" "
        if directory == "/" and WINDOWS:
            directory = "C:/"
            refresh = True
            yoffset = 0
            selected = 0
        elif directory.endswith(":") and WINDOWS:
            directory += "/"
            refresh = True
            yoffset = 0
            selected = 0
        if refresh:
            masterlist: list = list[Fileobj]
            directories = [directory+"/"+l for l in os.listdir(directory) if os.path.isdir(directory+"/"+l)]
            directories.sort()
            masterlist = [Fileobj(f) for f in directories]
        stdscr.addstr(0,0,title+f"|H for Help|Press {d_move_l} to move up directory"[0:mx],cp.set_colour(cp.BLUE,cp.WHITE))
        stdscr.addstr(1,0,directory[xoffset:xoffset+mx],cp.set_colour(cp.GREEN,cp.WHITE))
        stdscr.addstr(my-2,0,f"[{len(masterlist)} objects found]"[0:mx],cp.set_colour(cp.WHITE,cp.BLACK))
        stdscr.addstr(2,1,topline[0:mx-1])
        
        try:
            stdscr.addstr(my-1,0,masterlist[selected].path[xoffset:xoffset+mx],cp.set_colour(cp.RED,cp.WHITE))
        except:
            pass
        ind = yoffset#Track position in list
        indx = 0#track position in iter
        for fileobjects in masterlist[yoffset:yoffset+my-5]:
            wstr = fileobjects.strippedpath[xoffset:xoffset+MAXNL]
            wstr += " "*(MAXNL-len(wstr)+1)
            wstr += fileobjects.sizestr
            wstr += " "*(10-len(fileobjects.sizestr))
            wstr += fileobjects.date
            if selected == ind:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.GREEN))
            elif fileobjects.isdir:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.YELLOW))
            else:
                stdscr.addstr(3+indx,1,wstr)
            ind += 1
            indx += 1#Inc both

        
        stdscr.refresh()
        ch = stdscr.getch()
        refresh = False
        if ch == cp.curses.KEY_LEFT and xoffset > 0:
            xoffset -= 1
        elif ch == cp.curses.KEY_RIGHT:
            xoffset += 1
        elif ch == cp.curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < yoffset:
                yoffset -= 1
        elif ch == cp.curses.KEY_DOWN and selected < len(masterlist)-1:
            if selected - yoffset > my - 7:
                yoffset += 1
            selected += 1
        elif ch == cp.curses.KEY_ENTER or ch == 10 or ch == 13:
            if len(masterlist) == 0:
                messagebox.showwarning(stdscr,["This directory is empty"])
            else:
                if masterlist[selected].isdir:
                    try:
                        os.listdir(masterlist[selected].path)
                    except:
                        messagebox.showerror(stdscr,["Directory Access Forbidden"])
                    else:
                        directory = masterlist[selected].path
                        selected = 0
                        refresh = True
                        yoffset = 0
                        directory = directory.replace("//","/")
                else:
                    return masterlist[selected].path.replace("\\","/")
        elif ch == 115:
            return masterlist[selected].path.replace("\\","/")
        elif ch == cp.curses.KEY_SLEFT or ch == 98:
            directory = "/".join(directory.split("/")[0:-1])
            selected = 0
            yoffset = 0
            refresh = True
            if directory == "":
                directory = "/"
            
            directory = directory.replace("//","/")
        elif ch == 114:
            refresh = True#Refresh files list
        elif ch == 99:
            if allowcancel:
                return None
            else:
                messagebox.showwarning(stdscr,["Cancel is not allowed."])
        elif ch == 108:
            npath = cp.cursesinput(stdscr,"Please enter new path").replace("\n","")
            if os.path.isdir(npath):
                directory = npath
                selected = 0
                yoffset = 0
                refresh = True
            else:
                messagebox.showwarning(stdscr,["Path does not exist"])
        elif ch == 104:
            cp.displaymsg(stdscr,["List of Keybinds","Down Arrow: Scroll down","Up Arrow: Scroll up","Left Arrow: Scroll left","Right Arrow: Scroll right","Shift-left arrow: Move up to parent Directory","Enter: Open","S: Choose folder","L: Change location","Shift-D: Choose drive (WINDOWS ONLY)","C: Cancel"])
        elif ch == 68 and WINDOWS:
            #Drive letter select
            drives = __get_drives()
            ad = cp.optionmenu(stdscr,["Cancel"]+[drive+":\\" for drive in drives],"Please select a drive")
            if ad != 0:
                directory = drives[ad-1]+":/"
                refresh = True
                selected = 0 
                yoffset = 0
        #masterlist.clear()

def openfilesdialog(stdscr,title: str = "Please choose a file",filter: str = [["*","All Files"]],directory: str = os.getcwd(),allowcancel=True) -> list:
    """Start a filedialog to select multiple files. title is the prompt the user recieves. filter is the file filter. The filter syntax is the same as TK syntax. The first
    filter provided is the main filter. 
    Filter Syntax: 
    [[GLOB,NAME],[GLOB,NAME]]
    Glob is a pattern to match for files (like *.txt)
    Name is a file type like (Text Files)
    
    directory is the directory that the dialog opens to

    RETURNS a list of file paths chosen
    """
    xoffset: int = 0
    yoffset: int = 0
    activefilter: int = 0
    selected: int = 0
    chosen: list[str] = []
    chosen.append(" ")
    chosen.clear()
    update = True
    masterlist: list = list[Fileobj]
    while True:
        directory = directory.replace("\\","/")
        mx,my = os.get_terminal_size()
        MAXNL = mx - 33
        stdscr.clear()
        cp.rectangle(stdscr,2,0,my-2,mx-1)
        utils.fill_line(stdscr,0,cp.set_colour(cp.BLUE,cp.WHITE))
        utils.fill_line(stdscr,1,cp.set_colour(cp.GREEN,cp.WHITE))
        utils.fill_line(stdscr,my-2,cp.set_colour(cp.WHITE,cp.BLACK))
        utils.fill_line(stdscr,my-1,cp.set_colour(cp.RED,cp.WHITE))
        topline = "Name"+" "*(MAXNL-4)+"|"+"Size     "+"|Date Modified"
        topline = topline+(mx-2-len(topline))*" "
        if directory == "/" and WINDOWS:
            directory = "C:/"
            update = True
            yoffset = 0
            selected = 0
        elif directory.endswith(":") and WINDOWS:
            directory += "/"
            update = True
            yoffset = 0
            selected = 0
        if update:
            #masterlist.clear()
            directories = [directory+"/"+l for l in os.listdir(directory) if os.path.isdir(directory+"/"+l)]
            if filter[activefilter][0] == "*":
                files = [directory+"/"+l for l in os.listdir(directory) if os.path.isfile(directory+"/"+l)]
            else:
                files = glob.glob(directory+"/"+filter[activefilter][0])
            directories.sort()
            files.sort()
            #displaymsg(stdscr,directories+files)
            masterlist = [Fileobj(f) for f in (directories+files)]
        update = False
        stdscr.addstr(0,0,title+f"|H for Help|Press {d_move_l} to move up directory"[0:mx],cp.set_colour(cp.BLUE,cp.WHITE))
        stdscr.addstr(1,0,directory[xoffset:xoffset+mx],cp.set_colour(cp.GREEN,cp.WHITE))
        stdscr.addstr(my-2,0,f"{filter[activefilter][1]} ({filter[activefilter][0]}) [{len(masterlist)} objects found]"[0:mx],cp.set_colour(cp.WHITE,cp.BLACK))
        stdscr.addstr(2,1,topline[0:mx-1])
        
        try:
            stdscr.addstr(my-1,0,str(chosen)[xoffset:xoffset+mx],cp.set_colour(cp.RED,cp.WHITE))
        except:
            pass
        ind = yoffset#Track position in list
        indx = 0#track position in iter
        for fileobjects in masterlist[yoffset:yoffset+my-5]:
            wstr = fileobjects.strippedpath[xoffset:xoffset+MAXNL]
            wstr += " "*(MAXNL-len(wstr)+1)
            wstr += fileobjects.sizestr
            wstr += " "*(10-len(fileobjects.sizestr))
            wstr += fileobjects.date
            if selected == ind:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.YELLOW))
                if masterlist[selected].path in chosen:
                    stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLUE,cp.YELLOW))
            elif fileobjects.isdir:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLACK,cp.GREEN))
            elif fileobjects.path in chosen:
                stdscr.addstr(3+indx,1,wstr,cp.set_colour(cp.BLUE,cp.WHITE))
            else:
                stdscr.addstr(3+indx,1,wstr)
            ind += 1
            indx += 1#Inc both

        
        stdscr.refresh()
        ch = stdscr.getch()

        if ch == cp.curses.KEY_LEFT and xoffset > 0:
            xoffset -= 1
        elif ch == cp.curses.KEY_RIGHT:
            xoffset += 1
        elif ch == cp.curses.KEY_UP and selected > 0:
            selected -= 1
            if selected < yoffset:
                yoffset -= 1
        elif ch == cp.curses.KEY_DOWN and selected < len(masterlist)-1:
            if selected - yoffset > my - 7:
                yoffset += 1
            selected += 1
        elif ch == 102:
            activefilter = cp.displayops(stdscr,[f"{f[1]} ({f[0]})" for f in filter],"Please choose a filter")
            selected = 0
            yoffset = 0
            update = True
        elif ch == cp.curses.KEY_ENTER or ch == 10 or ch == 13:
            if len(masterlist) == 0:
                messagebox.showwarning(stdscr,["This directory is empty"])
            else:
                if masterlist[selected].isdir:
                    try:
                        os.listdir(masterlist[selected].path)
                    except:
                        messagebox.showerror(stdscr,["Directory Access Forbidden"])
                    else:
                        directory = masterlist[selected].path
                        selected = 0
                        update = True
                        yoffset = 0
                        directory = directory.replace("//","/")
                else:
                    chosen.clear()
                    chosen.append(masterlist[selected].path)
        elif ch == 115:
            #s for add to selection
            if not masterlist[selected].isdir:
                if masterlist[selected].path in chosen:
                    chosen.remove(masterlist[selected].path)
                else:
                    chosen.append(masterlist[selected].path)
        elif ch == cp.curses.KEY_SLEFT or ch == 98:
            directory = "/".join(directory.split("/")[0:-1])
            selected = 0
            yoffset = 0
            update = True
            if directory == "":
                directory = "/"
            directory = directory.replace("//","/")
        elif ch == 114:
            update = True#Refresh files list
        elif ch == 67:
            if allowcancel:
                return None
            else:
                messagebox.showwarning(stdscr,["Cancel is not allowed."])
        elif ch == 100 or cp.curses.keyname(ch).decode() == "^X":
            return [c.replace("\\","/") for c in chosen if os.path.isfile(c) and c.replace(" ","") != ""]#Only return files that still exist
        elif ch == 99:
            chosen.clear()
        elif ch == 108:
            npath = cp.cursesinput(stdscr,"Please enter new path").replace("\n","")
            if os.path.isdir(npath):
                directory = npath
                selected = 0
                yoffset = 0
                update = True
            else:
                messagebox.showwarning(stdscr,["Path does not exist"])
        elif ch == 104:
            cp.displaymsg(stdscr,["List of Keybinds","Down Arrow: Scroll down","Up Arrow: Scroll up","Left Arrow: Scroll left","Right Arrow: Scroll right","Shift-left arrow: Move up to parent Directory","Enter: Open/select","F: Change filter","S: Append / Remove from selection","D/Ctrl-X: Done","C: Clear selection","R: Refresh files list","L: Change location","Shift-C: Cancel","Shift-D: Choose drive (WINDOWS)"])
        elif ch == 68 and WINDOWS:
            #Drive letter select
            drives = __get_drives()
            ad = cp.optionmenu(stdscr,["Cancel"]+[drive+":\\" for drive in drives],"Please select a drive")
            if ad != 0:
                directory = drives[ad-1]+":/"
                update = True
                selected = 0 
                yoffset = 0
        #masterlist.clear()