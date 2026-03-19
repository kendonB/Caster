import importlib
import sys
import types
import unittest
from unittest.mock import mock_open, patch

from castervoice.lib.ctrl import dependencies


class TestDependencies(unittest.TestCase):

    def test_dep_missing_uses_full_requirement_spec(self):
        requirements = 'PySide2>=5.14;platform_system!="Windows"\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies.pkg_resources.require") as require_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        dependencies.dep_missing()

        require_mock.assert_called_once_with('PySide2>=5.14;platform_system!="Windows"')
        out_mock.assert_not_called()
        sleep_mock.assert_not_called()

    def test_dep_missing_reports_missing_dep_without_marker_in_hint(self):
        requirements = 'missing_dep>=1.0; platform_system=="Windows"\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies.pkg_resources.require") as require_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        require_mock.side_effect = dependencies.DistributionNotFound("missing_dep", [])
                        dependencies.dep_missing()

        out_mock.assert_called_once()
        warning_message = out_mock.call_args[0][0]
        self.assertIn('python -m pip install "missing_dep>=1.0"', warning_message)
        self.assertNotIn("platform_system", warning_message)
        sleep_mock.assert_called_once_with(10)

    def test_dep_missing_quotes_multiple_missing_requirements_in_hint(self):
        requirements = (
            'missing_dep>=1.0\n'
            'other_dep==2.0; platform_system=="Windows"\n'
        )
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies.pkg_resources.require") as require_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        require_mock.side_effect = [
                            dependencies.DistributionNotFound("missing_dep", []),
                            dependencies.DistributionNotFound("other_dep", []),
                        ]
                        dependencies.dep_missing()

        out_mock.assert_called_once()
        warning_message = out_mock.call_args[0][0]
        self.assertIn('python -m pip install "missing_dep>=1.0" "other_dep==2.0"', warning_message)
        self.assertNotIn("platform_system", warning_message)
        sleep_mock.assert_called_once_with(10)

    def test_dep_missing_skips_blank_and_comment_lines(self):
        requirements = '\n# optional dependency\nsix\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies.pkg_resources.require") as require_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        dependencies.dep_missing()

        require_mock.assert_called_once_with("six")
        out_mock.assert_not_called()
        sleep_mock.assert_not_called()

    def test_import_works_with_incomplete_pkg_resources_module(self):
        fake_pkg_resources = types.SimpleNamespace(require=lambda _requirement: None)
        original_module = dependencies
        try:
            with patch.dict(sys.modules, {"pkg_resources": fake_pkg_resources}):
                reloaded = importlib.reload(original_module)
                self.assertTrue(hasattr(reloaded, "DistributionNotFound"))
                self.assertTrue(hasattr(reloaded, "VersionConflict"))
                self.assertTrue(callable(reloaded.pkg_resources.require))
        finally:
            importlib.reload(original_module)

    def test_fallback_raises_version_conflict_for_invalid_installed_version(self):
        fake_pkg_resources = types.SimpleNamespace(require=lambda _requirement: None)
        original_module = dependencies
        try:
            with patch.dict(sys.modules, {"pkg_resources": fake_pkg_resources}):
                reloaded = importlib.reload(original_module)
                with patch.object(reloaded, "_installed_version", return_value="not_a_pep440_version"):
                    with self.assertRaises(reloaded.VersionConflict):
                        reloaded._require_fallback("example_pkg>=1.0")
        finally:
            importlib.reload(original_module)

    def test_fallback_checks_requested_extra_dependencies(self):
        fake_pkg_resources = types.SimpleNamespace(require=lambda _requirement: None)
        original_module = dependencies
        try:
            with patch.dict(sys.modules, {"pkg_resources": fake_pkg_resources}):
                reloaded = importlib.reload(original_module)

                def fake_distribution(name):
                    if name == "dragonfly2":
                        return types.SimpleNamespace(
                            version="0.34.0",
                            requires=['kaldi-active-grammar; extra == "kaldi"'],
                        )
                    raise reloaded.metadata.PackageNotFoundError

                with patch.object(reloaded.metadata, "distribution", side_effect=fake_distribution):
                    with self.assertRaises(reloaded.DistributionNotFound):
                        reloaded._require_fallback("dragonfly2[kaldi]>=0.34.0")
        finally:
            importlib.reload(original_module)

    def test_fallback_accepts_installed_requested_extra_dependencies(self):
        fake_pkg_resources = types.SimpleNamespace(require=lambda _requirement: None)
        original_module = dependencies
        try:
            with patch.dict(sys.modules, {"pkg_resources": fake_pkg_resources}):
                reloaded = importlib.reload(original_module)

                def fake_distribution(name):
                    if name == "dragonfly2":
                        return types.SimpleNamespace(
                            version="0.34.0",
                            requires=['kaldi-active-grammar; extra == "kaldi"'],
                        )
                    if name == "kaldi-active-grammar":
                        return types.SimpleNamespace(version="1.0", requires=[])
                    raise reloaded.metadata.PackageNotFoundError

                with patch.object(reloaded.metadata, "distribution", side_effect=fake_distribution):
                    reloaded._require_fallback("dragonfly2[kaldi]>=0.34.0")
        finally:
            importlib.reload(original_module)
