import os
import tarfile
import dirstack
import appdata
import json
import cursesplus

def package_server_script(indir:str,outfile:str) -> int:
    try:
        dirstack.pushd(indir)
        with tarfile.open(outfile,"w:xz") as tar:
            tar.add(".")
        dirstack.popd()
    except:
        return 1
    return 0

def unpackage_server(infile:str,outdir:str) -> int:
    try:
        if not os.path.isdir(outdir):
            os.mkdir(outdir)
        dirstack.pushd(outdir)
        with tarfile.open(infile,"r:xz") as tar:
            tar.extractall(".")
        dirstack.popd()
    except:
        return 1
    return 0

def package_server(stdscr,serverdir:str,chosenserver:int):
    sdata = appdata.APPDATA["servers"][chosenserver]
    with open(serverdir+"/exdata.json","w+") as f:
        f.write(json.dumps(sdata))
        #Write server data into a temporary file
    wdir=cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a folder for the output server file")
    if os.path.isdir(wdir):
        wxfileout=wdir+"/"+sdata["name"]+".amc"
        nwait = cursesplus.PleaseWaitScreen(stdscr,["Packaging Server"])
        nwait.start()
        package_server_script(serverdir,wxfileout)
        nwait.stop()
        nwait.destroy()
        #if pr != 0:
        #    cursesplus.messagebox.showerror(stdscr,["An error occured packaging your server"])
        os.remove(serverdir+"/exdata.json")
        cursesplus.messagebox.showinfo(stdscr,["Server is packaged."])