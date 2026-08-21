"""
A dummy plugin for testing and illustrative purposes.

It doesn't do anything very useful, but it does implement the plugin interface. It's used to enable unit testing of
the unit test harness making it a test harness test harness.

It could also serve as a template for a new plugin.
It displays journal events as they occur and stores the latest journal, dashboard, and carrier data in global variables for inspection.
"""
import tkinter as tk
from dataclasses import dataclass, field
from typing import Dict
from companion import CAPIData # type: ignore

from demoplugin.utils.debug import Debug, catch_exceptions
from demoplugin.utils.updater import Updater, read_version_file
from demoplugin.ui import UI

PLUGIN_NAME = "DemoPlugin"
VERSION = "0.0.0" # placeholder -- plugin_start3() overwrites this

GH_OWNER = "dwomble" # Github owner name
GH_PROJECT = 'EDMC-DemoPlugin' #  Github project name

@dataclass
class plugin:
    plugin_dir:str = ""
    updater:Updater|None = None
    parent:tk.Frame|None = None
    ui:UI|None = None
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

def get_overlay(modern:bool):
    """ Try loading an overlay plugin. Return True if it was successful, False if not. """
    try:
        from EDMCOverlay import edmcoverlay # type: ignore
        if modern:
            from overlay_plugin.overlay_api import define_plugin_group # type: ignore
        return edmcoverlay.Overlay()
    except ImportError:
        pass
    return None

def plugin_start3(plugin_dir):
    """ Load this plugin into EDMC """
    global VERSION
    version = read_version_file(plugin_dir, "0.0.0")
    VERSION = str(version)

    plugin.plugin_dir = plugin_dir
    plugin.updater = Updater(str(plugin.plugin_dir), GH_OWNER, GH_PROJECT)
    # Let's not since this is a dummy plugin
    #plugin.updater.check_for_update(version)

    return PLUGIN_NAME

def plugin_stop():
    """ EDMC is closing """
    if plugin.updater and plugin.updater.install_update:
        plugin.updater.install()

    plugin.closing = True

@catch_exceptions
def plugin_app(parent:tk.Frame):
    """ Return a TK Frame for adding to the EDMC main window """
    plugin.parent = parent
    frame:tk.Frame = tk.Frame(parent)
    plugin.ui = UI(frame)

    return frame

def plugin_prefs(parent:tk.Frame, cmdr: str, is_beta: bool):
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

    if not plugin.ui:
        return

    plugin.ui.add_entry(entry)

def dashboard_entry(cmdr:str, is_beta:bool, entry:dict) -> None:
    """ Handle dashboard state changes """

    dashboard.cmdr = cmdr
    dashboard.is_beta = is_beta
    dashboard.entry = entry

    if plugin.ui:
        plugin.ui.update_dashboard(entry)

def capi_fleetcarrier(data:CAPIData):
    """ Handle Fleet carrier data """

    carrier.data = data
