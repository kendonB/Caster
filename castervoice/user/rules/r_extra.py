from caster.lib import control
from caster.lib.dfplus.merge.mergepair import MergeInf
from caster.lib.dfplus.state.short import R

def replace_spec(rule, target, replacement):
    if target in rule.mapping_actual().keys():
        action = rule.mapping_actual()[target]
        del rule.mapping_actual()[target]
        rule.mapping_actual()[replacement] = action

def replace_spec_function_r(mp):
    if mp.time == MergeInf.BOOT:
        target = "<function>"
        replacement = "fun <function>"

        if mp.rule1 is not None: 
            replace_spec(mp.rule1, target, replacement)
        replace_spec(mp.rule2, target, replacement)

control.nexus().merger.add_filter(replace_spec_function_r)

