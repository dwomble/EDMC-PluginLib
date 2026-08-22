"""
Unit tests for updater.py's Notices: parsing "## N" headings from
NOTICES.md and tracking which one's been dismissed via config.

Run with:
    .venv/bin/python -m pytest tests/test_notices.py -v --tb=short
"""
import pytest
from typing import Generator

import tests.edmc.requests as mock_requests
from demoplugin.utils.updater import Notices, parse_notices

@pytest.fixture(autouse=True)
def clear_mock_calls() -> Generator[None, None, None]:
    mock_requests._mock_requests.calls.clear()
    yield
    mock_requests._mock_requests.calls.clear()

def _queue(text:str) -> None:
    mock_requests.queue_response("get", mock_requests.MockResponse(status_code=200, content=text))

NOTICES_MD = """# Notices

## 3
Fleet Carrier routes now track tritium separately from cargo.

## 2
An older notice.

## 1
The oldest notice.
"""

class TestParseNotices:

    def test_returns_highest_id_first(self) -> None:
        notices = parse_notices(NOTICES_MD)
        assert [n[0] for n in notices] == [3, 2, 1]

    def test_captures_the_body_between_headings(self) -> None:
        notices = parse_notices(NOTICES_MD)
        assert notices[0] == (3, "Fleet Carrier routes now track tritium separately from cargo.")

    def test_no_headings_yields_no_notices(self) -> None:
        assert parse_notices("# Notices\n\nNo entries yet.") == []

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

    def test_notices_url_uses_raw_githubusercontent(self) -> None:
        notices = Notices("dwomble", "EDMC-DummyPlugin", gh_branch="develop")
        assert notices._notices_url() == "https://raw.githubusercontent.com/dwomble/EDMC-DummyPlugin/develop/NOTICES.md"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
