from castervoice.lib import settings
from castervoice.lib.ccr.recording.alias.base_alias import BaseAliasRule
from castervoice.lib.const import CCRType
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


class ChainAlias(BaseAliasRule):
    pronunciation = "chain alias"

    def __init__(self):
        super(ChainAlias, self).__init__(settings.settings(["paths", "SM_CHAIN_ALIAS_PATH"]))

    def get_pronunciation(self):
        return ChainAlias.pronunciation


def get_rule():
    return ChainAlias, RuleDetails(ccrtype=CCRType.SELFMOD)
