# All credit goes to caspark
# This is adapted from caspark's grammar at https://gist.github.com/caspark/9c2c5e2853a14b6e28e9aa4f121164a6

from __future__ import print_function

import re
import time

import six
from dragonfly import DictList, Window, get_current_engine, get_engine

from castervoice.lib.util import recognition_history

_history = recognition_history.get_and_register_history(1)

open_windows_dictlist = DictList("open_windows")

WORD_SPLITTER = re.compile('[^a-zA-Z0-9]+')


def get_caster_messaging_window():
    if get_current_engine().name == 'natlink':
        from natlinkcore import natlinkstatus  # pylint: disable=import-error
        status = natlinkstatus.NatlinkStatus()
        if status.NatlinkIsEnabled() == 1:
            return "Messages from Natlink"
    return "Caster: Status Window"


def lower_if_not_abbreviation(s):
    if len(s) <= 4 and s.upper() == s:
        return s
    else:
        return s.lower()


def find_window(window_matcher_func, timeout_ms=3000):
    """
    Returns a Window matching the given matcher function, or raises an error otherwise
    """
    steps = int(timeout_ms / 100)
    for i in range(steps):
        for win in Window.get_all_windows():
            if window_matcher_func(win):
                return win
        time.sleep(0.1)
    raise ValueError(
        "no matching window found within {} ms".format(timeout_ms))


def refresh_open_windows_dictlist():
    """
    Refreshes `open_windows_dictlist`
    """
    window_options = {}
    for window in (x for x in Window.get_all_windows() if
                   x.is_valid and
                   x.is_enabled and
                   x.is_visible and
                   not x.executable.startswith("C:\\Windows") and
                   x.classname != "DgnResultsBoxWindow"):
        for word in {lower_if_not_abbreviation(word)
                     for word
                     in WORD_SPLITTER.split(window.title)
                     if len(word)}:
            if word in window_options:
                window_options[word] += [window]
            else:
                window_options[word] = [window]

    open_windows_dictlist.set(window_options)


def debug_window_switching():
    """
    Prints out contents of `open_windows_dictlist`
    """
    options = open_windows_dictlist.copy()
    print("*** Windows known:\n",
          "\n".join(sorted({w.title for list_of_windows in six.itervalues(options)
                            for w in list_of_windows})))

    print("*** Single word switching options:\n", "\n".join(
        "{}: '{}'".format(
            k.ljust(20), "', '".join(window.title for window in options[k])
        ) for k in sorted(six.iterkeys(options)) if len(options[k]) == 1))
    print("*** Ambiguous switching options:\n", "\n".join(
        "{}: '{}'".format(
            k.ljust(20), "', '".join(window.title for window in options[k])
        ) for k in sorted(six.iterkeys(options)) if len(options[k]) > 1))


def switch_window(windows):
    """
    Matches keywords to window titles stored in `open_windows_dictlist`
    """
    matched_window_handles = {w.handle: w for w in windows[0]}
    for window_options in windows[1:]:
        matched_window_handles = {
            w.handle: w for w in window_options if w.handle in matched_window_handles}
    if six.PY2:
        matched_windows = matched_window_handles.values()
    else:
        matched_windows = list(matched_window_handles.values())
    if len(matched_windows) == 1:
        window = matched_windows[0]
        print("Window Management: Switching to", window.title)
        window.set_foreground()
    else:
        try:
            messaging_title = get_caster_messaging_window()
            messaging_window = find_window(
                lambda w: messaging_title in w.title, timeout_ms=100)
            if messaging_window.is_minimized:
                messaging_window.restore()
            else:
                messaging_window.set_foreground()
        except ValueError:
            pass
        if len(matched_windows) >= 2:
            print("Ambiguous window switch command:\n", "\n".join(
                "'{}' from {} (handle: {})".format(w.title, w.executable, w.handle)
                for w in matched_windows))
        else:
            spec_n_word = 2
            words = list(map(str, _history[0]))
            del words[:spec_n_word]
            print("Window Management: No matching window title containing keywords: `{}`".
                  format(' '.join(map(str, words))))


class Timer:
    """
    Dragonfly timer runs every 2 seconds updating open_windows_dictlist
    """
    timer = None

    def __init__(self):
        pass

    def set(self):
        if self.timer is None:
            self.timer = get_engine().create_timer(refresh_open_windows_dictlist, 2)
            self.timer.start()

    def stop(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer = None


_previous_timerinstance = globals().get("timerinstance")
if _previous_timerinstance is not None:
    _previous_timer = getattr(_previous_timerinstance, "timer", None)
    if _previous_timer is not None:
        _previous_timer.stop()
timerinstance = Timer()
