# Original code kept for reference.
# class MarkdownParser:
#     def __init__(self):
#         self.name = "markdown-parser"
#         self.version = "1.0.0"
#         self.description = "Markdown Parser"
#
#     def MarkdownRun(self):
#         print("Markdown Parser Running ...")
#         print("Version: " + self.version)
#         print("Markdown Parser Finished")

from plugin_api import PluginBase, SandboxContext, register_plugin

@register_plugin
class MarkdownParserPlugin(PluginBase):
    plugin_id = "markdown-parser"
    version = "2.1.0"
    description = "Markdown to HTML converter"
    dependencies = ()
    plugin_type = "built-in"

    def activate(self, context: SandboxContext) -> str:
        context.register_output_format(".md", "HTML converter")
        return 'registered: .md -> HTML converter'

    def deactivate(self, context: SandboxContext) -> str:
        context.output_formats.pop(".md", None)
        return "unregistered: .md converter"
