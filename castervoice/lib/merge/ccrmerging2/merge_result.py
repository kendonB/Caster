class CCRRuleLoadSpec(object):
    def __init__(self, rule, context, display_name):
        self.rule = rule
        self.context = context
        self.display_name = display_name


class MergeResult(object):

    def __init__(self, ccr_rules_and_contexts, all_rule_class_names, rules_enabled_diff):
        """
        :param ccr_rules_and_contexts: 1-n CCRRuleLoadSpec instances
        :param all_rule_class_names: list of str
        :param rules_enabled_diff: RulesEnabledDiff
        """
        self.ccr_rules_and_contexts = ccr_rules_and_contexts
        self.all_rule_class_names = all_rule_class_names
        self.rules_enabled_diff = rules_enabled_diff
