"""
Test suite for and EDMC plugin using pytest.

Run with:
    .venv/bin/python -m pytest tests/test_plugin.py -v --tb=short
or
    .venv/bin/python -m pytest tests/test_basic.py
"""
import pytest
from typing import Generator
import json

from harness import TestHarness
import load
from .edmc.requests import queue_response, MockResponse
import requests

@pytest.fixture
def harness(request) -> Generator[TestHarness, None, None]:
    """ Provide a fresh test harness for each test. """
    global plugin, dashboard, journal, carrier, capi_fleetcarrier

    live = request.node.get_closest_marker('live_requests') is not None

    test_harness = TestHarness(live_requests=live)

    from load import plugin_start3, plugin_app, journal_entry, capi_fleetcarrier

    plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)

    plugin = load.plugin
    dashboard = load.dashboard
    journal = load.journal
    carrier = load.carrier

    test_harness.load_events("journal_events.json")
    test_harness.register_journal_handler(journal_entry, 'Testy', 'Sol', False)

    yield test_harness

class TestInitialization:
    """Test basic initialization features."""

    def test_harness_initialization(self, harness:TestHarness) -> None:
        """Test basic harness initialization."""
        assert harness is not None
        assert harness.config.get_str('DummyPlugin_status', default='Disabled') == 'Active'

    def test_plugin_registration(self, harness:TestHarness) -> None:
        """Test that the plugin registered correctly."""

        assert harness.plugin_dir != ""
        assert harness.parent is not None

        assert plugin.plugin_dir == str(harness.plugin_dir)
        assert plugin.parent == harness.parent
        assert plugin.frame is not None

    def test_mock_config(self, harness:TestHarness) -> None:
        """Test the mock config."""

        harness.config.set('DummyPlugin_intval', 42)
        harness.config.set('DummyPlugin_strval', "Hello, World!")

        assert harness.config.get_str('DummyPlugin_status', default='Disabled') == 'Active'
        assert harness.config.get_int('DummyPlugin_intval') == 42
        assert harness.config.get_str('DummyPlugin_strval') == "Hello, World!"

    def test_load_state(self, harness:TestHarness) -> None:
        """Test that state files are loaded correctly."""

        assert harness.monitor.state['Credits'] == 1000000
        state_data = harness.load_state('state.json')
        assert state_data is not None
        assert harness.monitor.state['Credits'] == 111111
        assert harness.monitor.state['GameBuild'] == "r324607/r0 "
        assert harness.monitor.state['Captain'] == "Testy"
        assert harness.monitor.state['Horizons'] == True
        assert harness.monitor.state['Odyssey'] == True

class TestHTTPRequests:
    def test_mock_http_requests(self, harness:TestHarness) -> None:
        """Test that mock requests work."""

        queue_response('get', MockResponse(200, url='https://testy.com/file.txt', json_data={'result': 'success'}),
                                           url='https://testy.com/file.txt')

        # This is just a smoke test to ensure the request machinery is working.
        response = requests.get('https://testy.com/file.txt')
        assert response.status_code == 200

    @pytest.mark.live_requests
    def test_live_http_requests(self, harness:TestHarness) -> None:
        """Test that live requests work."""
        if not harness.live_requests:
            pytest.skip("Live requests not enabled for this test.")

        # This is just a smoke test to ensure the request machinery is working.
        response = requests.get('https://www.python.org')
        assert response.status_code == 200

    def test_mock_capi_event(self, harness) -> None:
        """ Test a capi event is processed and saved correctly. """

        # Load a minimalist sample CAPI json and verify it doesn't fail.
        capi_data:dict = harness.get_config_data('capi_data.json')
        assert capi_data is not None
        capi_fleetcarrier(capi_data)
        assert carrier.data is not None
        assert carrier.data == capi_data

class TestJournalEvents:

    def test_null_event(self, harness) -> None:
        """ Just a music event to test the machinery of loading and playing events. """

        harness.load_events("journal_events.json")
        harness.play_sequence("null", 0.1)
        assert journal.cmdr == "Testy"
        assert journal.is_beta == False

    def test_startup_events(self, harness) -> None:
        """ Test a sequence of journal events are processed and saved correctly. """

        harness.load_events("journal_events.json")
        harness.play_sequence("startup", 0.1)

        assert journal.cmdr == "Someone"
        assert journal.is_beta == False
        assert journal.system == "Bleae Thua ED-D c12-5"

    def test_cargo_event_state(self, harness) -> None:
        """ Test cargo events. Verify the cargo count is updated in the state and the Cargo.json is saved. """

        amt:int = 1298
        assert harness.monitor.state['Cargo']['steel'] == 0
        harness.load_events("journal_events.json", count=amt, price=4179)
        harness.play_sequence("cargo", 0.1)

        assert harness.monitor.state['Cargo']['steel'] == amt

    def test_cargo_event_json(self, harness) -> None:
        """ Test cargo events. Verify the cargo count is updated in the state and the Cargo.json is saved. """

        amt:int = 1298
        harness.load_events("journal_events.json", count=amt, price=4179)
        harness.play_sequence("cargo", 0.1)

        with open(str(harness.plugin_dir / "journal_folder" / "Cargo.json"), 'r') as file:
            content = json.load(file)
        assert content.get('Inventory', [])[0].get('Name') == "steel"
        assert content.get('Inventory', [])[0].get('Count') == amt

    def incomplete_test_backpack_event(self, harness) -> None:
        """ Test backpack events. Verify the cargo count is updated in the state and the Backpack.json is saved. """

        seq:dict = harness.load_events("journal_events.json")
        harness.play_sequence("backpack", 0.1)

        assert harness.monitor.state['Backpack']['Data']['??'] == 0

        with open(str(harness.plugin_dir / "journal_folder" / "Backpack.json"), 'r') as file:
            content = file.read()
        assert content == seq['backpack'][0]

    def test_event_sequence(self, harness) -> None:
        """ Test a sequence of journal events are processed and saved correctly. """

        harness.load_events("journal_events.json")
        harness.play_sequence("jump", 0.1)

        assert journal.cmdr == "Testy"
        assert journal.is_beta == False
        assert journal.system == "Bleae Thua ED-D c12-5"
        assert journal.entry['event'] == "NavBeaconScan"

    @pytest.mark.slow
    def test_manual_only(self, harness) -> None:
        """ A demo slow test that won't be run by the unit-testing.yml. """
        assert True

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
