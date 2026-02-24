'''
Created on Oct 7, 2015

@author: synkarius
'''
import os, sys, time, pkg_resources
from pkg_resources import VersionConflict, DistributionNotFound
from castervoice.lib import printer

DARWIN = sys.platform == "darwin"
LINUX = sys.platform == "linux"

def install_type():
    # Checks if Caster install is Classic or PIP.
    try:
        pkg_resources.require("castervoice")
    except VersionConflict:
        pass
    except DistributionNotFound:
        return "classic"
    return "pip"


def find_pip():
    # Find the pip script for Python.
    python_scripts = os.path.join(sys.exec_prefix,
                                  "bin" if DARWIN or LINUX else "Scripts")
    pip_exec = "pip.exe" if sys.platform == "win32" else "pip"
    return os.path.join(python_scripts, pip_exec)


def dep_missing():
    uppath = lambda _path, n: os.sep.join(_path.split(os.sep)[:-n])
    requirements_file = "requirements-mac-linux.txt" if DARWIN or LINUX else "requirements.txt"
    requirements = os.path.join(uppath(__file__, 4), requirements_file)
    missing_list = []
    with open(requirements) as f:
        requirements = f.read().splitlines()
    for dep in requirements:
        dep = dep.strip()
        if not dep or dep.startswith("#"):
            continue
        try:
            pkg_resources.require(dep)
        except VersionConflict:
            pass
        except DistributionNotFound:
            # Keep markers for evaluation, but exclude them in pip install guidance.
            missing_list.append(dep.split(";", 1)[0].strip())
    if missing_list:
        # Quote each requirement to avoid shell redirection parsing in version specifiers (for example >=).
        pippackages = " ".join(['"{0}"'.format(dep) for dep in missing_list])
        printer.out("\nCaster: dependencys are missing. Use 'python -m pip install {0}'".format(pippackages))
        time.sleep(10)


def dep_min_version():
    # For classic: Checks for Maintainer specified package requirements.
    # Needs to be manually resolved if Caster requires a specific version of dependency
    # A GitHub Issue URL needed to explain the change to version specific '==' dependency.
    listdependency = ([
        ["dragonfly2", ">=", "0.34.0", "https://github.com/dictation-toolbox/dragonfly/blob/master/CHANGELOG.rst#fixed"],
    ])
    for dep in listdependency:
        package = dep[0]
        operator = dep[1]
        version = dep[2]
        issue_url = dep[3]
        try:
            pkg_resources.require('{0} {1} {2}'.format(package, operator, version))
        except VersionConflict as e:
            if operator == ">=":
                if issue_url is not None:
                    printer.out("\nCaster: Requires {0} v{1} or greater.\nIssue reference: {2}".format(package, version, issue_url))
                printer.out("Update with: 'python -m pip install {} --upgrade' \n".format(package))
            if operator == "==":
                printer.out("\nCaster: Requires an exact version of {0}.\nIssue reference: {1}".format(package, issue_url))
                print("Install with: 'python -m pip install {}' \n".format(e.req))


class DependencyMan:
    # Initializes functions
    def initialize(self):
        install = install_type()
        if install == "classic":
            dep_missing()
            dep_min_version()
