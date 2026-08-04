# EDMC-PluginLib

Bringing EDMC plugin development out of the dark ages.

The library has three components.

1. A unit testing tool
1. A library of useful utility classes and functions
1. Some handy github workflows

## Unit Testing

A unit testing tool for EDMC that mocks up EDMC functionality in order to run `pytest` unit tests, use the python debugger, and run `pycov` test coverage analyses.

<img width="158" height="371" alt="Code test coverage" src="https://github.com/user-attachments/assets/21d05913-a93c-48fa-b600-f6d67fa33f9f" />
<img width="595" height="290" alt="Debugging a plugin" src="https://github.com/user-attachments/assets/bf475976-b5aa-4efa-bf60-539893eceb1f" />

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

### Where to copy `utils/` into your plugin

**Copy it under your plugin's own top-level package -- not into your plugin's root directory.** For example, if your plugin's own code lives under `myplugin/`, copy this library's `utils/` folder to `myplugin/utils/` (and import it as `from myplugin.utils.th import Frame`, etc.), rather than dropping a bare `utils/` folder next to `load.py`.

Why this matters: EDMC loads every installed plugin into the *same* Python process, adding each plugin's directory to a shared `sys.path`. If two plugins both vendor a copy of this library at their own root as a bare top-level package literally named `utils`, Python's module cache (`sys.modules`) means only the *first*-loaded plugin's copy is ever actually used -- every other plugin's `from utils.X import Y` silently resolves to the first plugin's version instead of its own, regardless of which version is actually on disk in that plugin's own folder. This showed up in practice as a `TypeError` crash when two plugins vendoring different versions of `utils/updater.py` were installed together.

Nesting under your plugin's own (already-unique) package name avoids this entirely -- `myplugin.utils.updater` and `otherplugin.utils.updater` are different, non-colliding module paths, even though the files are separate copies of the same code. All of this library's own internal cross-references use relative imports specifically so it works correctly at any nesting depth.

## Github Workflows

`GitHub` workflow scripts for EDMC plugins.

### release.yml

Removes development artifacts and creates a release `.zip` asset, puts it through VirusTotal, and adds the result to the release notes.

### unit-testing.yml

Runs `flake8` and `pytest` when code is pushed to the main branch or a PR is created for the main branch.
