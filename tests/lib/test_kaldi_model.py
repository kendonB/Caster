import io
import json
import shutil
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

from castervoice.lib.kaldi_model import MODEL_DIR_NAME
from castervoice.lib.kaldi_model import MODEL_METADATA_NAME
from castervoice.lib.kaldi_model import USER_LEXICON_NAME
from castervoice.lib.kaldi_model import install_model_archive
from castervoice.lib.kaldi_model import parse_models_markdown
from castervoice.lib.kaldi_model import select_latest_models_by_tier


class _FakeResponse:

    def __init__(self, payload):
        self._buffer = io.BytesIO(payload)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        return self._buffer.read(size)


class _FixedTempDir:

    def __init__(self, path):
        self.path = Path(path)

    def __enter__(self):
        if self.path.exists():
            shutil.rmtree(self.path)
        self.path.mkdir(parents=True)
        return str(self.path)

    def __exit__(self, exc_type, exc, tb):
        if self.path.exists():
            shutil.rmtree(self.path)
        return False


class TestKaldiModel(unittest.TestCase):

    def test_select_latest_models_by_tier_uses_first_current_entry(self):
        markdown = """
* [kaldi_model_daanzu_20211030-mediumlm](https://example.invalid/v3.0.0/kaldi_model_daanzu_20211030-mediumlm.zip) (651 MB)
* [kaldi_model_daanzu_20211030-smalllm](https://example.invalid/v3.0.0/kaldi_model_daanzu_20211030-smalllm.zip) (400 MB)
* [kaldi_model_daanzu_20211030-biglm](https://example.invalid/v3.0.0/kaldi_model_daanzu_20211030-biglm.zip) (1.05 GB)
* [kaldi_model_daanzu_20200905_1ep-mediumlm](https://example.invalid/v1.8.0/kaldi_model_daanzu_20200905_1ep-mediumlm.zip) (651 MB)
"""

        selected = select_latest_models_by_tier(parse_models_markdown(markdown))

        self.assertEqual("kaldi_model_daanzu_20211030-mediumlm", selected["medium"]["name"])
        self.assertEqual("kaldi_model_daanzu_20211030-smalllm", selected["small"]["name"])
        self.assertEqual("kaldi_model_daanzu_20211030-biglm", selected["big"]["name"])

    def test_install_model_archive_preserves_user_lexicon_and_writes_metadata(self):
        archive_bytes = io.BytesIO()
        with zipfile.ZipFile(archive_bytes, "w") as archive:
            archive.writestr("kaldi_model_daanzu_20211030-mediumlm/graph/phones.txt", "phones")
            archive.writestr("kaldi_model_daanzu_20211030-mediumlm/conf/model.conf", "conf")

        model = {
            "name": "kaldi_model_daanzu_20211030-mediumlm",
            "tier": "medium",
            "size": "651 MB",
            "url": "https://example.invalid/kaldi_model_daanzu_20211030-mediumlm.zip",
            "source_release": "v3.0.0",
        }

        tmp_user_root = Path("tmp_user")
        repo_root = tmp_user_root / ("kaldi_model_test_repo_" + uuid.uuid4().hex)
        repo_root.mkdir(parents=True)
        try:
            target_dir = repo_root / MODEL_DIR_NAME
            target_dir.mkdir()
            (target_dir / USER_LEXICON_NAME).write_text("keep-me", encoding="utf-8")
            temp_work_dir = repo_root / "installer-temp"

            with patch("castervoice.lib.kaldi_model.tempfile.TemporaryDirectory", return_value=_FixedTempDir(temp_work_dir)):
                installed_dir = install_model_archive(
                    model,
                    repo_root,
                    urlopen_fn=lambda request, timeout=60: _FakeResponse(archive_bytes.getvalue()),
                )

            self.assertEqual(target_dir, installed_dir)
            self.assertEqual("keep-me", (target_dir / USER_LEXICON_NAME).read_text(encoding="utf-8"))
            self.assertTrue((target_dir / "graph" / "phones.txt").is_file())
            metadata = json.loads((target_dir / MODEL_METADATA_NAME).read_text(encoding="utf-8"))
            self.assertEqual("kaldi_model_daanzu_20211030-mediumlm", metadata["model_name"])
            self.assertEqual("medium", metadata["tier"])
        finally:
            if repo_root.exists():
                shutil.rmtree(repo_root, ignore_errors=True)
            try:
                tmp_user_root.rmdir()
            except OSError:
                pass
