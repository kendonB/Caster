'''
Mike Roberts 13/09/18
'''

from dragonfly import (Dictation, Grammar, IntegerRef, Key, MappingRule,
                       Pause, Repeat, Text)
from dragonfly.actions.action_mimic import Mimic

from caster.lib import control, settings
from caster.lib.dfplus.additions import IntegerRefST
from caster.lib.dfplus.merge import gfilter
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.short import R
from caster.lib.context import AppContext

class RStudioRule(MergeRule):
    pronunciation = "are studio"

    mapping = {
	"look terminal":                    
	    R(Key("as-t"), rdescript="R: Focus terminal"),
	
    }
    extras = [
        IntegerRefST("n", 1, 10000),
    ]
    defaults = {}

context = AppContext(executable="rstudio", title="RStudio")
grammar = Grammar("RStudio", context=context)
if settings.SETTINGS["apps"]["rstudio"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(RStudioRule())
    else:
        rule = RStudioRule()
        gfilter.run_on(rule)
        grammar.add_rule(RStudioRule(name="rstudio"))
        grammar.load()
