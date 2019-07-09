from castervoice.lib.imports import *

CONFIG = utilities.load_toml_file(settings.SETTINGS["paths"]["BRINGME_PATH"])
if not CONFIG:
    CONFIG = utilities.load_toml_file(settings.SETTINGS["paths"]["BRINGME_DEFAULTS_PATH"])
if not CONFIG:
    print("Could not load bringme defaults")

def _rebuild_folders():
    return {
        key: (os.path.expandvars(value), 'folder') for key, value in CONFIG['folder'].iteritems()
    }

def navigate_to(desired_item):
    item, item_type = desired_item
    if item_type == 'folder':
        Text("cd " + item.replace("\\", "/")).execute()
        Key("enter").execute()

def type_path(desired_item):
    item, item_type = desired_item
    if item_type == 'folder':
        Text(item.replace("\\", "/")).execute()

def _apply(n):
    if n != 0:
        Text("stash@{" + str(int(n)) + "}").execute()


class GitBashRule(MergeRule):
    pronunciation = "git bash"
    GIT_ADD_ALL = "g, i, t, space, a, d, d, space, minus, A"
    GIT_COMMIT = "g, i, t, space, c, o, m, m, i, t, space, minus, m, space, quote, quote, left"
    mapping = {
        "(git|get) base":
            Text("git "),
        "(git|get) (initialize repository|init)":
            Text("git init"),
        "(git|get) add":
            R(Key("g, i, t, space, a, d, d, space, dot")),
        "(git|get) add all":
            R(Key(GIT_ADD_ALL)),
        "(git|get) commit all":
            R(Key("%s, ;, space, %s" % (GIT_ADD_ALL, GIT_COMMIT))),
        "(git|get) status":
            R(Key("g, i, t, space, s, t, a, t, u, s")),
        "(git|get) commit":
            R(Key(GIT_COMMIT)),
        "(git|get) bug fix commit <n>":
            R(Mimic("get", "commit") + Text("fixes #%(n)d ") + Key("backspace")),
        "(git|get) reference commit <n>":
            R(Mimic("get", "commit") + Text("refs #%(n)d ") + Key("backspace")),
        "(git|get) checkout":
            R(Text("git checkout ")),
        "(git|get) checkout mine":
            R(Text("git checkout what_i_use")),
        "(git|get) branch":
            R(Text("git branch ")),
        "(git|get) remote":
            R(Text("git remote ")),
        "(git|get) merge":
            R(Text("git merge ")),
        "(git|get) merge tool":
            R(Text("git mergetool")),
        "(git|get) fetch":
            R(Text("git fetch ")),
        "(git|get) push":
            R(Text("git push ")),
        "(git|get) pull":
            R(Text("git pull ")),
        "CD up":
            R(Text("cd ..")),
        "CD":
            R(Text("cd ")),
        "list":
            R(Text("ls")),
        "make directory":
            R(Text("mkdir ")),
        "undo [last] commit | (git|get) reset soft head":
            R(Text("git reset --soft HEAD~1")),
        "(undo changes | (git|get) reset hard)":
            R(Text("git reset --hard")),
        "stop tracking [file] | (git|get) remove":
            R(Text("git rm --cached ")),
        "preview remove untracked | (git|get) clean preview":
            R(Text("git clean -nd")),
        "remove untracked | (git|get) clean untracked":
            R(Text("git clean -fd")),
        "(git|get) visualize":
            R(Text("gitk")),
        "(git|get) visualize file":
            R(Text("gitk -- PATH")),
        "(git|get) visualize all":
            R(Text("gitk --all")),
        "(git|get) stash":
            R(Text("git stash")),
        "(git|get) stash apply [<n>]":
            R(Text("git stash apply") + Function(_apply)),
        "(git|get) stash list":
            R(Text("git stash list")),
        "(git|get) stash branch":
            R(Text("git stash branch NAME")),
        "(git|get) cherry pick":
            R(Text("git cherry-pick ")),
        "(git|get) (abort cherry pick | cherry pick abort)":
            R(Text("git cherry-pick --abort")),
        "(git|get) (GUI | gooey)":
            R(Text("git gui")),
        "(git|get) blame":
            R(Text("git blame PATH -L FIRSTLINE,LASTLINE")),
        "(git|get) gooey blame":
            R(Text("git gui blame PATH")),
        "search recursive":
            R(Text("grep -rinH \"PATTERN\" *")),
        "search recursive count":
            R(Text("grep -rinH \"PATTERN\" * | wc -l")),
        "search recursive filetype":
            R(Text("find . -name \"*.java\" -exec grep -rinH \"PATTERN\" {} \\;")),
        "to file":
            R(Text(" > FILENAME")),

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
        "[folder] path <desired_item>":
            R(Function(type_path), rdescript="GIT: type in folder path"),
        "(CD | go to | navigate to | [shell] bring me) <desired_item>":
            R(Function(navigate_to), rdescript="GIT: go to folder"),
    }
    extras = [
        IntegerRefST("n", 1, 10000),
        Choice("desired_item", _rebuild_folders()),
    ]
    defaults = {"n": 0}


terminal_context = AppContext(executable=[
    "\\sh.exe",
    "\\bash.exe",
    "\\cmd.exe",
    "\\mintty.exe",
    "\\powershell.exe"
    ])

jetbrains_context = AppContext(executable="idea", title="IntelliJ") \
          | AppContext(executable="idea64", title="IntelliJ") \
          | AppContext(executable="studio64") \
          | AppContext(executable="pycharm")

context = terminal_context | jetbrains_context

control.ccr_app_rule(GitBashRule(), context)
