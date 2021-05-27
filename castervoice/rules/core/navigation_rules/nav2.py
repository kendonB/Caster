from dragonfly import Function, Repeat, Dictation, Choice, MappingRule, ShortIntegerRef

from castervoice.lib.actions import Key, Mouse, Text
from castervoice.lib import navigation, utilities
from castervoice.rules.core.navigation_rules import navigation_support

try:  # Try first loading from caster user directory
    from alphabet_rules import alphabet_support
except ImportError: 
    from castervoice.rules.core.alphabet_rules import alphabet_support

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.actions import AsynchronousAction
from castervoice.lib.merge.state.short import S, L, R

from castervoice.lib import contexts

def tmp_fun():
    print("Foreground window: %r, %r" % (Window.get_foreground().executable, Window.get_foreground().title))

class NavigationNon(MappingRule):

    pronunciation = "navigation companion"

    mapping = {
        "save":
            R(Key("c-s")),
        "display context":
            R(Function(tmp_fun)),
        "save as":
            R(Key("a-f/30, a")),
        "open":
            R(
                ContextAction(default=Key("c-o/150") + Key("c-l/40, tab/40:4"),
                              actions=[
                                  (contexts.LINUX_CONTEXT, Key("c-o")),
                                  (AppContext(executable=["rstudio", "texstudio", "notepad++"]),
                                   Key("c-o/150") + Key("s-tab/40:2"))
                              ])),
        "<direction> <time_in_seconds>":
            AsynchronousAction(
                [L(S(["cancel"], Key("%(direction)s"), consume=False))],
                repetitions=1000,
                blocking=False),
        "erase multi clipboard":
            R(Function(navigation.erase_multi_clipboard)),
        "find everywhere":
            R(Key("cs-f")),
        "replace":
            R(Key("c-h")),
        "hit F<function_key>":
            R(Key("f%(function_key)s")),
        "[show] context menu":
            R(Key("s-f10")),
        "lean":
            R(Function(navigation.right_down)),
        "hoist":
            R(Function(navigation.right_up)),
        "kick mid":
            R(Function(navigation.middle_click)),
        "shift right click":
            R(Key("shift:down") + Mouse("right") + Key("shift:up")),
        "curse <direction> [<direction2>] [<nnavi500>] [<dokick>]":
            R(Function(navigation.curse)),
        "scree <direction> [<nnavi500>]":
            R(Function(navigation.wheel_scroll)),
        "colic":
            R(Key("control:down") + Mouse("left") + Key("control:up")),
        "garb [<nnavi500>]":
            R(Mouse("left") + Mouse("left") + Function(
                navigation.stoosh_keep_clipboard)),
        "sure stoosh":
            R(Key("c-c")),
        "sure cut":
            R(Key("c-x")),
        "sure spark":
            R(Key("c-v")),
        "refresh":
            R(Key("c-r")),
        "maxiwin | maximise":
            R(Key("w-up")),
        "move window":
            R(Key("a-space, r, a-space, m")),
        "window (left | lease) [<n>]":
            R(Key("w-left"))*Repeat(extra="n"),
        "window (right | ross) [<n>]":
            R(Key("w-right"))*Repeat(extra="n"),
        "monitor (left | lease) [<n>]":
            R(Key("sw-left"))*Repeat(extra="n"),
        "monitor (right | ross) [<n>]":
            R(Key("sw-right"))*Repeat(extra="n"),
        "zinc <direction> <time_in_seconds>":
            R(AsynchronousAction(
                [L(S(["cancel"], Function(navigation.wheel_scroll, nnavi500=1)))],
                repetitions=1000,
                blocking=False)),            
        "(next | prior) window":
            R(Key("ca-tab, enter")),
        "switch (window | windows)":
            R(ContextAction(Key("ca-tab"), [
                (contexts.LINUX_CONTEXT, Key("alt:down, tab"))
            ])),
        "toggle smart word features":
            R(Pause("200") + Key("escape/50, escape/50, a-f/50, t/50, a/50, a-w/50, space/50, a-m/50, space/50, a-e/50, space/50, escape")),     
        "next tab [<n>]":
            R(Key("c-pgdown"))*Repeat(extra="n"),
        "prior tab [<n>]":
            R(Key("c-pgup"))*Repeat(extra="n"),
        "close tab [<n>]":
            R(Key("c-w/20"))*Repeat(extra="n"),
        "elite translation <text>":
            R(Function(alphabet_support.elite_text)),
    }

    extras = [
        Dictation("text"),
        Dictation("mim"),
        ShortIntegerRef("function_key", 1, 13),
        ShortIntegerRef("n", 1, 50),
        ShortIntegerRef("nnavi500", 1, 500),
        Choice("time_in_seconds", {
            "super slow": 5,
            "slow": 2,
            "normal": 0.6,
            "fast": 0.1,
            "superfast": 0.05
        }),
        navigation_support.get_direction_choice("direction"),
        navigation_support.get_direction_choice("direction2"),
        navigation_support.TARGET_CHOICE,
        Choice("dokick", {
            "kick": 1,
            "psychic": 2
        }),
        Choice("wm", {
            "ex": 1,
            "tie": 2
        }),
    ]
    defaults = {
        "n": 1,
        "mim": "",
        "nnavi500": 1,
        "direction2": "",
        "dokick": 0,
        "text": "",
        "wm": 2
    }


def get_rule():
    return NavigationNon, RuleDetails(name="navigation companion")
