---
title: CLI reference
nav_title: CLI
order: 2
---

# CLI reference

pyssg is invoked as a module: `python -m pyssg [--site PATH] <command> [options]`.
Through uv that is `uv run python -m pyssg ...`.

## Global option

| Option | Default | Description |
|---|---|---|
| `--site PATH` | `.` | The site directory. All other paths in the config (`content_dir`, `output_dir`, `layout`) are relative to it. |

Run any command with `--help` to see its options.

## `init`

Scaffold a new site for a preset.

```bash
uv run python -m pyssg --site my-site init --preset docs
```

| Option | Default | Description |
|---|---|---|
| `--preset {docs,blog}` | `docs` | Which preset to scaffold. |
| `--force` | off | Overwrite an existing `pyssg.config.py` (otherwise `init` refuses, to avoid clobbering a real site). |

Writes a one-line `pyssg.config.py` plus a little sample content. Scaffolding is
deterministic: sample dates are fixed literals, so running it twice produces
identical files.

## `build`

Full build to the output directory.

```bash
uv run python -m pyssg --site my-site build
```

| Option | Default | Description |
|---|---|---|
| `--no-cache` | off | Ignore the persistent cache (prove a clean build from scratch). |
| `--profile` | off | Print per-phase touched counts and cache hits. |

Prints `build: N pages written`.

## `serve`

Watch the content, rebuild incrementally, and serve with live reload.

```bash
uv run python -m pyssg --site my-site serve
```

| Option | Default | Description |
|---|---|---|
| `--host HOST` | `127.0.0.1` | Address to bind. |
| `--port PORT` | `8000` | Port to bind. |
| `--no-cache` | off | Ignore the persistent cache. |

Edit any file under `content/` and the affected page rebuilds and the browser
reloads automatically.

## `clean`

Remove the output directory and the cache.

```bash
uv run python -m pyssg --site my-site clean
```

| Option | Default | Description |
|---|---|---|
| `--yes` | off | Skip the interactive confirmation. |

Without `--yes`, `clean` lists what it will remove and asks for confirmation.

## `eject-layout`

Copy a built-in theme into the site so you can customize it.

```bash
uv run python -m pyssg --site my-site eject-layout --theme docs --to layouts/theme
```

| Option | Default | Description |
|---|---|---|
| `--theme {docs,blog}` | *(required)* | Built-in theme to copy. |
| `--to DIR` | `layouts/theme` | Destination directory, relative to the site. |

Refuses to overwrite an existing destination. After copying, set `layout="<DIR>"`
in your `pyssg.config.py`. See [Customize a theme](../how-to/customize-theme.md).
