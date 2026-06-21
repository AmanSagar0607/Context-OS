"""
Plugin System — Community plugins for custom providers.

Enables extending ContextOS with custom providers, tools, and integrations.
"""

from __future__ import annotations

import importlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional, Protocol

logger = logging.getLogger(__name__)


class PluginType(str, Enum):
    EMBEDDING = "embedding"
    SEARCH = "search"
    CRAWL = "crawl"
    STORAGE = "storage"
    AUTH = "auth"
    BILLING = "billing"
    TOOL = "tool"


class PluginStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: list[str] = field(default_factory=list)
    config_schema: dict = field(default_factory=dict)


class Plugin(Protocol):
    """Plugin protocol that all plugins must implement."""

    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        ...

    async def initialize(self, config: dict) -> bool:
        """Initialize the plugin with config."""
        ...

    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        ...


@dataclass
class PluginConfig:
    """Plugin system configuration."""
    enabled: bool = True
    plugins_dir: str = "plugins"
    auto_load: bool = True
    max_plugins: int = 50


class PluginManager:
    """Plugin management system."""

    def __init__(self, config: Optional[PluginConfig] = None):
        self.config = config or PluginConfig()
        self._plugins: dict[str, tuple[Plugin, PluginMetadata]] = {}
        self._hooks: dict[str, list[Callable]] = {}

    def register(self, plugin: Plugin) -> bool:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance implementing Plugin protocol

        Returns:
            True if registration successful
        """
        if not self.config.enabled:
            return False

        metadata = plugin.metadata

        if metadata.name in self._plugins:
            logger.warning(f"Plugin {metadata.name} already registered")
            return False

        if len(self._plugins) >= self.config.max_plugins:
            logger.warning("Max plugins reached")
            return False

        self._plugins[metadata.name] = (plugin, metadata)
        logger.info(f"Registered plugin: {metadata.name} v{metadata.version}")
        return True

    def unregister(self, name: str) -> bool:
        """Unregister a plugin."""
        if name in self._plugins:
            del self._plugins[name]
            return True
        return False

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a registered plugin."""
        if name in self._plugins:
            return self._plugins[name][0]
        return None

    def get_metadata(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata."""
        if name in self._plugins:
            return self._plugins[name][1]
        return None

    def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
    ) -> list[PluginMetadata]:
        """List all registered plugins."""
        plugins = [meta for _, meta in self._plugins.values()]

        if plugin_type:
            plugins = [p for p in plugins if p.plugin_type == plugin_type]

        return plugins

    async def initialize_all(self, configs: Optional[dict[str, dict]] = None) -> dict[str, bool]:
        """Initialize all registered plugins."""
        configs = configs or {}
        results = {}

        for name, (plugin, metadata) in self._plugins.items():
            try:
                config = configs.get(name, {})
                success = await plugin.initialize(config)
                results[name] = success
            except Exception as e:
                logger.error(f"Failed to initialize plugin {name}: {e}")
                results[name] = False

        return results

    async def shutdown_all(self) -> None:
        """Shutdown all plugins."""
        for name, (plugin, _) in self._plugins.items():
            try:
                await plugin.shutdown()
            except Exception as e:
                logger.error(f"Failed to shutdown plugin {name}: {e}")

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback."""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    async def trigger_hook(self, hook_name: str, *args, **kwargs) -> list[Any]:
        """Trigger all callbacks for a hook."""
        results = []
        for callback in self._hooks.get(hook_name, []):
            try:
                result = await callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_name} callback failed: {e}")
        return results

    def load_from_directory(self, directory: str) -> int:
        """
        Load plugins from a directory.

        Returns number of plugins loaded.
        """
        import os
        import sys

        loaded = 0
        if not os.path.exists(directory):
            return 0

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and not item.startswith("_"):
                init_file = os.path.join(item_path, "__init__.py")
                if os.path.exists(init_file):
                    try:
                        # Add to sys.path temporarily
                        sys.path.insert(0, item_path)
                        module = importlib.import_module(item)

                        # Look for plugin class
                        if hasattr(module, "Plugin"):
                            plugin_cls = module.Plugin
                            plugin = plugin_cls()
                            if self.register(plugin):
                                loaded += 1

                        sys.path.pop(0)
                    except Exception as e:
                        logger.error(f"Failed to load plugin {item}: {e}")

        return loaded


# Built-in hooks
HOOKS = {
    "pre_memory_add": "Called before adding a memory",
    "post_memory_add": "Called after adding a memory",
    "pre_search": "Called before search",
    "post_search": "Called after search",
    "pre_crawl": "Called before crawling",
    "post_crawl": "Called after crawling",
    "pre_knowledge_extract": "Called before knowledge extraction",
    "post_knowledge_extract": "Called after knowledge extraction",
}


# Example plugin template
EXAMPLE_PLUGIN_TEMPLATE = '''
"""
Example ContextOS Plugin.
"""

from contextos.plugins import Plugin, PluginMetadata, PluginType


class MyPlugin:
    """Example plugin implementation."""

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="0.1.0",
            description="My custom plugin",
            author="Your Name",
            plugin_type=PluginType.TOOL,
        )

    async def initialize(self, config: dict) -> bool:
        """Initialize the plugin."""
        return True

    async def shutdown(self) -> None:
        """Shutdown the plugin."""
        pass

    async def execute(self, **kwargs) -> dict:
        """Execute plugin action."""
        return {"success": True}
'''
