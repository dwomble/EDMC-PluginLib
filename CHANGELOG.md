# EDMC-PluginLib Changelog

## v0.2.0 2026-??-??

### New Features

* Made the demo plugin do something slightly useful

* Added an EDMC theme-aware ttk/tk object library (th) including:
  * TopLevel
  * Frame
  * LabelFrame
  * Label
  * Text
  * Entry with placeholder text
  * Entry with autocompletion
  * Button
  * RadioButton
  * Checkbutton
  * Combobox
  * Listbox
  * Scale
  * Spinbox
  * Progressbar
  * Tooltip

### Changes

* The updater now has a configurable re-check frequency limit
* Added richtext support to tooltips
* Added mock get_bool and get_list config methods
* Added mock EDMC-Hotkeys support
* Added enable/disable overlay test support
* Improved l10n mock support
* Added mock support for tk clipboard
* `hfplus()` now formats numbers and dates using the process locale (via
  `locale.format_string()`/`:n`) instead of hardcoded comma/period separators

### Bug Fixes

* Fixed various placeholder and autocomplete issues with different EDMC theme modes

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
