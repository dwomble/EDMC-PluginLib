"""
Integration test for the dashboard status row: load.py's dashboard_entry()
wired through to UI.update_dashboard() and the mode/pips/badges labels.

Run with:
    .venv/bin/python -m pytest tests/test_dashboard_ui.py -v --tb=short
"""
import pytest
from typing import Generator

from harness import TestHarness, reset_plugin_modules
from edmc_data import FlagsDocked, FlagsLowFuel # type: ignore

@pytest.fixture
def harness() -> Generator[TestHarness, None, None]:
    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness = TestHarness(live_requests=False)

    from load import plugin_start3, plugin_app, dashboard_entry
    plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)
    test_harness.register_dashboard_handler(dashboard_entry)

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

def test_updates_mode_and_pips_and_hides_badges_when_clean(harness:TestHarness) -> None:
    harness.fire_dashboard_event({"Flags": FlagsDocked, "Pips": [8, 8, 8]})

    from load import plugin
    assert plugin.ui is not None
    assert plugin.ui.mode_label.cget("text") == "Docked"
    assert plugin.ui.pips_label.cget("text") == "4/4/4"
    assert not plugin.ui.badges_label.grid_info()

def test_shows_and_updates_badges_when_something_is_wrong(harness:TestHarness) -> None:
    harness.fire_dashboard_event({"Flags": FlagsLowFuel})

    from load import plugin
    assert plugin.ui is not None
    assert plugin.ui.badges_label.cget("text") == "Low Fuel"
    assert plugin.ui.badges_label.grid_info() != {}

    harness.fire_dashboard_event({"Flags": FlagsDocked})
    assert plugin.ui.badges_label.cget("text") == ""
    assert not plugin.ui.badges_label.grid_info()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
