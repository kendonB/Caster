# -*- coding: UTF-8 -*-
'''
Created on May 20, 2019

@author: Kendon Bell
'''
from dragonfly import Function, Choice

from castervoice.lib import control
from castervoice.lib.actions import Key, Text
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R
from castervoice.lib import textformat

maori_phrases = { 
    "(kyah order | kia ora)":                                        u"kia ora",
    "ngaa mihhy":                                                    u"ngā mihi",
    "(a wa teh de | Awatere)":                                       u"Awatere",
    "kaitiakitanga":                                                 u"kaitiakitanga",
    "(manaaki whenua | manaaki fenoo a)":                            u"Manaaki Whenua",
    "(tamaki makaurau | tah mucky Makoto | Auckland)":               u"Tāmaki Makaurau",
    "maori | multi-":                                                u"Māori", 
    "Whakatipu Rawa | fakatipu dawa":                                u"Whakatipu Rawa", 
    "LTO door | aa o teah doah | Aotearoa":                          u"Aotearoa", 
    "tear nah koto car tour | tena koutou katoa":                    u"tēnā koutou katoa", 
    "mahuika | ma who eek a":                                        u"Mahuika", 
}

def maori_words(capitalization, spacing, phrase):
    if capitalization == 0:
        capitalization = 6
    textformat.master_format_text(capitalization, spacing, phrase)

class Maori(MergeRule):
    pronunciation = "maori" 

    mapping = {
        "kupu maori [(<capitalization> <spacing> | <capitalization> | <spacing>)] <phrase>":
            R(Function(maori_words, extra={"capitalization", "spacing", "phrase"}) + Text(" "),
              rdescript="Maori: Insert phrase"),
    }

    extras = [
        Choice("capitalization", {
            "yell": 1,
            "tie": 2,
            "Gerrish": 3,
            "sing": 4,
            "laws": 5
        }),
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
        Choice("phrase", maori_phrases),
    ]
    defaults = {
        "capitalization": 0,
        "spacing": 0,
    }
    
control.nexus().merger.add_global_rule(Maori())
