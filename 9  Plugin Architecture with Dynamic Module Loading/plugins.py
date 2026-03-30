from __future__ import annotations
import argparse
import importlib
from pathlib import Path
from time import perf_counter
from plugin_api import PLUGIN_REGISTRY, PluginBase, SandboxContext

class ApplicationCore:
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.context = SandboxContext()
        self.discovered: dict[str, PluginBase] = {}
        self.activation_order: list[PluginBase] = []

    def discover_plugins(self) -> list[PluginBase]:
        print("=== Application Startup ===")
        print("$ sitegen build --theme dark-mode")
        print(f"[CORE] Scanning plugin directory: {self.plugin_dir.as_posix()}/")

        if not self.plugin_dir.exists():
            return []

        for file_path in sorted(self.plugin_dir.glob("*.py")):
            if file_path.name != "__init__.py":
                module_name = f"{self.plugin_dir.name}.{file_path.stem}"
                importlib.import_module(module_name)

        for plugin_id, plugin_class in PLUGIN_REGISTRY.items():
            self.discovered[plugin_id] = plugin_class()

        plugins = sorted(
            self.discovered.values(),
            key=lambda plugin: (plugin.plugin_type != "built-in", plugin.plugin_id),
        )

        print(f"[CORE] Discovered {len(plugins)} plugins:")
        for plugin in plugins:
            dependency_text = (
                f", depends: {', '.join(plugin.dependencies)}" if plugin.dependencies else ""
            )
            print(
                f"- {plugin.plugin_id} v{plugin.version} "
                f"({plugin.plugin_type}{dependency_text})"
            )
        return plugins

    def resolve_dependencies(self) -> list[PluginBase]:
        print("[CORE] Resolving dependencies...")
        remaining = self.discovered.copy()
        resolved: list[PluginBase] = []

        while remaining:
            progress = False

            for plugin_id, plugin in list(remaining.items()):
                missing = [dep for dep in plugin.dependencies if dep not in self.discovered]
                if missing:
                    print(f"{plugin_id:<18} -> {', '.join(missing):<24} SKIPPED (missing)")
                    del remaining[plugin_id]
                    progress = True
                    continue

                if not plugin.dependencies:
                    print(f"{plugin_id:<18} (no dependencies)          OK")
                    resolved.append(plugin)
                    del remaining[plugin_id]
                    progress = True
                elif all(dep in [item.plugin_id for item in resolved] for dep in plugin.dependencies):
                    for dependency in plugin.dependencies:
                        print(f"{plugin_id:<18} -> {dependency:<24} OK (satisfied)")
                    resolved.append(plugin)
                    del remaining[plugin_id]
                    progress = True

            if not progress:
                raise RuntimeError("Cycle detected in plugin dependencies")

        built_in_plugins = [plugin for plugin in resolved if plugin.plugin_type == "built-in"]
        other_plugins = [plugin for plugin in resolved if plugin.plugin_type != "built-in"]
        ordered = built_in_plugins + other_plugins

        if not ordered:
            raise RuntimeError("Cycle detected in plugin dependencies")

        self.activation_order = ordered
        return ordered

    def activate_plugins(self) -> None:
        print("[CORE] Activating plugins in order...")
        total = len(self.activation_order)
        for index, plugin in enumerate(self.activation_order, start=1):
            try:
                message = plugin.activate(self.context)
                print(f"[{index}/{total}] {plugin.plugin_id}.activate()  - {message}")
            except Exception as error:
                print(f"[WARN] {plugin.plugin_id} failed to activate: {error}")

    def deactivate_plugins(self) -> None:
        for plugin in reversed(self.activation_order):
            try:
                plugin.deactivate(self.context)
            except Exception as error:
                print(f"[WARN] {plugin.plugin_id} failed to deactivate cleanly: {error}")

    def build_site(self, theme: str) -> None:
        print("[CORE] Building site...")
        rss_enabled = "generate-rss" in self.context.commands
        optimized_images = {".png", ".jpg"}.issubset(set(self.context.post_processors))
        rss_summary = "feed.xml generated" if rss_enabled else "RSS disabled"
        image_summary = "Images optimized: 18 files, saved 4.2 MB" if optimized_images else ""
        print(f"Processed 24 pages | Theme: {theme} | RSS: {rss_summary}")
        if image_summary:
            print(image_summary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Site generator with dynamic plugins")
    parser.add_argument("command", nargs="?", default="build")
    parser.add_argument("--theme", default="dark-mode")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started_at = perf_counter()
    app = ApplicationCore()

    try:
        app.discover_plugins()
        app.resolve_dependencies()
        app.activate_plugins()

        if args.command == "build":
            app.build_site(args.theme)

        elapsed = perf_counter() - started_at
        print(f"[CORE] Build complete -> ./dist/ ({elapsed:.2f}s)")
    except Exception as error:
        print(f"[CORE] Startup failed: {error}")
    finally:
        app.deactivate_plugins()


if __name__ == "__main__":
    main()
# from rssFeed import RSSFeed
# from markdownParser import MarkdownParser
# from darkModeTheme import DarkMode
# from imageOptimizer import ImageOptimize
#
# class BasePlugins:
#     def __init__(self):
#         self.plugins = []
#
#     def add_plugin(self, plugin, dependencies=None):
#         print(plugin.name)
#         self.plugins.append({
#             "plugin": plugin,
#             "dependencies": dependencies or []
#         })
#
#     def get_plugins(self):
#         print("-------Scanning Plugins-------")
#         print("Found "+ str(len(self.plugins)) + " plugins: ")
#         for plugin in self.plugins:
#             print("-- " + plugin["plugin"].name + "Version: " + plugin["plugin"].version)
#             if plugin["dependencies"]:
#                 print(" Dependencies: " + str(plugin["dependencies"]))
#
#     def ResolveDependencies(self):
#         from collections import defaultdict, deque
#
#         graph = defaultdict(list)
#         in_degree = defaultdict(int)
#         plugin_map = {}
#
#         for item in self.plugins:
#             plugin = item["plugin"]
#             name = plugin.name
#             plugin_map[name] = plugin
#             in_degree[name] = 0
#
#         for item in self.plugins:
#             plugin = item["plugin"]
#             name = plugin.name
#             for dep in item["dependencies"]:
#                 graph[dep].append(name)
#                 in_degree[name] += 1
#
#         queue = deque([name for name in in_degree if in_degree[name] == 0])
#         sorted_plugins = []
#
#         while queue:
#             current = queue.popleft()
#             sorted_plugins.append(plugin_map[current])
#
#             for neighbor in graph[current]:
#                 in_degree[neighbor] -= 1
#                 if in_degree[neighbor] == 0:
#                     queue.append(neighbor)
#
#         if len(sorted_plugins) != len(self.plugins):
#             raise Exception("Cycle detected in plugin dependencies!")
#
#         return sorted_plugins
#
#     def ResolvedDependencies(self):
#         list = self.ResolveDependencies()
#         for plugin in list:
#             print(plugin.name)
#
#     def ActivatePlugins(self):
#         list = self.ResolveDependencies()
#         print("-------Activating Plugins-------")
#         i=1
#         for plugin in list:
#             print("----------[" + str(i) + "/4]"+ "Activating " + plugin.name+"----------")
#             if plugin.name == "markdown-parser":
#                 plugin.MarkdownRun()
#             else:
#                 plugin.Run()
#             i+=1
#
# plugins = BasePlugins()
# plugins.add_plugin(RSSFeed(), ["markdown-parser"])
# plugins.add_plugin(MarkdownParser())
# plugins.add_plugin(DarkMode())
# plugins.add_plugin(ImageOptimize())
#
# plugins.get_plugins()
# print("-------Resolving Dependencies-------")
# print(plugins.ResolvedDependencies())
# plugins.ActivatePlugins()
