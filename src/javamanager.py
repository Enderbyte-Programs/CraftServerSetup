"""Manage java installs"""

import appdata
import uicomponents
import os
import cursesplus
import staticflags
import curses
import subprocess

def choose_java_install(stdscr) -> str:

    #Return path of selected java- Smart java?
    while True:
        stdscr.erase()
        jsl = uicomponents.menu(stdscr,["ADD NEW INSTALLATION"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in appdata.APPDATA["javainstalls"]],"Please choose a Java installation from the list")
        if jsl == 0:
            managejavainstalls(stdscr)
        else:
            break
    return appdata.APPDATA["javainstalls"][jsl-1]["path"]

def managejavainstalls(stdscr):
    
    if "java" in [j["path"] for j in appdata.APPDATA["javainstalls"]]:
        pass
    else:
        if os.system("java --help") == 0 or os.system("java /?") == 0 or os.system("java -help") == 0:
        
            appdata.APPDATA["javainstalls"].append({"path":"java","ver":get_java_version()})
        stdscr.clear()
    while True:
        stdscr.erase()
        jmg = uicomponents.menu(stdscr,["ADD INSTALLATION","FINISH"]+[jp["path"]+" (Java "+jp["ver"]+")" for jp in appdata.APPDATA["javainstalls"]])
        if jmg == 0:
            njavapath = cursesplus.filedialog.openfiledialog(stdscr,"Please choose a java executable",directory=os.path.expanduser("~"))
            if os.system(njavapath.replace("\\","/")+" -help") != 0:
                if not cursesplus.messagebox.askyesno(stdscr,["You may have selected an invalid java file.","Are you sure you would like to add it"]):
                    continue
                else:
                    stdscr.erase()
                    ndict = {"path":njavapath.replace("\\","/"),"ver":"Unknown"}
                    if cursesplus.messagebox.askyesno(stdscr,["Do you know what java version this is?"]):
                        ndict["ver"] = uicomponents.crssinput(stdscr,"Java version?",maxlen=10)
                        appdata.APPDATA["javainstalls"].append(ndict)
            else:
                fver = get_java_version(njavapath.replace("\\","/"))
                ndict = {"path":njavapath.replace("\\","/"),"ver":fver}
                appdata.APPDATA["javainstalls"].append(ndict)
        elif jmg == 1:
            return
        else:
            
            jdl = appdata.APPDATA["javainstalls"][jmg-2]
            stdscr.clear()
            stdscr.addstr(0,0,"MANAGING JAVA INSTALLATION")
            stdscr.addstr(2,0,"Path")
            stdscr.addstr(3,0,"Version")
            stdscr.addstr(5,0,"Press V to verify installation | Press D to delete | Press any other key to return",cursesplus.cp.set_colour(cursesplus.WHITE,cursesplus.BLACK))
            stdscr.addstr(2,10,jdl["path"])
            stdscr.addstr(3,10,jdl["ver"])
            k = stdscr.getch()
            if k == curses.KEY_DC or k == 100:
                if cursesplus.messagebox.askyesno(stdscr,["Are you sure you want to remove the java installation",jdl["path"]],default=cursesplus.messagebox.MessageBoxStates.NO):
                    del appdata.APPDATA["javainstalls"][jmg-2]
            elif k == 118:
                jdl["ver"] = get_java_version(jdl["path"])
                if jdl["ver"] == "Error":
                    cursesplus.messagebox.showwarning(stdscr,["Java installaion is corrupt"])
                    del appdata.APPDATA["javainstalls"][jmg-2]
                else:
                    cursesplus.messagebox.showinfo(stdscr,["Java installation is safe"])

        appdata.updateappdata()

def get_java_version(file="java") -> str:
    try:
        if not staticflags.ON_WINDOWS:
            return subprocess.check_output(fr"{file} -version 2>&1 | grep -Eow '[0-9]+\.[0-9]+' | head -1",shell=True).decode().strip()
        else:
            return subprocess.check_output(f"{file} --version").decode().splitlines()[0].split(" ")[1]
    except:
        return "Unknown"