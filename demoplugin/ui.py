"""
A dummy plugin for testing and illustrative purposes.
"""
from datetime import datetime, timezone
import tkinter as tk
from tkinter import font

from config import config # type: ignore
import edmc_data as ed # type: ignore

import demoplugin.utils.th as th

MAX_HEIGHT:int = 100 # Pixels
BADGE_COLOR:str = "orange" # reads well in both light and dark theme
PANEL_ENABLED:str = f"PluginLib-PanelEnabled"

JOURNAL_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DISP_FORMAT = "%m-%d %H:%M:%S"
# (label, bit, is_flags2) -- first match in order wins
_MODES:list[tuple[str, int, bool]] = [
    ("On Foot", ed.Flags2OnFoot, True),
    ("In SRV", ed.FlagsInSRV, False),
    ("In Fighter", ed.FlagsInFighter, False),
    ("Docked", ed.FlagsDocked, False),
    ("Landed", ed.FlagsLanded, False),
    ("Jumping", ed.FlagsFsdJump, False),
    ("FSD Charging", ed.FlagsFsdCharging, False),
    ("Mass Locked", ed.FlagsFsdMassLocked, False),
    ("FSD Cooldown", ed.FlagsFsdCooldown, False),
    ("Scooping Fuel", ed.FlagsScoopingFuel, False),
    ("Supercruise", ed.FlagsSupercruise, False),
]

_FOCUS:dict[int, str] = {
    ed.GuiFocusNoFocus: "",
    ed.GuiFocusInternalPanel: "Internal",
    ed.GuiFocusExternalPanel: "External",
    ed.GuiFocusCommsPanel: "Comms",
    ed.GuiFocusRolePanel: "Role",
    ed.GuiFocusStationServices: "Station",
    ed.GuiFocusGalaxyMap: "Galaxy Map",
    ed.GuiFocusSystemMap: "System Map",
    ed.GuiFocusOrrery: "Orrery",
    ed.GuiFocusFSS: "FSS",
    ed.GuiFocusSAA: "SAA",
    ed.GuiFocusCodex: "Codex"
}

# (label, bit, is_flags2) -- shown, in order, only while true
_BADGES:list[tuple[str, int, bool]] = [
    ("Gear Down", ed.FlagsLandingGearDown, False),
    ("Cargo Scoop", ed.FlagsCargoScoopDeployed, False),
    ("In Danger", ed.FlagsIsInDanger, False),
    ("Interdicted", ed.FlagsBeingInterdicted, False),
    ("Low Fuel", ed.FlagsLowFuel, False),
    ("Overheating", ed.FlagsOverHeating, False),
    ("Low Health", ed.Flags2LowHealth, True),
    ("Low O2", ed.Flags2LowOxygen, True),
    ("Handbrake On", ed.FlagsSrvHandbrake, False)
]
class UI:
    """
    It just creates a scrollable frame and writes events into it.

    It can also serve as a template for a new plugin.
    """

    def __init__(self, parent:tk.Frame):
        self.frame:th.Frame = th.Frame(parent)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.frame.columnconfigure(0, weight=1)

        self.view:th.Collapsible = th.Collapsible(self.frame, hidden=not config.get_bool(PANEL_ENABLED, default=True),
                                                  on_toggle=self._toggle)
        expanded:th.Frame = self.view.expanded
        collapsed:th.Frame = self.view.collapsed
        expanded.columnconfigure(0, weight=1)
        expanded.columnconfigure(1, weight=1)
        expanded.columnconfigure(2, weight=1)
        collapsed.columnconfigure(0, weight=1)

        # Header row
        row:int = 0
        title:th.Label = th.Label(expanded, text="PluginLib Demo")
        title.grid(row=row, column=0, columnspan=3, sticky=tk.W)
        self.hide_button:th.Button = self.view.hide_button(expanded, tooltip="Hide panel")
        self.hide_button.grid(row=row, column=3, sticky=tk.E)

        fnt:font.Font = font.Font(font=title.cget("font"))
        fnt.configure(weight="bold")
        title.configure(font=fnt)
        th.Label(collapsed, text="PluginLib Demo", font=fnt).grid(row=0, column=0, sticky=tk.W)
        self.show_button:th.Button = self.view.show_button(collapsed, tooltip="Show panel")
        self.show_button.grid(row=0, column=1, sticky=tk.E)

        # Dashboard status row: mode, pips, badges
        row += 1
        self.mode:th.Button = th.Button(expanded, text="", width=13)
        th.Tooltip(self.mode, "Mode flags")
        self.mode.grid(row=row, column=0, padx=(0, 2), sticky=tk.W)
        self.gui:th.Button = th.Button(expanded, text="", width=13)
        th.Tooltip(self.gui, "GUI Focus")
        self.gui.grid(row=row, column=1, padx=2, sticky=tk.W)
        self.pips:th.Button = th.Button(expanded, text="", width=13)
        th.Tooltip(self.pips, "Pips")
        self.pips.grid(row=row, column=2, padx=2, sticky=tk.W)
        self.badges:th.Button = th.Button(expanded, text="", width=13)
        th.Tooltip(self.badges, "Warning flags")
        self.badges.grid(row=row, column=3, padx=(2, 0), sticky=tk.W)

        # Scrollable display frame
        row += 1
        self.panel:th.ScrollableFrame = th.ScrollableFrame(expanded, maxheight=MAX_HEIGHT)
        self.panel.grid(row=row, column=0, columnspan=4, sticky=tk.EW)
        self.panel.interior.columnconfigure(0, weight=1)

        # Content of the scrollable frame
        self.content:th.Text = th.Text(self.panel.interior, wrap=tk.WORD)
        self.content.grid(row=0, column=0)

    def _toggle(self, hidden:bool) -> None:
        """ Persist the state; collection keeps going either way. """
        config.set(PANEL_ENABLED, not hidden)

    def add_entry(self, event:dict) -> None:
        """ Add a new entry to the scrollable frame. """
        ts:datetime = datetime.strptime(event['timestamp'], JOURNAL_FORMAT)
        tsl:datetime = ts.replace(tzinfo=timezone.utc).astimezone()

        self.content.insert("1.0", f"{tsl.strftime(DISP_FORMAT)}: {event['event']}\n")
        #self.content.insert(tk.END, f"{tsl.strftime(DISP_FORMAT)}: {event['event']}\n")

    def update_dashboard(self, entry:dict) -> None:
        """ Refresh the mode/pips/badges row from a Status.json entry. """
        self.mode.configure(text=self._mode_text(entry))
        self.gui.configure(text=self._gui_text(entry))
        self.pips.configure(text=self._pips_text(entry))
        self.badges.configure(text=self._badges_text(entry))

    def _mode_text(self, entry:dict) -> str:
        """ One word for where/what you're in -- first match wins. """
        flags:int = entry.get('Flags', 0)
        flags2:int = entry.get('Flags2', 0)
        for label, bit, is_flags2 in _MODES:
            if (flags2 if is_flags2 else flags) & bit:
                return label
        return "Flying"

    def _gui_text(self, entry:dict) -> str:
        """ GUI Focus"""
        return _FOCUS[entry.get('GuiFocus', ed.GuiFocusNoFocus)]

    def _pips_text(self, entry:dict) -> str:
        """ Sys/Eng/Wep in whole pips -- Status.json stores half-pips. """
        pips:list = entry.get('Pips', [8, 8, 8]) # raw units are half-pips
        return "/".join(str(p // 2) for p in pips)

    def _badges_text(self, entry:dict) -> str:
        """ Space-joined warnings, or "" when nothing is wrong. """
        flags:int = entry.get('Flags', 0)
        flags2:int = entry.get('Flags2', 0)
        active:list[str] = [
            label for label, bit, is_flags2 in _BADGES
            if (flags2 if is_flags2 else flags) & bit
        ]
        return "  ".join(active)
