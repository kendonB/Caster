from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import patch

from castervoice.lib.merge.ccrmerging2.hooks.events.activation_event import RuleActivationEvent
from castervoice.lib.merge.ccrmerging2.hooks.standard_hooks import format_hook


class TestFormattingHook(TestCase):

    def setUp(self):
        self.hook = format_hook.FormattingHook()
        self.format_mock = Mock()
        self.secondary_format_mock = Mock()
        self.settings = {
            "formats": {
                "ExampleRule": {
                    "text_format": [1, 2],
                    "secondary_format": [3, 4],
                }
            }
        }

        self.settings_patcher = patch.object(format_hook.settings, "SETTINGS", self.settings)
        self.text_format_patcher = patch.object(format_hook.textformat, "format", self.format_mock)
        self.secondary_format_patcher = patch.object(format_hook.textformat, "secondary_format", self.secondary_format_mock)

        self.settings_patcher.start()
        self.text_format_patcher.start()
        self.secondary_format_patcher.start()

        self.addCleanup(self.settings_patcher.stop)
        self.addCleanup(self.text_format_patcher.stop)
        self.addCleanup(self.secondary_format_patcher.stop)

    def test_run_applies_format_from_activation_event(self):
        self.hook.run(RuleActivationEvent("ExampleRule", True))

        self.format_mock.set_text_format.assert_called_once_with(1, 2)
        self.secondary_format_mock.set_text_format.assert_called_once_with(3, 4)
        self.format_mock.clear_text_format.assert_not_called()
        self.secondary_format_mock.clear_text_format.assert_not_called()

    def test_run_clears_formats_when_rule_deactivates(self):
        self.hook.run(RuleActivationEvent("ExampleRule", False))

        self.format_mock.clear_text_format.assert_called_once_with()
        self.secondary_format_mock.clear_text_format.assert_called_once_with()
        self.format_mock.set_text_format.assert_not_called()
        self.secondary_format_mock.set_text_format.assert_not_called()
