# EDMC-PluginLib

Bringing EDMC plugin development out of the dark ages.

## tests

A unit testing tool for EDMC that mocks up EDMC functionality in order to run `pytest` unit tests, use the python debugger, and `pycov` test coverage analysis.

<img width="158" height="371" alt="Screenshot 2026-04-10 180114" src="https://github.com/user-attachments/assets/21d05913-a93c-48fa-b600-f6d67fa33f9f" />
<img width="595" height="290" alt="Screenshot 2026-04-10 180309" src="https://github.com/user-attachments/assets/bf475976-b5aa-4efa-bf60-539893eceb1f" />

*Features*

* Replay journal events with customization
* Mock (or live) HTTPS requests
* A read and writable mock EDMC config object
* Mock state handling
* Mock CAPI event handling
* A mock overlay
* Mock localization functions

This is a work in progress, not all EDMC or tool functionality is mocked up yet and it may take a little effort to get it working with your plugin, but it does work with some quite complex plugins that use a wide range of EDMC features.

But if you want to run unit tests, replay ED logs, or run your plugin with a debugger it may be worth it.

Examples using the harness include [Navl's Neutron Dancer](https://github.com/dwomble/EDMC-NeutronDancer), [BGS-Tally](https://github.com/aussig/BGS-Tally) and [EDMC Mining Analytics](https://github.com/SweetJonnySauce/EDMC-Mining-Analytics).


## utils

A Library of utilities for EDMC plugins and an EDMC headless test harness. Some utilities are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin. They have comments or README's describing their functionality.
