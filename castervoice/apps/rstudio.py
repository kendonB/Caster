from dragonfly import Key, Pause, Function, Choice, MappingRule, Repeat, BringApp

from castervoice.lib import navigation
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.additions import IntegerRefST
from castervoice.lib.merge.state.short import R
from castervoice.lib.temporary import Store, Retrieve


class RStudioRule(MappingRule):
    mapping = {
    "new (file | tab)":
        R(Key("cs-n"), rdescript="RStudio: New File"),
    "open file":
        R(Key("c-o")),
    "open recent project":
        R(Key("a-f, j")),
  	"open project":
        R(Key("a-f, n, enter")),
    "save all":
        R(Key("ac-s")),
    "select all":
        R(Key("c-a")),
    "find":
        R(Key("c-f"), rdescript="RStudio: Find"),
    "add comment":
        R(Key("cs-c"), rdescript="RStudio: Comment"),
    "terminate R":
        R(Key("a-s, t"), rdescript="RStudio: Comment"),
	"[file] save as":
	    R(Key("a-f, a"), rdescript="RStudio: Save as"),

    "[go to] line <nrstudio500>":
        R(Key("as-g") + Pause("10") + Text("%(nrstudio500)s") + Key("enter"),
          rdescript="RStudio: Go to Line #"),
    "look soul":
        R(Key("c-2")),
    "look ed":
        R(Key("c-1"), rdescript="RStudio: Focus Main"),
    "look terminal":
        R(Key("as-t"), rdescript="RStudio: Focus Terminal"),
    "look help":
        R(Key("c-3"), rdescript="RStudio: Focus Help"),

    "(zoom | unzoom) console":
        R(Key("cs-2"), rdescript="RStudio: Zoom Console"),
    "(zoom | unzoom)  main":
        R(Key("cs-1"), rdescript="RStudio: Zoom Main"),
    "(zoom | unzoom)  help":
        R(Key("cs-3"), rdescript="RStudio: Zoom Help"),

	"new terminal":
        R(Key("as-r"), rdescript="RStudio: New Terminal"),
	"next terminal":
        R(Key("cas-pagedown"), rdescript="RStudio: Next Terminal"),
	"prior terminal":
        R(Key("cas-pageup"), rdescript="RStudio: Prior Terminal"),
    "close terminal":
        R(Key("cas-backspace"), rdescript="RStudio: Close Terminal"),

    "next tab [<nrstudio50>]":
        R(Key("c-pagedown"), rdescript="RStudio: Next Tab")*Repeat(extra="nrstudio50"),
    "first tab [<nrstudio50>]":
        R(Key("cs-f11"), rdescript="RStudio: First Tab"),
    "(previous | prior) tab [<nrstudio50>]":
        R(Key("c-pageup"), rdescript="RStudio: Previous Tab")*Repeat(extra="nrstudio50"),
    "last tab":
        R(Key("cs-f12")),
    "close tab":
        R(Key("c-w")),


    "run line":
        R(Key("c-enter")),
    "run document":
        R(Key("ac-r")),
    "comment (line | selected)":
        R(Key("cs-c")),

    "next plot":
        R(Key("ac-f12")),
    "previous plot":
        R(Key("ac-f11")),

    "open":
        R(Key("c-o"), rdescript="RStudio: Open"),
	"build package":
        R(Key("cs-b"), rdescript="RStudio: Build package"),

	"next [<nrstudio500>]":
        Key("c-2") + R(Text("n") + Key("enter"), rdescript="R: Next while debugging")*Repeat(extra="nrstudio500"),

	"step in":
	    Key("c-2") + R(Text("s") + Key("enter"), rdescript="R: Step in while debugging"),
	"continue":
	    Key("c-2") + R(Text("c") + Key("enter"), rdescript="R: Continue while debugging"),
	"stop":
	    Key("c-2") + R(Text("Q") + Key("enter"), rdescript="R: Stop debugging"),
        
    "<action> [line] <ln1> [by <ln2>]"  :
        R(Function(navigation.action_lines, go_to_line="as-g/10", select_line_down="s-down", wait="/3", upon_arrival="home, ")),

    "connect nesi":
        R(Text("nes") + 
            Key("enter") + 
            Pause("50") +
            BringApp("chrome.exe") + Pause("50") + 
            Key("escape/10, as-t/10, left:3/10, enter/50") + Text("nesi") + 
            Pause("50") + Key("down/10, right:2/10, enter/10, down:2/10, enter/10") + Key("a-tab") + 
            Pause("50") +
            Key("s-insert/25, enter") + BringApp("Authy Desktop.exe")),
    }
    extras = [
        IntegerRefST("n", 1, 10000),
		IntegerRefST("nrstudio500", 1, 500),
		IntegerRefST("nrstudio50", 1, 50),
        IntegerRefST("ln1", 1, 10000),
        IntegerRefST("ln2", 1, 10000),
        Choice("action", navigation.actions),
    ]
    defaults = {
	    "n" : 1,
		"nrstudio500": 1,
		"nrstudio50": 1,
        "ln2": ""
	}




def get_rule():
    details = RuleDetails(name="are studio", executable="rstudio")
    return RStudioRule, details
