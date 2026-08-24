"""
Unit test for load.py's VERSION handling: resolved from a "version" file (the
same file CI's release.yml stamps and Updater.install() writes) rather than a
hardcoded string, exposed as load.VERSION for plugin-browser tooling.

Run with:
    .venv/bin/python -m pytest tests/test_load.py -v --tb=short
"""
import pytest
from typing import Generator
from unittest.mock import Mock, patch

from harness import TestHarness, reset_plugin_modules

@pytest.fixture
def harness() -> Generator:
    TestHarness.reset_instance()
    reset_plugin_modules()

    test_harness = TestHarness(live_requests=True, overlay=False, hotkeys=False)

    from load import plugin_start3, plugin_app, journal_entry, dashboard_entry, plugin

    # Prevent network updater thread from making tests hang on teardown.
    with patch('load.Updater.check_for_update', return_value=None):
        plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)

    test_harness.plugin = plugin

    # ND-specific, this is the journal handling function and the default journal params
    test_harness.load_events("journal_events.json")
    test_harness.register_journal_handler(journal_entry, 'Testy', 'Sol', True)

    # This is the dashboard handlling function
    test_harness.register_dashboard_handler(dashboard_entry, 'Testy', True)

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()
    reset_plugin_modules()

def test_plugin_start3_resolves_version_from_the_version_file(harness, tmp_path) -> None:
    (tmp_path / "version").write_text("9.9.9")

    from load import plugin_start3, VERSION as initial_version
    assert initial_version == "0.0.0" # placeholder, before plugin_start3() runs

    plugin_start3(str(tmp_path))

    import load
    assert load.VERSION == "9.9.9"

def test_prefs_changed_refreshes_progressbar_style(harness) -> None:
    """ ttk widgets have no fg/bg for theme.py to repaint --
    prefs_changed() must re-apply Progressbar's style for a
    live theme change to actually show up. """
    from tkinter import ttk
    from load import prefs_changed
    from demoplugin.utils.th import Progressbar

    harness.config.set('theme', 1)
    try:
        prefs_changed('Testy', False)
        assert ttk.Style().lookup(Progressbar.STYLE, 'troughcolor') == 'grey4'
    finally:
        harness.config.set('theme', 0)
        Progressbar.refresh_style()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
