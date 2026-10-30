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
import random
import sys
from pathlib import Path
import pytest
import tkinter as tk
from tkinter import ttk
from typing import Any, Generator

from theme import theme # type: ignore
from config import config # type: ignore
from harness import TestHarness, reset_plugin_modules

from demoplugin.utils.th import ScrollableFrame, Frame, Label, TopLevel, Button, Checkbutton, Text, RichText, RichScrolledText, Autocompleter, fit_window, Collapsible, PluginSlot

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

    def test_grid_skips_duplicate_registration(self, harness:TestHarness, monkeypatch) -> None:
        """ Repeated identical .grid() calls register only once. """
        calls:list = []
        monkeypatch.setattr(theme, 'register_alternate', lambda pair, gridopts: calls.append(gridopts))

        btn = Button(harness.parent, text="Go")
        btn.grid(row=0, column=0)
        btn.grid(row=0, column=0) # same options -- must not register again
        assert len(calls) == 1

        btn.grid(row=1, column=0) # genuinely different -- must register
        assert len(calls) == 2

    def test_grid_picks_dark_widget(self, harness:TestHarness) -> None:
        """ Dark theme grids the dark widget, light theme the light one. """
        previous:int|None = config.get_int('theme')
        try:
            config.set('theme', 1) # dark
            btn = Button(harness.parent, text="Go")
            btn.grid(row=0, column=0)
            assert btn.alt.winfo_manager() == "grid"
            assert btn.obj.winfo_manager() == ""

            config.set('theme', 0) # default/light
            btn2 = Button(harness.parent, text="Go")
            btn2.grid(row=0, column=1)
            assert btn2.obj.winfo_manager() == "grid"
            assert btn2.alt.winfo_manager() == ""
        finally:
            if previous is not None:
                config.set('theme', previous)

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

class TestFitWindow:
    def _window(self, harness:TestHarness, explicit:bool) -> tuple:
        top = tk.Toplevel(harness.root)
        frame = tk.Frame(top)
        frame.grid()
        rows = [tk.Label(frame, text=f"row {i}", width=20) for i in range(8)]
        for i, row in enumerate(rows): row.grid(row=i)
        top.update()
        if explicit: top.geometry(f"{top.winfo_width()}x{top.winfo_height()}")
        top.update()
        return top, frame, rows

    def test_hide(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, True)
        width:int = top.winfo_width()
        for row in rows[2:]: row.grid_remove()
        fit_window(frame)
        top.update()
        assert top.winfo_height() == top.winfo_reqheight()
        assert top.winfo_width() == width
        top.destroy()

    def test_show(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, True)
        full:int = top.winfo_height()
        for row in rows[2:]: row.grid_remove()
        fit_window(frame)
        top.update()
        assert top.winfo_height() < full
        for row in rows[2:]: row.grid()
        fit_window(frame)
        top.update()
        assert top.winfo_height() == full
        top.destroy()

    def test_grows_width(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, True)
        before:int = top.winfo_width()
        tk.Label(frame, text="wide", width=60).grid(row=20)
        fit_window(frame)
        top.update()
        assert top.winfo_width() == top.winfo_reqwidth() > before
        top.destroy()

    def test_keeps_width(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, True)
        wide:int = top.winfo_width() + 200
        top.geometry(f"{wide}x{top.winfo_height()}")
        top.update()
        for row in rows[2:]: row.grid_remove()
        fit_window(frame)
        top.update()
        assert top.winfo_width() == wide
        top.destroy()

    def test_auto_size(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, False)
        for row in rows[2:]: row.grid_remove()
        fit_window(frame)
        for row in rows[2:]: row.grid()
        top.update()
        assert top.winfo_height() == top.winfo_reqheight()
        top.destroy()

    def test_unmapped_is_noop(self, harness:TestHarness) -> None:
        top, frame, rows = self._window(harness, True)
        top.withdraw()
        top.update()
        before:str = top.geometry()
        for row in rows[2:]: row.grid_remove()
        fit_window(frame)
        assert top.geometry() == before
        top.destroy()

# th sits inside the repo, so Collapsible's key comes from the repo folder that holds load.py
_VIEW_KEY:str = f"th_{Path(__file__).resolve().parents[1].name}"

class TestCollapsible:
    @pytest.fixture(autouse=True)
    def _clear_keys(self) -> None:
        data:dict = _cfg().data
        for k in [k for k in data if k.startswith(_VIEW_KEY)]: del data[k]

    def _view(self, harness:TestHarness, hidden:bool = False, movable:bool = False, parent:Any = None) -> tuple:
        calls:list = []
        if hidden: _cfg().set(f"{_VIEW_KEY}_hidden", True)
        view = Collapsible(parent or harness.parent, movable=movable, on_toggle=calls.append)
        harness.parent.grid()
        return view, calls

    def test_expanded(self, harness:TestHarness) -> None:
        view, calls = self._view(harness)
        assert view.key == _VIEW_KEY
        assert view.expanded.winfo_manager() == 'grid'
        assert view.collapsed.winfo_manager() == ''
        assert calls == []

    def test_hidden(self, harness:TestHarness) -> None:
        view, _ = self._view(harness, True)
        assert view.expanded.winfo_manager() == ''
        assert view.collapsed.winfo_manager() == 'grid'

    def test_toggle(self, harness:TestHarness) -> None:
        view, calls = self._view(harness)
        view.toggle()
        assert (view.expanded.winfo_manager(), view.collapsed.winfo_manager()) == ('', 'grid')
        view.toggle()
        assert (view.expanded.winfo_manager(), view.collapsed.winfo_manager()) == ('grid', '')
        assert calls == [True, False]

    def test_set_state(self, harness:TestHarness) -> None:
        view, calls = self._view(harness)
        view.toggle(False)
        view.toggle(True)
        assert calls == [False, True]
        assert view.hidden is True

    def test_default_hidden(self, harness:TestHarness) -> None:
        assert Collapsible(harness.parent, hidden=True).hidden is True
        _cfg().set(f"{_VIEW_KEY}_hidden", False)
        assert Collapsible(harness.parent, hidden=True).hidden is False

    def test_saves_hidden(self, harness:TestHarness) -> None:
        view, _ = self._view(harness)
        view.toggle()
        assert _cfg().get_bool(f"{_VIEW_KEY}_hidden") is True

        again = Collapsible(harness.parent)
        assert again.hidden is True
        assert again.collapsed.winfo_manager() == 'grid'

    def test_default_buttons(self, harness:TestHarness) -> None:
        view, _ = self._view(harness)
        hide, show = view.button("hide"), view.button("show")
        assert (hide.master, show.master) == (view.expanded, view.collapsed)
        assert (hide.grid_info()['row'], hide.grid_info()['column']) == (0, 99)
        assert (show.grid_info()['row'], show.grid_info()['column']) == (0, 99)
        assert hide['text'] != show['text']
        assert view._buttons["hide"][1].text == "Hide panel"
        with pytest.raises(KeyError): view.button("up")

    def test_buttons_toggle(self, harness:TestHarness) -> None:
        view, calls = self._view(harness)
        view.button("hide").obj.invoke()
        view.button("show").obj.invoke()
        assert calls == [True, False]

    def test_button_customise(self, harness:TestHarness) -> None:
        view, _ = self._view(harness)
        btn = view.button("hide", text="X", tooltip="Close", row=1, column=4)
        assert btn is view.button("hide")
        assert btn['text'] == "X"
        assert btn['width'] == 0
        assert view._buttons["hide"][1].text == "Close"
        info:dict = btn.grid_info()
        assert (info['row'], info['column'], info['sticky']) == (1, 4, 'ne')

        view.button("hide", tooltip="Shut")
        assert btn['text'] == "X"
        assert btn.grid_info()['column'] == 4

    def test_in_raises_button(self, harness:TestHarness) -> None:
        view, _ = self._view(harness)
        later:tk.Frame = tk.Frame(view.expanded)
        btn = view.button("hide", in_=later, row=0, column=0)
        assert view.expanded.winfo_children()[-2:] == [btn.obj, btn.alt]

    def test_movable(self, harness:TestHarness) -> None:
        box, _ = _edmc_box(harness, [1, 2, 3], set())
        view, _ = self._view(harness, movable=True, parent=box.nametowidget("plugin_2"))
        up, down = view.button("up"), view.button("down")
        assert (up.master, down.master) == (view.collapsed, view.collapsed)
        assert (up.grid_info()['column'], down.grid_info()['column']) == (97, 98)

        up.obj.invoke()
        assert _order(box) == [2, 1, 3]
        assert _cfg().get_int(f"{_VIEW_KEY}_slot") == 0
        down.obj.invoke()
        down.obj.invoke()
        assert _order(box) == [1, 3, 2]

    def test_toggle_before_fit(self, harness:TestHarness, monkeypatch) -> None:
        order:list = []
        monkeypatch.setattr('demoplugin.utils.th.collapsible.fit_window', lambda w: order.append('fit'))
        view = Collapsible(harness.parent, on_toggle=lambda h: order.append('toggle'))
        view.toggle()
        assert order == ['toggle', 'fit']

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])

def _cfg() -> Any:
    """ The config object PluginSlot actually reads and writes. """
    return sys.modules[PluginSlot.__module__].config

def _edmc_box(harness:TestHarness, idxs:list, th:set, keys:dict|None = None) -> tuple:
    """ Lay out plugin rows like EDMC's _config_plugins, creating PluginSlots as each plugin_app would. """
    box:tk.Frame = tk.Frame(harness.parent)
    for row, text in enumerate(("cmdr", "ship", "system"), start=1):
        tk.Label(box, text=text).grid(row=row, column=0)
    row = box.grid_size()[1]

    slots:dict = {}
    for idx in idxs:
        frame:tk.Frame = tk.Frame(box, name=f"plugin_{idx}")
        if idx in th: slots[idx] = PluginSlot(tk.Label(frame), (keys or {}).get(idx, f"slot_{idx}"))
        # EDMC grids the frame after plugin_app, which may flush idle tasks (e.g. ScrollableFrame)
        harness._pump_ui(timeout_s=0)
        tk.Frame(box, name=f"plugin_hr_{idx}").grid(row=row, columnspan=2)
        frame.grid(row=row + 1, columnspan=2)
        row += 2

    tk.Button(box, name="update_button").grid(row=row, columnspan=2)
    return box, slots

def _order(box:tk.Misc) -> list:
    """ Plugin idxs in display order, checking each separator sits directly above its frame. """
    frames:list = [w for w in box.winfo_children() if w.winfo_name().startswith("plugin_") and "hr" not in w.winfo_name()]
    frames.sort(key=lambda w: int(w.grid_info()['row']))
    for f in frames:
        sep:Any = box.nametowidget(f.winfo_name().replace("plugin_", "plugin_hr_"))
        assert int(sep.grid_info()['row']) == int(f.grid_info()['row']) - 1
    return [int(f.winfo_name()[7:]) for f in frames]

class TestPluginSlot:
    @pytest.fixture(autouse=True)
    def _clear_slots(self) -> None:
        data:dict = _cfg().data
        for k in [k for k in data if k.startswith(("slot_", "dup_"))]: del data[k]

    def test_move_swaps_rows(self, harness:TestHarness) -> None:
        box, slots = _edmc_box(harness, [1, 2, 4, 5], {4})
        _pump(harness)
        fixed:dict = {w: w.grid_info()['row'] for w in box.winfo_children() if not w.winfo_name().startswith("plugin_")}

        assert slots[4].move(-1) is True
        assert _order(box) == [1, 4, 2, 5]
        assert _cfg().get_int("slot_4") == 1
        assert {w: w.grid_info()['row'] for w in fixed} == fixed

        assert slots[4].move(2) is True
        assert _order(box) == [1, 2, 5, 4]
        assert _cfg().get_int("slot_4") == 3

    def test_neighbour_saves_slot(self, harness:TestHarness) -> None:
        box, slots = _edmc_box(harness, [1, 2, 3], {1, 2})
        _pump(harness)

        slots[1].move(1)
        _pump(harness)
        assert _order(box) == [2, 1, 3]
        assert (_cfg().get_int("slot_1"), _cfg().get_int("slot_2")) == (1, 0)

    def test_boundaries(self, harness:TestHarness) -> None:
        box, slots = _edmc_box(harness, [1, 2, 3], {1, 3})
        _pump(harness)

        assert slots[1].move(-1) is False
        assert slots[3].move(1) is False
        assert _order(box) == [1, 2, 3]
        assert _cfg().get_int("slot_1") is None

        assert slots[1].move(5) is True
        assert _order(box) == [2, 3, 1]

    def test_outside_edmc_inert(self, harness:TestHarness) -> None:
        slot = PluginSlot(tk.Label(harness.parent), "slot_x")
        _pump(harness)
        assert slot.move(1) is False
        assert _cfg().get_int("slot_x") is None

    @pytest.mark.parametrize("th", [{1, 2, 3, 4}, {1, 2, 3, 4, 5, 6}, {2, 5}, {1, 3, 6}, {2, 3, 4}])
    @pytest.mark.parametrize("seed", range(6))
    def test_restore_round_trip(self, harness:TestHarness, th:set, seed:int) -> None:
        idxs:list = [1, 2, 3, 4, 5, 6]
        box, slots = _edmc_box(harness, idxs, th)
        _pump(harness)

        rnd = random.Random(seed)
        for _ in range(12):
            slots[rnd.choice(sorted(th))].move(rnd.choice([-2, -1, 1, 2]))
            _pump(harness)
        saved:list = _order(box)
        stored:dict = {i: _cfg().get_int(f"slot_{i}") for i in th}
        box.destroy()

        box, _ = _edmc_box(harness, idxs, th)
        _pump(harness)
        assert _order(box) == saved
        assert {i: _cfg().get_int(f"slot_{i}") for i in th} == stored

    def test_restore_shift_failure(self, harness:TestHarness) -> None:
        """ An arrangement that restoring by shifting in load order rebuilds wrongly. """
        for slot, idx in enumerate([4, 3, 1, 2]): _cfg().set(f"slot_{idx}", slot)
        box, _ = _edmc_box(harness, [1, 2, 3, 4], {1, 2, 3, 4})
        _pump(harness)
        assert _order(box) == [4, 3, 1, 2]

    def test_restore_edge_cases(self, harness:TestHarness) -> None:
        _cfg().set("slot_1", 9)
        _cfg().set("dup_a", 0)
        _cfg().set("dup_b", 0)
        box, _ = _edmc_box(harness, [1, 2, 3], {1})
        other, _ = _edmc_box(harness, [1, 2, 3], {1, 2}, {1: "dup_a", 2: "dup_b"})
        _pump(harness)

        assert _order(box) == [2, 3, 1]
        assert sorted(_order(other)) == [1, 2, 3]
