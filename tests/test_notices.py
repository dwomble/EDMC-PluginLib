"""
Unit tests for Notices

Run with:
    .venv/bin/python -m pytest tests/test_notices.py -v --tb=short
"""
import pytest
import tkinter as tk
from pathlib import Path
from typing import Generator

from harness import TestHarness, reset_plugin_modules
import tests.edmc.requests as mock_requests
from demoplugin.utils.updater import Notices
from demoplugin.utils.th import RichText

@pytest.fixture(autouse=True)
def clear_mock_calls() -> Generator[None, None, None]:
    """ Also forces mock mode -- _use_live is a global a prior harness test may have left True, and it never
    resets on its own. """
    previous:bool = mock_requests.live_requests()
    mock_requests.live_requests(False)
    yield
    mock_requests.live_requests(previous)

def _queue(text:str) -> None:
    mock_requests.queue_response("get", mock_requests.MockResponse(status_code=200, content=text))

@pytest.fixture
def harness() -> Generator[TestHarness, None, None]:
    """ A fresh per-test harness, matching test_th.py. """
    TestHarness.reset_instance()
    reset_plugin_modules()
    harness:TestHarness = TestHarness()

    yield harness

    harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

NOTICES_MD:str = ""
with open(Path(__file__).parent / "config" / 'notices.md', 'r', encoding='utf-8') as file:
    NOTICES_MD = file.read()

class TestParseNotices:

    def test_returns_highest_id(self) -> None:
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert [n[0] for n in notices._parse_notices(NOTICES_MD)] == [3, 2, 1]

    def test_captures_body(self) -> None:
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices._parse_notices(NOTICES_MD)[0] == (3, "Fleet Carrier routes now track tritium separately from cargo.")

    def test_no_notices(self) -> None:
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices._parse_notices("# Notices\n\nNo entries yet.") == []

class TestNotices:

    def test_fetches_latest(self) -> None:
        _queue(NOTICES_MD)
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices.pending_notice is None

        notices._check_notices()

        assert notices.notice_id == 3
        assert notices.pending_notice == "Fleet Carrier routes now track tritium separately from cargo."

    def test_dismiss(self) -> None:
        _queue(NOTICES_MD)
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin-2")
        notices._check_notices()
        notices.dismiss_notice()
        assert notices.pending_notice is None

        again = Notices("dwomble", "EDMC-DummyPlugin-2")
        _queue(NOTICES_MD)
        again._check_notices()
        assert again.pending_notice is None # same id, already dismissed

    def test_newer_shows_again(self) -> None:
        _queue("## 1\nfirst")
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin-3")
        notices._check_notices()
        notices.dismiss_notice()
        assert notices.pending_notice is None

        _queue("## 2\nsecond")
        notices._check_notices()
        assert notices.pending_notice == "second"

class TestNoticesDisplay:
    """ End to end: fetch -> parse -> render. """

    def test_full_lifecycle(self, harness:TestHarness) -> None:
        _queue(NOTICES_MD)
        notices:Notices = Notices("dwomble", "EDMC-DummyPlugin-5")
        notices._check_notices()
        assert notices.pending_notice is not None

        widget:RichText = RichText(harness.parent, markdown=notices.pending_notice)
        assert "Fleet Carrier" in widget.get("1.0", tk.END)

        notices.dismiss_notice()
        assert notices.pending_notice is None

        # A newer notice still shows despite the dismissal.
        _queue("## 4\nA newer notice.")
        notices._check_notices()
        assert notices.pending_notice == "A newer notice."

        again:RichText = RichText(harness.parent, markdown=notices.pending_notice)
        assert "A newer notice" in again.get("1.0", tk.END)

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
