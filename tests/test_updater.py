"""
Unit tests for utils/updater.py's PLUGINS.md-compliant HTTP conventions
(new_session() + a User-Agent blended with EDMC's own, not a bespoke string).

Run with:
    .venv/bin/python -m pytest tests/test_updater.py -v --tb=short
"""
import os
import zipfile
import pytest
from typing import Generator

import tests.edmc.requests as mock_requests
from demoplugin.utils.updater import Updater, read_version_file

@pytest.fixture(autouse=True)
def clear_mock_calls() -> Generator[None, None, None]:
    """ Also forces mock mode -- _use_live is a global a
    prior harness test may have left True, and it never
    resets on its own. """
    previous:bool = mock_requests.live_requests()
    mock_requests.live_requests(False)
    yield
    mock_requests.live_requests(previous)

class TestUpdaterUserAgent:

    def test_get_release_sends_agent(self, tmp_path) -> None:
        updater = Updater(str(tmp_path), "dwomble", "EDMC-DummyPlugin")
        mock_requests.queue_response("get", mock_requests.MockResponse(status_code=404))

        updater.get_release()

        call = mock_requests._mock_requests.calls[-1]
        assert call['headers']['User-Agent'] == "EDMC-TestHarness/1.0 EDMC-DummyPlugin-Updater"

    def test_download_sends_agent(self, tmp_path) -> None:
        updater = Updater(str(tmp_path), "dwomble", "EDMC-DummyPlugin")
        updater.update_version = "1.2.3" # type: ignore
        updater.download_url = "https://example.invalid/release.zip"
        mock_requests.queue_response("get", mock_requests.MockResponse(status_code=404))

        updater.download_zip()

        call = mock_requests._mock_requests.calls[-1]
        assert call['headers']['User-Agent'] == "EDMC-TestHarness/1.0 EDMC-DummyPlugin-Updater"

def _make_updater_with_zip(tmp_path, zip_contents:dict[str, str]) -> Updater:
    """ Build a ready to install zip file. """
    updater = Updater(str(tmp_path), "dwomble", "EDMC-DummyPlugin")
    updater.install_update = True
    updater.update_version = "1.2.3" # type: ignore

    (tmp_path / "updates").mkdir(exist_ok=True)
    zip_file:str = str(tmp_path / "updates" / "release.zip")
    with zipfile.ZipFile(zip_file, 'w') as zf:
        for name, content in zip_contents.items():
            zf.writestr(name, content)
    updater.zip_downloaded = zip_file
    return updater

class TestUpdaterInstall:

    def test_install_backup_before_extracting(self, tmp_path) -> None:
        """ Old files must not just be overwritten in place. """
        (tmp_path / "old_module.py").write_text("stale code")
        (tmp_path / ".git").mkdir()
        (tmp_path / ".git" / "HEAD").write_text("ref: refs/heads/master")

        updater = _make_updater_with_zip(tmp_path, {"load.py": "new code", "version": "1.2.3"})
        updater.install()

        assert not (tmp_path / "old_module.py").exists()
        assert not (tmp_path / ".git").exists()
        assert (tmp_path / "updates" / "backup" / "old_module.py").read_text() == "stale code"
        assert (tmp_path / "updates" / "backup" / ".git" / "HEAD").exists()
        assert (tmp_path / "load.py").read_text() == "new code"

    def test_install_preserves_named_directories(self, tmp_path) -> None:
        """ Don't destroy data directories. """
        (tmp_path / "data").mkdir()
        (tmp_path / "data" / "state.json").write_text('{"cmdr": "test"}')

        updater = _make_updater_with_zip(tmp_path, {"load.py": "new code"})
        updater.install(["data"])

        assert (tmp_path / "data" / "state.json").read_text() == '{"cmdr": "test"}'
        assert not (tmp_path / "updates" / "backup" / "data").exists()

    def test_install_preserves_updates_dir(self, tmp_path) -> None:
        """ updates/ holds the just-downloaded zip -- moving it into its own backup subfolder
        mid-extraction would destroy the zip while install() is still reading from it. """
        updater = _make_updater_with_zip(tmp_path, {"load.py": "new code"})
        zip_name:str = os.path.basename(updater.zip_downloaded)

        updater.install()

        assert (tmp_path / "updates" / zip_name).exists()

    def test_install_clears_backup(self, tmp_path) -> None:
        """ A leftover backup/ from an earlier install() must be replaced, not merged into. """
        (tmp_path / "updates").mkdir()
        (tmp_path / "updates" / "backup").mkdir()
        (tmp_path / "updates" / "backup" / "stale.txt").write_text("from a previous update")

        updater = _make_updater_with_zip(tmp_path, {"load.py": "new code"})
        updater.install()

        assert not (tmp_path / "updates" / "backup" / "stale.txt").exists()

class TestReadVersionFile:

    def test_reads_version_file(self, tmp_path) -> None:
        (tmp_path / "version").write_text("1.2.3")
        assert str(read_version_file(str(tmp_path), "0.0.0-dev")) == "1.2.3"

    def test_version_file_fallback(self, tmp_path) -> None:
        assert str(read_version_file(str(tmp_path), "0.1.0-dev")) == "0.1.0-dev"

    def test_unparseable_fallback(self, tmp_path) -> None:
        (tmp_path / "version").write_text("not-a-version!!")
        assert str(read_version_file(str(tmp_path), "0.1.0-dev")) == "0.1.0-dev"

    def test_strips_surrounding_whitespace(self, tmp_path) -> None:
        """ CI's release.yml writes the tag via `echo`, which appends a newline. """
        (tmp_path / "version").write_text("1.2.3\n")
        assert str(read_version_file(str(tmp_path), "0.0.0-dev")) == "1.2.3"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
