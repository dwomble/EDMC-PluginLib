"""
Test suite for and EDMC plugin using pytest.

Run with: .venv/bin/python -m pytest tests/test_plugin.py -v --tb=short 2>&1 | tail -30
Run with: .venv_win\\Scripts\\python.exe -m pytest tests\\test_plugin.py -v --tb=short
"""

import pytest # type: ignore
from typing import Generator
from time import sleep
from unittest.mock import patch

# Config is already mocked by conftest.py
from harness import TestHarness

@pytest.fixture
def harness(request) -> Generator[TestHarness, None, None]:
    """ Provide a fresh test harness for each test. """
    live = request.node.get_closest_marker('live_requests') is not None

    test_harness = TestHarness(live_requests=live)

    # Now we can import our plugin modules
    from load import plugin_start3, plugin_app, journal_entry
    from my_plugin import me
    test_harness.plugin = me

    plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)

    test_harness.load_events("journal_events.json")
    test_harness.register_journal_handler(journal_entry, 'Testy', 'Sol', False)

    yield test_harness

class TestStartup:
    """Test plugin startup behavior."""

    @pytest.mark.live_requests
    def test_harness_initialization(self, harness:TestHarness) -> None:
        """Test basic harness initialization."""
        assert harness is not None
        assert harness.config.get_str('Plugin_status', default='On') == 'Yes'
