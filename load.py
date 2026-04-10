"""
A dummy plugin for testing and illustrative purposes.
It's not intended to be useful other than as a test harness for a test harness.
It just stores the latest journal and dashboard data in global variables for inspection.
"""
import semantic_version
import tkinter as tk
from dataclasses import dataclass, field
from typing import Dict
from companion import CAPIData # type: ignore

PLUGIN_NAME = "DummyPlugin"
PLUGIN_VERSION = semantic_version.Version.coerce("0.0.1-dev")
VERSION = str(PLUGIN_VERSION) # For compatability with the EDMC Plugin Registry

@dataclass
class plugin:
    plugin_dir:str = ""
    parent:tk.Frame|None = None
    frame:tk.Frame|None = None
    closing:bool = False
@dataclass
class dashboard:
    cmdr:str = ""
    is_beta:bool = False
    entry:Dict[str, int] = field(default_factory=dict)
    parent:tk.Frame|None = None
    frame:tk.Frame|None = None
@dataclass
class journal:
    cmdr:str = ""
    is_beta:bool = False
    system:str = ""
    station:str = ""
    entry:Dict[str, int] = field(default_factory=dict)
    state:Dict[str, int] = field(default_factory=dict)

@dataclass
class carrier:
    data:CAPIData|None = None

def plugin_start3(plugin_dir):
    """ Load this plugin into EDMC """
    plugin.plugin_dir = plugin_dir
    return PLUGIN_NAME

def plugin_stop():
    """ EDMC is closing """
    plugin.closing = True

def plugin_app(parent):
    """ Return a TK Frame for adding to the EDMC main window """
    frame:tk.Frame = tk.Frame(parent)
    plugin.parent = parent
    plugin.frame = frame
    return frame

def plugin_prefs(parent, cmdr: str, is_beta: bool):
    """ Return a TK Frame for adding to the EDMC settings dialog """
    prefs:tk.Frame = tk.Frame(parent)
    return prefs

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """ Save settings. """
    pass

def journal_entry(cmdr, is_beta, system, station, entry, state):
    """ Parse an incoming journal entry and store the data we need """
    global journal
    journal.cmdr = cmdr
    journal.is_beta = is_beta
    journal.system = system
    journal.station = station
    journal.entry = entry
    journal.state = state

def dashboard_entry(cmdr:str, is_beta:bool, entry:dict) -> None:
    """ Handle dashboard state changes """
    global dashboard
    dashboard.cmdr = cmdr
    dashboard.is_beta = is_beta
    dashboard.entry = entry

def capi_fleetcarrier(data:CAPIData):
    """ Handle Fleet carrier data """
    carrier.data = data
