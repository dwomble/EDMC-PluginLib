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
from tkinter import ttk
from typing import Generator

from theme import theme # type: ignore
from harness import TestHarness, reset_plugin_modules

from demoplugin.utils.th import ScrollableFrame, Frame, Label, TopLevel, Button, Checkbutton, Text, RichText, RichScrolledText, Autocompleter

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

    def test_no_scrollbar(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=200)
        _add_line(harness, sf)
        _add_line(harness, sf)
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_scrollbar_appears(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True
        sf.destroy()

    def test_scrollbar_hides(self, harness:TestHarness) -> None:
        # A single line is ~22px (per test_scrollbar_appears: 10 lines ~220px),
        # so maxheight must be generous enough to fit exactly one -- 20 legitimately
        # still needs a scrollbar for even one line.
        sf = ScrollableFrame(harness.parent, maxheight=100)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is True

        sf.clear()
        _add_line(harness, sf, "one line")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_clear_removes_all(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(5):
            _add_line(harness, sf, f"line {i}")
        assert len(sf.interior.winfo_children()) == 5

        sf.clear()
        _pump(harness)
        assert len(sf.interior.winfo_children()) == 0
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_no_maxheight(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent)
        for i in range(20):
            _add_line(harness, sf, f"line {i}")
        assert sf._scrollbar_visible is False
        sf.destroy()

    def test_mousewheel(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=20)
        for i in range(10):
            _add_line(harness, sf, f"line {i}")

        sf._bind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") != ""

        sf._unbind_mousewheel()
        assert sf._canvas.bind_all("<MouseWheel>") == ""
        sf.destroy()

    def test_maxheight_readable(self, harness:TestHarness) -> None:
        sf = ScrollableFrame(harness.parent, maxheight=42)
        assert sf.cget('maxheight') == 42
        assert sf['maxheight'] == 42
        sf.destroy()

    def test_maxheight_setable(self, harness:TestHarness) -> None:
        """ `maxheight` behaves like any other Tk option (e.g. borderwidth) """
        sf = ScrollableFrame(harness.parent, maxheight=200)
        _add_line(harness, sf)
        _add_line(harness, sf)
        assert sf._scrollbar_visible is False

        sf.configure(maxheight=20)
        _pump(harness)
        assert sf.cget('maxheight') == 20
        assert sf._scrollbar_visible is True

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

    def test_text_defaults_match_label(self, harness:TestHarness) -> None:
        # Regression: real theme.register() sees Text's own native
        # colors as pre-customized against tk.Label's defaults --
        # it must start out matching Label's to stay theme-managed.
        txt = Text(harness.parent)
        lbl = tk.Label(harness.parent)
        assert txt["foreground"] == lbl["foreground"]
        assert txt["background"] == lbl["background"]
        assert txt["font"] == lbl["font"]
        assert txt["insertbackground"] == lbl["foreground"]

    def test_text_respects_explicit_colors(self, harness:TestHarness) -> None:
        txt = Text(harness.parent, foreground="red", background="blue")
        assert txt["foreground"] == "red"
        assert txt["background"] == "blue"

    def test_richtext_defaults_match_label(self, harness:TestHarness) -> None:
        rt = RichText(harness.parent)
        lbl = tk.Label(harness.parent)
        assert rt["foreground"] == lbl["foreground"]
        assert rt["background"] == lbl["background"]
        # The internal wrapping frame must match too, or it shows as
        # an unthemed border around the text.
        assert str(rt.frame["background"]) == str(lbl["background"])

    def test_richtext_renders_markdown(self, harness:TestHarness) -> None:
        rt = RichText(harness.parent, markdown="**bold** text")
        assert "bold" in rt.get("1.0", tk.END)

    def test_richscrolledtext_defaults_match_label(self, harness:TestHarness) -> None:
        rst = RichScrolledText(harness.parent)
        lbl = tk.Label(harness.parent)
        assert rst["foreground"] == lbl["foreground"]
        assert rst["background"] == lbl["background"]
        assert str(rst.frame["background"]) == str(lbl["background"])

class TestThemedPairWidgets:
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

class TestAutocompleterPopup:
    @pytest.mark.manual_only
    def test_popup_ontop(self, harness:TestHarness, monkeypatch) -> None:
        root:tk.Misc = harness.parent.winfo_toplevel()
        ac = Autocompleter(harness.parent, "placeholder", func=lambda s: ["Sol"])
        # Real focus assignment is unreliable headless -- show_list()'s
        # own guard only cares that focus_get() reports this widget.
        monkeypatch.setattr(ac.parent, 'focus_get', lambda: ac)
        # MockTheme never populates .current -- real EDMC's theme.apply() does.
        monkeypatch.setattr(theme, 'current', {
            'background': 'grey', 'foreground': 'white',
            'activebackground': 'grey', 'activeforeground': 'white',
        }, raising=False)
        root.attributes('-topmost', True)
        try:
            ac.show_list(1, 10)
            assert bool(ac.popup.attributes('-topmost')) is True
        finally:
            root.attributes('-topmost', False)
            ac.destroy()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
