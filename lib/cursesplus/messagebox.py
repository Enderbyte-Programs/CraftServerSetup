from . import cp
import os
from curses.textpad import rectangle
import curses
import enum

class MessageBoxStates(enum.Enum):
    OK = 1
    CANCEL = 0
    YES = 1
    NO = 0
    RETRY = 1

def askyesno(stdscr,message: list = [],colour=False,default=MessageBoxStates.YES) -> bool:
    """Display a messagebox that asks a user a questions. Returns TRUE on Yes and FALSE on No. Colour is green"""
    selected = default == MessageBoxStates.YES
    x,y = os.get_terminal_size()
    ox = 0
    if colour:
        BGCL = cp.GREEN
    else:
        BGCL = cp.BLACK
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        stdscr.addstr(y//2+(len(message)//2)+4,x//2-(maxs//2),"Y: Yes | N: No")
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[Yes]",[cp.set_colour(cp.WHITE,cp.BLACK) if selected else cp.set_colour(cp.BLACK,cp.WHITE)][0])
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2)+10,"[No]",[cp.set_colour(cp.BLACK,cp.WHITE) if selected else cp.set_colour(cp.WHITE,cp.BLACK)][0])   
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == curses.KEY_RIGHT or ch == curses.KEY_LEFT:
            selected = not selected
        elif ch == 121 or ch == 110:
            return ch == 121
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return selected

def askokcancel(stdscr,message: list = [],colour=False,default=MessageBoxStates.OK) -> bool:
    """Display a messagebox that asks a user a question OK or canel  Returns TRUE on OK and FALSE on Cancel. Colour is green"""
    selected = default == MessageBoxStates.OK
    x,y = os.get_terminal_size()
    ox = 0
    if colour:
        BGCL = cp.GREEN
    else:
        BGCL = cp.BLACK
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[OK]",[cp.set_colour(cp.WHITE,cp.BLACK) if selected else cp.set_colour(cp.BLACK,cp.WHITE)][0])
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2)+10,"[Cancel]",[cp.set_colour(cp.BLACK,cp.WHITE) if selected else cp.set_colour(cp.WHITE,cp.BLACK)][0])   
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == curses.KEY_RIGHT or ch == curses.KEY_LEFT:
            selected = not selected
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return selected
        
def askretrycancel(stdscr,message: list = [],colour=False,default=MessageBoxStates.RETRY) -> bool:
    """Display a messagebox that asks a user a question OK or canel  Returns TRUE on OK and FALSE on Cancel. Colour is green"""
    selected = default == MessageBoxStates.RETRY
    x,y = os.get_terminal_size()
    ox = 0
    if colour:
        BGCL = cp.GREEN
    else:
        BGCL = cp.BLACK
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[Retry]",[cp.set_colour(cp.WHITE,cp.BLACK) if selected else cp.set_colour(cp.BLACK,cp.WHITE)][0])
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2)+10,"[Cancel]",[cp.set_colour(cp.BLACK,cp.WHITE) if selected else cp.set_colour(cp.WHITE,cp.BLACK)][0])   
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == curses.KEY_RIGHT or ch == curses.KEY_LEFT:
            selected = not selected
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return selected
    

def showinfo(stdscr,message: list = [],title:str="Info",colour=False) -> None:
    """Display a messagebox that shows info to a user. Background BLUE"""
    selected = True
    if colour:
        BGCL = cp.BLUE
    else:
        BGCL = cp.BLACK
    x,y = os.get_terminal_size()
    ox = 0
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        stdscr.addstr(y//2-(len(message)//2)-1, x//2-(maxs//2),"┤"+title+"├")
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[OK]",cp.set_colour(cp.WHITE,cp.BLACK)) 
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return

def showwarning(stdscr,message: list = [],title:str="Warning",colour=False) -> None:
    """Display a messagebox that shows a warning to a user. Background YELLOW"""
    selected = True
    if colour:
        BGCL = cp.YELLOW
    else:
        BGCL = cp.BLACK
    x,y = os.get_terminal_size()
    ox = 0
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        stdscr.addstr(y//2-(len(message)//2)-1, x//2-(maxs//2),"┤"+title+"├")
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[OK]",cp.set_colour(cp.WHITE,cp.BLACK)) 
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return

def showerror(stdscr,message: list = [],title:str="Error",colour=False) -> None:
    """Display a message to a user that shows an error. background red."""
    selected = True
    x,y = os.get_terminal_size()
    ox = 0
    if colour:
        BGCL = cp.RED
    else:
        BGCL = cp.BLACK
    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])
    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+4):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",cp.set_colour(BGCL,cp.WHITE))
        rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+4, x//2+(maxs//2+1)+1)
        stdscr.addstr(y//2-(len(message)//2)-1, x//2-(maxs//2),"┤"+title+"├")
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[OK]",cp.set_colour(cp.WHITE,cp.BLACK)) 
        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl,cp.set_colour(BGCL,cp.WHITE))
    
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return