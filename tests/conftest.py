# Sections marked PLUGIN need editing to reuse this file for another plugin; the rest is generic.
import threading
import time
from time import monotonic, sleep as real_sleep
from typing import Generator

import pytest
from harness import TestHarness, reset_plugin_modules

JOIN_S:float = 2

# GENERIC: set at teardown to end every worker thread sleeping via _sleep
stop:threading.Event = threading.Event()

# GENERIC: must run in a fixture, as the pool workers are joined before atexit handlers run
@pytest.fixture(scope="session", autouse=True)
def _stop_lookups() -> Generator[None, None, None]:
    """Cancel queued autocompleter lookups at session end so they can't hold up interpreter exit."""
    yield
    TestHarness.stop_lookups()

# GENERIC: keep as is; test files override it
@pytest.fixture
def pre_start():
    """Per-file setup run before the plugin starts; override to return a function taking (request, harness)."""
    return lambda request, harness: None


# PLUGIN: wires TestHarness to your plugin; edit the marked steps, keep the harness, yield and teardown
@pytest.fixture
def harness(request, pre_start) -> Generator:
    """Fresh harness with the plugin started and journal events loaded."""
    live:bool = request.node.get_closest_marker('live_requests') is not None
    mark = request.node.get_closest_marker('overlay')
    overlay:bool|str = mark.args[0] if mark else 'All'

    TestHarness.reset_instance()
    reset_plugin_modules()
    test_harness:TestHarness = TestHarness(live_requests=live, overlay=overlay)

    pre_start(request, test_harness)

    # PLUGIN: import and start your plugin through its load.py entry points
    from load import plugin_start3, plugin_app, journal_entry, dashboard_entry, plugin
    plugin_start3(str(test_harness.plugin_dir))
    plugin_app(test_harness.parent)
    test_harness.plugin = plugin

    # PLUGIN: your journal events file, and the commander and system to simulate
    test_harness.load_events("journal_events.json")
    test_harness.register_journal_handler(journal_entry, 'Testy', 'Sol', False)
    test_harness.register_dashboard_handler(dashboard_entry)

    yield test_harness
    test_harness.assert_no_unhandled_exceptions()
    TestHarness.reset_instance()
    reset_plugin_modules()

def _sleep(secs:float) -> None:
    """Sleep, but end a worker thread as soon as stop is set."""
    if threading.current_thread() is threading.main_thread(): return real_sleep(secs)
    if stop.wait(secs): raise SystemExit

# Installed once at import so any later "from time import sleep" binds this; per-test patching would miss them
time.sleep = _sleep

@pytest.fixture(autouse=True)
def stop_workers():
    """Stop and join the workers started during each test."""
    stop.clear()
    before:set = set(threading.enumerate())

    yield

    stop.set()
    # PLUGIN: wake any worker blocked on a queue (e.g. queue.put(None)) so it sees stop; the demo plugin has none

    deadline:float = monotonic() + JOIN_S
    # PLUGIN: your worker threads' name prefix
    for t in set(threading.enumerate()) - before:
        if t.name.startswith('EDMC-DemoPlugin'): t.join(max(0, deadline - monotonic()))
