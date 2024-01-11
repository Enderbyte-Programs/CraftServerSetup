"""
This module reads documentation files in Enderbyte Programs format.
"""
import cursesplus

class EPDocfile:
    textblocks = {}
    def __init__(self,filetext:str,program_name:str):
        """Prepares an Enderbyte Programs Doc File. Run this.load() to read file."""
        self.text = filetext
        self.name = program_name
    def load(self):
        """Read file and generate documentation sections (__INIT__ DOES NOT DO THIS AUTOMATICALLY)"""
        self.textblocks = {}
        flines = self.text.splitlines()
        k = "Unknown Section"
        for line in flines:
            
            if line.startswith("$"):
                k = line[1:]
                self.textblocks[k] = ""
            else:
                self.textblocks[k] += line + "\n"
    def read_from_name(self,stdscr,block_name):
        """show the text of a documentation section by providing the section name."""
        if not block_name in list(self.textblocks.keys()):
            cursesplus.messagebox.showwarning(stdscr,["A documentation entry was not availble under this name"])
        else:
            cursesplus.textview(stdscr,text=self.textblocks[block_name],message=f"{self.name} Documentation : {block_name}")
    def read_from_index(self,stdscr,index):
        """show the text of a documentation section by providing the section index."""
        cursesplus.textview(stdscr,text=list(self.textblocks.items())[index],message=f"{self.name} Documentation : {list(self.textblocks.keys())[index]}")
    def show_documentation(self,stdscr):
        """Show user-friendly cursesplus documentation menu"""
        while True:
            z = cursesplus.optionmenu(stdscr,["BACK"]+list(self.textblocks.keys()),"Please choose a documentation chapter")
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