from castervoice.lib.ctrl.mgr.errors.base_class_error import DontUseBaseClassError


class BaseMergingStrategy(object):
    """
    Merging strategies define how the transformed, sorter, compat-checked
    rules become one or more merged CCR rules.
    """

    def merge_into_single(self, sorted_checked_rules):
        selected_rules = self.select_rules_to_merge(sorted_checked_rules)
        return self.merge_selected_rules(selected_rules)

    def merge_selected_rules(self, compat_results):
        merged_rule = None
        for compat_result in compat_results:
            if merged_rule is None:
                merged_rule = compat_result.rule()
            else:
                merged_rule = merged_rule.merge(compat_result.rule())
        return merged_rule

    def select_rules_to_merge(self, sorted_checked_rules):
        raise DontUseBaseClassError() # pylint: disable=no-value-for-parameter
