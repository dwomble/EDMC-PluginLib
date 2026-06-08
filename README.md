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

* Replay journal events (with customization)
* Mock (or live) HTTPS responses
* Mock EDMC config object
* Mock state handling
* Mock CAPI event handling
* A mock overlay
* Mock localization functions

Though it works with some quite complex plugins that use a wide range of EDMC features, this is a work in progress and not all EDMC or tool functionality is mocked up yet so it may take a little effort to get it working with your plugin.

Examples using the harness include [Navl's Neutron Dancer](https://github.com/dwomble/EDMC-NeutronDancer), [BGS-Tally](https://github.com/aussig/BGS-Tally) and [EDMC Mining Analytics](https://github.com/SweetJonnySauce/EDMC-Mining-Analytics).

### Installation

Copy the `/tests` folder into your plugin, edit the `test_conformance.py` to implement your tests. 

The library includes a simplistic plugin and conformance tests that exercise the harness itself. i.e. The library uses the test harness to test the test harness.

## Utility classes and functions

A Library of utilities for EDMC plugins and an EDMC headless test harness. Some utilities are drop-in ready to go, some may require some configuration, and others may need adapting to your plugin. They have comments or README's describing their functionality.

## Github Workflows

Some useful `GitHub` workflow scripts.

### release.yml

Creates a release `.zip` and puts it through VirusTotal and adds the result to the release notes.

### unit-testing.yml

Runs `flake8` and `pytest` when code is pushed to the main branch or a PR is created for the main branch.
