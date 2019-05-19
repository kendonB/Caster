# -*- coding: UTF-8 -*-
'''
Created on Sep 4, 2018

@author: Mike Roberts
'''
from dragonfly import Function, Choice

from castervoice.lib import control
from castervoice.lib.actions import Key, Text
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R

def maori_words(big, word):
    word = unicode(word)
    if big:
        word = word.capitalize()
    Text(word).execute()

class Maori(MergeRule):
    pronunciation = "maori" 

    mapping = {
        "maori word [<big>] <word>":
            R(Function(maori_words, extra={"big", "word"}) + Text(" "),
              rdescript="Maori: Insert word"),
    }

    extras = [
        Choice("big", 
        {
            "big": True,
        }),
        Choice("word", {
            "kyah order": "kia ora",
            "ngaa mihhy": u"ngā mihi",
        }),
    ]
    defaults = {
        "big": False,
    }

control.nexus().merger.add_global_rule(Maori())
