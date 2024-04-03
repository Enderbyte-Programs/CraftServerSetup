import tomllib
from functools import reduce as __r
import operator as __o
import cursesplus

MASTER = {}

class Config:
    choice:str = "en"

def load(file:str):
    global MASTER
    with open(file,'rb') as f:
        MASTER = tomllib.load(f)
    Config.choice = MASTER["-info"]["default"]

def prompt(stdscr,message="Please choose a language"):
    Config.choice = list(MASTER["-info"]["available"].keys())[cursesplus.optionmenu(stdscr,MASTER["-info"]["available"].values(),message)]
  
def __find(element, json):
    return __r(__o.getitem, element.split('.'), json)
      
def t(translatekey):
    try:
        return __find(translatekey,MASTER)[Config.choice]
    except:
        try:
            return __find(translatekey,MASTER)[MASTER["-info"]["fallback"]]
        except:
            return "X"