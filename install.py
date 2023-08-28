#!/usr/bin/python3
import curses
import os

if not os.path.isdir("scripts") or not os.path.isfile("scripts/install.sh"):
    print("ERROR! Please run this inside the source tree (cwd is the same folder as scripts and src)")

def main(stdscr):
    recent = 0
    curses.start_color()
    curses.init_pair(7,curses.COLOR_GREEN,curses.COLOR_BLACK)
    curses.init_pair(8,curses.COLOR_RED,curses.COLOR_BLACK)
    while True:
        stdscr.addstr(0,0,"AutoMCServer Installer. \n\rPlease press the key on the left to execute the action to the right")
        stdscr.addstr(2,0,f"LAST ACTION: {['good' if recent == 0 else 'bad. See recent.log'][0]}",curses.color_pair(int(recent != 0)+7))
        stdscr.addstr(3,0,"I      Install AutoMCServer")
        stdscr.addstr(4,0,"R      Uninstall AutoMCServer")
        stdscr.addstr(5,0,"C      Reset AutoMCServer")
        stdscr.addstr(6,0,"Q      Exit installer")
        ch = curses.keyname(stdscr.getch()).decode()
        if ch == "i" or ch == "I":
            stdscr.addstr(6,0," ")
            stdscr.refresh()
            curses.reset_shell_mode()
            recent = os.system("bash scripts/install.sh > recent.log")
            curses.reset_prog_mode()
        elif ch == "r" or ch == "R":
            stdscr.addstr(6,0," ")
            stdscr.refresh()
            curses.reset_shell_mode()
            recent = os.system("bash scripts/remove.sh > recent.log")
            curses.reset_prog_mode()
        elif ch == "c" or ch == "C":
            stdscr.addstr(6,0," ")
            stdscr.refresh()
            curses.reset_shell_mode()
            recent = os.system("bash scripts/clear.sh > recent.log")
            curses.reset_prog_mode()
        elif ch == "q" or ch == "Q":
            return
        stdscr.erase()
        stdscr.clear()
        
curses.wrapper(main)