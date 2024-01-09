"""
# Curses Plus
Curses Plus is an extension to the curses module that provides some useful featues. This library will be distributed as part of many Enderbyte Programs software products
(c) 2022-2023 Enderbyte Programs, no rights reserved

Source code at https://github.com/Enderbyte-Programs/Curses-Plus
Available on the Python Package Index

## Sub-Packages List
cursesplus.cp         : Standard utilities. Automatically imported by just `import cursesplus`

cursesplus.__init__   : Wrapper for standard utilites but with __package__ and __version__

cursesplus.filedialog : Advanced menus for user-friendly file selection.

cursesplus.messagebox : Package for message-boxes which are messages displayed on top of data instead of over-writing it.

cursesplus.transitions : Module for transitions

"""

__version__ = "3.16.0"
__author__ = "Enderbyte Programs"
__package__ = "cursesplus"

from .cp import *# Maintain backwards compatibility
from . import transitions as transitions
from . import filedialog as filedialog
from . import messagebox as messagebox
from . import utils as utils
from .constants import *#Make colours readily available