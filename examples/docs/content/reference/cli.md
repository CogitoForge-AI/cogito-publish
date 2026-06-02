---
title: CLI reference
tags: [reference]
---
All commands take the form `widgetizer <command> [options]`. Flags override the
matching keys in `widgetizer.toml` (see the [[Configuration reference]]).

## `widgetizer build`

Build widgets from an input directory.

```bash
widgetizer build <input> --out <dir> [--incremental]
```

| Flag            | Description                                          |
| --------------- | ---------------------------------------------------- |
| `<input>`       | Directory of widget descriptions to read.            |
| `--out <dir>`   | Where to write the built widgets.                    |
| `--incremental` | Rebuild only records whose inputs changed.           |

## `widgetizer clean`

Remove the output directory.

```bash
widgetizer clean --out <dir>
```

## `widgetizer --version`

Print the installed version and exit. Used in [[Installation]] to confirm a
working setup.
