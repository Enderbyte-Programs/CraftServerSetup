"""
This module reads documentation files in Enderbyte Programs format.
"""
import cursesplus

class EPDocfile:
    textblocks = {}
    def __init__(self,filetext:str,program_name:str):
        self.text = filetext
        self.name = program_name
    def load(self):
        self.textblocks = {}
        flines = self.text.splitlines()
        for line in flines:
            k = ""
            if line.startswith("$"):
                k = line[1:]
                self.textblocks[line[1:]] = ""
            else:
                self.textblocks[k] += line + "\n"
    def read_from_name(self,stdscr,block_name):
        if not block_name in list(self.textblocks.keys()):
            cursesplus.messagebox.messagebox.showwarning(stdscr,["A documentation entry was not availble under this name"])
        else:
            cursesplus.textview(stdscr,text=self.textblocks[block_name])
    def read_from_index(self,stdscr,index):
        cursesplus.textview(stdscr,text=list(self.textblocks.items())[index])
    def uf_tui(self,stdscr):
        while True:
            z = cursesplus.displayops(stdscr,["BACK"]+list(self.textblocks.keys()))
            if z == 0:
                return
            else:
                self.read_from_name(stdscr,list(self.textblocks.keys())[z-1])

def load_from_text(text:str,name:str) -> EPDocfile:
    return EPDocfile(text,name)

def load_from_file(file:str,name:str) -> EPDocfile:
    with open(file) as f:
        data = f.read()
    return EPDocfile(data,name)