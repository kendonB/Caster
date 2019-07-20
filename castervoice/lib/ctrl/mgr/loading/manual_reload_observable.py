from dragonfly import Function, MappingRule
from castervoice.lib.ctrl.mgr.loading.base_reload_observable import BaseReloadObservable
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails


class ManualReloadObservable(BaseReloadObservable):
    """
    Allows for reloading changed files on command.
    """

    def __init__(self):
        BaseReloadObservable.__init__(self)

        '''
        This class itself will never be reloaded, but it can
        be registered like the other rules and so can have
        transformers run over it, etc.
        '''
        class ManualGrammarReloadRule(MappingRule):
            mapping = {
                "reload all rules": Function(lambda: self._update())
            }

        self._rule_class = ManualGrammarReloadRule

    def get_loadable(self):
        details = RuleDetails()
        return [self._rule_class, details]
