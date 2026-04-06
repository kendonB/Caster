from unittest import TestCase
from unittest.mock import patch

from castervoice.lib import settings


class TestSettings(TestCase):

    def setUp(self):
        self.addCleanup(self._reset_settings_state)
        self._reset_settings_state()

    def _reset_settings_state(self):
        settings.SETTINGS = None
        settings.SYSTEM_INFORMATION = None
        settings._BASE_PATH = None
        settings._USER_DIR = None
        settings._SETTINGS_PATH = None

    def test_runtime_python_paths_removed_from_defaults(self):
        with patch.object(settings, "_BASE_PATH", "C:/Caster/castervoice"), \
                patch.object(settings, "_USER_DIR", "C:/Users/Main/AppData/Local/caster"), \
                patch.object(settings, "SYSTEM_INFORMATION", {"hidden console binary": "C:/Python/pythonw.exe"}), \
                patch.object(settings, "_validate_engine_path", return_value=""), \
                patch("castervoice.lib.settings.os.path.isfile", return_value=False):
            defaults = settings._get_defaults()

        self.assertNotIn("WSR_RUNTIME_PYTHON_PATH", defaults["paths"])
        self.assertNotIn("KALDI_RUNTIME_PYTHON_PATH", defaults["paths"])
        self.assertNotIn("PYTHONW", defaults["paths"])

    def test_runtime_hidden_console_binary_prefers_active_runtime(self):
        runtime_pythonw = "C:/Caster/.venv/Scripts/pythonw.exe"
        settings.SYSTEM_INFORMATION = {"hidden console binary": runtime_pythonw}
        settings.SETTINGS = {"paths": {"PYTHONW": "C:/Legacy/pythonw.exe"}}

        with patch("castervoice.lib.settings.os.path.isfile", side_effect=lambda path: path == runtime_pythonw):
            self.assertEqual(runtime_pythonw, settings.runtime_hidden_console_binary())

    def test_runtime_hidden_console_binary_ignores_configured_fallback(self):
        runtime_pythonw = "C:/Caster/.venv/Scripts/pythonw.exe"
        settings.SETTINGS = {"paths": {"PYTHONW": "C:/Legacy/pythonw.exe"}}

        with patch("castervoice.lib.settings._hidden_console_binary_for", return_value=runtime_pythonw), \
                patch("castervoice.lib.settings.os.path.isfile", return_value=False):
            self.assertEqual(runtime_pythonw, settings.runtime_hidden_console_binary())

    def test_detected_user_dir_prefers_environment_override(self):
        with patch("castervoice.lib.settings.os.getenv", return_value="C:/Users/Main/CasterData"), \
                patch("castervoice.lib.settings.user_data_dir") as user_data_dir:
            self.assertEqual("C:/Users/Main/CasterData", settings.detected_user_dir())

        user_data_dir.assert_not_called()
