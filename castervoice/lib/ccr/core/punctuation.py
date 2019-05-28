from dragonfly import Choice, Repeat

from castervoice.lib import control
from castervoice.lib.actions import Key, Text
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge.ccrmerger import CCRMerger
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R


class Punctuation(MergeRule):
    pronunciation = CCRMerger.CORE[3]

    mapping = {
        "[<long>] <single_character>": R(Text("%(long)s" + "%(single_character)s" + "%(long)s")),
        "[is] greater [than] [or] equal [to]":
            R(Key("rangle, equals"), rdescript="Core: >= Comparison"),
        "long [is] equal to":
            R(Key("space,equals,equals,space"), rdescript="Core: Equality"),
        "quotes":
            R(Key("dquote,dquote,left"), rdescript="Core: Quotation Marks"),
        "thin quotes":
            R(Key("apostrophe,apostrophe,left"), rdescript="Core: Thin Quotation Marks"),
        "bakes":
            R(Key("backtick, backtick, left"), rdescript="Core: Backtick Pair"),
        "prekris":
            R(Key("lparen, rparen, left"), rdescript="Core: Parentheses"),
        "brax":
            R(Key("lbracket, rbracket, left"), rdescript="Core: Square Brackets"),
        "curly":
            R(Key("lbrace, rbrace, left"), rdescript="Core: Curly Braces"),
        "angle":
            R(Key("langle, rangle, left"), rdescript="Core: Angle Brackets"),
        "[<long>] equals":
            R(Text("%(long)s" + "=" + "%(long)s"), rdescript="Core: Equals Sign"),
        "[<long>] plus":
            R(Text("%(long)s" + "+" + "%(long)s"), rdescript="Core: Plus Sign"),
        "[<long>] minus":
            R(Text("%(long)s" + "-" + "%(long)s"), rdescript="Core: Dash"),
        "pipe (sim | symbol)":
            R(Text("|"), rdescript="Core: Pipe Symbol"),
        "long pipe (sim | symbol)":
            R(Text(" | "), rdescript="Core: Pipe Symbol surrounded by spaces"),
        'ace [<npunc>]':
            R(Key("space"), rdescript="Core: Space")*Repeat(extra="npunc"),
        "clamor":
            R(Text("!"), rdescript="Core: Exclamation Mark"),
        "deckle":
            R(Text(":"), rdescript="Core: Colon"),
        "long deckle":
            R(Key("right") + Text(": "), rdescript="Core: move right type colon then space"),
        "starling":
            R(Key("asterisk"), rdescript="Core: Asterisk"),
        "questo":
            R(Text("?"), rdescript="Core: Question Mark"),
        "comma":
            R(Text(","), rdescript="Core: Comma"),
        "carrot":
            R(Text("^"), rdescript="Core: Carat"),
        "(period | dot) [<npunc>]":
            R(Text("."), rdescript="Core: Dot")*Repeat(extra="npunc"),
        "at E":
            R(Text("@"), rdescript="Core: At Sign"),
        "hash tag":
            R(Text("#"), rdescript="Core: Hash Tag"),
        "apostrophe":
            R(Text("'"), rdescript="Core: Apostrophe"),
        "underscore":
            R(Text("_"), rdescript="Core: Underscore"),
        "backslash":
            R(Text("\\"), rdescript="Core: Back Slash"),
        "slash":
            R(Text("/"), rdescript="Core: Forward Slash"),
        "Dolly":
            R(Text("$"), rdescript="Core: Dollar Sign"),
        "modulo":
            R(Key("percent"), rdescript="Core: Percent Sign"),
        'tabby [<npunc>]':
            R(Key("tab"), rdescript="Core: Tab")*Repeat(extra="npunc"),
        'lay tabby [<npunc>]':
            R(Key("s-tab"), rdescript="Core: Shift Tab")*Repeat(extra="npunc"),
        "boom":
            R(Text(", "), rdescript="Core: Comma + Space"),
        "ampersand":
            R(Key("ampersand"), rdescript="Core: Ampersand"),
        "tilde":
            R(Key("tilde"), rdescript="Core: Tilde"),
		"long tilde":
            R(Key("space, tilde, space"), rdescript="Core: Long Tilde"),
		"ren":
            R(Key("lparen"), rdescript="Core: Left Parentheses"),
		"glow ren":
            R(Key("rparen"), rdescript="Core: Right Parentheses"),
		"bray":
            R(Key("lbrace"), rdescript="Core: Left Brace"),
		"glow bray":
            R(Key("rbrace"), rdescript="Core: Right Brace"),
		

    }

    extras = [
        IntegerRefST("npunc", 0, 10),
        Choice("long", {
              "long": " ",
        }),
        Choice("single_character", {
                "semper":                              ";",
                "[is] greater than":                   ">",  
                "[is] less than":                      "<",
                "[is] greater [than] [or] equal [to]": ">=",
        }),
    ]
    defaults = {
        "npunc": 1,
        "long": "",
    }


        
control.nexus().merger.add_global_rule(Punctuation())
