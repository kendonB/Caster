from castervoice.lib.ctrl.mgr.validation.rules.base_validator import BaseRuleValidator

class SelfModifyingRuleValidator(BaseRuleValidator):
    def _is_valid(self, rule, params):
        return hasattr(rule, "set_merger")
    def _invalid_message(self):
        return "must be or inherit SelfModifyingRule"