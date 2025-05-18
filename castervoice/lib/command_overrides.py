from castervoice.lib import settings
from castervoice.lib.config.config_toml import TomlConfig


class CommandOverrides(TomlConfig):
    """Persist command override specifications."""

    _ENABLED = "enabled"
    _SPEC = "spec"

    def __init__(self):
        super(CommandOverrides, self).__init__(
            settings.settings(["paths", "COMMAND_OVERRIDES_PATH"]))
        self.load()

    def is_enabled(self, rule_name):
        entry = self._config.get(rule_name)
        return bool(entry.get(CommandOverrides._ENABLED)) if entry else False

    def get_spec(self, rule_name):
        entry = self._config.get(rule_name, {})
        return entry.get(CommandOverrides._SPEC)

    def set_override(self, rule_name, enabled, spec):
        self._config[rule_name] = {
            CommandOverrides._ENABLED: bool(enabled),
            CommandOverrides._SPEC: spec,
        }
        self.save()

    def merge_override(self, rule_name, enabled=None, spec=None):
        entry = self._config.get(rule_name, {})
        if enabled is not None:
            entry[CommandOverrides._ENABLED] = bool(enabled)
        if spec is not None:
            entry[CommandOverrides._SPEC] = spec
        self._config[rule_name] = entry
        self.save()

    def __contains__(self, rule_name):
        return rule_name in self._config
