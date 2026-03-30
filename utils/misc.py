import subprocess
import os
import sys
import shutil
import tkinter as tk
from typing import Any
from functools import reduce
import operator

"""
  Miscellaneous utility functions
"""
def get_by_path(dic:dict[str, Any], keys:list[str], default:Any = None) -> Any:
    """ Return an element from a nested object by item sequence. """
    try:
        return reduce(operator.getitem, keys, dic) or default
    except (KeyError, IndexError, TypeError):
        return default

def copy_to_clipboard(parent:tk.Widget|None, text:str = '') -> None:
    """ Copy text to the clipboard o windows or Linx, X11 or Wayland """
    if parent == None: return

    # Non-linux is easy.
    if sys.platform not in ['linux', 'linux2']:
        # Use the native clipboard method
        parent.clipboard_clear()
        parent.clipboard_append(text)
        parent.update()
        return

    cmds:dict = { "wl-copy": "wayland",
                "xsel --clipboard --input": "x11",
                "xclip -selection c -target UTF8_STRING": "x11"}

    # Try to use the appropriate CLI clipboard tool
    clipboard_cli:str|None = os.getenv("EDMC_CLIPBOARD_CLI", None)
    if clipboard_cli == None:
        for cmd, session in cmds.items():
            if os.getenv("XDG_SESSION_TYPE") == session and shutil.which(cmd.split()[0]):
                clipboard_cli = cmd
                break

    if clipboard_cli != None:
        try:
            subprocess.run(clipboard_cli.split(), input=text.encode('utf-8'), check=True)
        except subprocess.CalledProcessError as e:
            pass
        return

    # Still nothing? Then run all the ones we can find regardless of session type.
    for cmd in cmds:
        if shutil.which(cmd.split()[0]):
            clipboard_cli = cmd
            try:
                if clipboard_cli != None:
                    subprocess.run(clipboard_cli.split(), input=text.encode('utf-8'), check=True)
            except subprocess.CalledProcessError as e:
                pass

    if clipboard_cli != None:
        return

    # Final fallback to the tkinter version
    parent.clipboard_clear()
    parent.clipboard_append(text)
    parent.update()
