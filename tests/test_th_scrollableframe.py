"""
Unit tests for utils.th.ScrollableFrame.

Run with:
    .venv/bin/python -m pytest tests/test_th_scrollableframe.py -v --tb=short

Note: the harness fixture here is module-scoped (one shared Tk root for the whole file, one
ScrollableFrame per test function within it) rather than the usual per-test TestHarness
reset+recreate. Repeatedly creating/destroying a tk.Tk() root with Canvas+ttk.Scrollbar
widgets across many tests in the same process has been observed to hang on the second such
test under this harness/environment (ui_scale=120 on macOS Aqua) -- reproduced with a bare
Canvas+Scrollbar+Label combination with none of this module's own logic involved, so it's a
harness/platform fragility, not something to work around inside ScrollableFrame itself.
"""
import pytest
import tkinter as tk
from typing import Generator

from harness import TestHarness, reset_plugin_modules

from utils.th import ScrollableFrame

@pytest.fixture(scope="module")
def harness() -> Generator[TestHarness, None, None]:
    """ One shared bare harness for the whole file -- see module docstring for why. """
    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness = TestHarness()

    yield test_harness

    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()

def _pump(harness:TestHarness) -> None:
    """
    Let the UI settle, including draining ScrollableFrame's after_idle-deferred recompute.

    The harness's HarnessTkScheduler intercepts after()/after_idle() for deterministic testing,
    so those callbacks only run via _pump_ui() (which drains the scheduler *and* processes real
    Tk events) -- a plain root.update()/update_idletasks() never reaches them under the harness.
    """
    harness._pump_ui(timeout_s=0.25)

def _add_line(harness:TestHarness, sf:ScrollableFrame, text:str = "line") -> None:
    tk.Label(sf.interior, text=text, height=1).pack(fill="x")
    _pump(harness)

class TestScrollableFrame:

    def test_no_scrollbar_when_content_fits(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, max_height=200)
        _add_line(harness, sf)
        _add_line(harness, sf)
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_scrollbar_appears_when_content_overflows(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, max_height=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True
        sf.destroy()

    def test_scrollbar_hides_again_after_clear(self, harness:TestHarness) -> None:
        # A single line is ~22px (per test_scrollbar_appears_when_content_overflows: 10 lines
        # ~220px), so max_height must be generous enough to fit exactly one -- 20 legitimately
        # still needs a scrollbar for even one line.
        sf = ScrollableFrame(harness.parent, max_height=100)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True

        sf.clear()
        _add_line(harness, sf, "one line")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_clear_removes_all_children(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, max_height=20)
        for i in range(5):
            _add_line(harness, sf, f"line {i}")
        assert len(sf.interior.winfo_children()) == 5

        sf.clear()
        _pump(harness)
        assert len(sf.interior.winfo_children()) == 0
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_no_max_height_never_scrolls(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent)
        for i in range(20):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_mousewheel_binds_only_while_hovered(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, max_height=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")

        sf._bind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") != ""

        sf._unbind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") == ""
        sf.destroy()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
