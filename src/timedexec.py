"""A module to make a time out messagebox"""
import os
import curses.textpad
import time
from cursesplus import set_colour,WHITE,BLACK,YELLOW

def timeout_askyesno(stdscr,message:list[str],default:bool,timeout:int):
    """Display a messagebox that asks a user a questions. Returns TRUE on Yes and FALSE on No. The user has timeout seconds to answer. If they don't defaul tiwll be returned."""
    stdscr.nodelay(True)
    selected = default
    x,y = os.get_terminal_size()
    ox = 0

    framesremaining = timeout * 10

    for o in message:
        ox += 1
        if "\n" in o:
            message.insert(ox,o.split("\n")[1])
    message = [m[0:x-5].split("\n")[0] for m in message[0:y-5]]#Limiting characters
    maxs = max([len(s) for s in message])

    if maxs < len("Dismissing in "+str(timeout))+1:
        maxs = len("Dismissing in "+str(timeout))+1

    while True:
        for by in range(y//2-(len(message)//2)-1,y//2+(len(message)//2)+5):
            for bx in range(x//2-(maxs//2)-1,x//2+(maxs//2+1)+1):
                stdscr.addstr(by,bx," ",set_colour(BLACK,WHITE))
        curses.textpad.rectangle(stdscr,y//2-(len(message)//2)-1, x//2-(maxs//2)-1, y//2+(len(message)//2)+5, x//2+(maxs//2+1)+1)
        stdscr.addstr(y//2+(len(message)//2)+5,x//2-(maxs//2),"Y: Yes | N: No")
        mi = -(len(message)/2)
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2),"[Yes]",[set_colour(WHITE,BLACK) if selected else set_colour(BLACK,WHITE)][0])
        stdscr.addstr(y//2+(len(message)//2)+3,x//2-(maxs//2)+10,"[No]",[set_colour(BLACK,WHITE) if selected else set_colour(WHITE,BLACK)][0])  
        stdscr.addstr(y//2+(len(message)//2)+4,x//2-(maxs//2),f"Dismissing in {framesremaining // 10}s",set_colour(BLACK,YELLOW))

        for msgl in message:
            mi += 1
            stdscr.addstr(int(y//2+mi),int(x//2-len(msgl)//2),msgl)
    
        stdscr.refresh()
        framesremaining -= 1
        if framesremaining == 0:
            stdscr.nodelay(False)
            return selected
        time.sleep(1/10)#10 FPS should be fine

        ch = stdscr.getch()
        if ch == curses.KEY_RIGHT or ch == curses.KEY_LEFT:
            selected = not selected
        elif ch == 121 or ch == 110:
            stdscr.nodelay(False)
            return ch == 121
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            stdscr.nodelay(False)

            return selected