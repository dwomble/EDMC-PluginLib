"""
A dummy plugin for testing and illustrative purposes.
"""
from datetime import datetime, timezone
import tkinter as tk

import edmc_data as ed # type: ignore

import demoplugin.utils.th as th

MAX_HEIGHT:int = 100 # Pixels
BADGE_COLOR:str = "orange" # reads well in both light and dark theme
PANEL_SHOWN_GLYPH:str = "\U0001F648" # see-no-evil monkey -- "pause" analog while visible
PANEL_HIDDEN_GLYPH:str = "\U0001F441" # eye -- "play" analog while hidden

JOURNAL_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DISP_FORMAT = "%m-%d %H:%M:%S"

# (label, bit, is_flags2) -- first match in order wins
_MODES:list[tuple[str, int, bool]] = [
    ("On Foot", ed.Flags2OnFoot, True),
    ("In SRV", ed.FlagsInSRV, False),
    ("Docked", ed.FlagsDocked, False),
    ("Landed", ed.FlagsLanded, False),
    ("Supercruise", ed.FlagsSupercruise, False),
    ("In Fighter", ed.FlagsInFighter, False),
]

# (label, bit, is_flags2) -- shown, in order, only while true
_BADGES:list[tuple[str, int, bool]] = [
    ("In Danger", ed.FlagsIsInDanger, False),
    ("Interdicted", ed.FlagsBeingInterdicted, False),
    ("Low Fuel", ed.FlagsLowFuel, False),
    ("Overheating", ed.FlagsOverHeating, False),
    ("Low Health", ed.Flags2LowHealth, True),
    ("Low O2", ed.Flags2LowOxygen, True),
]
class UI:
    """
    It just creates a scrollable frame and writes events into it.

    It can also serve as a template for a new plugin.
    """

    def __init__(self, parent:tk.Frame):
        self._panel_enabled:bool = True

        self.frame:th.Frame = th.Frame(parent)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.frame.columnconfigure(0, weight=1)

        # Header row
        self.header:th.Frame = th.Frame(self.frame)
        self.header.grid(row=0, column=0, sticky=tk.NSEW)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)
        self.header.columnconfigure(2, weight=1)

        row:int = 0
        title:th.Label = th.Label(self.header, text="PluginLib Demo")
        title.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.toggle_button:th.Button = th.Button(self.header, text=self._toggle_glyph(), width=3, command=self._toggle_panel)
        self.toggle_button.grid(row=row, column=2, sticky=tk.E)

        # Dashboard status row: mode, pips, badges
        row += 1
        self.mode_label:th.Label = th.Label(self.header, text="", width=20)
        self.mode_label.grid(row=row, column=0, sticky=tk.W)
        self.pips_label:th.Label = th.Label(self.header, text="", width=20)
        self.pips_label.grid(row=row, column=1, sticky=tk.W, padx=(8, 8))
        self.badges_label:th.Label = th.Label(self.header, text="", foreground=BADGE_COLOR, width=20)
        self.badges_label.grid(row=row, column=2, sticky=tk.W)

        # Scrollable display frame
        row += 1
        self.panel:th.ScrollableFrame = th.ScrollableFrame(self.frame, maxheight=MAX_HEIGHT)
        self.panel.grid(row=row, column=0,  columnspan=2, sticky=tk.EW)
        self.panel.interior.columnconfigure(0, weight=1)

        # Content of the scrollable frame
        self.content:th.Text = th.Text(self.panel.interior, wrap=tk.WORD)
        self.content.grid(row=0, column=0)


    def _toggle_panel(self) -> None:
        """ Shows/hides content; collection keeps going. """
        self._panel_enabled = not self._panel_enabled

        self.toggle_button.configure(text=self._toggle_glyph())
        if self._panel_enabled:
            self.panel.grid(row=2, column=0, sticky=tk.EW)
        else:
            self.panel.grid_forget()

    def _toggle_glyph(self) -> str:
        return PANEL_SHOWN_GLYPH if self._panel_enabled else PANEL_HIDDEN_GLYPH

    def add_entry(self, event:dict) -> None:
        """ Add a new entry to the scrollable frame. """
        ts:datetime = datetime.strptime(event['timestamp'], JOURNAL_FORMAT)
        tsl:datetime = ts.replace(tzinfo=timezone.utc).astimezone()

        self.content.insert("1.0", f"{tsl.strftime(DISP_FORMAT)}: {event['event']}\n")
        #self.content.insert(tk.END, f"{tsl.strftime(DISP_FORMAT)}: {event['event']}\n")

    def update_dashboard(self, entry:dict) -> None:
        """ Refresh the mode/pips/badges row from a Status.json entry. """
        self.mode_label.configure(text=self._mode_text(entry))
        self.pips_label.configure(text=self._pips_text(entry))
        self.badges_label.configure(text=self._badges_text(entry))

    def _mode_text(self, entry:dict) -> str:
        """ One word for where/what you're in -- first match wins. """
        flags:int = entry.get('Flags', 0)
        flags2:int = entry.get('Flags2', 0)
        for label, bit, is_flags2 in _MODES:
            if (flags2 if is_flags2 else flags) & bit:
                return label
        return "Flying"

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
