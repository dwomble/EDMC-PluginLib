"""
A dummy plugin for testing and illustrative purposes.
"""
from datetime import datetime, timezone

import tkinter as tk
import demoplugin.utils.th as th

MAX_HEIGHT:int = 75 # Pixels
PANEL_SHOWN_GLYPH:str = "\U0001F648" # see-no-evil monkey -- "pause" analog while visible
PANEL_HIDDEN_GLYPH:str = "\U0001F441" # eye -- "play" analog while hidden

JOURNAL_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DISP_FORMAT = "%m-%d %H:%M:%S"

class UI:
    """
    It just creates a scrollable frame and writes events into it.

    It can also serve as a template for a new plugin.
    """

    def __init__(self, parent:tk.Frame):
        self.frame = th.Frame(parent)

        self._panel_enabled = True

        self.header:th.Frame = th.Frame(self.frame)
        self.header.grid(row=0, column=0, sticky=tk.EW)
        self.header.columnconfigure(0, weight=1)
        self.header.columnconfigure(1, weight=1)

        title:th.Label = th.Label(self.header, text="PluginLib Demo")
        title.grid(row=0, column=0, sticky=tk.W)

        self.toggle_button:th.Button = th.Button(self.header, text=self._toggle_glyph(), width=3, command=self._toggle_panel)
        self.toggle_button.grid(row=0, column=2, sticky=tk.E)

        self.panel:th.ScrollableFrame = th.ScrollableFrame(self.frame, maxheight=MAX_HEIGHT)
        self.panel.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
        self.panel.interior.columnconfigure(0, weight=1)
        if not self._panel_enabled:
             self.panel.grid_forget()

        self.content:tk.Text = tk.Text(self.panel.interior, wrap=tk.WORD)
        self.content.grid(row=0, column=0)

        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

    def _toggle_panel(self) -> None:
        """ Shows/hides content; collection keeps going. """
        self._panel_enabled = not self._panel_enabled

        self.toggle_button.configure(text=self._toggle_glyph())
        if self._panel_enabled:
            self.panel.grid(row=1, column=0, sticky=tk.EW)
        else:
            self.panel.grid_forget()

    def _toggle_glyph(self) -> str:
        return PANEL_SHOWN_GLYPH if self._panel_enabled else PANEL_HIDDEN_GLYPH

    def add_entry(self, event:dict) -> None:
        """ Add a new entry to the scrollable frame. """
        ts:datetime = datetime.strptime(event['timestamp'], JOURNAL_FORMAT)
        tsl:datetime = ts.replace(tzinfo=timezone.utc).astimezone()

        self.content.insert("1.0", f"{event['timestamp']}: {event['event']}\n")
        #self.content.insert(tk.END, f"{tsl.strftime(DISP_FORMAT)}: {event['event']}\n")
