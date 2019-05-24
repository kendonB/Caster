'''
Created on May 5 2019

@author: kendonb
'''
from dragonfly import Function, MappingRule

from castervoice.lib import control, automation
from castervoice.lib.dfplus.state.short import R
from castervoice.lib.dfplus.merge.mergerule import MergeRule

_NEXUS = control.nexus()

# non ccr
class GithubNon(MappingRule):
    mapping = {
        "checkout [this] pull request [locally]":
            R(Function(automation.github_fetch_pull_request, new=True)),
        "update [this] pull request [locally]":
            R(Function(automation.github_fetch_pull_request, new=False)),
    }

class Github(MergeRule):
    pronunciation = "github"
    non = GithubNon

control.nexus().merger.add_global_rule(Github())
