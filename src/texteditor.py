import curses
import os
import cursesplus
import tempdir
import dirstack
import appdata

def text_editor(text:str,headmessage="edit") -> str:
    tmpdir = tempdir.generate_temp_dir()
    dirstack.pushd(tmpdir)
    with open(tmpdir+"/"+headmessage,"w+") as f:
        f.write(text)
    editcmd = (appdata.APPDATA["settings"]["editor"]["value"] % "\""+headmessage+"\"")
    curses.reset_shell_mode()
    os.system(editcmd)#Wait for finish
    curses.reset_prog_mode()
    with open(tmpdir+"/"+headmessage) as f:
        newdata = f.read()
    cursesplus.utils.hidecursor()
    dirstack.popd()
    return newdata