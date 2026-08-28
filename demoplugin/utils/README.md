# EDMC Plugin Utilities

A Library of useful utilities for EDMC plugins.

## Updater and Notifier

A class to check if a new release of the plugin is available, download the zip asset, and install it on exit.

```python
from utils.updater import Updater

def plugin_start3(plugin_dir) -> str:
    updater = Updater(plugin_dir)
    updater.check_for_update(plugin_version, plugin_name)
    return NAME

def plugin_stop() -> None:
    if updater.install_update:
        updater.install()
```

A class to display a notice in the UI.

```python
from utils.updater import Notices

def plugin_start3(plugin_dir):
    plugin.notices = Notices(GH_OWNER, GH_PROJECT, GH_MAIN)
    plugin.notices.check_for_notices()

    return PLUGIN_NAME

def show_notice() -> None:
    global notice
    if not plugin.notices or not plugin.notices.pending_notice:
        return
    notice:th.RichText = th.RichText(plugin.frame, width=60, height=2, markdown=Context.notices.pending_notice)
    notice.bind("<Button-1>", partial(self.dismiss_notice))
    notice.grid(row=0, column=0, sticky=tk.W)

def dismiss_notice(tkEvent = None) -> None:
    plugin.notices.dismiss_notice()
    notice.destroy()
    plugin.frame.update_idletasks()
```

### Example NOTICES.md

```markdown
# Notices

## 2
A **second** notification.

## 1
A **first** notification.
```

## Debug

A class for EDMC logging that automatically registers a debug handler and adjusts the debug level dependent on whether the plugin is in development mode. Also a decorator to automatically catch and log runtime errors that may not get caught by EDMC or caught too late by EDMC.

```python
from utils.debug import Debug, catch_exceptions

Debug(plugin_dir, dev_mode)
Debug.logger.debug(f"debug message {param}")

@catch_exceptions
my_func()
    " My function "
    return 23 / 0
```

## An EDMC-theme aware library of tk objects

These are suitable for the main EDMC window and will automatically adapt to regular, dark or transparent modes. Just like EDMC they use ttk objects where possible for light mode and tk equivalents for dark and transparent.

Note they only support `grid` not `pack` layout and scrollbars are OS native so cannot be made to adjust to the dark or transparent theme.

### Standard tk

* Theme-aware versions of the following standard objects: Frame, LabelFrame, ScrollableFrame, Label, Entry, Text, RichLabel, RichText, RichScrolledText, Button, Radiobutton, ComboBox, Listbox, Checkbutton, Scale, Spinbox, Tooltip, Autocompleter, Placeholder

### th.ScrollableFrame

A themed frame whose `.interior` scrolls vertically once its content exceeds `maxheight`, hiding the scrollbar entirely while content fits. Use `.clear()` to replace all of `.interior`'s content in one shot rather than destroying its children individually.

### th.Placeholder

An themed tk.Entry class that includes a placeholder value and popup menu.

```python
mymenu:dict = {
    "Source": [ self.set_source, "src"],
    "Destination": [self.destination_func, "dest"]
}
my_field:th.Placeholder = th.Placeholder(frame, "Placeholder text", menu=mymenu)
```

### th.Autocompleter

An themed tk.Entry class that supports placeholder text and a callback function to provide autocomplete functionality.

```python
def callback(inp:str) -> list:
    """ Function called by Autocompleter """
    try:
        results:requests.Response = session.get(my_endpoint, params={'q': inp.strip()}, timeout=3)
    except:
        return [inp]
    return json.loads(results.content)

label:th.Autocompleter = th.Autocompleter(frame, "Placeholder", width=30, func=callback)
```

### th.Tooltip

A popup tooltip for any th object.

```python
th.Tooltip(my_label, "My tooltip string")
```

## Richtext tk objects

tk objects to directly render Markdown or HTML text in EDMC. Provides `RichScrolledText`, `RichText`, and `RichLabel`

```python
from utils.tkrichtext import RichScrolledText

rt:RichScrolledText = RichScrolledText(frame, markdown="#Heading\nSome text...")
rt.pack(fill="both", expand=True, ipadx=5, ipady=5)
```

## Enhanced Treeview

A standalone treeview that functions like a normal ttk Treeview object but with sortable columns and a callback for when an item is clicked.

```python
from utils.treeviewplus import TreeviewPlus

def _selected(values, column, tr:TreeviewPlus, iid:str) -> None:
    frame.clipboard_clear()
    frame.clipboard_append(values[0])

tree:ttk.Treeview = TreeviewPlus(frame, columns=["one", "two", "three"], callback=_selected, show="headings")
tree.heading("one", text="Date", sort_by="datetime")
tree.heading("two", text="Text", sort_by="name")
tree.heading("three", text="Count", sort_by="num")
```

## ScrollableNotebook

A ttk Notebook with scrollable tabs.

## Overlay

a thin wrapper that detects whichever overlay backend is installed (classic `EDMCOverlay`, or EDMCModernOverlay's `edmcoverlay`-compatible transport plus its `define_plugin_group` layout API) and exposes `send_text`/`send_shape`/`send_vect`/`define_group` primitives that no-op cleanly when no overlay is running.

## Miscellaneous

### Date utilities

(python-dateutil)<https://github.com/dateutil/dateutil> modified to run in and EDMC plugin. Provides powerful date parsing and delta functions.

```python
from utils.dateutil.parser import parse

date = parse(string)
```

See [https://dateutil.readthedocs.io/en/stable/index.html] for detailed documentation.

### Clipboard copy

A cross-platform method to copy text into the system paste buffer including environment variable support for unusual situations.

```python
from utils.misc import copy_to_clipboard

copy_to_clipboard("Some text")
```

### Nested object retrieval

Method to retrieve a value from a a nested object by item sequence.

```python
from utils.misc import get_by_path

val = get_by_path(mydict, ['level1', 'level2'], 0)
```

### Singleton decorator

A thread-safe singleton decorator.

```python
from utils.misc import singleton

@singleton
class my_singleton:
    __init__():
        pass

x = my_singleton()
y = my_singleton()
x == y
```

## Where to copy `utils/` into your plugin

**Copy it under your plugin's own top-level package -- not into your plugin's root directory.** For example, if your plugin's own code lives under `myplugin/`, copy this library's `utils/` folder to `myplugin/utils/` (and import it as `from myplugin.utils.th import Frame`, etc.), rather than dropping a bare `utils/` folder next to `load.py`.

Why this matters: EDMC loads every installed plugin into the *same* Python process, adding each plugin's directory to a shared `sys.path`. If a user has two plugins using this library only the *first* one will ever be used. Nesting under your plugin's own (already-unique) package name avoids this.
