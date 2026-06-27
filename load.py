"""
A dummy plugin for testing and illustrative purposes.

It doesn't do anything useful, but it does implement the plugin interface. It's used to enable unit testing of
the unit test harness making it a test harness test harness.

It could also serve as a template for a new plugin.
It stores the latest journal, dashboard, and carrier data in global variables for inspection.
"""
import semantic_version
import tkinter as tk
from dataclasses import dataclass, field
from typing import Dict
from companion import CAPIData # type: ignore

from utils.debug import Debug
from utils.updater import Updater

PLUGIN_NAME = "DummyPlugin"
PLUGIN_VERSION = semantic_version.Version.coerce("0.0.1-dev")
VERSION = str(PLUGIN_VERSION) # For compatability with the EDMC Plugin Registry

GH_PROJECT = 'EDMC-DummyPlugin' #  Github project name

@dataclass
class plugin:
    plugin_dir:str = ""
    updater:Updater|None = None
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
    data:CAPIData

def has_overlay(modern:bool) -> bool:
    """ Try loading an overlay plugin. Return True if it was successful, False if not. """
    try:
        from EDMCOverlay import edmcoverlay # type: ignore
        if modern:
            from overlay_plugin.overlay_api import define_plugin_group # type: ignore
        return True
    except ImportError:
        pass
    return False

def plugin_start3(plugin_dir):
    """ Load this plugin into EDMC """
    plugin.plugin_dir = plugin_dir
    plugin.updater = Updater(str(plugin.plugin_dir), GH_PROJECT)
    # Let's not since this is a dummy plugin
    #plugin.updater.check_for_update(PLUGIN_VERSION)

    return PLUGIN_NAME

def plugin_stop():
    """ EDMC is closing """
    if plugin.updater and plugin.updater.install_update:
        plugin.updater.install()

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

    journal.cmdr = cmdr
    journal.is_beta = is_beta
    journal.system = system
    journal.station = station
    journal.entry = entry
    journal.state = state

def dashboard_entry(cmdr:str, is_beta:bool, entry:dict) -> None:
    """ Handle dashboard state changes """

    dashboard.cmdr = cmdr
    dashboard.is_beta = is_beta
    dashboard.entry = entry

def capi_fleetcarrier(data:CAPIData):
    """ Handle Fleet carrier data """

    carrier.data = data
