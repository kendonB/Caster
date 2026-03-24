import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


MODELS_MD_URL = "https://raw.githubusercontent.com/daanzu/kaldi-active-grammar/master/docs/models.md"
MODEL_DIR_NAME = "kaldi_model"
MODEL_METADATA_NAME = ".caster-model.json"
USER_LEXICON_NAME = "user_lexicon.txt"

TIER_LABELS = {
    "medium": "Balanced (Recommended)",
    "small": "Smaller download",
    "big": "Largest model",
}


class ModelResolutionError(RuntimeError):
    pass


def fetch_models_markdown(models_url=MODELS_MD_URL, urlopen_fn=urlopen):
    request = Request(
        models_url,
        headers={
            "User-Agent": "Caster Kaldi Installer",
        },
    )
    with urlopen_fn(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_models_markdown(markdown_text):
    models = []
    for index, line in enumerate(markdown_text.splitlines()):
        match = re.match(r'^\s*\*\s+\[(kaldi_model_[^\]]+)\]\((https://[^)]+\.zip)\)\s+\(([^)]+)\)', line)
        if not match:
            continue
        model_name, url, size = match.groups()
        tier_match = re.search(r'-(smalllm|mediumlm|biglm)$', model_name)
        if not tier_match:
            continue
        source_release = ""
        release_match = re.search(r"/download/([^/]+)/", url)
        if release_match:
            source_release = release_match.group(1)
        date_match = re.search(r"_(\d{8})", model_name)
        models.append(
            {
                "index": index,
                "name": model_name,
                "tier": tier_match.group(1).replace("lm", ""),
                "size": size,
                "url": url,
                "source_release": source_release,
                "date": date_match.group(1) if date_match else "",
            }
        )
    return models


def select_latest_models_by_tier(models):
    selected = {}
    for model in models:
        selected.setdefault(model["tier"], model)
    return selected


def prompt_for_choice(model_options, input_fn=input, output_fn=print):
    available = [tier for tier in ("medium", "small", "big") if tier in model_options]
    if not available:
        raise ModelResolutionError("No Kaldi models were available from the upstream models list.")

    output_fn("Available Kaldi models:")
    for tier in available:
        model = model_options[tier]
        output_fn(
            "  {0}: {1} ({2}, source {3})".format(
                TIER_LABELS[tier],
                model["name"],
                model["size"],
                model["source_release"] or "unknown release",
            )
        )

    prompt = "Select model [M]edium, [S]mall, [B]ig, or [N]one: "
    while True:
        selection = input_fn(prompt).strip().lower()
        if not selection:
            return "medium" if "medium" in model_options else available[0]
        if selection in ("n", "no", "none", "skip"):
            return None
        if selection in ("m", "medium") and "medium" in model_options:
            return "medium"
        if selection in ("s", "small") and "small" in model_options:
            return "small"
        if selection in ("b", "big") and "big" in model_options:
            return "big"
        output_fn("Please choose medium, small, big, or none.")


def download_to_path(url, destination, urlopen_fn=urlopen):
    request = Request(
        url,
        headers={
            "User-Agent": "Caster Kaldi Installer",
        },
    )
    with urlopen_fn(request, timeout=60) as response, destination.open("wb") as output_file:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output_file.write(chunk)


def find_model_directory(extract_root):
    direct = extract_root / MODEL_DIR_NAME
    if direct.is_dir():
        return direct

    prefixed_dirs = [path for path in extract_root.iterdir() if path.is_dir() and path.name.startswith(MODEL_DIR_NAME)]
    if len(prefixed_dirs) == 1:
        return prefixed_dirs[0]

    nested = [path for path in extract_root.rglob(MODEL_DIR_NAME) if path.is_dir()]
    if len(nested) == 1:
        return nested[0]

    raise ModelResolutionError("Could not determine the Kaldi model directory from the downloaded archive.")


def write_model_metadata(target_dir, model):
    metadata = {
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "model_name": model["name"],
        "tier": model["tier"],
        "size": model["size"],
        "source_release": model["source_release"],
        "url": model["url"],
    }
    metadata_path = target_dir / MODEL_METADATA_NAME
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def install_model_archive(model, repo_root, urlopen_fn=urlopen, temp_dir_parent=None):
    repo_root = Path(repo_root)
    target_dir = repo_root / MODEL_DIR_NAME
    existing_lexicon = None
    lexicon_path = target_dir / USER_LEXICON_NAME
    if lexicon_path.exists():
        existing_lexicon = lexicon_path.read_bytes()

    with tempfile.TemporaryDirectory(prefix="caster_kaldi_model_", dir=temp_dir_parent) as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        archive_path = temp_dir / "model.zip"
        extract_root = temp_dir / "extract"
        extract_root.mkdir()

        download_to_path(model["url"], archive_path, urlopen_fn=urlopen_fn)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_root)

        source_dir = find_model_directory(extract_root)
        staged_target = temp_dir / MODEL_DIR_NAME
        shutil.copytree(source_dir, staged_target)

        if existing_lexicon is not None:
            (staged_target / USER_LEXICON_NAME).write_bytes(existing_lexicon)

        write_model_metadata(staged_target, model)

        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.move(str(staged_target), str(target_dir))

    return target_dir


def resolve_model_options(models_url=MODELS_MD_URL, urlopen_fn=urlopen):
    markdown = fetch_models_markdown(models_url=models_url, urlopen_fn=urlopen_fn)
    models = parse_models_markdown(markdown)
    return select_latest_models_by_tier(models)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Download and install a Kaldi speech model for Caster.")
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--models-url", default=MODELS_MD_URL)
    parser.add_argument("--choice", choices=["medium", "small", "big", "skip"], default=None)
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        model_options = resolve_model_options(models_url=args.models_url)
        choice = args.choice or os.environ.get("CASTER_KALDI_MODEL")
        if choice:
            choice = choice.strip().lower()
            if choice == "skip":
                print("Skipping Kaldi model download.")
                return 2
            if choice not in model_options:
                raise ModelResolutionError("Requested Kaldi model '{0}' is not available.".format(choice))
        else:
            choice = prompt_for_choice(model_options)
            if choice is None:
                print("Skipping Kaldi model download.")
                return 2

        model = model_options[choice]
        print("Downloading {0}: {1} ({2})".format(TIER_LABELS.get(choice, choice), model["name"], model["size"]))
        target_dir = install_model_archive(model, args.repo_root)
        print("Installed Kaldi model to {0}".format(target_dir))
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
