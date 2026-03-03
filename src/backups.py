"""Backup profile manager - seems to be a dead end? What happened? As it turns out, no"""

import appdata
import uicomponents
import cursesplus
import dirstack
import json
import datetime
import os
import shutil
import glob
import utils

def parse_bp_ielist(data:dict) -> list[str]:
    final = []
    for include in data["include"]:
        final.append("+ include "+include)
    for exclude in data["exclude"]:
        final.append("- exclude "+exclude)
    return final

def edit_backup_profile(stdscr,backupname: str) :
    bdata = appdata.APPDATA["backupprofiles"][backupname]
    bname = backupname
    while True:
        lditems = parse_bp_ielist(bdata)
        m = uicomponents.menu(stdscr,["FINISH","CHANGE PROFILE NAME","Delete Profile","Create Rule"]+lditems,f"Editing backup profile {bname}")
        if m == 0:
            del appdata.APPDATA["backupprofiles"][backupname]
            appdata.APPDATA["backupprofiles"][bname] = bdata
            return
        elif m == 1:
            while True:
                bname = uicomponents.crssinput(stdscr,"Name the backup profile")
                if bname in appdata.APPDATA["backupprofiles"] and bname != backupname:
                    #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
                    if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Do you want to over-write it?"]):
                        break
                else:
                    break
        elif m == 2:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete this","backup profile?"]):
                del appdata.APPDATA["backupprofiles"][bname]
                return
        elif m == 3:
            wtype = uicomponents.menu(stdscr,["Cancel","Include (files to include)","Exclude (files to not include)"],"What type of rule should this be?")
            if wtype == 0:
                continue
            isexclude = wtype == 2
            imethod = uicomponents.menu(stdscr,["Handwrite a Glob pattern","Select Files/Folders"],"How would you like to input this rule?")
            pattern = [""]
            if imethod == 0:
                cursesplus.displaymsg(stdscr,[
                    "Notes for writing Glob statements",
                    "Use * for wildcard, ** for recursive wildcard",
                    "Do not end with a / for a folder, use /* or /** instead."
                ])
                pattern[0] = uicomponents.crssinput(stdscr,"Write the GLOB pattern to match. Use #SD/ for the server directory.")
            else:
                itype = uicomponents.menu(stdscr,["Choose a directory","Choose file(s)"])
                if itype == 0:
                    idir = cursesplus.filedialog.openfolderdialog(stdscr,"Choose a directory to match.")
                    pattern[0] = idir + "/**"
                else:
                    ifiles = cursesplus.filedialog.openfilesdialog(stdscr,"Choose files to match")
                    pattern = ifiles
                    
            if isexclude:
                bdata["exclude"] += pattern
            else:
                bdata["include"] += pattern
            
        else:
            isexclude = lditems[m-4].startswith("-")
            if cursesplus.messagebox.askyesno(stdscr,["Do you want to delete this rule?"]):
                relname = lditems[m-4].replace("+ include ","").replace("- exclude ","")
                if isexclude:
                    bdata["exclude"].remove(relname)
                else:
                    bdata["include"].remove(relname)
            

def new_backup_profile(stdscr) -> str:
    while True:
        name = uicomponents.crssinput(stdscr,"Name the backup profile")
        if name in appdata.APPDATA["backupprofiles"]:
            if cursesplus.messagebox.askyesno(stdscr,["Name already exists.","Would you like to over-write it?"],default=cursesplus.messagebox.MessageBoxStates.NO):
                return name
            #cursesplus.messagebox.showerror(stdscr,["Name already exists.","Please choose a new one."])
        else:
            #Add to dict
            appdata.APPDATA["backupprofiles"][name] = {
                "include" : ["#SD/*"],
                "exclude" : []
            }
            return name
    
def backup_manager(stdscr):
    while True:
        co = uicomponents.menu(stdscr,["Quit","Create backup profile"]+list(appdata.APPDATA["backupprofiles"].keys()),"Backup Profile Manager")
        if co == 0:
            appdata.updateappdata()
            return
        elif co == 1:
            edit_backup_profile(stdscr,new_backup_profile(stdscr))
        else:
            edit_backup_profile(stdscr,list(appdata.APPDATA["backupprofiles"].keys())[co-2])

def server_backups(stdscr,serverdir:str,serverdata:dict):
    """UI for server backup manager"""
    LBKDIR = serverdata["backupdir"]
    dirstack.pushd(serverdir)#Just in case some super weird bug
    #if not os.path.isdir(LBKDIR):
    #    os.mkdir(LBKDIR)
    while True:
        z = uicomponents.menu(stdscr,["Back","Create a Backup","Load a Backup",f"Choose backup directory ({LBKDIR})","Delete all backups"])
        if z == 0:
            dirstack.popd()
            break
        elif z == 1:
            if uicomponents.resource_warning(stdscr):
                continue
            with open(serverdir+"/crss.json","w+") as f:
                f.write(json.dumps(serverdata))
            useprofile = appdata.APPDATA["backupprofiles"][list(appdata.APPDATA["backupprofiles"].keys())[uicomponents.menu(stdscr,list(appdata.APPDATA["backupprofiles"].keys()),"Select which backup profile to use")]]
            cursesplus.displaymsg(stdscr,["Calculating backup size..."],False)
            totalbackupsize = 0
            filestoindex = []
            for irule in useprofile["include"]:
                filestoindex += glob.glob(irule.replace("#SD",serverdir),recursive=True)
            for includefile in filestoindex:
                if os.path.isdir(includefile):
                    continue
                totalbackupsize += os.path.getsize(includefile)
                
            filetoremove = []
            for erule in useprofile["exclude"]:
                filetoremove += glob.glob(erule.replace("#SD",serverdir),recursive=True)
            for excludefile in filetoremove:
                
                try:
                    filestoindex.remove(excludefile)
                    totalbackupsize -= os.path.getsize(excludefile)
                except:
                    pass
            
            
            if cursesplus.messagebox.askyesno(stdscr,["The backup will take up",utils.parse_size(totalbackupsize),"Do you want to continue?"]):
                dstsname = str(datetime.datetime.now())[0:-7].replace(" ","_").replace(":","")
                p = cursesplus.ProgressBar(stdscr,totalbackupsize+1,bar_location=cursesplus.ProgressBarLocations.CENTER,message="Creating backup")
                for file in filestoindex:
                    if os.path.isdir(file):
                        continue
                    p.value += os.path.getsize(file) - 1
                    p.step(file)
                    
                    dst = LBKDIR + f'/{dstsname}/' + file.replace(serverdir,"")
                    os.makedirs(os.path.dirname(dst),exist_ok=True)
                    try:
                        shutil.copyfile(file,dst)
                    except:
                        pass#Fix bug - temp files crash
                p.done()
                cursesplus.messagebox.showinfo(stdscr,["Completed backup"])
                
        elif z == 2:
            if len(os.listdir(LBKDIR)) == 0:
                cursesplus.messagebox.showwarning(stdscr,["You do not have any backups"])
                continue
            if cursesplus.messagebox.askyesno(stdscr,["This will completely overwrite your server directory","Are you sure you wish to proceed"]):
                selbk = cursesplus.filedialog.openfolderdialog(stdscr,"Please choose a backup dir",directory=LBKDIR)
                #cursesplus.displaymsg(stdscr,["Restoring Backup"],False)
                w = cursesplus.PleaseWaitScreen(stdscr,["Restoring Backup"])
                w.start()
                os.chdir("/")
                shutil.rmtree(serverdir)
                shutil.copytree(selbk,serverdir)
                try:
                    with open(serverdir+"/crss.json") as f:
                        nd = json.load(f)
                        locateid = nd["id"]
                        tom_index = next((index for (index, d) in enumerate(appdata.APPDATA["servers"]) if d["id"] == locateid), None)
                        appdata.APPDATA["servers"][tom_index] = nd
                except:
                    pass
                w.stop()
                cursesplus.messagebox.showinfo(stdscr,["Restore completed"])
                os.chdir(serverdir)       
        elif z == 3:
            serverdata["backupdir"] = cursesplus.filedialog.openfolderdialog(stdscr,"Choose a new backup directory")
            LBKDIR = serverdata["backupdir"]
            appdata.updateappdata()       
        elif z == 4:
            if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to delete all backups?"]):
                shutil.rmtree(LBKDIR,True)
                os.mkdir(LBKDIR)