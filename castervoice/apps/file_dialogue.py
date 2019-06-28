from castervoice.lib.imports import *


class FileDialogueRule(MergeRule):
    pronunciation = "file dialogue"

    mapping = {
        "get up [<n>]"           : R(Key("a-up"))*Repeat(extra="n"),
        "get back [<n>]"         : R(Key("a-left"))*Repeat(extra="n"),
        "get forward [<n>]"      : R(Key("a-right"))*Repeat(extra="n"),
        "(files | file list)": R(Key("a-d, f6:3")),
        "navigation [pane]"  : R(Key("a-d, f6:2")),
        "[file] name"        : R(Key("a-d, f6:5")),
    }
    extras = [IntegerRefST("n", 1, 10)]
    defaults = {
        "n": 1,
    }


dialogue_names = [
    "open",
    "save",
    "select",
]
context = AppContext(title=dialogue_names)
control.non_ccr_app_rule(FileDialogueRule(), context=context)
