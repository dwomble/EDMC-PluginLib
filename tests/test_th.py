"""
Unit tests for utils.th

Run with:
    .venv/bin/python -m pytest tests/test_th_scrollableframe.py -v --tb=short

A tk.Canvas widget (this module builds one per ScrollableFrame) hangs on .update() if it's
created in any tk.Tk() root other than the FIRST one the process ever made -- an observed
platform/Tk quirk (macOS Aqua + ui_scale=120), reproduced with a bare Canvas+Scrollbar+Label,
no ScrollableFrame logic involved. TestHarness works around this at the source (see
harness.py's `_shared_root`): one root is kept alive for the whole test process regardless of
how many times reset_instance() runs, so a normal per-test reset+recreate here is safe.
"""
import pytest
import tkinter as tk
from typing import Generator

from harness import TestHarness, reset_plugin_modules

from demoplugin.utils.th import ScrollableFrame, Frame, Label, TopLevel, Button, Checkbutton

@pytest.fixture
def harness() -> Generator[TestHarness, None, None]:
    """ A fresh per-test harness, same pattern as the other test files. """
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

class Testth:

    def test_no_scrollbar_when_content_fits(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=200)
        _add_line(harness, sf)
        _add_line(harness, sf)
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_scrollbar_appears_when_content_overflows(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True
        sf.destroy()

    def test_scrollbar_hides_again_after_clear(self, harness:TestHarness) -> None:
        # A single line is ~22px (per test_scrollbar_appears_when_content_overflows: 10 lines
        # ~220px), so maxheight must be generous enough to fit exactly one -- 20 legitimately
        # still needs a scrollbar for even one line.
        sf = ScrollableFrame(harness.parent, maxheight=100)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True

        sf.clear()
        _add_line(harness, sf, "one line")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_clear_removes_all_children(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(5):
            _add_line(harness, sf, f"line {i}")
        assert len(sf.interior.winfo_children()) == 5

        sf.clear()
        _pump(harness)
        assert len(sf.interior.winfo_children()) == 0
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_no_maxheight_never_scrolls(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent)
        for i in range(20):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_mousewheel_binds_only_while_hovered(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")

        sf._bind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") != ""

        sf._unbind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") == ""
        sf.destroy()

    def test_maxheight_readable_via_cget_and_getitem(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=42)
        assert sf.cget('maxheight') == 42
        assert sf['maxheight'] == 42
        sf.destroy()

    def test_maxheight_settable_via_configure(self, harness:TestHarness) -> None:
        """ `maxheight` behaves like any other Tk option (e.g. borderwidth) -- settable via
        configure()/config() at any time, not just at construction, and recomputes immediately. """
        sf = ScrollableFrame(harness.parent, maxheight=200)
        _add_line(harness, sf)
        _add_line(harness, sf)
        assert sf._scrollbar_visible is False

        sf.configure(maxheight=20)
        _pump(harness)
        assert sf.cget('maxheight') == 20
        assert sf._scrollbar_visible is True
        sf.destroy()

    def test_maxheight_settable_via_getitem_and_mixed_configure(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=200)

        sf['maxheight'] = 36
        assert sf.cget('maxheight') == 36

        # A real Tk option alongside maxheight in the same call -- both must apply.
        sf.config(borderwidth=2, maxheight=54)
        assert sf.cget('maxheight') == 54
        assert sf.cget('borderwidth') == 2
        sf.destroy()

class TestPlainWidgets:
    """ Frame/Label/TopLevel are real single widgets, not light/dark pairs. """

    def test_frame(self, harness:TestHarness) -> None:
        f = Frame(harness.parent)
        assert isinstance(f, tk.Frame)

    def test_label(self, harness:TestHarness) -> None:
        lbl = Label(harness.parent, text="hi")
        assert lbl["text"] == "hi"

    def test_toplevel(self, harness:TestHarness) -> None:
        # Regression: TopLevel used to call theme.update(self), which raises since
        # tk.Toplevel isn't a tk.Widget subclass.
        top = TopLevel(harness.parent)
        assert isinstance(top, tk.Toplevel)
        top.destroy()

class TestThemedPairWidgets:
    """ Button/Checkbutton are light/dark pairs -- only one half should ever be gridded. """

    def test_button_grid(self, harness:TestHarness) -> None:
        btn = Button(harness.parent, text="Go")
        btn.grid()
        managers = {btn.obj.winfo_manager(), btn.alt.winfo_manager()}
        assert managers == {"grid", ""}

    def test_checkbutton(self, harness:TestHarness) -> None:
        var = tk.BooleanVar(value=False)
        cb = Checkbutton(harness.parent, variable=var)

        # Variable should be shared between the two halves of the pair, so that checking one checks the other.
        assert str(cb.obj["variable"]) == str(var) == str(cb.alt["variable"])

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
