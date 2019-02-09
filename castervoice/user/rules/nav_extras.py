'''
Created on Sep 1, 2015

@author: synkarius
'''
from dragonfly import Repeat, Function, Key, Dictation, Choice, Mouse, MappingRule, Playback

from caster.lib import context, navigation, alphanumeric, textformat
from caster.lib import control
from caster.lib.dfplus.additions import IntegerRefST
from caster.lib.dfplus.merge.ccrmerger import CCRMerger
from caster.lib.dfplus.merge.mergerule import MergeRule
from caster.lib.dfplus.state.actions import AsynchronousAction, ContextSeeker
from caster.lib.dfplus.state.actions2 import UntilCancelled
from caster.lib.dfplus.state.short import L, S, R
from dragonfly.actions.action_mimic import Mimic
from caster.lib.ccr.standard import SymbolSpecs

_NEXUS = control.nexus()

class NavigationExtra(MergeRule):
    pronunciation = "navigation extra"
    mapping = {
    # keyboard shortcuts
	
	    "quit":                   
		    R(Key("escape"), rdescript="Press escape"),		
		"end":                   
		    R(Key("end"), rdescript="End of the line"),		
		"hum":                   
		    R(Key("home"), rdescript="Start of the line"),		
		"dock start":                   
		    R(Key("c-home"), rdescript="Start of the document"),		
		"dock end":                   
		    R(Key("c-end"), rdescript="End of the document"),		
		
		"doon [<nnavi500>]":                   
		    R(Key("pgdown"), rdescript="Page down") * Repeat(extra="nnavi500"),		
		"sun [<nnavi500>]":                   
		    R(Key("pgup"), rdescript="Page up") * Repeat(extra="nnavi500"),		
		
		"laib [<nnavi500>]":                   
		    R(Key("c-left"), rdescript="Left by words") * Repeat(extra="nnavi500"),		
		"rope [<nnavi500>]":                   
		    R(Key("c-right"), rdescript="Right by words") * Repeat(extra="nnavi500"),			
		
		"nope [<nnavi500>]":                   
		    R(Key("cs-left"), rdescript="Delete left by words") * Repeat(extra="nnavi500") + Key("backspace"),		
		"kay [<nnavi500>]":                   
		    R(Key("cs-right"), rdescript="Delete right by words") * Repeat(extra="nnavi500") + Key("backspace"),		
    # text formatting
        "(<capitalization> <spacing> | <capitalization> | <spacing>) <textnv> [brunt]":
            R(Function(textformat.master_format_text), rdescript="Text Format"),
		"shine hum":
            R(Playback([(["shine", "lease", "Wally"], 0.0)]), rdescript="My spec: Select to start of line"),
		"shine end":
            R(Playback([(["shine", "Ross", "Wally"], 0.0)]), rdescript="My spec: Select to end of line"),
		"ren":
		    R(Key("lparen"), rdescript="My spec: Open parenthesis"),
		"glow ren":
		    R(Key("rparen"), rdescript="My spec: Close parenthesis"),
		"bray":
		    R(Key("lbrace"), rdescript="My spec: Open curly"),
		"glow bray":
		    R(Key("rbrace"), rdescript="My spec: Close curly"),
		"bake techie":
		    R(Key("backtick"), rdescript="My spec: Backtick"),
    }

    extras = [
        IntegerRefST("nnavi500", 1, 500),
		Choice("capitalization", {
            "yell": 1,
            "tie": 2,
            "Gerrish": 3,
            "sing": 4,
            "laws": 5
        }),
        Dictation("textnv"),
        Choice(
            "spacing", {
                "gum": 1,
                "gun": 1,
                "spine": 2,
                "snake": 3,
                "pebble": 4,
                "incline": 5,
                "dissent": 6,
                "descent": 6
            }),
    ]

    defaults = {
        "nnavi500": 1,
		"textnv": "",
        "capitalization": 0,
        "spacing": 0
    }


control.nexus().merger.add_global_rule(NavigationExtra())
