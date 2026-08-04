# EDMC Plugin Utilities

A Library of useful utilities for EDMC plugins. Some are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin.

## debug

A class for EDMC logging that automatically registers a debug handler and adjusts the debug level dependent on whether the plugin is in development mode and a decorator to automatically catch and log runtime errors.

```python
from utils.debug import Debug, catch_exceptions

Debug(plugin_dir, dev_mode)
Debug.logger.debug(f"debug message {param}")

@catch_exceptions
my_func()
    " My function "
    return 23 / 0
```

## updater

A class to check if a new release of the plugin is available, download the zip asset, and install it on exit.

```python
from utils.updater import Updater

def plugin_start3(plugin_dir) -> None:
    updater = Updater(plugin_dir)
    updater.check_for_update(plugin_version, plugin_name)

def plugin_stop() -> None:
    if updater.install_update:
        updater.install()
```

## dateutil

(python-dateutil)<https://github.com/dateutil/dateutil> modified to run in and EDMC plugin. Provides powerful date parsing and delta functions.

```python
from utils.dateutil.parser import parse

date = parse(string)
```

See [https://dateutil.readthedocs.io/en/stable/index.html] for detailed documentation.

## copy_to_clipboard

A cross-platform method to copy text into the system paste buffer including environment variable support for unusual situations.

```python
from utils.misc import copy_to_clipboard

copy_to_clipboard("Some text")
```

## get_by_path

Method to retrieve a value from a a nested object by item sequence.

```python
from utils.misc import get_by_path

val = get_by_path(mydict, ['level1', 'level2'], 0)
```

## Singleton

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

## th – an EDMC-theme aware library of tk objects

These are suitable for the main EDMC window and will adapt to regular, dark or transparent modes. Note they only support `grid` not `pack` layout

* TopLevel
* Frame
* LabelFrame
* ScrollableFrame
* Label
* Button
* Radiobutton
* ComboBox
* Listbox
* Checkbutton
* Scale
* Spinbox
* Tooltip
* Autocompleter
* Placeholder

### th.ScrollableFrame

A themed frame whose `.interior` scrolls vertically once its content exceeds a `max_height`, hiding the scrollbar entirely while content fits. Use `.clear()` to replace all of `.interior`'s content in one shot rather than destroying its children individually.

### th.Placeholder

An entry class that includes a placeholder value.

```python
my_field:th.Placeholder = th.Placeholder(frame, "Placeholder text")
```

### th.Autocompleter

An Entry class that supports placeholder text and a callback function to provide autocomplete functionality.

```python
import plugin.utils.th as th

def callback(inp:str) -> list:
    """ Function called by Autocompleter """
    try:
        results:requests.Response = requests.get(my_endpoint, params={'q': inp.strip()}, timeout=3)
    except:
        return [inp]
    return json.loads(results.content)

label:th.Autocompleter = th.Autocompleter(frame, "Placeholder", width=30, func=callback)
```

## TreeviewPlus

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

## SrollableNotebook

A ttk Notebook with scrollable tabs.

## tkRichText

tk objects to directly render Markdown or HTML text in EDMC. Provides `RichScrolledText`, `RichText`, and `RichLabel`

```python
from utils.tkrichtext import RichScrolledText

tkobj:RichScrolledText = RichScrolledText(frame, markdown="#Heading\nSome text...")
tkobj.pack(fill="both", expand=True, ipadx=5, ipady=5)
```

## Overlay

a thin wrapper that detects whichever overlay backend is installed (classic `EDMCOverlay`, or EDMCModernOverlay's `edmcoverlay`-compatible transport plus its `define_plugin_group` layout API) and exposes `send_text`/`send_shape`/`send_vect`/`define_group` primitives that no-op cleanly when no overlay is running.
