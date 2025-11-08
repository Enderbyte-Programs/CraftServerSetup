"""Assorted curses-related utilities that are not full wizards but are useful nonetheless"""

import os
import curses

def fill_line(stdscr,line: int,colour: int):
    """Fill a line, colour is the result of set_colour(fg,bg)"""
    stdscr.addstr(line,0," "*(os.get_terminal_size()[0]-1),colour)

def hidecursor():
    """Hide Cursor. Can only be called in an active curses window"""
    curses.curs_set(0)

def showcursor():
    """Show cursor. Can only be called in an active curses window"""
    curses.curs_set(1)