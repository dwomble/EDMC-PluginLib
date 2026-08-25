"""
Unit tests for updater.py's Notices: parsing "## N" headings from
NOTICES.md and tracking which one's been dismissed via config.

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

NOTICES_MD:str = ""
with open(Path(__file__).parent / "config" / 'notices.md', 'r', encoding='utf-8') as file:
    NOTICES_MD = file.read()

class TestParseNotices:

    def test_returns_highest_id_first(self) -> None:
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert [n[0] for n in notices._parse_notices(NOTICES_MD)] == [3, 2, 1]

    def test_captures_the_body_between_headings(self) -> None:
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices._parse_notices(NOTICES_MD)[0] == (3, "Fleet Carrier routes now track tritium separately from cargo.")

    def test_no_headings_yields_no_notices(self) -> None:
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices._parse_notices("# Notices\n\nNo entries yet.") == []

class TestNotices:

    def test_fetches_and_exposes_the_latest_notice(self) -> None:
        _queue(NOTICES_MD)
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        notices._check_notices()

        assert notices.notice_id == 3
        assert notices.pending_notice == "Fleet Carrier routes now track tritium separately from cargo."

    def test_pending_notice_is_none_before_any_fetch(self) -> None:
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        assert notices.pending_notice is None

    def test_dismiss_hides_it_and_survives_a_new_instance(self) -> None:
        _queue(NOTICES_MD)
        notices = Notices("dwomble", "EDMC-DummyPlugin-2")
        notices._check_notices()
        notices.dismiss_notice()
        assert notices.pending_notice is None

        again = Notices("dwomble", "EDMC-DummyPlugin-2")
        _queue(NOTICES_MD)
        again._check_notices()
        assert again.pending_notice is None # same id, already dismissed

    def test_a_newer_notice_shows_again_after_dismissal(self) -> None:
        _queue("## 1\nfirst")
        notices = Notices("dwomble", "EDMC-DummyPlugin-3")
        notices._check_notices()
        notices.dismiss_notice()
        assert notices.pending_notice is None

        _queue("## 2\nsecond")
        notices._check_notices()
        assert notices.pending_notice == "second"

    def test_uses_edmc_user_agent_plus_project_name(self) -> None:
        _queue(NOTICES_MD)
        notices = Notices("dwomble", "EDMC-DummyPlugin")
        notices._check_notices()

        call = mock_requests._mock_requests.calls[-1]
        assert call['headers']['User-Agent'] == "EDMC-TestHarness/1.0 EDMC-DummyPlugin-Updater"

@pytest.fixture
def harness() -> Generator[TestHarness, None, None]:
    """ A fresh per-test harness, matching test_th.py. """
    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness = TestHarness()

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

class TestNoticesDisplay:
    """ End to end: fetch -> parse -> render via th.RichText
    (what a consuming plugin's show_notice() would build) ->
    dismiss -> config keeps only the latest one showing. """

    def test_full_lifecycle_through_the_display_widget(self, harness:TestHarness) -> None:
        _queue(NOTICES_MD)
        notices = Notices("dwomble", "EDMC-DummyPlugin-5")
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
