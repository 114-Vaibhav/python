# Original code kept for reference.
# from markdownParser import MarkdownParser
#
# class RSSFeed(MarkdownParser):
#     def __init__(self):
#         self.name = "rss-feed"
#         self.version = "1.0.0"
#         self.description = "RSS Feed"
#
#     def Run(self):
#         print("Loading Depencies...")
#         self.MarkdownRun()
#         print("RSS Feed Running ...")
#         print("Version: " + self.version)
#         print("RSS Feed Finished")

from plugin_api import PluginBase, SandboxContext, register_plugin

@register_plugin
class RSSFeedPlugin(PluginBase):
    plugin_id = "rss-feed"
    version = "1.0.0"
    description = "RSS feed generator"
    dependencies = ("markdown-parser",)
    plugin_type = "third-party"

    def activate(self, context: SandboxContext) -> str:
        if ".md" not in context.output_formats:
            raise RuntimeError("markdown-parser must activate before rss-feed")
        context.register_command("generate-rss", 'command "generate-rss"')
        return 'registered: command "generate-rss"'

    def deactivate(self, context: SandboxContext) -> str:
        context.commands.pop("generate-rss", None)
        return 'unregistered: command "generate-rss"'
