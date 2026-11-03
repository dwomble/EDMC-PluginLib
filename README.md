# EDMC-PluginLib

Bringing EDMC plugin development out of the dark ages. 😜

The library has four components.

1. Demo plugin
1. A unit testing tool
1. A library of display objects
1. A library of useful utility classes and functions
1. Some handy github workflows

## Demo Plugin

Created as a platform to test and exercise the library functionality it also acts as a simple plugin template and displays a journal event list and a lightweight status mode/pips/alert-badge summary.

## Testing

A unit and regression testing tool for EDMC that mocks EDMC functionality enabling `pytest`, python debugger, and `pycov` test coverage analyses.

You can use `pytest` without it to run many functions but this provides a mocked up EDMC environment so you can run realistic scenarios including replaying journal events.

![Debugging a plugin](https://github.com/user-attachments/assets/bf475976-b5aa-4efa-bf60-539893eceb1f)
![Code test coverage](https://github.com/user-attachments/assets/21d05913-a93c-48fa-b600-f6d67fa33f9f)

### Features

* Journal event replay, with customization
* Mock state handling
* Mock EDMC config
* Mock ED logging
* Mock outfitting
* Mock i10n translation
* Mock CAPI event handling
* Mock EDMC Overlay
* Mock HotKeys
* Mock (or live) HTTPS requests
* Mock dashboard event replay

## Display objects

These fall into two main groups. The `th` library contains are objects that self-register with EDMC to match the current theme including use of the EDMC Windows Default theme. When the theme is changed they automatically change with it. There are variants of standard ttk/tk objects and more advanced objects that are useful to plugins. The second group are modified versions of non-standard tk objects.

### th

Advanced objects:

* `Collapsible` – An object that enables collapsed/exapanded views and handles switching between them. It also supports plugin reordering.
* `ScrollableFrame` – A frame that automatically displays or hides a scrollbar depending on whether the content exceeds its configured configured maximum height.
* `RichLabel`, `RichText` and `RichScrolledText` – versions of Label, Text and ScrolledText objects capable of natively displaying Markdown or HTML content.
* `Tooltip` – a mouseover tooltip object
* `Placeholder` – An Entry object that can display a placeholder value
* `Autocompleter` – An Entry object derived from `Placeholder` that will display a dropdown list of autocomplete options returned from a callback.

Standard objects: `Frame`, `LabelFrame`, `Label`, `Entry`, `Text`, `Button`, `Radiobutton`, `ComboBox`, `Listbox`, `Checkbutton`, `Scale`, `Spinbox`

### Non-standard objects

* Richtext tk objects (standalone version of the `RichLabel`, `RichText` and `RichScrolledText`)
* Enhanced Treeview
* Scrollable notebook

## Utility classes and functions

A Library of utilities for EDMC plugins. Some utilities are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin. They have comments or README's describing their functionality.

### Features

* Debug
* Plugin updater
* Notifications capability
* Overlay handler
* Miscellaneous functions (Date utilities, Cross-platform clipboard copy, Nested object retrieval, Singleton decorator)

## Github Workflows

`GitHub` workflow scripts for EDMC plugins.

### release.yml

Removes development artifacts and creates a release `.zip` asset, puts it through VirusTotal, and adds the result to the release notes.

### unit-testing.yml

Runs `flake8` and `pytest` when code is pushed to the main branch or a PR is created for the main branch.
