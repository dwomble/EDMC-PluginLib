# EDMC-PluginLib Changelog

## v0.2.0 2026-??-??

### New Features

* Added an EDMC theme-aware ttk/tk object library (th) including:
  * TopLevel
  * Frame
  * LabelFrame
  * Label
  * Entry with placeholder text
  * Entry with autocompletion
  * Button
  * RadioButton
  * Checkbutton
  * Combobox
  * Listbox
  * Scale
  * Spinbox
  * Tooltip

### Changes

* The updater now has a configurable re-check frequency limit

### Bug Fixes

* Fixed various placeholder and autocomplete issues with different EDMC theme modes
* Added mock support for tk clipboard

## v0.1.0 2026-04-15

### New Features

* Added rich text support to tooltips
* Added theme support to placeholder and autocompleter
* Added `get_bool` and `get_list` to config mocks
* Added enable/disable overlay capability to test harness
* Added hotkey support to mocks

### Changes

* Removed singleton patterns to improve test harness isolation
* Improved example plugin
* Added more tests
* Simplified the updater configuration
* Extended the test/demo plugin
* Documentation updates

### Bug Fixes

* Fixed a config delete bug

## v0.0.1 2026-04-15

Initial release
