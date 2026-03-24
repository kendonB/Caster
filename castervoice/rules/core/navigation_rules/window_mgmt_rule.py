from dragonfly import DictListRef, Function, MappingRule, Repeat, Repetition, ShortIntegerRef

from castervoice.lib import utilities
from castervoice.lib import virtual_desktops
from castervoice.lib.actions import Key
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.short import R

try:  # Try first loading from caster user directory
    from navigation_rules.window_mgmt_rule_support import (  # pylint: disable=import-error
        debug_window_switching, open_windows_dictlist, switch_window, timerinstance,
    )
except ImportError:
    from castervoice.rules.core.navigation_rules.window_mgmt_rule_support import (
        debug_window_switching,
        open_windows_dictlist,
        switch_window,
        timerinstance,
    )


class WindowManagementRule(MappingRule):
    mapping = {
        'window maximize':
            R(Function(utilities.maximize_window)),
        'window minimize':
            R(Function(utilities.minimize_window)),
        'window restore':
            R(Function(utilities.restore_window)),
        'window close':
            R(Function(utilities.close_window)),
        "window switch <windows>":
            R(Function(switch_window), rdescript=""),
        "window switch show":
            R(Function(debug_window_switching)),

        # Workspace management
        "show work [spaces]":
            R(Key("w-tab")),
        "(create | new) work [space]":
            R(Key("wc-d")),
        "close work [space]":
            R(Key("wc-f4")),
        "close all work [spaces]":
            R(Function(virtual_desktops.close_all_workspaces)),
        "next work [space] [<n>]":
            R(Key("wc-right"))*Repeat(extra="n"),
        "(previous | prior) work [space] [<n>]":
            R(Key("wc-left"))*Repeat(extra="n"),

        "go work [space] <n>":
            R(Function(virtual_desktops.go_to_desktop_number)),
        "send work [space] <n>":
            R(Function(virtual_desktops.move_current_window_to_desktop)),
        "move work [space] <n>":
            R(Function(virtual_desktops.move_current_window_to_desktop, follow=True)),
    }

    extras = [
        ShortIntegerRef("n", 1, 20, default=1),
        Repetition(name="windows", min=1, max=5,
                   child=DictListRef("window_by_keyword", open_windows_dictlist)),
    ]


timerinstance.set()


def get_rule():
    details = RuleDetails(name="window management rule")
    return WindowManagementRule, details
