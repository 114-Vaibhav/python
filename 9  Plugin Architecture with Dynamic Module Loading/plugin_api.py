from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable


PLUGIN_REGISTRY: dict[str, type["PluginBase"]] = {}

def register_plugin(plugin_class: type["PluginBase"]) -> type["PluginBase"]:
    """Decorator-based registry for dynamically imported plugin classes."""
    plugin_id = getattr(plugin_class, "plugin_id", "").strip()
    if not plugin_id:
        raise ValueError(f"{plugin_class.__name__} must define plugin_id")
    PLUGIN_REGISTRY[plugin_id] = plugin_class
    return plugin_class


@dataclass
class SandboxContext:
    """Restricted surface exposed to plugins during activation."""

    commands: dict[str, Callable[[], str]] = field(default_factory=dict)
    themes: dict[str, str] = field(default_factory=dict)
    output_formats: dict[str, str] = field(default_factory=dict)
    post_processors: dict[str, str] = field(default_factory=dict)

    def register_command(self, name: str, description: str) -> None:
        self.commands[name] = description

    def register_theme(self, name: str, description: str) -> None:
        self.themes[name] = description

    def register_output_format(self, extension: str, description: str) -> None:
        self.output_formats[extension] = description

    def register_post_processor(self, extension: str, description: str) -> None:
        self.post_processors[extension] = description


class PluginBase(ABC):
    plugin_id = ""
    version = "0.0.0"
    description = ""
    dependencies: tuple[str, ...] = ()
    plugin_type = "third-party"

    @abstractmethod
    def activate(self, context: SandboxContext) -> str:
        """Activate the plugin inside the controlled application context."""

    @abstractmethod
    def deactivate(self, context: SandboxContext) -> str:
        """Clean up any plugin-owned registrations before shutdown."""
