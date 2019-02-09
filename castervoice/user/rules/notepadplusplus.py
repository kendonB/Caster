#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#
"""
Command-module for Notepad++

"""
#---------------------------------------------------------------------------

from dragonfly import (Grammar, Dictation, Repeat)

from caster.lib import control
from caster.lib import settings
from caster.lib.actions import Key, Mouse
from caster.lib.context import AppContext
from caster.lib.dfplus.additions import IntegerRefST
from caster.lib.dfplus.merge import gfilter
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.short import R


class NPPRule(MergeRule):
    pronunciation = "notepad plus plus"

    mapping = {
	"get up":                                
	    R(Key("a-up"), rdescript="Notepad++: Navigate up"),
	"open":                                
	    R(Key("c-o"), rdescript="Notepad++: Open"),
	"get back":                           
	    R(Key("a-left"), rdescript="Notepad++: Navigate back"),
	"get forward":                        
	    R(Key("a-right"), rdescript="Notepad++: Navigate forward"),
    }
    extras = [
        Dictation("text"),
        IntegerRefST("n", 1, 100),
        IntegerRefST("n2", 1, 10),
    ]
    defaults = {"n": 1}


#---------------------------------------------------------------------------

context = AppContext(executable="notepad++")
grammar = Grammar("Notepad++", context=context)

if settings.SETTINGS["apps"]["notepadplusplus"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(NPPRule())
    else:
        rule = NPPRule(name="notepad plus plus")
        gfilter.run_on(rule)
        grammar.add_rule(rule)
        grammar.load()
