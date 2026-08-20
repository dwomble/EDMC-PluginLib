# EDMC-PluginLib

Bringing EDMC plugin development out of the dark ages. 😜

The library has four components.

1. Demo plugin
1. A unit testing tool
1. A library of useful utility classes and functions
1. Some handy github workflows

## Demo Plugin

Created as a platform to test and exercise the library functionality it also acts as a simple plugin template and displays a journal event list and a lightweight status mode/pips/alert-badge summary.

## Testing

A unit and regression testing tool for EDMC that mocks EDMC functionality enabling `pytest`, python debugger, and `pycov` test coverage analyses.

* Development is much faster when you can use the python debugger; replay sequences of events; and run regression tests.
* AI tools such as Claude Code are far more effective when they can write and run regression tests.
* Debugging user issues is much easier when you can replay their journal in your environment to reproduce problems.

[Code test coverage](https://github.com/user-attachments/assets/21d05913-a93c-48fa-b600-f6d67fa33f9f)
[Debugging a plugin](https://github.com/user-attachments/assets/bf475976-b5aa-4efa-bf60-539893eceb1f)

### Features

* Journal event replay, with customization
* Mock state handling
* Mock EDMC config
* Mock ED logging
* Mock i10n translation
* Mock CAPI event handling
* Mock EDMC Overlay
* Mock HotKeys
* Mock (or live) HTTPS requests
* Mock dashboard event replay

## Utility classes and functions

A Library of utilities for EDMC plugins. Some utilities are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin. They have comments or README's describing their functionality.

### Features

* An EDMC-theme aware library of tk objects (Frame, LabelFrame, ScrollableFrame, Label, Button, Radiobutton, ComboBox, Listbox, Checkbutton, Scale, Spinbox, Tooltip, Autocompleter, Placeholder)
* Richtext tk objects (easily display HTML and Markdown)
* Enhanced Treeview
* Scrollable notebook
* Debug
* Plugin updater
* Overlay handler
* Miscellaneous functions (Date utilities, Cross-platform clipboard copy, Nested object retrieval, Singleton decorator)

## Github Workflows

`GitHub` workflow scripts for EDMC plugins.

### release.yml

Removes development artifacts and creates a release `.zip` asset, puts it through VirusTotal, and adds the result to the release notes.

### unit-testing.yml

Runs `flake8` and `pytest` when code is pushed to the main branch or a PR is created for the main branch.
