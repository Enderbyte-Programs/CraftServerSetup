"""Tools for working with code of conduct"""

import os
import propertiesfiles
import langcodes
import cursesplus
import glob
import staticflags

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