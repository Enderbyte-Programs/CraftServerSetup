"""Shell manager - load the OS shell or terminal emulator"""

import staticflags
import subprocess
import curses
import cursesplus

def launch_shell():

    cursesplus.utils.showcursor()
    curses.reset_shell_mode()

    if staticflags.ON_WINDOWS:
        subprocess.run("powershell")

    else:
        subprocess.run("bash")

    curses.reset_prog_mode()
    cursesplus.utils.hidecursor()