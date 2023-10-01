"""
This module contains advertisement support using the Enderbyte Programs ad network.
"""

import webbrowser       #Open ads in browser
import requests         #Procure ad data
import cursesplus       #Display ads

POST_MESSAGE = ""

class Advertisement:
    def __init__(self,url:str,msg:str):
        self.url = url
        self.message = msg
    def show(self,stdscr):
        if cursesplus.messagebox.askyesno(stdscr,["Advertisement",""] + self.message.splitlines() + ["","Open website?"]+[POST_MESSAGE]):
            webbrowser.open(self.url)
            stdscr.clear()
            stdscr.erase()

ADLIB_BASE = "https://pastebin.com/raw/Jm1NV9u6"#   I'm sorry I had to do this.
ADS:list[Advertisement] = []

def gen_adverts(message=""):
    global POST_MESSAGE
    POST_MESSAGE = message
    """Send a request and generate advertisements"""
    d = requests.get(ADLIB_BASE).text
    for ad in d.splitlines():
        if ad == "":
            continue
        ADS.append(Advertisement(ad.split("|")[0],ad.split("|")[1].replace("\\n","\n")))
