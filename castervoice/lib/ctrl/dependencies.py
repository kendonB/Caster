'''
Created on Oct 7, 2015

@author: synkarius
'''
import os
import sys
import time
from importlib import metadata
from importlib.metadata import PackageNotFoundError, version

try:
    from packaging.markers import default_environment
    from packaging.requirements import Requirement
    from packaging.utils import canonicalize_name
    from packaging.version import InvalidVersion, Version
except ModuleNotFoundError:  # pragma: no cover - fallback when packaging isn't installed directly
    from pip._vendor.packaging.markers import default_environment  # pylint: disable=import-error
    from pip._vendor.packaging.requirements import Requirement  # pylint: disable=import-error
    from pip._vendor.packaging.utils import canonicalize_name  # pylint: disable=import-error
    from pip._vendor.packaging.version import InvalidVersion, Version  # pylint: disable=import-error

from castervoice.lib import printer

DARWIN = sys.platform == "darwin"
LINUX = sys.platform == "linux"
DIST_ALIAS_MAP = {
    "dragonfly2": ("dragonfly2", "dragonfly"),
    "dragonfly": ("dragonfly", "dragonfly2"),
}


def _installed_distribution(distribution_name):
    candidates = []
    primary_names = DIST_ALIAS_MAP.get(canonicalize_name(distribution_name), (distribution_name,))
    for primary_name in primary_names:
        candidates.extend((
            primary_name,
            primary_name.replace("_", "-"),
            primary_name.replace("-", "_"),
            canonicalize_name(primary_name),
        ))
    seen = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            return metadata.distribution(candidate)
        except PackageNotFoundError:
            continue
    raise PackageNotFoundError(distribution_name)


def _requirement_is_installed(requirement_spec, marker_environment=None, visited=None):
    requirement = Requirement(requirement_spec)
    marker_environment = dict(marker_environment or default_environment())
    if requirement.marker and not requirement.marker.evaluate(marker_environment):
        return True

    visited = visited if visited is not None else set()
    visited_key = (
        canonicalize_name(requirement.name),
        str(requirement.specifier),
        tuple(sorted(requirement.extras)),
        str(requirement.marker) if requirement.marker else None,
        marker_environment.get("extra"),
    )
    if visited_key in visited:
        return True
    visited.add(visited_key)

    try:
        distribution = _installed_distribution(requirement.name)
    except PackageNotFoundError:
        return False

    if requirement.specifier:
        try:
            installed_version = Version(distribution.version)
        except InvalidVersion:
            return False
        if installed_version not in requirement.specifier:
            return False

    for child_spec in distribution.requires or []:
        if not _requirement_is_installed(child_spec, marker_environment, visited):
            return False

    for extra in requirement.extras:
        extra_environment = dict(marker_environment)
        extra_environment["extra"] = extra
        for child_spec in distribution.requires or []:
            if not _requirement_is_installed(child_spec, extra_environment, visited):
                return False

    return True


def _install_hint(requirement_spec):
    requirement = Requirement(requirement_spec)
    extras = "[{0}]".format(",".join(sorted(requirement.extras))) if requirement.extras else ""
    return "{0}{1}{2}".format(requirement.name, extras, requirement.specifier)

def install_type():
    # Checks if Caster install is Classic or PIP.
    try:
        version("castervoice")
    except PackageNotFoundError:
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
        if not _requirement_is_installed(dep):
            missing_list.append(_install_hint(dep))
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
        req_version = dep[2]
        issue_url = dep[3]
        try:
            installed = Version(_installed_distribution(package).version)
            required = Version(req_version)
            if operator == ">=" and installed < required:
                if issue_url is not None:
                    printer.out("\nCaster: Requires {0} v{1} or greater.\nIssue reference: {2}".format(package, req_version, issue_url))
                printer.out("Update with: 'python -m pip install {} --upgrade' \n".format(package))
            elif operator == "==" and installed != required:
                printer.out("\nCaster: Requires an exact version of {0}.\nIssue reference: {1}".format(package, issue_url))
                printer.out("Install with: 'python -m pip install {0}=={1}' \n".format(package, req_version))
        except PackageNotFoundError:
            pass


class DependencyMan:
    # Initializes functions
    def initialize(self):
        install = install_type()
        if install == "classic":
            dep_missing()
            dep_min_version()
