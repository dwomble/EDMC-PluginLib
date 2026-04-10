# EDMC-PluginLib

## utils

A Library of utilities for EDMC plugins and an EDMC headless test harness. Some utilities are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin. They have comments or README's describing their functionality.

## tests

A unit testing tool for EDMC that mocks up EDMC functionality in order to run `pytest` unit tests, use the python debugger, and `pycov` test coverage analysis.

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
