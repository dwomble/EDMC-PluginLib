"""
Integration test for the dashboard status row: load.py's dashboard_entry()
wired through to UI.update_dashboard() and the mode/pips/badges labels.

Run with:
    .venv/bin/python -m pytest tests/test_dashboard_ui.py -v --tb=short
"""
import pytest
from typing import Generator

from edmc_data import ( # type: ignore
    FlagsDocked, FlagsLanded, FlagsSupercruise, FlagsInSRV, FlagsLowFuel,
    FlagsOverHeating, FlagsIsInDanger, Flags2OnFoot, Flags2LowHealth
    )

from harness import TestHarness, reset_plugin_modules
from demoplugin.ui import _MODES, _BADGES

@pytest.fixture
def harness() -> Generator[TestHarness, None, None]:
    global plugin, dashboard, journal, carrier

    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness = TestHarness(live_requests=False)

    from load import plugin_start3, plugin_app, journal_entry, dashboard_entry, plugin, dashboard, journal, carrier

    plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)

    plugin = plugin
    dashboard = dashboard
    journal = journal
    carrier = carrier

    test_harness.load_events("journal_events.json")
    test_harness.register_journal_handler(journal_entry, 'Testy', 'Sol', True)

    test_harness.register_dashboard_handler(dashboard_entry)

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

def _label_for(table:list[tuple[str, int, bool]], bit:int, is_flags2:bool = False) -> str:
    """ Whichever label the table associates with a bit -- so a
    test only checks the right rule fired, not its wording. """
    return next(label for label, b, f2 in table if b == bit and f2 == is_flags2)

class TestModeText:
    def test_defaults_to_flying(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({}) == "Flying"

    def test_docked(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({"Flags": FlagsDocked}) == _label_for(_MODES, FlagsDocked)

    def test_landed(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({"Flags": FlagsLanded}) == _label_for(_MODES, FlagsLanded)

    def test_supercruise(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({"Flags": FlagsSupercruise}) == _label_for(_MODES, FlagsSupercruise)

    def test_in_srv(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({"Flags": FlagsInSRV}) == _label_for(_MODES, FlagsInSRV)

    def test_on_foot(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._mode_text({"Flags2": Flags2OnFoot}) == _label_for(_MODES, Flags2OnFoot, is_flags2=True)

    def test_on_foot_beats_docked(self, harness:TestHarness) -> None:
        """ Walking around a station concourse is more specific. """
        entry:dict = {"Flags": FlagsDocked, "Flags2": Flags2OnFoot}
        assert plugin.ui is not None
        assert plugin.ui._mode_text(entry) == _label_for(_MODES, Flags2OnFoot, is_flags2=True)

class TestPipsText:

    def test_formats_half_pips_as_whole_pips(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._pips_text({"Pips": [6, 6, 4]}) == "3/3/2"

    def test_defaults_to_four_four_four(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._pips_text({}) == "4/4/4"

class TestBadgesText:

    def test_empty_when_nothing_is_wrong(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._badges_text({"Flags": FlagsDocked}) == ""

    def test_single_badge(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._badges_text({"Flags": FlagsLowFuel}) == _label_for(_BADGES, FlagsLowFuel)

    def test_multiple_badges_in_order(self, harness:TestHarness) -> None:
        flags:int = FlagsIsInDanger | FlagsOverHeating
        expected:str = "  ".join([_label_for(_BADGES, FlagsIsInDanger), _label_for(_BADGES, FlagsOverHeating)])
        assert plugin.ui is not None
        assert plugin.ui._badges_text({"Flags": flags}) == expected

    def test_checks_flags2_too(self, harness:TestHarness) -> None:
        assert plugin.ui is not None
        assert plugin.ui._badges_text({"Flags2": Flags2LowHealth}) == _label_for(_BADGES, Flags2LowHealth, is_flags2=True)

class TestDashboardUI:
    def test_updates_mode_and_pips_and_hides_badges_when_clean(self, harness:TestHarness) -> None:
        harness.fire_dashboard_event({"Flags": FlagsDocked, "Pips": [8, 0, 8]})

        from load import plugin
        assert plugin.ui is not None
        assert plugin.ui.mode.cget("text") == "Docked"
        assert plugin.ui.pips.cget("text") == "4/0/4"
        assert plugin.ui.badges.cget("text") == ""

    def test_shows_and_updates_badges_when_something_is_wrong(self, harness:TestHarness) -> None:
        harness.fire_dashboard_event({"Flags": FlagsLowFuel})

        from load import plugin
        assert plugin.ui is not None
        assert plugin.ui.badges.cget("text") == "Low Fuel"
        assert plugin.ui.badges.grid_info() != {}

        harness.fire_dashboard_event({"Flags": FlagsDocked})
        assert plugin.ui.badges.cget("text") == ""

class TestJournalUI:
    def test_handles_journal_entry(self, harness:TestHarness) -> None:
        """ Play a sequence of journal events through the UI. """
        harness.play_sequence('sequence')

        assert plugin.ui is not None
        assert 'StartJump' in plugin.ui.content.get("1.0", "end-1c")
        assert 'ReceiveText' in plugin.ui.content.get("1.0", "end-1c")
        assert 'Undocked' in plugin.ui.content.get("1.0", "end-1c")
        assert 'FSDTarget' in plugin.ui.content.get("1.0", "end-1c")
        assert 'Music' in plugin.ui.content.get("1.0", "end-1c")

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
