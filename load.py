
import semantic_version
import tkinter as tk
from companion import CAPIData # type: ignore

PLUGIN_NAME = "DummyPlugin"
PLUGIN_VERSION = semantic_version.Version.coerce("0.0.1-dev")
VERSION = str(PLUGIN_VERSION) # For compatability with the EDMC Plugin Registry


def plugin_start3(plugin_dir):
    """ Load this plugin into EDMC """
    return PLUGIN_NAME

def plugin_stop():
    """ EDMC is closing """
    pass

def plugin_app(parent):
    """ Return a TK Frame for adding to the EDMC main window """
    frame:tk.Frame = tk.Frame(parent)
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
    pass

def dashboard_entry(cmdr:str, is_beta:bool, entry:dict) -> None:
    """ Handle dashboard state changes """
    pass

def capi_fleetcarrier(data: CAPIData):
    """ Handle Fleet carrier data """
    pass
