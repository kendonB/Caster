from dragonfly.grammar.elements import RuleRef, Alternative, Repetition
from dragonfly.grammar.rule_compound import CompoundRule
from castervoice.lib.const import CCRType
from castervoice.lib.context import AppContext


class CCRMerger2(object):

    def __init__(self, transformers, rule_sorter, compatibility_checker, merging_strategy, max_repetitions,
                 smr_configurer):
        """
        5-Step Merge Process
        ====================
        1. Run all transformers over all rules.
        2. Use a rule set sorter to sort rules.
        3. Use a compatibility checker to calculate incompatibility.
        4. Pass the transformed/sorted/checked rules to the merging strategy.
        5. Use the old trick from _multiedit.py to turn a MappingRule into a CCR rule.
        ====================
        :param transformers: collection of Transformers
        :param rule_sorter: BaseRuleSetSorter impl
        :param compatibility_checker: BaseCompatibilityChecker impl
        :param merging_strategy: BaseMergingStrategy impl
        :param max_repetitions
        :param smr_configurer
        """
        self._transformers = transformers
        self._rule_sorter = rule_sorter
        self._compatibility_checker = compatibility_checker
        self._merging_strategy = merging_strategy
        #
        self._sequence = 0
        self._max_repetitions = max_repetitions
        self._smr_configurer = smr_configurer

    def add_transformer(self, transformer):
        self._transformers.append(transformer)

    def merge(self, managed_rules):
        """
        :param managed_rules: list of ManagedRules
        :return: list of tuples: (repeat-rule, context)
        """
        rcns_to_details = CCRMerger2._rule_details_dict(managed_rules)
        instantiated_rules = self._instantiate_and_configure_rules(managed_rules)

        # 1: run transformers over rules
        transformed_rules = self._run_transformers(instantiated_rules, rcns_to_details)
        # 2: sort rules into the order they'll be merged in
        sorted_rules = self._rule_sorter.sort_rules(transformed_rules)
        # 3: compute compatibility results for all rules vs all rules in O(n) for total specs
        compat_results = [self._compatibility_checker.compatibility_check(r) for r in sorted_rules]
        # 4: create one merged rule for each context, plus the no-contexts merged rule
        app_crs, non_app_crs = self._separate_app_rules(compat_results, rcns_to_details)
        merged_rules = self._create_merged_rules(app_crs, non_app_crs)
        # 5: turn the merged rules into repeat rules
        ccr_rules = [self._create_repeat_rule(merged_rule) for merged_rule in merged_rules]
        contexts = CCRMerger2._create_contexts(app_crs)

        return zip(ccr_rules, contexts)

    def _instantiate_and_configure_rules(self, managed_rules):
        instantiated_rules = []
        for mr in managed_rules:
            mergerule = mr.get_rule_instance()
            # smr configurer only configures selfmodrules, but checks all
            self._smr_configurer.configure(mergerule)
            instantiated_rules.append(mergerule)
        return instantiated_rules

    def _run_transformers(self, instantiated_rules, rcns_to_details):
        transformed_rules = []
        for rule in instantiated_rules:
            has_exclusion = rcns_to_details[rule.get_rule_class_name()].transformer_exclusion
            if not has_exclusion:
                for transformer in self._transformers:
                    rule = transformer.get_transformed_rule(rule)
            transformed_rules.append(rule)
        return transformed_rules

    def _separate_app_rules(self, compat_results, rcns_to_details):
        """
        Given M non-app rules and N app rules, we want to produce
        N+1 merged rules, where one of them has no app rules and the rest
        each have one app rule.
        """
        app_crs = []
        non_app_crs = []
        for cr in compat_results:
            details = rcns_to_details[cr.rule_class_name()]
            if details.declared_ccrtype == CCRType.APP:
                app_crs.append(cr)
            else:
                non_app_crs.append(cr)
        return app_crs, non_app_crs

    def _create_merged_rules(self, app_crs, non_app_crs):
        merged_rules = [self._merging_strategy.merge(non_app_crs)]
        for app_cr in app_crs:
            with_one_app = list(non_app_crs)
            with_one_app.append(app_cr)
            merged_rules.append(self._merging_strategy.merge(with_one_app))
        return merged_rules

    @staticmethod
    def _create_contexts(app_crs, rcns_to_details):
        """
        Returns a list of AppContexts, based on 'executable', one for each
        app rule, and if more than zero app rules, the negation context for the
        global ccr rule. (Global rule should be active when none of the other
        contexts are.) If there are zero app rules, [None] will be returned
        so the result can be zipped.

        :param app_crs: list of CompatibilityResult for app rules
        :param rcns_to_details: map of {rule class name: rule details}
        :return:
        """
        contexts = []
        negation_context = None
        for cr in app_crs:
            details = rcns_to_details[cr.rule_class_name()]
            context = AppContext(executable=details.executable)
            contexts.append(context)
            if negation_context is None:
                negation_context = ~context
            else:
                negation_context += ~context
        contexts.insert(0, negation_context)
        return contexts

    @staticmethod
    def _rule_details_dict(managed_rules):
        """
        :param managed_rules: list of ManagedRule
        :return: dict of {class name (str): RuleDetails}
        """
        result = {}
        for managed_rule in managed_rules:
            result.put(managed_rule.get_rule_class_name(), managed_rule.get_details())
        return result

    def _create_repeat_rule(self, rule):
        ORIGINAL, SEQ, TERMINAL = "original", "caster_base_sequence", "terminal"
        alts = [RuleRef(rule=rule)]  # +[RuleRef(rule=sm) for sm in selfmod]
        single_action = Alternative(alts)
        sequence = Repetition(single_action, min=1, max=self._max_repetitions, name=SEQ)
        original = Alternative(alts, name=ORIGINAL)
        terminal = Alternative(alts, name=TERMINAL)

        class RepeatRule(CompoundRule):
            spec = "[<" + ORIGINAL + "> original] [<" + SEQ + ">] [terminal <" + TERMINAL + ">]"
            extras = [sequence, original, terminal]

            def _process_recognition(self, node, extras):
                original = extras[ORIGINAL] if ORIGINAL in extras else None
                sequence = extras[SEQ] if SEQ in extras else None
                terminal = extras[TERMINAL] if TERMINAL in extras else None
                if original is not None: original.execute()
                if sequence is not None:
                    for action in sequence:
                        action.execute()
                if terminal is not None: terminal.execute()

        return RepeatRule(name=self._get_new_rule_name())

    def _get_new_rule_name(self):
        self._sequence += 1
        return "Repeater{}".format(str(self._sequence))
