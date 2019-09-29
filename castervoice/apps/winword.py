from dragonfly import Key, Dictation, MappingRule

from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.additions import IntegerRefST
from castervoice.lib.merge.state.short import R

def symbol_letters(big, symbol):
    if big:
        symbol = symbol.title()
    Text(str(symbol)).execute()

class MSWordRule(MappingRule):
    mapping = {
        "insert image": R(Key("alt, n, p")),
        "symbol [<big>] <symbol>":
            R(Text("\\") + Function(symbol_letters, extra={"big", "symbol"}) + Text(" "),
              rdescript="Word: Insert symbols"),
        "eek":
            R(Key("a-equals")),
        "quick access one":
            R(Key("a-1")),
        "quick access two":
            R(Key("a-2")),
        "quick access three":
            R(Key("a-3")),
        "quick access four":
            R(Key("a-4")),
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


def get_rule():
    details = RuleDetails(name="Microsoft Word", executable="winword")
    return MSWordRule, details
