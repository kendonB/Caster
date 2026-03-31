import contextlib
import io
import json
import unittest
from importlib.metadata import PackageNotFoundError
from unittest import mock

from castervoice.lib.kaldi_wheel import discover_kaldi_requirement
from castervoice.lib.kaldi_wheel import discover_kaldi_requirement_specifier
from castervoice.lib.kaldi_wheel import main
from castervoice.lib.kaldi_wheel import WheelResolutionError
from castervoice.lib.kaldi_wheel import resolve_latest_wheel
from castervoice.lib.kaldi_wheel import select_compatible_wheel


class _FakeResponse:

    def __init__(self, payload):
        self._buffer = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self._buffer

    def __exit__(self, exc_type, exc, tb):
        return False


class TestKaldiWheel(unittest.TestCase):

    def test_discover_kaldi_requirement_specifier_reads_dragonfly_metadata(self):
        distribution = mock.Mock()
        distribution.requires = [
            'kaldi-active-grammar (~=3.1.0) ; extra == "kaldi"',
            "sounddevice (==0.3.*) ; extra == 'kaldi'",
        ]

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", return_value=distribution):
            self.assertEqual("~=3.1.0", discover_kaldi_requirement_specifier())

    def test_discover_kaldi_requirement_prefers_local_dragonfly_source_install(self):
        local_distribution = mock.Mock()
        local_distribution.requires = [
            'kaldi-active-grammar (~=3.2.0) ; extra == "kaldi"',
        ]
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", "dir_info": {"editable": True}}
        )

        packaged_distribution = mock.Mock()
        packaged_distribution.requires = [
            'kaldi-active-grammar (~=3.1.0) ; extra == "kaldi"',
        ]
        packaged_distribution.read_text.return_value = None

        def fake_distribution(name):
            if name == "dragonfly":
                return local_distribution
            if name == "dragonfly2":
                return packaged_distribution
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            result = discover_kaldi_requirement()

        self.assertEqual("dragonfly", result["distribution_name"])
        self.assertEqual("~=3.2.0", result["kaldi_version_spec"])
        self.assertEqual("file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", result["source_url"])
        self.assertIn("Local dragonfly install detected", result["warning"])

    def test_discover_kaldi_requirement_prefers_local_dragonfly2_source_install(self):
        default_distribution = mock.Mock()
        default_distribution.requires = [
            'kaldi-active-grammar (~=3.4.0) ; extra == "kaldi"',
        ]
        default_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly2", "dir_info": {"editable": True}}
        )

        legacy_distribution = mock.Mock()
        legacy_distribution.requires = [
            'kaldi-active-grammar (~=3.2.0) ; extra == "kaldi"',
        ]
        legacy_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", "dir_info": {"editable": True}}
        )

        def fake_distribution(name):
            if name == "dragonfly2":
                return default_distribution
            if name == "dragonfly":
                return legacy_distribution
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution) as lookup:
            result = discover_kaldi_requirement()

        self.assertEqual("dragonfly2", result["distribution_name"])
        self.assertEqual("~=3.4.0", result["kaldi_version_spec"])
        self.assertEqual("file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly2", result["source_url"])
        self.assertEqual("", result["warning"])
        self.assertEqual([mock.call("dragonfly2")], lookup.call_args_list)

    def test_discover_kaldi_requirement_does_not_treat_local_dragonfly_archive_as_source_install(self):
        local_distribution = mock.Mock()
        local_distribution.requires = [
            'kaldi-active-grammar (~=3.2.0) ; extra == "kaldi"',
        ]
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file:///C:/tmp/dragonfly-1.0.0.whl", "archive_info": {"hash": "sha256=abc"}}
        )

        packaged_distribution = mock.Mock()
        packaged_distribution.requires = [
            'kaldi-active-grammar (~=3.1.0) ; extra == "kaldi"',
        ]
        packaged_distribution.read_text.return_value = None

        def fake_distribution(name):
            if name == "dragonfly":
                return local_distribution
            if name == "dragonfly2":
                return packaged_distribution
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            result = discover_kaldi_requirement()

        self.assertEqual("dragonfly2", result["distribution_name"])
        self.assertEqual("~=3.1.0", result["kaldi_version_spec"])
        self.assertEqual("", result["source_url"])
        self.assertEqual("", result["warning"])

    def test_select_compatible_wheel_picks_windows_asset(self):
        assets = [
            {"name": "kaldi_active_grammar-3.2.0-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.whl"},
            {"name": "kaldi_active_grammar-3.2.0-py3-none-macosx_10_9_x86_64.whl"},
            {"name": "kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl"},
        ]

        asset = select_compatible_wheel(
            assets,
            system_name="Windows",
            machine_name="AMD64",
            version_info=(3, 12),
        )

        self.assertEqual("kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl", asset["name"])

    def test_select_compatible_wheel_prefers_exact_python_tag(self):
        assets = [
            {"name": "kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl"},
            {"name": "kaldi_active_grammar-3.2.0-cp312-none-win_amd64.whl"},
        ]

        asset = select_compatible_wheel(
            assets,
            system_name="Windows",
            machine_name="AMD64",
            version_info=(3, 12),
        )

        self.assertEqual("kaldi_active_grammar-3.2.0-cp312-none-win_amd64.whl", asset["name"])

    def test_select_compatible_wheel_raises_without_supported_asset(self):
        assets = [
            {"name": "kaldi_active_grammar-3.2.0-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.whl"},
        ]

        with self.assertRaises(WheelResolutionError):
            select_compatible_wheel(
                assets,
                system_name="Windows",
                machine_name="AMD64",
                version_info=(3, 12),
            )

    def test_resolve_latest_wheel_returns_release_metadata(self):
        release = {
            "tag_name": "v3.2.0",
            "assets": [
                {
                    "name": "kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                    "browser_download_url": "https://example.invalid/kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                },
            ],
        }

        result = resolve_latest_wheel(
            system_name="Windows",
            machine_name="AMD64",
            version_info=(3, 12),
            version_specifier="~=3.2.0",
            urlopen_fn=lambda request, timeout=30: _FakeResponse(release),
        )

        self.assertEqual("v3.2.0", result["tag_name"])
        self.assertEqual("kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl", result["asset_name"])
        self.assertEqual(
            "https://example.invalid/kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
            result["browser_download_url"],
        )
        self.assertEqual("~=3.2.0", result["kaldi_version_spec"])

    def test_resolve_latest_wheel_returns_local_dragonfly_warning_metadata(self):
        release = {
            "tag_name": "v3.2.0",
            "assets": [
                {
                    "name": "kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                    "browser_download_url": "https://example.invalid/kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                },
            ],
        }
        local_distribution = mock.Mock()
        local_distribution.requires = ['kaldi-active-grammar (~=3.2.0) ; extra == "kaldi"']
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", "dir_info": {"editable": True}}
        )

        def fake_distribution(name):
            if name == "dragonfly":
                return local_distribution
            if name == "dragonfly2":
                raise PackageNotFoundError
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            result = resolve_latest_wheel(
                system_name="Windows",
                machine_name="AMD64",
                version_info=(3, 12),
                urlopen_fn=lambda request, timeout=30: _FakeResponse(release),
            )

        self.assertEqual("dragonfly", result["kaldi_requirement_distribution"])
        self.assertEqual("file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", result["local_dragonfly_source_url"])
        self.assertIn("Local dragonfly install detected", result["kaldi_requirement_warning"])

    def test_resolve_latest_wheel_uses_latest_matching_release(self):
        releases = [
            {
                "tag_name": "v3.2.0",
                "assets": [
                    {
                        "name": "kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                        "browser_download_url": "https://example.invalid/kaldi_active_grammar-3.2.0-py3-none-win_amd64.whl",
                    },
                ],
            },
            {
                "tag_name": "v3.1.0",
                "assets": [
                    {
                        "name": "kaldi_active_grammar-3.1.0-py3-none-win_amd64.whl",
                        "browser_download_url": "https://example.invalid/kaldi_active_grammar-3.1.0-py3-none-win_amd64.whl",
                    },
                ],
            },
        ]

        result = resolve_latest_wheel(
            system_name="Windows",
            machine_name="AMD64",
            version_info=(3, 12),
            version_specifier="~=3.1.0",
            urlopen_fn=lambda request, timeout=30: _FakeResponse(releases),
        )

        self.assertEqual("v3.1.0", result["tag_name"])
        self.assertEqual("kaldi_active_grammar-3.1.0-py3-none-win_amd64.whl", result["asset_name"])

    def test_main_emits_local_dragonfly_metadata_when_resolution_fails(self):
        requirement_info = {
            "distribution_name": "dragonfly",
            "kaldi_version_spec": "~=3.2.0",
            "source_url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly",
            "warning": "Local dragonfly install detected; using its Kaldi compatibility metadata instead of dragonfly2.",
        }
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()

        with mock.patch(
            "castervoice.lib.kaldi_wheel.resolve_latest_wheel",
            side_effect=WheelResolutionError("GitHub lookup failed"),
        ):
            with mock.patch(
                "castervoice.lib.kaldi_wheel.discover_kaldi_requirement",
                return_value=requirement_info,
            ):
                with contextlib.redirect_stdout(stdout_buffer):
                    with contextlib.redirect_stderr(stderr_buffer):
                        exit_code = main([])

        self.assertEqual(1, exit_code)
        self.assertIn("kaldi_requirement_distribution=dragonfly", stdout_buffer.getvalue())
        self.assertIn(
            "local_dragonfly_source_url=file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly",
            stdout_buffer.getvalue(),
        )
        self.assertIn(
            "kaldi_requirement_warning=Local dragonfly install detected; using its Kaldi compatibility metadata instead of dragonfly2.",
            stdout_buffer.getvalue(),
        )
        self.assertIn("GitHub lookup failed", stderr_buffer.getvalue())

    def test_main_detect_local_source_dragonfly_emits_source_url_for_dragonfly2(self):
        local_distribution = mock.Mock()
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly2", "dir_info": {"editable": True}}
        )
        stdout_buffer = io.StringIO()

        def fake_distribution(name):
            if name == "dragonfly2":
                return local_distribution
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            with contextlib.redirect_stdout(stdout_buffer):
                exit_code = main(["--detect-local-source-dragonfly"])

        self.assertEqual(0, exit_code)
        self.assertEqual(
            "local_dragonfly_distribution=dragonfly2\n"
            "local_dragonfly_source_url=file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly2\n",
            stdout_buffer.getvalue(),
        )

    def test_main_detect_local_source_dragonfly_emits_source_url_for_legacy_dragonfly(self):
        local_distribution = mock.Mock()
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly", "dir_info": {"editable": True}}
        )
        stdout_buffer = io.StringIO()

        def fake_distribution(name):
            if name == "dragonfly2":
                raise PackageNotFoundError(name)
            if name == "dragonfly":
                return local_distribution
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            with contextlib.redirect_stdout(stdout_buffer):
                exit_code = main(["--detect-local-source-dragonfly"])

        self.assertEqual(0, exit_code)
        self.assertEqual(
            "local_dragonfly_distribution=dragonfly\n"
            "local_dragonfly_source_url=file://wsl.localhost/Ubuntu/home/tester/projects/dragonfly\n",
            stdout_buffer.getvalue(),
        )

    def test_main_detect_local_source_dragonfly_ignores_local_archive_install(self):
        local_distribution = mock.Mock()
        local_distribution.read_text.return_value = json.dumps(
            {"url": "file:///C:/tmp/dragonfly-1.0.0.whl", "archive_info": {"hash": "sha256=abc"}}
        )
        stdout_buffer = io.StringIO()

        def fake_distribution(name):
            if name == "dragonfly2":
                return local_distribution
            if name == "dragonfly":
                raise PackageNotFoundError(name)
            raise AssertionError("Unexpected distribution lookup: {0}".format(name))

        with mock.patch("castervoice.lib.kaldi_wheel.metadata.distribution", side_effect=fake_distribution):
            with contextlib.redirect_stdout(stdout_buffer):
                exit_code = main(["--detect-local-source-dragonfly"])

        self.assertEqual(0, exit_code)
        self.assertEqual("", stdout_buffer.getvalue())
