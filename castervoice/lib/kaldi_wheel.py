import argparse
import json
import platform
import sys
from importlib import metadata
from importlib.metadata import PackageNotFoundError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

try:
    from packaging.requirements import Requirement
    from packaging.specifiers import SpecifierSet
    from packaging.version import InvalidVersion, Version
except ModuleNotFoundError:  # pragma: no cover - fallback when packaging isn't installed directly
    from pip._vendor.packaging.requirements import Requirement  # pylint: disable=import-error
    from pip._vendor.packaging.specifiers import SpecifierSet  # pylint: disable=import-error
    from pip._vendor.packaging.version import InvalidVersion, Version  # pylint: disable=import-error


RELEASES_URL = "https://api.github.com/repos/daanzu/kaldi-active-grammar/releases"
KALDI_PACKAGE_NAME = "kaldi-active-grammar"
DEFAULT_DRAGONFLY_DISTRIBUTION = "dragonfly2"
LOCAL_DRAGONFLY_DISTRIBUTION = "dragonfly"


class WheelResolutionError(RuntimeError):
    pass


def normalize_system(system_name):
    system_name = (system_name or "").lower()
    if system_name.startswith("win"):
        return "windows"
    if system_name.startswith("linux"):
        return "linux"
    if system_name in ("darwin", "mac", "macos", "osx"):
        return "darwin"
    return system_name


def normalize_machine(machine_name):
    machine_name = (machine_name or "").lower()
    aliases = {
        "amd64": "x86_64",
        "x86_64": "x86_64",
        "x64": "x86_64",
        "arm64": "arm64",
        "aarch64": "arm64",
        "x86": "x86",
        "i386": "x86",
        "i686": "x86",
    }
    return aliases.get(machine_name, machine_name)


def parse_wheel_filename(asset_name):
    if not asset_name.endswith(".whl"):
        return None
    parts = asset_name[:-4].split("-")
    if len(parts) < 5:
        return None
    try:
        version = Version(parts[-4])
    except InvalidVersion:
        return None
    py_tag, abi_tag, plat_tag = parts[-3:]
    return {
        "name": asset_name,
        "version": version,
        "py_tags": py_tag.split("."),
        "abi_tags": abi_tag.split("."),
        "plat_tags": plat_tag.split("."),
    }


def python_tags_match(py_tags, version_info):
    major, minor = version_info[:2]
    exact_tags = {"cp{0}{1}".format(major, minor), "py{0}{1}".format(major, minor)}
    for tag in py_tags:
        if tag == "py{0}".format(major):
            return True
        if tag in exact_tags:
            return True
    return False


def python_tag_priority(py_tags, version_info):
    major, minor = version_info[:2]
    if "cp{0}{1}".format(major, minor) in py_tags:
        return 2
    if "py{0}{1}".format(major, minor) in py_tags:
        return 2
    if "py{0}".format(major) in py_tags:
        return 1
    return 0


def platform_tags_match(plat_tags, system_name, machine_name):
    machine_name = normalize_machine(machine_name)
    system_name = normalize_system(system_name)
    if system_name == "windows":
        if machine_name == "x86_64":
            return "win_amd64" in plat_tags
        if machine_name == "x86":
            return "win32" in plat_tags
        if machine_name == "arm64":
            return "win_arm64" in plat_tags
        return False
    if system_name == "linux":
        if machine_name == "x86_64":
            return any(tag.endswith("_x86_64") for tag in plat_tags)
        if machine_name == "arm64":
            return any(tag.endswith("_aarch64") for tag in plat_tags)
        return False
    if system_name == "darwin":
        if machine_name == "x86_64":
            return any(tag.endswith("_x86_64") for tag in plat_tags)
        if machine_name == "arm64":
            return any(tag.endswith("_arm64") for tag in plat_tags)
        return False
    return False


def normalize_releases_payload(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return [payload]
    raise WheelResolutionError("Unexpected release payload returned by GitHub API")


def normalize_kaldi_requirement_specifier(version_specifier):
    if version_specifier is None:
        return SpecifierSet()
    return SpecifierSet(str(version_specifier))


def get_distribution(distribution_name):
    try:
        return metadata.distribution(distribution_name)
    except PackageNotFoundError:
        return None


def distribution_direct_url(distribution):
    try:
        direct_url_text = distribution.read_text("direct_url.json")
    except FileNotFoundError:  # pragma: no cover - importlib.metadata may raise on some Python versions
        return None
    if not direct_url_text:
        return None
    try:
        return json.loads(direct_url_text)
    except (TypeError, ValueError):
        return None


def local_directory_source_url(distribution):
    direct_url = distribution_direct_url(distribution)
    if not isinstance(direct_url, dict):
        return ""
    parsed = urlparse(direct_url.get("url", ""))
    if parsed.scheme != "file":
        return ""
    if not isinstance(direct_url.get("dir_info"), dict):
        return ""
    return direct_url.get("url", "")


def dragonfly_distribution_candidates(distribution_name=None):
    if distribution_name not in (None, "", "auto"):
        return (distribution_name,)
    return (DEFAULT_DRAGONFLY_DISTRIBUTION, LOCAL_DRAGONFLY_DISTRIBUTION)


def detect_local_source_dragonfly_distribution(distribution_name=None):
    explicit_distribution = distribution_name not in (None, "", "auto")

    for candidate_name in dragonfly_distribution_candidates(distribution_name):
        distribution = get_distribution(candidate_name)
        source_url = local_directory_source_url(distribution) if distribution is not None else ""
        if distribution is None or not source_url:
            continue

        warning = ""
        if not explicit_distribution and candidate_name == LOCAL_DRAGONFLY_DISTRIBUTION:
            warning = (
                "Local dragonfly install detected; using its Kaldi compatibility metadata "
                "instead of dragonfly2."
            )

        return {
            "distribution": distribution,
            "distribution_name": candidate_name,
            "source_url": source_url,
            "warning": warning,
        }

    return None


def resolve_dragonfly_distribution(distribution_name=None):
    local_source_distribution = detect_local_source_dragonfly_distribution(distribution_name=distribution_name)
    if local_source_distribution is not None:
        return local_source_distribution

    for candidate_name in dragonfly_distribution_candidates(distribution_name):
        distribution = get_distribution(candidate_name)
        if distribution is not None:
            return {
                "distribution": distribution,
                "distribution_name": candidate_name,
                "source_url": "",
                "warning": "",
            }

    if distribution_name not in (None, "", "auto"):
        raise WheelResolutionError(
            "Installed distribution '{0}' could not be found".format(distribution_name)
        )

    raise WheelResolutionError(
        "Installed distributions '{0}' and '{1}' could not be found".format(
            DEFAULT_DRAGONFLY_DISTRIBUTION,
            LOCAL_DRAGONFLY_DISTRIBUTION,
        )
    )


def discover_kaldi_requirement(distribution_name=None):
    distribution_info = resolve_dragonfly_distribution(distribution_name=distribution_name)
    distribution = distribution_info["distribution"]
    selected_distribution_name = distribution_info["distribution_name"]

    for requirement_text in distribution.requires or []:
        requirement = Requirement(requirement_text)
        if normalize_distribution_name(requirement.name) == KALDI_PACKAGE_NAME:
            return {
                "distribution_name": selected_distribution_name,
                "kaldi_version_spec": str(requirement.specifier),
                "source_url": distribution_info["source_url"],
                "warning": distribution_info["warning"],
            }

    raise WheelResolutionError(
        "Installed distribution '{0}' does not declare a '{1}' dependency".format(
            selected_distribution_name,
            KALDI_PACKAGE_NAME,
        )
    )


def discover_kaldi_requirement_specifier(distribution_name=None):
    return discover_kaldi_requirement(distribution_name=distribution_name)["kaldi_version_spec"]


def normalize_distribution_name(distribution_name):
    return (distribution_name or "").replace("_", "-").lower()


def select_compatible_wheel(assets, system_name=None, machine_name=None, version_info=None, version_specifier=None):
    system_name = normalize_system(system_name or platform.system())
    machine_name = normalize_machine(machine_name or platform.machine())
    version_info = version_info or sys.version_info
    version_specifier = normalize_kaldi_requirement_specifier(version_specifier)

    candidates = []
    for asset in assets:
        parsed = parse_wheel_filename(asset.get("name", ""))
        if not parsed:
            continue
        if parsed["version"] not in version_specifier:
            continue
        if not platform_tags_match(parsed["plat_tags"], system_name, machine_name):
            continue
        if not python_tags_match(parsed["py_tags"], version_info):
            continue
        candidate = dict(asset)
        candidate["_parsed_version"] = parsed["version"]
        candidates.append((parsed["version"], python_tag_priority(parsed["py_tags"], version_info), candidate))

    if not candidates:
        message = "No compatible kaldi-active-grammar wheel found for {0} {1} Python {2}.{3}".format(
            system_name,
            machine_name,
            version_info[0],
            version_info[1],
        )
        if version_specifier:
            message += " matching '{0}'".format(version_specifier)
        raise WheelResolutionError(message)

    candidates.sort(key=lambda item: (item[0], item[1], item[2].get("name", "")), reverse=True)
    selected = candidates[0][2]
    selected.pop("_parsed_version", None)
    return selected


def fetch_releases(releases_url=RELEASES_URL, urlopen_fn=urlopen):
    request = Request(
        releases_url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Caster Kaldi Installer",
        },
    )
    with urlopen_fn(request, timeout=30) as response:
        return normalize_releases_payload(json.load(response))


def release_assets(releases):
    flattened_assets = []
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue
        for asset in release.get("assets", []):
            flattened_asset = dict(asset)
            flattened_asset["tag_name"] = release.get("tag_name", "")
            flattened_assets.append(flattened_asset)
    return flattened_assets


def resolve_latest_wheel(
    releases_url=RELEASES_URL,
    system_name=None,
    machine_name=None,
    version_info=None,
    version_specifier=None,
    distribution_name="auto",
    urlopen_fn=urlopen,
):
    requirement_info = {"distribution_name": "", "source_url": "", "warning": ""}
    if version_specifier is None:
        requirement_info = discover_kaldi_requirement(distribution_name=distribution_name)
        version_specifier = requirement_info["kaldi_version_spec"]

    releases = fetch_releases(releases_url=releases_url, urlopen_fn=urlopen_fn)
    asset = select_compatible_wheel(
        release_assets(releases),
        system_name=system_name,
        machine_name=machine_name,
        version_info=version_info,
        version_specifier=version_specifier,
    )
    result = {
        "tag_name": asset.get("tag_name", ""),
        "asset_name": asset.get("name", ""),
        "browser_download_url": asset.get("browser_download_url", ""),
        "kaldi_version_spec": str(version_specifier),
    }
    if requirement_info["distribution_name"]:
        result["kaldi_requirement_distribution"] = requirement_info["distribution_name"]
    if requirement_info["source_url"]:
        result["local_dragonfly_source_url"] = requirement_info["source_url"]
    if requirement_info["warning"]:
        result["kaldi_requirement_warning"] = requirement_info["warning"]
    return result


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Resolve the latest compatible kaldi-active-grammar wheel.")
    parser.add_argument("--release-url", "--releases-url", dest="releases_url", default=RELEASES_URL)
    parser.add_argument("--system", default=platform.system())
    parser.add_argument("--machine", default=platform.machine())
    parser.add_argument("--python-major", type=int, default=sys.version_info.major)
    parser.add_argument("--python-minor", type=int, default=sys.version_info.minor)
    parser.add_argument("--kaldi-version-spec", default=None)
    parser.add_argument("--dragonfly-distribution", default="auto")
    parser.add_argument("--detect-local-source-dragonfly", action="store_true")
    return parser.parse_args(argv)


def emit_requirement_info(requirement_info):
    if requirement_info.get("distribution_name"):
        print("kaldi_requirement_distribution={0}".format(requirement_info["distribution_name"]))
    if requirement_info.get("source_url"):
        print("local_dragonfly_source_url={0}".format(requirement_info["source_url"]))
    if requirement_info.get("warning"):
        print("kaldi_requirement_warning={0}".format(requirement_info["warning"]))


def main(argv=None):
    args = parse_args(argv)
    if args.detect_local_source_dragonfly:
        distribution_info = detect_local_source_dragonfly_distribution(
            distribution_name=args.dragonfly_distribution
        )
        if distribution_info is not None:
            print("local_dragonfly_distribution={0}".format(distribution_info["distribution_name"]))
            print("local_dragonfly_source_url={0}".format(distribution_info["source_url"]))
        return 0

    requirement_info = None
    try:
        result = resolve_latest_wheel(
            releases_url=args.releases_url,
            system_name=args.system,
            machine_name=args.machine,
            version_info=(args.python_major, args.python_minor),
            version_specifier=args.kaldi_version_spec,
            distribution_name=args.dragonfly_distribution,
        )
    except Exception as exc:
        if args.kaldi_version_spec is None:
            try:
                requirement_info = discover_kaldi_requirement(distribution_name=args.dragonfly_distribution)
            except Exception:  # pragma: no cover - best effort metadata for installer fallback decisions
                requirement_info = None
        if requirement_info:
            emit_requirement_info(requirement_info)
        print(str(exc), file=sys.stderr)
        return 1

    print("tag_name={0}".format(result["tag_name"]))
    print("asset_name={0}".format(result["asset_name"]))
    print("browser_download_url={0}".format(result["browser_download_url"]))
    print("kaldi_version_spec={0}".format(result["kaldi_version_spec"]))
    emit_requirement_info(
        {
            "distribution_name": result.get("kaldi_requirement_distribution", ""),
            "source_url": result.get("local_dragonfly_source_url", ""),
            "warning": result.get("kaldi_requirement_warning", ""),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
