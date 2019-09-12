from unittest import TestCase

from castervoice.lib.ccr.core.alphabet import Alphabet
from castervoice.lib.ccr.core.nav import Navigation
from castervoice.lib.merge.ccrmerging2.sorting.alpha_ruleset_sorter import AlphaRuleSetSorter
from castervoice.lib.util.rules.caster_rule import CasterRule


class TestAlphaPronunciationRuleSetSorter(TestCase):
    def test_sort_rules(self):
        sorter = AlphaRuleSetSorter()
        a = Alphabet()
        c = CasterRule()
        n = Navigation()
        rules = [n, a, c]
        sorted_rules = sorter.sort_rules(rules)
        self.assertEqual(0, sorted_rules.index(a))
        self.assertEqual(1, sorted_rules.index(c))
        self.assertEqual(2, sorted_rules.index(n))
