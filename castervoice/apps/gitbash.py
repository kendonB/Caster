#
# This file is a command-module for Dragonfly.
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#
"""
Command-module for git

"""
# ---------------------------------------------------------------------------

from dragonfly import (Grammar, Mimic, Function, Choice)

from castervoice.lib import control, settings, utilities
from castervoice.lib.dfplus.additions import IntegerRefST
from castervoice.lib.dfplus.merge import gfilter
from castervoice.lib.dfplus.merge.mergerule import MergeRule
from castervoice.lib.dfplus.state.short import R
from castervoice.lib.context import AppContext, paste_string_without_altering_clipboard
from castervoice.lib.actions import (Key, Text)
from castervoice.lib.dfplus.merge.ccrmerger import CCRMerger

CONFIG = utilities.load_toml_file(settings.SETTINGS["paths"]["BRINGME_PATH"])
if not CONFIG:
    CONFIG = utilities.load_toml_file(settings.SETTINGS["paths"]["BRINGME_DEFAULTS_PATH"])
if not CONFIG:
    # logger.warn("Could not load bringme defaults")
    print("Could not load bringme defaults")

def _apply(n):
    if n != 0:
        Text("stash@{" + str(int(n)) + "}").execute()


class GitBashRule(MergeRule):
    pronunciation = "git bash"
    mwith = CCRMerger.CORE
    GIT_ADD_ALL = "g, i, t, space, a, d, d, space, minus, A"
    GIT_COMMIT = "g, i, t, space, c, o, m, m, i, t, space, minus, m, space, quote, quote, left"
    mapping = {
        "(git|get) base":
            Text("git "),
        "(git|get) (initialize repository|init)":
            Text("git init"),
        "(git|get) add":
            R(Key("g, i, t, space, a, d, d, space, dot"),
              rdescript="GIT: Add all in directory"),
        "(git|get) add all":
            R(Key(GIT_ADD_ALL),
              rdescript="GIT: Add all"),
        "(git|get) commit all":
            R(Key("%s, ;, space, %s" % (GIT_ADD_ALL, GIT_COMMIT))),
        "(git|get) status":
            R(Key("g, i, t, space, s, t, a, t, u, s"), rdescript="GIT: Status"),
        "(git|get) commit":
            R(Key(GIT_COMMIT),
              rdescript="GIT: Commit"),
        "(git|get) bug fix commit <n>":
            R(Mimic("get", "commit") + Text("fixes #%(n)d ") + Key("backspace"),
              rdescript="GIT: Bug Fix Commit"),
        "(git|get) reference commit <n>":
            R(Mimic("get", "commit") + Text("refs #%(n)d ") + Key("backspace"),
              rdescript="GIT: Reference Commit"),
        "(git|get) checkout":
            R(Text("git checkout "), rdescript="GIT: Check Out"),
        "(git|get) checkout mine":
            R(Text("git checkout what_i_use"), rdescript="GIT: Check Out Mine"),
        "(git|get) branch":
            R(Text("git branch "), rdescript="GIT: Branch"),
        "(git|get) remote":
            R(Text("git remote "), rdescript="GIT: Remote"),
        "(git|get) merge":
            R(Text("git merge "), rdescript="GIT: Merge"),
        "(git|get) merge tool":
            R(Text("git mergetool"), rdescript="GIT: Merge Tool"),
        "(git|get) fetch":
            R(Text("git fetch "), rdescript="GIT: Fetch"),
        "(git|get) push":
            R(Text("git push "), rdescript="GIT: Push"),
        "(git|get) pull":
            R(Text("git pull "), rdescript="GIT: Pull"),
        "CD up":
            R(Text("cd .."), rdescript="GIT: Up Directory"),
        "CD":
            R(Text("cd "), rdescript="GIT: Navigate Directory"),
        "list":
            R(Text("ls"), rdescript="GIT: List"),
        "make directory":
            R(Text("mkdir "), rdescript="GIT: Make Directory"),
        "undo [last] commit | (git|get) reset soft head":
            R(Text("git reset --soft HEAD~1"),
              rdescript="GIT: Undo Commit"),
        "(undo changes | (git|get) reset hard)":
            R(Text("git reset --hard"),
              rdescript="GIT: Undo or Reset Since Last Commit"),
        "stop tracking [file] | (git|get) remove":
            R(Text("git rm --cached "), rdescript="GIT: Stop Tracking"),
        "preview remove untracked | (git|get) clean preview":
            R(Text("git clean -nd"),
              rdescript="GIT: Preview Remove Untracked"),
        "remove untracked | (git|get) clean untracked":
            R(Text("git clean -fd"), rdescript="GIT: Remove Untracked"),
        "(git|get) visualize":
            R(Text("gitk"), rdescript="GIT: gitk"),
        "(git|get) visualize file":
            R(Text("gitk -- PATH"), rdescript="GIT: gitk Single File"),
        "(git|get) visualize all":
            R(Text("gitk --all"), rdescript="GIT: gitk All Branches"),
        "(git|get) stash":
            R(Text("git stash"), rdescript="GIT: Stash"),
        "(git|get) stash apply [<n>]":
            R(Text("git stash apply") + Function(_apply), rdescript="GIT: Stash Apply"),
        "(git|get) stash list":
            R(Text("git stash list"), rdescript="GIT: Stash List"),
        "(git|get) stash branch":
            R(Text("git stash branch NAME"), rdescript="GIT: Stash Branch"),
        "(git|get) cherry pick":
            R(Text("git cherry-pick "), rdescript="GIT: Cherry Pick"),
        "(git|get) (abort cherry pick | cherry pick abort)":
            R(Text("git cherry-pick --abort"), rdescript="GIT: Abort Cherry Pick"),
        "(git|get) (GUI | gooey)":
            R(Text("git gui"), rdescript="GIT: gui"),
        "(git|get) blame":
            R(Text("git blame PATH -L FIRSTLINE,LASTLINE"), rdescript="GIT: Blame"),
        "(git|get) gooey blame":
            R(Text("git gui blame PATH"), rdescript="GIT: GUI Blame"),
        "search recursive":
            R(Text("grep -rinH \"PATTERN\" *"), rdescript="GREP: Search Recursive"),
        "search recursive count":
            R(Text("grep -rinH \"PATTERN\" * | wc -l"),
              rdescript="GREP: Search Recursive Count"),
        "search recursive filetype":
            R(Text("find . -name \"*.java\" -exec grep -rinH \"PATTERN\" {} \\;"),
              rdescript="GREP: Search Recursive Filetype"),
        "to file":
            R(Text(" > FILENAME"), rdescript="Bash: To File"),

        "git merge into mine":
            R(Text("git branch | grep \"*\" | awk '{ print $2 }' | clip") +
              Key("enter/100") + Text("git checkout what_i_use") +
              Key("enter/100") + Text("git merge ") + Key("insert")),
        "hub pull request":
            R(Text("hub pull-request -o -b develop -a kendonB")),
        "git push [back to] pull request":
            R(Text("git branch | grep \"*\" | awk '{ print $2 }' | clip") +
              Key("enter/100") + Text("git push <pr_url> ") + Key("insert") +
              Text(":<pr_branch_name>") + Key("home") + Key("right:17")),
        "git push [back to] pull request alex":
            R(Text("git branch | grep \"*\" | awk '{ print $2 }' | clip") +
              Key("enter/100") + Text("git push https://github.com/alexboche/caster-1.git ") + Key("insert") +
              Text(":<pr_branch_name>")),
        "git push [back to] pull request em rob":
            R(Text("git branch | grep \"*\" | awk '{ print $2 }' | clip") +
              Key("enter/100") + Text("git push https://github.com/mrob95/caster.git ") + Key("insert") +
              Text(":<pr_branch_name>")),
        "update [my] develop [branch]":
            R(Text("git checkout pure_develop && git pull upstream develop")),

        # Folder path commands (not git specific)
        "[folder] path <folder_path>":
            R(Text("%(folder_path)s"), rdescript="GIT: type in folder path"),
        "(CD | go to | navigate to | [shell] bring me) <folder_path>":
            R(Text("cd %(folder_path)s") + Key("enter"), rdescript="GIT: go to folder"),

    }
    extras = [
        IntegerRefST("n", 1, 10000),
        Choice("folder_path", CONFIG["folder"]),
    ]
    defaults = {"n": 0}


# ---------------------------------------------------------------------------

<<<<<<< HEAD
context = AppContext(executable=["\\sh.exe", "\\bash.exe", "\\cmd.exe", "\\mintty.exe"])
=======
context = AppContext(executable="\\sh.exe") | \
          AppContext(executable="\\bash.exe") | \
          AppContext(executable="\\cmd.exe") | \
          AppContext(executable="\\powershell.exe") | \
          AppContext(executable="\\mintty.exe")
>>>>>>> dictation-toolbox/Caster/pull/476

if settings.SETTINGS["apps"]["gitbash"]:
    if settings.SETTINGS["miscellaneous"]["rdp_mode"]:
        control.nexus().merger.add_global_rule(GitBashRule())
    else:
        control.nexus().merger.add_app_rule(GitBashRule(), context)
