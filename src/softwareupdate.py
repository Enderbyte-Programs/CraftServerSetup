"""Utilities and managers for handling the update of the software"""

from staticflags import *
import cursesplus
import requests
import urllib.request
import os
import shutil
import subprocess
import dirstack
import uicomponents
import archiveutils

def windows_update_software(stdscr,interactive=True):

    """Check for and if applicable download a windows update"""

    if interactive:
        cursesplus.displaymsg(stdscr,["Checking for updates"],False)
    
    lastreleaseinfo = requests.get("https://api.github.com/repos/Enderbyte-Programs/CraftServerSetup/releases/latest").json()
    foundurl = None
    ver = lastreleaseinfo["tag_name"]

    if compare_versions(ver.replace("v",""),APP_FRIENDLY_VERSION.replace("v","")) == 1:

        for releaseasset in lastreleaseinfo["assets"]:

            url = releaseasset["browser_download_url"]
            if "installer" in url and url.endswith("exe"):
                foundurl = url

        if cursesplus.messagebox.askyesno(stdscr,["An update is available",f"{APP_FRIENDLY_VERSION} -> {ver}","Would you like to install it?"]):

            if foundurl is not None:
                urllib.request.urlretrieve(foundurl,os.path.expandvars("%TEMP%/crssupdate.exe"))
                os.startfile(os.path.expandvars("%TEMP%/crssupdate.exe")) # type: ignore - This works on windows
                sys.exit()
            else:
                cursesplus.messagebox.showerror(stdscr,["No suitable release asset could be found.","Please report this to devs AT ONCE"])
    else:
        if interactive:
            cursesplus.messagebox.showinfo(stdscr,["No new updates are available"])

def do_linux_update(stdscr,interactive=True) -> bool:
    """Check for and if applicable do a linux update f software"""
    if os.path.isfile("/usr/lib/craftserversetup/updateblock"):
        cursesplus.messagebox.showerror(stdscr,["You are using a debian or arch install setup","Please download the latest version from GitHub"])
        return False
    try:
        if interactive:
            cursesplus.displaymsg(stdscr,["Querrying updates"],False)
        r = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/releases/latest")
        mostrecentreleasedversion = r.url.split("/")[-1][1:]
        if compare_versions(mostrecentreleasedversion,APP_FRIENDLY_VERSION) == 1:
            #New update
            if cursesplus.messagebox.askyesno(stdscr,["There is a new update available.",f"{mostrecentreleasedversion} over {APP_FRIENDLY_VERSION}","Would you like to install it?"]):
                if not os.path.isfile("/usr/lib/craftserversetup/deb"):
                    cursesplus.displaymsg(stdscr,["Downloading new update"],False)
                    downloadurl = f"https://github.com/Enderbyte-Programs/CraftServerSetup/releases/download/v{mostrecentreleasedversion}/craftserversetup.tar.xz"
                    if os.path.isdir("/tmp/crssupdate"):
                        shutil.rmtree("/tmp/crssupdate")
                    os.mkdir("/tmp/crssupdate")
                    urllib.request.urlretrieve(downloadurl,"/tmp/crssupdate/craftserversetup.tar.xz")
                    cursesplus.displaymsg(stdscr,["Installing update"],False)
                    if archiveutils.unpackage_server("/tmp/crssupdate/craftserversetup.tar.xz","/tmp/crssupdate") == 1:
                        cursesplus.messagebox.showerror(stdscr,["There was an error unpacking the update"])
                        return False
                    dirstack.pushd("/tmp/crssupdate")
                    if os.path.isfile("/usr/bin/craftserversetup"):
                        #admin
                        spassword = uicomponents.crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(f"echo -e \"{spassword}\" | sudo -S -k python3 /tmp/crssupdate/installer install",stdout=std0,stderr=std0,shell=True)
                    else:
                        with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                            r = subprocess.call(["python3","/tmp/crssupdate/installer","install"],stdout=std0,stderr=std0)
                    dirstack.popd()
                    if r == 0:
                        return True
                    else:
                        cursesplus.messagebox.showwarning(stdscr,["Update failed.","Check /tmp/crssupdate/UPDATELOG.txt"])
                    
                    # Equivilant of tar -xf
                else:
                    #Attempt deb install
                    cursesplus.displaymsg(stdscr,["Downloading new update"],False)
                    downloadurl = f"https://github.com/Enderbyte-Programs/CraftServerSetup/releases/download/v{mostrecentreleasedversion}/craftserversetup.deb"
                    if os.path.isdir("/tmp/crssupdate"):
                        shutil.rmtree("/tmp/crssupdate")
                    os.mkdir("/tmp/crssupdate")
                    urllib.request.urlretrieve(downloadurl,"/tmp/crssupdate/craftserversetup.deb")
                    cursesplus.displaymsg(stdscr,["Installing update"],False)
                    spassword = uicomponents.crssinput(stdscr,"Please input your sudo password so CraftServerSetup can be updated",passwordchar="#")
                    with open("/tmp/crssupdate/UPDATELOG.txt","w+") as std0:
                        r = subprocess.call(f"echo -e \"{spassword}\n\" | sudo -S -k dpkg -i /tmp/crssupdate/craftserversetup.deb",stdout=std0,stderr=std0,shell=True)

            else:
                return False#Quit by user preference
        else:
            if interactive:
                cursesplus.messagebox.showinfo(stdscr,["No new updates are available"])
            return False#Quit because no update
    except:
        cursesplus.messagebox.showerror(stdscr,["There was an error applying an update"])
        return False#Quit because errpr
    
    return False
    
def compare_versions(version1, version2):
    """0: Same, -1: 1 < 2. 1: 1 > 2"""
    version1_parts = tuple(map(int, version1.split('.')))
    version2_parts = tuple(map(int, version2.split('.')))

    for v1, v2 in zip(version1_parts, version2_parts):
        if v1 < v2:
            return -1
        elif v1 > v2:
            return 1

    if len(version1_parts) < len(version2_parts):
        return -1
    elif len(version1_parts) > len(version2_parts):
        return 1

    return 0

def show_changelog_info(stdscr):
    """Display the latest changelog info"""
    cursesplus.displaymsg(stdscr,["Getting Info"],wait_for_keypress=False)
    changeloginfo = requests.get("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/refs/heads/main/changelog").text
    final = []
    for ln in changeloginfo.splitlines():
        if ln.replace(" ","") == "":
            continue
        if ln.startswith("-") or ln.startswith(" "):
            #Info
            final.append(ln)
        else:
            final.append("")
            final.append("")
            final.append(f"Added in {ln}")
            
    cursesplus.textview(stdscr,text="\n".join(final),message="Changelog Info")


def update_menu(stdscr):
    global UPDATEINSTALLED
    while True:
        m = uicomponents.menu(stdscr,["Back","Check for Updates","View Changelog"])
        if m == 0:
            break
        elif m == 1:
            if ON_WINDOWS:
                windows_update_software(stdscr)
                return
            #OLD UPDATE MAY BE REMOVED IN 0.18.3
            if do_linux_update(stdscr):
                UPDATEINSTALLED = True
                return
        elif m == 2:
            show_changelog_info(stdscr)