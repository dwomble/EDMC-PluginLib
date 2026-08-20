"""
Unit tests for utils.overlay.Overlay.

Run with:
    .venv/bin/python -m pytest tests/test_overlay.py -v --tb=short
"""
import pytest
from typing import Generator

from harness import TestHarness, reset_plugin_modules

from demoplugin.utils.overlay import Overlay

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
    def test_send_vect_is_a_safe_noop(self, harness:TestHarness) -> None:
        overlay = Overlay()
        overlay.send_vect("id", [{"x": 0, "y": 0}, {"x": 10, "y": 10}], "#ffffff")  # must not raise

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
    def test_send_vect_reaches_the_mock_overlay(self, harness:TestHarness) -> None:
        """
        Regression: send_vect used to call send_shape(..., vector=vector, ...), but neither the
        classic edmcoverlay.Overlay nor EDMCModernOverlay's compat shim accept a `vector`
        keyword on send_shape() (confirmed against both backends' real source) -- it raised
        TypeError at runtime the first time a real vector shape was actually drawn. Vector
        payloads must go through send_raw() with "vector" as a message-dict key instead.
        """
        overlay = Overlay()
        points = [{"x": 0, "y": 0}, {"x": 10, "y": 10}, {"x": 0, "y": 0}]
        overlay.send_vect("test-vect", points, "#00ff00")
        msg, kw = overlay._overlay.shapes["test-vect"]
        assert msg["shape"] == "vect"
        assert msg["vector"] == points
        assert msg["color"] == "#00ff00"

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
    def test_single_failed_send_does_not_disable_output(self, harness:TestHarness, monkeypatch) -> None:
        """
        Regression: one send failure used to permanently disable the whole overlay for the rest
        of the session -- e.g. a one-off bad API call during setup (a define_group() mismatch)
        would blackout every subsequent draw call too, with no recovery short of restarting
        EDMC. A single failure alone shouldn't be fatal; only a run of consecutive ones should.
        """
        overlay = Overlay()
        assert overlay.available is True

        def boom(*args, **kw):
            raise RuntimeError("overlay connection lost")
        monkeypatch.setattr(overlay._overlay, "send_message", boom)

        overlay.send_text("id", "hello", "#ffffff", 0, 0)  # must not raise
        assert overlay.available is True

    @pytest.mark.overlay('Modern')
    def test_failed_send_disables_after_consecutive_failures(self, harness:TestHarness, monkeypatch) -> None:
        overlay = Overlay()

        def boom(*args, **kw):
            raise RuntimeError("overlay connection lost")
        monkeypatch.setattr(overlay._overlay, "send_message", boom)

        for _ in range(Overlay.FAILURE_THRESHOLD):
            overlay.send_text("id", "hello", "#ffffff", 0, 0)  # must not raise
        assert overlay.available is False

        # Further calls stay quiet no-ops rather than re-raising.
        overlay.send_text("id", "hello again", "#ffffff", 0, 0)

    @pytest.mark.overlay('Modern')
    def test_success_resets_the_consecutive_failure_count(self, harness:TestHarness, monkeypatch) -> None:
        overlay = Overlay()

        def boom(*args, **kw):
            raise RuntimeError("overlay connection lost")
        monkeypatch.setattr(overlay._overlay, "send_message", boom)

        for _ in range(Overlay.FAILURE_THRESHOLD - 1):
            overlay.send_text("id", "hello", "#ffffff", 0, 0)
        assert overlay.available is True # one below the threshold -- still alive

        monkeypatch.undo() # let the next call actually succeed
        overlay.send_text("id", "hello", "#ffffff", 0, 0)

        monkeypatch.setattr(overlay._overlay, "send_message", boom)
        for _ in range(Overlay.FAILURE_THRESHOLD - 1):
            overlay.send_text("id", "hello", "#ffffff", 0, 0)
        assert overlay.available is True # the earlier success reset the count -- still under threshold

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
