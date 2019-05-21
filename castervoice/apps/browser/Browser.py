#
# __author__ = "lexxish"
#
from dragonfly import Choice, Dictation

from castervoice.lib.dfplus.additions import IntegerRefST

OPEN_NEW_WINDOW = "new window"
OPEN_NEW_INCOGNITO_WINDOW = "(new incognito window | incognito)"
NEW_TAB_N_TIMES = "new tab [<n>]"
REOPEN_TAB_N_TIMES = "reopen tab [<n>]"
CLOSE_TAB_N_TIMES = "close tab [<n>]"
CLOSE_ALL_TABS = "close all tabs"
NEXT_TAB_N_TIMES = "next tab [<n>]"
PREVIOUS_TAB_N_TIMES = "previous tab [<n>]"
OPEN_NEW_TAB_BASED_ON_CURSOR = "new tab that"
SWITCH_TO_NTH_TAB = "<nth> tab"
SWITCH_TO_LAST_TAB = "last tab"
SWITCH_TO_SECOND_TO_LAST_TAB = "second last tab"
GO_BACK_N_TIMES = "go back [<n>]"
GO_FORWARD_N_TIMES = "go forward [<n>]"
ZOOM_IN_N_TIMES = "zoom in [<n>]"
ZOOM_OUT_N_TIMES = "zoom out [<n>]"
ZOOM_RESET_DEFAULT = "zoom reset"
FORCE_HARD_REFRESH = "super refresh"
FIND_NEXT_MATCH = "[find] next match [<n>]"
FIND_PREVIOUS_MATCH = "[find] prior match [<n>]"
TOGGLE_CARET_BROWSING = "[toggle] caret browsing"
GO_TO_HOMEPAGE = "home page"
SHOW_HISTORY = "[show] history"
SELECT_ADDRESS_BAR = "address bar"
SHOW_DOWNLOADS = "[show] downloads"
ADD_BOOKMARK = "add bookmark"
BOOKMARK_ALL_TABS = "bookmark all tabs"
TOGGLE_BOOKMARK_TOOLBAR = "[toggle] bookmark bar"
SHOW_BOOKMARKS = "[show] bookmarks"
TOGGLE_FULL_SCREEN = "[toggle] full-screen"
SHOW_PAGE_SOURCE = "view [page] source"
DEBUG_RESUME = "resume"
DEBUG_STEP_OVER = "step over"
DEBUG_STEP_INTO = "step into"
DEBUG_STEP_OUT = "step out"
DUPLICATE_TAB = "duplicate tab"
DUPLICATE_WINDOW = "duplicate window"
SHOW_EXTENSIONS = "extensions"
SHOW_MENU = "(menu | three dots)"
SHOW_SETTINGS = "settings"
SHOW_TASK_MANAGER = "chrome task manager"
CLEAR_BROWSING_DATA = "clear browsing data"
SHOW_DEVELOPER_TOOLS = "developer tools"

EXTRAS = [
        Choice(
            "click_by_voice_options",
            {
                "go": "f",
                "click": "c",
                "push": "b",  # open as new tab but don't go to it
                "tab": "t",  # open as new tab and go to it
                "window": "w",
                "hover": "h",
                "link": "k",
                "copy": "s",
            }),
        Choice("nth", {
            "first": "1",
            "second": "2",
            "third": "3",
            "fourth": "4",
            "fifth": "5",
            "sixth": "6",
            "seventh": "7",
            "eighth": "8",
        }),
        Dictation("dictation"),

        IntegerRefST("n", 1, 100),
        IntegerRefST("m", 1, 10),
        IntegerRefST("numbers", 0, 1000),
    ]