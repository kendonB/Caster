from castervoice.lib.imports import *


class SSMSRule(MergeRule):
    pronunciation = "sequel server management studio"

    mapping = {
        # There doesn't seem to be a hotkey for sequential tab navigation in SSMS, but something is better than nothing...
        "next tab [<n>]": R(Key("c-tab"))*Repeat(extra="n"),
        "prior tab [<n>]": R(Key("cs-tab"))*Repeat(extra="n"),
        "close tab [<n>]": R(Key("c-f4/20"))*Repeat(extra="n"),
        "go to line": R(Key("c-g")),
        "comment line": R(Key("c-k, c-c")),
        "comment block": R(Key("c-k, c-c")),
        "(un | on) comment line": R(Key("c-k/50, c-u")),
        "(un | on) comment block": R(Key("c-k/50, c-u")),
        "[toggle] full screen": R(Key("sa-enter")),
        "(set | toggle) bookmark": R(Key("c-k, c-k")),
        "next bookmark": R(Key("c-k, c-n")),
        "prior bookmark": R(Key("c-k, c-p")),
        "[toggle] breakpoint": R(Key("f9")),
        "step over [<n>]": R(Key("f10/50")*Repeat(extra="n")),
        "step into": R(Key("f11")),
        "step out [of]": R(Key("s-f11")),
        "resume": R(Key("f5")),
    }
    extras = [
        Dictation("text"),
        Dictation("mim"),
        IntegerRefST("n", 1, 1000),
    ]
    defaults = {"n": 1, "mim": ""}


context = AppContext(executable="ssms")
control.non_ccr_app_rule(SSMSRule(), context=context)