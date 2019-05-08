#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#
"""
Command-module for TexStudio++

"""
#---------------------------------------------------------------------------

from dragonfly import (Grammar, Dictation, Repeat, Pause)

from castervoice.lib import control
from castervoice.lib import settings
from castervoice.lib.actions import Key, Mouse, Text
from castervoice.lib.context import AppContext
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge import gfilter
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R
from castervoice.lib.ccr.standard import SymbolSpecs

class NPPRule(MergeRule):
    pronunciation = "notepad plus plus"

    mapping = {
        "open":
            R(Key("c-o"), rdescript="TexStudio++: Open"),
        "[go to] line <n>":
            R(Key("c-g/10") + Text("%(n)s") + Key("enter"),
              rdescript="TexStudio++: Go to Line #"),
        "tex studio press F three <n50>":
             Key("f3")*Repeat(extra="n50"),
        "[go to] section <n50>":
            Key("c-g/10") + Text("1") + Key("enter/10") + Key("c-f") + Text("^$\\\\begin\\{document|^$\\\\section") + Key("left")*Repeat(count=29) + Key("backspace") + Key("right")*Repeat(count=20) + Key("backspace, f3") + Key("f3/100")*Repeat(extra="n50") + Key("s-f3/100") + Key("escape/100"),
    }
    extras = [
        Dictation("text"),
        IntegerRefST("n", 1, 10000),
        IntegerRefST("n50", 1, 50),
    ]
    defaults = {"n": 1}


#---------------------------------------------------------------------------

context = AppContext(executable="texstudio")
grammar = Grammar("TexStudio", context=context)

if settings.SETTINGS["apps"]["texstudio"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(NPPRule())
    else:
        rule = NPPRule(name="tech studio")
        gfilter.run_on(rule)
        grammar.add_rule(rule)
        grammar.load()
