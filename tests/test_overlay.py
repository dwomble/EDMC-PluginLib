"""
Unit tests for utils.overlay.Overlay.

Run with:
    .venv/bin/python -m pytest tests/test_overlay.py -v --tb=short
"""
import pytest
from typing import Generator

from harness import TestHarness, reset_plugin_modules

from utils.overlay import Overlay

@pytest.fixture
def harness(request) -> Generator[TestHarness, None, None]:
    overlay = 'All'
    if request.node.get_closest_marker('overlay'):
        overlay = request.node.get_closest_marker('overlay').args[0]

    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness = TestHarness(overlay=overlay)

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

class TestOverlayDetection:

    @pytest.mark.overlay('None')
    def test_unavailable_when_no_overlay_installed(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.available is False
        assert overlay.is_modern is False

    @pytest.mark.overlay('Legacy')
    def test_legacy_overlay_detected(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.available is True
        assert overlay.is_modern is False

    @pytest.mark.overlay('Modern')
    def test_modern_overlay_detected(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.available is True
        assert overlay.is_modern is True

class TestOverlayPrimitivesNoOpSafely:

    @pytest.mark.overlay('None')
    def test_send_text_is_a_safe_noop(self, harness:TestHarness) -> None:
        overlay = Overlay()
        overlay.send_text("id", "hello", "#ffffff", 0, 0)  # must not raise

    @pytest.mark.overlay('None')
    def test_send_shape_is_a_safe_noop(self, harness:TestHarness) -> None:
        overlay = Overlay()
        overlay.send_shape("id", "rect", "#ffffff", "#000000", 0, 0, 10, 10)  # must not raise

    @pytest.mark.overlay('None')
    def test_define_group_is_false_without_modern_overlay(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.define_group(plugin_group="Test") is False

class TestOverlayPrimitivesWhenAvailable:

    @pytest.mark.overlay('Modern')
    def test_send_text_reaches_the_mock_overlay(self, harness:TestHarness) -> None:
        overlay = Overlay()
        overlay.send_text("test-id", "hello", "#ffffff", 1, 2, ttl=5, size="large")
        assert overlay._overlay.messages["test-id"][:5] == ["test-id", "hello", "#ffffff", 1, 2]

    @pytest.mark.overlay('Modern')
    def test_send_shape_reaches_the_mock_overlay(self, harness:TestHarness) -> None:
        overlay = Overlay()
        overlay.send_shape("test-shape", "rect", "#ffffff", "#000000", 1, 2, 10, 10)
        assert overlay._overlay.shapes["test-shape"][:8] == ["test-shape", "rect", "#ffffff", "#000000", 1, 2, 10, 10]

    @pytest.mark.overlay('Modern')
    def test_define_group_succeeds_with_modern_overlay(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.define_group(plugin_group="Test", id_prefixes=["test-"]) is True

    @pytest.mark.overlay('Legacy')
    def test_define_group_false_with_legacy_overlay(self, harness:TestHarness) -> None:
        overlay = Overlay()
        assert overlay.define_group(plugin_group="Test") is False

class TestOverlayFailureHandling:

    @pytest.mark.overlay('Modern')
    def test_failed_send_disables_further_output(self, harness:TestHarness, monkeypatch) -> None:
        overlay = Overlay()
        assert overlay.available is True

        def boom(*args, **kw):
            raise RuntimeError("overlay connection lost")
        monkeypatch.setattr(overlay._overlay, "send_message", boom)

        overlay.send_text("id", "hello", "#ffffff", 0, 0)  # must not raise
        assert overlay.available is False

        # Further calls stay quiet no-ops rather than re-raising.
        overlay.send_text("id", "hello again", "#ffffff", 0, 0)

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
