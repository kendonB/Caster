import types
import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import mock_open, patch

from castervoice.lib.ctrl import dependencies


class TestDependencies(unittest.TestCase):

    def test_dep_missing_passes_full_requirement_spec_to_checker(self):
        requirements = 'PySide2>=5.14;platform_system!="Windows"\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies._requirement_is_installed", return_value=True) as installed_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        dependencies.dep_missing()

        installed_mock.assert_called_once_with('PySide2>=5.14;platform_system!="Windows"')
        out_mock.assert_not_called()
        sleep_mock.assert_not_called()

    def test_dep_missing_reports_missing_dep_without_marker_in_hint(self):
        requirements = 'missing_dep>=1.0; platform_system=="Windows"\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies._requirement_is_installed", return_value=False):
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
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
            with patch("castervoice.lib.ctrl.dependencies._requirement_is_installed", side_effect=[False, False]):
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        dependencies.dep_missing()

        out_mock.assert_called_once()
        warning_message = out_mock.call_args[0][0]
        self.assertIn('python -m pip install "missing_dep>=1.0" "other_dep==2.0"', warning_message)
        self.assertNotIn("platform_system", warning_message)
        sleep_mock.assert_called_once_with(10)

    def test_dep_missing_skips_blank_and_comment_lines(self):
        requirements = '\n# optional dependency\nsix\n'
        with patch("builtins.open", mock_open(read_data=requirements)):
            with patch("castervoice.lib.ctrl.dependencies._requirement_is_installed", return_value=True) as installed_mock:
                with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                    with patch("castervoice.lib.ctrl.dependencies.time.sleep") as sleep_mock:
                        dependencies.dep_missing()

        installed_mock.assert_called_once_with("six")
        out_mock.assert_not_called()
        sleep_mock.assert_not_called()

    def test_requirement_is_installed_skips_requirements_with_false_markers(self):
        requirement = 'PySide2>=5.14; platform_system == "Darwin"'
        with patch("castervoice.lib.ctrl.dependencies.default_environment", return_value={"platform_system": "Windows"}):
            with patch("castervoice.lib.ctrl.dependencies.metadata.distribution") as distribution_mock:
                self.assertTrue(dependencies._requirement_is_installed(requirement))

        distribution_mock.assert_not_called()

    def test_requirement_is_installed_rejects_invalid_installed_version(self):
        installed = types.SimpleNamespace(version="not_a_pep440_version", requires=[])
        with patch("castervoice.lib.ctrl.dependencies._installed_distribution", return_value=installed):
            self.assertFalse(dependencies._requirement_is_installed("example_pkg>=1.0"))

    def test_requirement_is_installed_detects_missing_plain_dependency_chain(self):
        def fake_distribution(name):
            if name == "dragonfly2":
                return types.SimpleNamespace(
                    version="0.34.0",
                    requires=["comtypes>=1.1"],
                )
            raise PackageNotFoundError(name)

        with patch("castervoice.lib.ctrl.dependencies.metadata.distribution", side_effect=fake_distribution):
            self.assertFalse(dependencies._requirement_is_installed("dragonfly2>=0.34.0"))

    def test_requirement_is_installed_accepts_installed_plain_dependency_chain(self):
        def fake_distribution(name):
            if name == "dragonfly2":
                return types.SimpleNamespace(
                    version="0.34.0",
                    requires=["comtypes>=1.1"],
                )
            if name == "comtypes":
                return types.SimpleNamespace(version="1.2.0", requires=[])
            raise PackageNotFoundError(name)

        with patch("castervoice.lib.ctrl.dependencies.metadata.distribution", side_effect=fake_distribution):
            self.assertTrue(dependencies._requirement_is_installed("dragonfly2>=0.34.0"))

    def test_requirement_is_installed_detects_missing_requested_extra_dependencies(self):
        def fake_distribution(name):
            if name == "dragonfly2":
                return types.SimpleNamespace(
                    version="0.34.0",
                    requires=['kaldi-active-grammar; extra == "kaldi"'],
                )
            raise PackageNotFoundError(name)

        with patch("castervoice.lib.ctrl.dependencies.metadata.distribution", side_effect=fake_distribution):
            self.assertFalse(dependencies._requirement_is_installed("dragonfly2[kaldi]>=0.34.0"))

    def test_requirement_is_installed_accepts_installed_requested_extra_dependencies(self):
        def fake_distribution(name):
            if name == "dragonfly2":
                return types.SimpleNamespace(
                    version="0.34.0",
                    requires=['kaldi-active-grammar; extra == "kaldi"'],
                )
            if name == "kaldi-active-grammar":
                return types.SimpleNamespace(version="1.0", requires=[])
            raise PackageNotFoundError(name)

        with patch("castervoice.lib.ctrl.dependencies.metadata.distribution", side_effect=fake_distribution):
            self.assertTrue(dependencies._requirement_is_installed("dragonfly2[kaldi]>=0.34.0"))

    def test_requirement_is_installed_accepts_dragonfly_alias_for_dragonfly2(self):
        def fake_distribution(name):
            if name == "dragonfly2":
                raise PackageNotFoundError(name)
            if name == "dragonfly":
                return types.SimpleNamespace(version="1.0.0", requires=[])
            raise PackageNotFoundError(name)

        with patch("castervoice.lib.ctrl.dependencies.metadata.distribution", side_effect=fake_distribution):
            self.assertTrue(dependencies._requirement_is_installed("dragonfly2>=0.34.0"))

    def test_dep_min_version_accepts_dragonfly_alias_for_dragonfly2(self):
        with patch(
            "castervoice.lib.ctrl.dependencies._installed_distribution",
            return_value=types.SimpleNamespace(version="1.0.0"),
        ):
            with patch("castervoice.lib.ctrl.dependencies.printer.out") as out_mock:
                dependencies.dep_min_version()

        out_mock.assert_not_called()
