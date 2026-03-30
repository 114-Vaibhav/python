# Original code kept for reference.
# class DarkMode:
#     def __init__(self):
#         self.name = "dark-mode"
#         self.version = "1.0.0"
#         self.description = "Dark Mode Theme"
#
#     def Run(self):
#         print("DarkMode Running ...")
#         print("Version: " + self.version)
#         print("DarkMode Finished")

from plugin_api import PluginBase, SandboxContext, register_plugin

@register_plugin
class DarkModeThemePlugin(PluginBase):
    plugin_id = "dark-mode-theme"
    version = "1.3.2"
    description = 'Theme provider for "dark-mode"'
    dependencies = ()
    plugin_type = "third-party"

    def activate(self, context: SandboxContext) -> str:
        context.register_theme("dark-mode", 'theme "dark-mode"')
        return 'registered: theme "dark-mode"'

    def deactivate(self, context: SandboxContext) -> str:
        context.themes.pop("dark-mode", None)
        return 'unregistered: theme "dark-mode"'
