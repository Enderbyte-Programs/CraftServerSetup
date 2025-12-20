"""
A program to handle link fetching for bedrock
"""
import requests
import cursesplus
import urllib.request
import staticflags
import uicomponents
import os
import zipfile
import dirstack

BEDROCK_REQUEST = "https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"

def get_raw_links() -> dict:
    r = requests.get(BEDROCK_REQUEST).json()

    for link in r["result"]["links"]:
        r[link["downloadType"]] = link["downloadUrl"]

    return r

def get_links() -> list[str]:
    """Return a list[normal, preview] for the OS the user is on"""

    raw_links = get_raw_links()
    if staticflags.ON_WINDOWS:
        return [raw_links["serverBedrockWindows"],raw_links["serverBedrockPreviewWindows"]]
    else:
        return [raw_links["serverBedrockLinux"],raw_links["serverBedrockPreviewLinux"]]

def download_bedrock_software(installdir:str,selectedlink:str) -> None:
    urllib.request.urlretrieve(selectedlink,installdir+"/server.zip")
    dirstack.pushd(installdir)#Make install easier
    zf = zipfile.ZipFile(installdir+"/server.zip")
    zf.extractall(installdir)
    zf.close()
    os.remove(installdir+"/server.zip")
    if not staticflags.ON_WINDOWS:
        os.chmod(installdir+"/bedrock_server",0o777)

def ui_download_bedrock_software(stdscr,p:cursesplus.ProgressBar,installdir:str) -> list:
    """Returns link, ispreview"""
    mx = uicomponents.menu(stdscr,["Latest Bedrock Version","Latest Preview Bedrock Version"],"Please select a version")
    l2d = get_links()[mx]
    p.step("Downloading server file")
    urllib.request.urlretrieve(l2d,installdir+"/server.zip")
    p.step("Extracting server file")
    dirstack.pushd(installdir)#Make install easier
    zf = zipfile.ZipFile(installdir+"/server.zip")
    zf.extractall(installdir)
    zf.close()
    p.step("Removing excess files")
    os.remove(installdir+"/server.zip")
    p.step("Preparing exec")
    if not staticflags.ON_WINDOWS:
        os.chmod(installdir+"/bedrock_server",0o777)

    return [l2d,mx == 1]