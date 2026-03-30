# Original code kept for reference.
# class ImageOptimize:
#     def __init__(self):
#         self.name = "image-optimizer"
#         self.version = "1.0.0"
#         self.description = "Image Optimizer"
#
#     def Run(self):
#         print("Image Optimizer Running ...")
#         print("Version: " + self.version)
#         print("Image Optimizer Finished ...")

from plugin_api import PluginBase, SandboxContext, register_plugin

@register_plugin
class ImageOptimizerPlugin(PluginBase):
    plugin_id = "image-optimizer"
    version = "0.9.1"
    description = "Image optimization post-processor"
    dependencies = ()
    plugin_type = "third-party"

    def activate(self, context: SandboxContext) -> str:
        context.register_post_processor(".png", "post-processor for .png/.jpg")
        context.register_post_processor(".jpg", "post-processor for .png/.jpg")
        return "registered: post-processor for .png/.jpg"

    def deactivate(self, context: SandboxContext) -> str:
        context.post_processors.pop(".png", None)
        context.post_processors.pop(".jpg", None)
        return "unregistered: post-processor for .png/.jpg"
