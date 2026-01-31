"""Custom UI components for CRSS"""

import cursesplus
import appdata
import os
import curses
import utils


def menu(stdscr,options:list[str],title="Please choose an option from the list below",footer="") -> int:
    """An alternate optionmenu that will be used in primary areas. The only difference from Curses Plus is that it has some colour presets"""
    try:
        uselegacy = appdata.APPDATA["settings"]["oldmenu"]["value"]
    except:
        uselegacy = True
    
    if uselegacy:
        return cursesplus.optionmenu(stdscr,options,title)
    selected = 0
    offset = 0

    maxl = utils.list_get_maxlen(options)
    while True:
        stdscr.clear()
        mx,my = os.get_terminal_size()
        
        cursesplus.utils.fill_line(stdscr,0,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        cursesplus.utils.fill_line(stdscr,1,cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        stdscr.addstr(0,0,title,cursesplus.set_colour(cursesplus.BLUE,cursesplus.WHITE))
        stdscr.addstr(1,0,"Use the up and down arrow keys to navigate and enter to select",cursesplus.set_colour(cursesplus.WHITE,cursesplus.BLACK))
        oi = 0
        for op in options[offset:offset+my-7]:
            if utils.str_contains_word(op,"back") or utils.str_contains_word(op,"quit") or utils.str_contains_word(op,"cancel") or utils.str_contains_word(op,"delete") or utils.str_contains_word(op,"disable") or utils.str_contains_word(op,"reset") or utils.str_contains_word(op,"[-]"):
                col = cursesplus.RED
            elif utils.str_contains_word(op,"start") or utils.str_contains_word(op,"new") or utils.str_contains_word(op,"add") or utils.str_contains_word(op,"enable") or utils.str_contains_word(op,"create") or utils.str_contains_word(op,"[+]") or utils.str_contains_word(op,"finish"):
                col = cursesplus.GREEN
            elif op.upper() == op:
                col = cursesplus.CYAN
            elif utils.str_contains_word(op,"update") or utils.str_contains_word(op,"help"):
                col = cursesplus.MAGENTA
            else:
                col = cursesplus.WHITE
            if not oi == selected-offset:
                stdscr.addstr(oi+3,7,utils.smart_trim_text(op,mx - 8),cursesplus.set_colour(cursesplus.BLACK,col))
            else:
                stdscr.addstr(oi+3,7,utils.smart_trim_text(op,mx - 8),cursesplus.set_colour(cursesplus.BLACK,col) | curses.A_UNDERLINE | curses.A_BOLD)
            oi += 1
        stdscr.addstr(selected+3-offset,1,"-->")
        stdscr.addstr(oi+3,0,"━"*(mx-1))
        if offset > 0:
            stdscr.addstr(3,maxl+15,f"{offset} options above")
        if len(options) > offset+my-7:
            stdscr.addstr(oi+2,maxl+15,f"{len(options)-offset-my+7} options below")
        
        stdscr.addstr(oi+4,0,footer)#Add footer

        stdscr.refresh()
        ch = stdscr.getch()
        if ch == curses.KEY_DOWN and selected < len(options)-1:
            
            selected += 1
            if selected > my-8:
                offset += 1
        elif ch == curses.KEY_UP and selected > 0:
            
            selected -= 1
            if selected < offset:
                offset -= 1
        elif ch == 10 or ch == 13 or ch == curses.KEY_ENTER:
            return selected
        elif ch == curses.KEY_HOME:
            selected = 0
            offset = 0
        elif ch == curses.KEY_END:
            selected = len(options)-1
            if selected > my-8+offset:
                offset = selected-my+8

def crssinput(stdscr,
    prompt: str,
    lines: int = 1,
    maxlen: int = 0,
    passwordchar: str = None,#type:ignore
    retremptylines: bool = False,
    prefiltext: str = "",
    bannedcharacters: str = "") -> str:
    cursesplus.utils.showcursor()
    r = cursesplus.cursesinput(stdscr,prompt,lines,maxlen,passwordchar,retremptylines,prefiltext,bannedcharacters)
    cursesplus.utils.hidecursor()
    return r

def resource_warning(stdscr) -> bool:
    if appdata.APPDATA["settings"]["reswarn"]:
        return not cursesplus.messagebox.askyesno(stdscr,["What you just selected is a high resource operation.","Continuing may affect the performance of other apps running on this device.","Are you sure you wish to proceed?"])
    else:
        return False