import sys
import os
import argparse

_isportable:bool
_isdev:bool
_startid:int
_manageid:int
_file_to_import:str

def startup():
    """SHOULD ONLY BE CALLED ONCE - Enforce command line arguments and populate CLI config variables.
    Presently, this is getting called by static flags startup"""
    global _isportable
    global _isdev
    global _startid
    global _manageid
    global _file_to_import
    ogpath = sys.argv[0]
    execdir = os.path.dirname(os.path.abspath(ogpath))
    _isportable = False

    argparser = argparse.ArgumentParser("CraftServerSetup",description="A TUI Minecraft Server maker and manager. Run without arguments for a standard interactive experience.",epilog="(c) 2023-2025 Enderbyte programs, some rights reserved. For support, please email enderbyte09@gmail.com")
    argparser.add_argument('importfile',nargs="?",default="",help="An exported server to import if you want to import")
    argparser.add_argument('-p','--portable',action="store_true",required=False,help="Run CraftServerSetup self-contained",dest="p",default=False)
    argparser.add_argument('-d','--developer',action="store_true",required=False,help="Enable debug features",dest="d",default=False)
    argparser.add_argument('-m','--manage',help="Open management UI directly to the server id. Must not be used in conjunction with --start",required=False,default=0,dest="manage_id")#Manage a certain server
    argparser.add_argument("-s",'--start',help="Start the server id provided. Must not be used in conjunction with --manage",required=False,default=0,dest="start_id")#start a certain server
    out = argparser.parse_args()
    _isportable = out.p
    _isdev = out.d
    _file_to_import = os.path.abspath(out.importfile)

    try:
        int(out.manage_id)
        int(out.start_id)
    except:
        print("ARGUMENT ERROR - Please specify the server id to manage or start.")
        sys.exit(4)

    _manageid = int(out.manage_id)
    _startid = int(out.start_id)
    if _manageid != 0 and _startid != 0:
        print("ARGUMENT ERROR - You may not command a manage and a start at the same time.")
        sys.exit(4)

        #Read startup flag
    if os.path.isdir(execdir):
        if os.path.isfile(execdir+"/startupflags.txt"):
            with open(execdir+"/startupflags.txt") as f:
                sfd = f.read().lower()
            
            if "portable" in sfd :
                _isportable = True
            if "developer" in sfd:
                _isdev = True


def is_portable_mode() -> bool:
    return _isportable

def is_developer_mode() -> bool:
    return _isdev

def get_startup_id() -> int:
    return _startid

def get_manage_id() -> int:
    return _manageid

def get_file_to_import() -> str:
    return _file_to_import

def should_run_import_mode() -> bool:
    return _file_to_import != "" and os.path.isfile(_file_to_import)
