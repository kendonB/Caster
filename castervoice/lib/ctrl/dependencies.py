'''
Created on Oct 7, 2015

@author: synkarius
'''
import os
import sys
import time

try:
    import pkg_resources as _pkg_resources  # pylint: disable=import-error
except ModuleNotFoundError:
    _pkg_resources = None

if _pkg_resources is not None and all(
    hasattr(_pkg_resources, attr)
    for attr in ("require", "DistributionNotFound", "VersionConflict")
):
    pkg_resources = _pkg_resources
    DistributionNotFound = pkg_resources.DistributionNotFound
    VersionConflict = pkg_resources.VersionConflict
else:
    from importlib import metadata

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

    class DistributionNotFound(Exception):
        """Raised when a required distribution is not installed."""

    class VersionConflict(Exception):
        """Raised when an installed distribution does not satisfy the requested version."""

        def __init__(self, dist, req):
            self.dist = dist
            self.req = req
            super().__init__("{0} does not satisfy {1}".format(dist, req))

    def _installed_distribution(distribution_name):
        for candidate in (
            distribution_name,
            distribution_name.replace("_", "-"),
            distribution_name.replace("-", "_"),
        ):
            try:
                return metadata.distribution(candidate)
            except metadata.PackageNotFoundError:
                continue
        raise DistributionNotFound(distribution_name)

    def _installed_version(distribution_name):
        return _installed_distribution(distribution_name).version

    def _require_fallback(requirement_spec, marker_environment=None, visited=None):
        requirement = Requirement(requirement_spec)
        marker_environment = dict(marker_environment or default_environment())
        if requirement.marker and not requirement.marker.evaluate(marker_environment):
            return
        visited = visited if visited is not None else set()
        visited_key = (
            canonicalize_name(requirement.name),
            str(requirement.specifier),
            tuple(sorted(requirement.extras)),
            str(requirement.marker) if requirement.marker else None,
            marker_environment.get("extra"),
        )
        if visited_key in visited:
            return
        visited.add(visited_key)
        installed_version = _installed_version(requirement.name)
        if requirement.specifier:
            try:
                parsed_version = Version(installed_version)
            except InvalidVersion:
                raise VersionConflict(installed_version, requirement_spec)
            if parsed_version not in requirement.specifier:
                raise VersionConflict(installed_version, requirement_spec)
        if not requirement.extras:
            return
        distribution = _installed_distribution(requirement.name)
        for extra in requirement.extras:
            extra_environment = dict(marker_environment)
            extra_environment["extra"] = extra
            for child_spec in distribution.requires or []:
                child_requirement = Requirement(child_spec)
                if child_requirement.marker and not child_requirement.marker.evaluate(extra_environment):
                    continue
                _require_fallback(child_spec, extra_environment, visited)

    class _PkgResourcesShim:
        @staticmethod
        def require(requirement_spec):
            _require_fallback(requirement_spec)

    pkg_resources = _PkgResourcesShim()
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
