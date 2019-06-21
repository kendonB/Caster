from dragonfly import Function, ShortIntegerRef, Text

from castervoice.lib import control, alphanumeric
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge.ccrmerger import CCRMerger
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R

class Numbers(MergeRule):
    pronunciation = CCRMerger.CORE[2]
    mapping = {
        "word number <wn>":
            R(Function(alphanumeric.word_number, extra="wn"), rdescript="Core: Number as Word"),
        "numb <wnKK>":
            R(Function(alphanumeric.numbers2, extra="wnKK"),
              rspec="Number",
              rdescript="Core: Number"),
        "bum <wnKK>":
            R(Text(", ") + Function(alphanumeric.numbers2, extra="wnKK"),
              rspec="Number",
              rdescript="Core: Number with comma"),
    }

    extras = [
        IntegerRefST("wn", 0, 10),
        IntegerRefST("wnKK", 0, 1000000),
    ]
    defaults = {}


control.nexus().merger.add_global_rule(Numbers())
