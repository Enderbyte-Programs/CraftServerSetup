"""Tools for working with code of conduct"""

import os
import propertiesfiles
import langcodes
import cursesplus
import glob
import staticflags
import uicomponents
import utils
import texteditor

class CodeOfConductFile:
    def __init__(self):
        self.language_code_friendly_name:str  
        self.language_code:str
        self.filename:str
        self.data:str

    

def get_is_code_of_conduct_enabled(serverdir:str) -> bool:
    """Is the code of conduct enabled in this server?"""
    propfile = serverdir + os.sep + "server.properties"
    
    if os.path.isfile(propfile):
        with open(propfile) as f:
            try:
                propdic = propertiesfiles.load(f.read())
                return propdic["enable-code-of-conduct"]
            except:
                pass

    return False

def set_code_of_conduct_enabled(serverdir:str,newvalue:bool) -> None:
    propfile = serverdir + os.sep + "server.properties"
    rdata = propertiesfiles.load(staticflags.DEFAULT_SERVER_PROPERTIES)

    if os.path.isfile(propfile):
        rdata = propertiesfiles.loadf(propfile)

    rdata["enable-code-of-conduct"] = newvalue

    propertiesfiles.dumpf(propfile,rdata)

def get_all_codeofconduct_files(serverdir:str) -> list[CodeOfConductFile]:
    cocdir = serverdir + os.sep + "codeofconduct"
    if not os.path.isdir(cocdir):
        os.mkdir(cocdir)

    res = []

    for file in glob.glob(cocdir+os.sep+"*.txt"):
        with open(file) as f:
            rd = f.read()
        
        c = CodeOfConductFile()
        c.data = rd
        c.filename = file

        filename = os.path.basename(file).split(".")[0]
        c.language_code = filename
        c.language_code_friendly_name = langcodes.get_friendly_name(filename)

        res.append(c)
    
    return res

def codeofconduct_create_screen(stdscr,serverdir:str):
    sellanguage = cursesplus.searchable_option_menu(stdscr,list(langcodes.langcodes.values()),"Choose a language. If unsure, select English United States",["Cancel"])
    if sellanguage != 0:
        acsellcode = langcodes.get_langcode(list(langcodes.langcodes.values())[sellanguage - 1])
        newdata = texteditor.text_editor("",f"Write a code of conduct in {list(langcodes.langcodes.values())[sellanguage - 1]}")
        with open(serverdir+os.sep+"codeofconduct"+os.sep+acsellcode+".txt","w+") as f:
            f.write(newdata)
        cursesplus.messagebox.showinfo(stdscr,["Saved successfully"])

def modify_codeofconduct(stdscr,coc:CodeOfConductFile) -> None:
    op = uicomponents.menu(stdscr,["Back","View Code of Conduct","Edit Code of Conduct","Delete Code of Conduct"],f"COC file for {coc.language_code_friendly_name}")
    
    if op == 1:
        cursesplus.textview(stdscr,text=coc.data,message="Viewing Code of Conduct")

    elif op == 2:
        newdata = texteditor.text_editor(coc.data,f"Edit the file in {coc.language_code_friendly_name}")
        coc.data = newdata
        with open(coc.filename,"w+") as f:
            f.write(newdata)
        cursesplus.messagebox.showinfo(stdscr,["Saved successfully"])

    elif op == 3:
        if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete",f"the code of confuct in {coc.language_code_friendly_name}?"]):
            os.remove(coc.filename)
 
def codeofconductmenu(stdscr,serverdir:str):
    while True:
        cocfiles = get_all_codeofconduct_files(serverdir)
        op = uicomponents.menu(stdscr,["Back","Create"]+["[+] Enable code of conduct" if not get_is_code_of_conduct_enabled(serverdir) else "[-] Disable code of conduct"]+[f"{c.language_code_friendly_name} ({c.language_code})" for c in cocfiles],"Select an existing COC file to edit, or create a new one")
        if op == 0:
            return
        elif op == 1:
            codeofconduct_create_screen(stdscr,serverdir)
        elif op == 2:
            set_code_of_conduct_enabled(serverdir,not get_is_code_of_conduct_enabled(serverdir))
            if get_is_code_of_conduct_enabled(serverdir):
                cursesplus.messagebox.showinfo(stdscr,["Code of conduct will now be shown."])
            else:
                cursesplus.messagebox.showinfo(stdscr,["Code of conduct will no longer be shown."])

        else:
            scf = cocfiles[op-3]
            modify_codeofconduct(stdscr,scf)