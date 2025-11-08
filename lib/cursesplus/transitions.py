import os
import random
from time import sleep

block = "█"

def __exec(func,args):
    func(*args)

def horizontal_bars(stdscr,func_to_call=None,args=(),speed=1):
    mx,my = os.get_terminal_size()
    for y in range(my-1):
        stdscr.addstr(y,0,block*(mx-1))
        stdscr.refresh()
        sleep(0.01/speed)
    for y in range(my-1):
        stdscr.addstr(y,0," "*(mx-1))
        stdscr.refresh()
        sleep(0.01/speed)
    if func_to_call is not None:
        __exec(func_to_call,args)

def random_blocks(stdscr,func_to_call=None,args=(),speed=1):
    mx,my = os.get_terminal_size()
    
    _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
    while _grid:
        for i in range(round(((my*mx)/(24*80))*20)):# Fixing slow transitions on HD screens
            try:
                pk = random.choice(_grid)
                _grid.pop(_grid.index(pk))
                stdscr.addstr(pk[1],pk[0],block)
                stdscr.refresh()
            except:
                break
        sleep(0.01/speed)
    _grid = [(x,y) for y in range(my-1) for x in range(mx-1)]
    while _grid:
        for i in range(round(((my*mx)/(24*80))*20)):
            try:
                pk = random.choice(_grid)
                _grid.pop(_grid.index(pk))
                stdscr.addstr(pk[1],pk[0]," ")
                stdscr.refresh()
            except:
                break
        sleep(0.01/speed)
    if func_to_call is not None:
        __exec(func_to_call,args)

def vertical_bars(stdscr,func_to_call=None,args=(),speed=1):
    mx,my = os.get_terminal_size()
    for y in range(mx-1):
        for x in range(my-1):
            stdscr.addstr(x,y,block)
        stdscr.refresh()
        sleep(0.01/speed)
    for y in range(mx-1):
        for x in range(my-1):
            stdscr.addstr(x,y," ")
        stdscr.refresh()
        sleep(0.01/speed)
    if func_to_call is not None:
        __exec(func_to_call,args)