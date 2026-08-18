"""
Unit test for load.py's VERSION handling: resolved from a "version" file (the
same file CI's release.yml stamps and Updater.install() writes) rather than a
hardcoded string, exposed as load.VERSION for plugin-browser tooling.

Run with:
    .venv/bin/python -m pytest tests/test_load.py -v --tb=short
"""
import pytest

from harness import TestHarness, reset_plugin_modules

@pytest.fixture
def harness() -> None:
    TestHarness.reset_instance()
    reset_plugin_modules()

def test_plugin_start3_resolves_version_from_the_version_file(harness, tmp_path) -> None:
    (tmp_path / "version").write_text("9.9.9")

    from load import plugin_start3, VERSION as initial_version
    assert initial_version == "0.0.0" # placeholder, before plugin_start3() runs

    plugin_start3(str(tmp_path))

    import load
    assert load.VERSION == "9.9.9"

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
