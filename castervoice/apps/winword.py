#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#
"""
Command-module for word

"""
#---------------------------------------------------------------------------

from dragonfly import (Grammar, MappingRule, Dictation, Pause, Choice, Function)

from castervoice.lib import control
from castervoice.lib import settings
from castervoice.lib.actions import Key, Text
from castervoice.lib.context import AppContext
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge import gfilter
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R

def symbol_letters(big, symbol):
    if big:
        symbol = symbol.title()
    Text(str(symbol)).execute()


class MSWordRule(MergeRule):
    pronunciation = "Microsoft Word"

    mapping = {
        "insert image": R(Key("alt, n, p"), rdescript="Word: Insert Image"),
        "symbol [<big>] <symbol>":
            R(Text("\\") + Function(symbol_letters, extra={"big", "symbol"}) + Text(" "),
              rdescript="Word: Insert symbols"),
        "eek":
            R(Key("a-equals"))
    }
    extras = [
            Choice(
            "symbol",
            {
                "alpha": "alpha",
                "beater": "beta",
                "gamma": "gamma",
                "delta": "delta",
                "epsilon": "epsilon",
                "var epsilon": "varepsilon",
                "zita": "zeta",
                "eater": "eta",
                "theta": "theta",
                "iota": "iota",
                "kappa": "kappa",
                "lambda": "lambda",
                "mu": "mu",
                "new": "nu",
                "zee": "xi",
                "pie": "pi",
                "row": "rho",
                "sigma": "sigma",
                "tau": "tau",
                "upsilon": "upsilon",
                "phi": "phi",
                "chi": "chi",
                "sigh": "psi",
                "omega": "omega",
                #
                "times": "times",
                "divide": "div",
                "intersection": "cap",
                "union": "cup",
                "stop": "cdot",
                "approximate": "approx",
                "proportional": "propto",
                "not equal": "neq",
                "member": "in",
                "for all": "forall",
                "partial": "partial",
                "infinity": "infty",
                "dots": "dots",
                #
                "left arrow": "leftarrow",
                "right arrow": "rightarrow",
                "up arrow": "uparrow",
                "down arrow": "downarrow",
                #
                "left": "left(",
                "right": "right)",
            }),
        Choice("big", {
            "big": True,
        }),            
        Dictation("dict"),
        IntegerRefST("n", 1, 100),
    ]
    defaults = {"n": 1, "dict": "nothing", "big": False}


#---------------------------------------------------------------------------

context = AppContext(executable="winword")
grammar = Grammar("Microsoft Word", context=context)

if settings.SETTINGS["apps"]["winword"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(MSWordRule())
    else:
        rule = MSWordRule(name="microsoft word")
        gfilter.run_on(rule)
        grammar.add_rule(rule)
        grammar.load()
