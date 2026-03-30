# Plugin Architecture with Dynamic Module Loading

This project demonstrates a simple Python plugin system where the application core discovers plugins at runtime, resolves dependencies, activates them in order, and lets them register new features such as themes, commands, output formats, and post-processors.

The goal is to keep the core application mostly unchanged while new plugins can be added through the `./plugins/` directory.

## Features

- Dynamic plugin discovery using `importlib`
- Shared plugin contract using `abc.ABC`
- Plugin registry with a decorator
- Dependency-aware activation
- Lifecycle hooks with `activate()` and `deactivate()`
- Simple sandbox-style context for controlled plugin registration
- Extensible design for themes, commands, output formats, and image processors

## Project Structure

```text
.
|-- plugins.py
|-- plugin_api.py
|-- markdownParser.py
|-- darkModeTheme.py
|-- imageOptimizer.py
|-- rssFeed.py
|-- pyproject.toml
`-- plugins/
    |-- __init__.py
    |-- markdown_parser_plugin.py
    |-- dark_mode_theme_plugin.py
    |-- image_optimizer_plugin.py
    `-- rss_feed_plugin.py
```

## How It Works

### 1. Core Application

The main logic is inside `plugins.py`.

It does the following:

1. Scans the `./plugins/` folder.
2. Dynamically imports all plugin wrapper modules.
3. Collects plugin classes from the shared registry.
4. Creates plugin objects.
5. Resolves plugin dependencies.
6. Activates plugins in the correct order.
7. Simulates a site build using the registered plugin features.

### 2. Shared Plugin API

The `plugin_api.py` file defines:

- `PluginBase`: abstract base class for all plugins
- `register_plugin`: decorator used to register plugin classes
- `SandboxContext`: controlled context used by plugins to register features

### 3. Example Plugins

This project includes four sample plugins:

- `markdown-parser`
  Converts Markdown files into HTML output.
- `dark-mode-theme`
  Registers the `dark-mode` theme.
- `rss-feed`
  Registers the `generate-rss` command and depends on `markdown-parser`.
- `image-optimizer`
  Registers post-processing for `.png` and `.jpg` files.

## Requirements Used

This project uses the following Python concepts:

- `importlib`
- `importlib.metadata` in project metadata through `pyproject.toml`
- `abc.ABC` and `@abstractmethod`
- decorators and class registry
- dependency resolution
- runtime discovery of modules
- graceful error handling during plugin activation and shutdown

## Run the Project

Use:

```bash
python plugins.py build --theme dark-mode
```

## Example Output

```text
=== Application Startup ===
$ sitegen build --theme dark-mode
[CORE] Scanning plugin directory: plugins/
[CORE] Discovered 4 plugins:
- markdown-parser v2.1.0 (built-in)
- dark-mode-theme v1.3.2 (third-party)
- image-optimizer v0.9.1 (third-party)
- rss-feed v1.0.0 (third-party, depends: markdown-parser)
[CORE] Resolving dependencies...
dark-mode-theme    (no dependencies)          OK
image-optimizer    (no dependencies)          OK
markdown-parser    (no dependencies)          OK
rss-feed           -> markdown-parser          OK (satisfied)
[CORE] Activating plugins in order...
[1/4] markdown-parser.activate()  - registered: .md -> HTML converter
[2/4] dark-mode-theme.activate()  - registered: theme "dark-mode"
[3/4] image-optimizer.activate()  - registered: post-processor for .png/.jpg
[4/4] rss-feed.activate()  - registered: command "generate-rss"
[CORE] Building site...
Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated
Images optimized: 18 files, saved 4.2 MB
[CORE] Build complete -> ./dist/ (0.01s)
```

## Notes

- This is a learning-oriented implementation, so the code is intentionally simpler than a production plugin platform.
- The current version focuses on readability and dynamic loading from a local plugin directory.
- A more advanced production version could add full runtime unloading, stronger sandboxing, and entry-point based external plugin packages.

## References

1. Nawaz Dhandala, "How to Build Plugin Systems in Python," OneUptime, January 30, 2026.  
   Link: https://oneuptime.com/blog/post/2026-01-30-python-plugin-systems/view

2. "Crafting A Modular Plugin Architecture In Python For Dynamic Component Management," peerdh.com.  
   Link: https://peerdh.com/blogs/programming-insights/crafting-a-modular-plugin-architecture-in-python-for-dynamic-component-management

3. "Building a Dynamic Plugin Architecture in Python: A Comprehensive Guide," PyQuestHub, November 8, 2024.  
   Link: https://pyquesthub.com/building-a-dynamic-plugin-architecture-in-python-a-comprehensive-guide
