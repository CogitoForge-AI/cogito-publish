---
title: Configuration reference
tags: [reference]
---
Widgetizer reads `widgetizer.toml` from the project root. Every key is optional;
the defaults below apply when a key is omitted.

## Top-level keys

| Key            | Type     | Default      | Description                                  |
| -------------- | -------- | ------------ | -------------------------------------------- |
| `input_dir`    | string   | `"input"`    | Directory scanned for widget descriptions.   |
| `output_dir`   | string   | `"widgets"`  | Directory where built widgets are written.   |
| `incremental`  | bool     | `false`      | Skip records whose inputs are unchanged.     |
| `plugins`      | array    | `[]`         | Transform plugins, applied in order.         |

## Example

```toml
input_dir = "src"
output_dir = "dist"
incremental = true
plugins = ["uppercase_labels", "add_border"]
```

## Plugin ordering

Plugins run top to bottom. Order matters: a plugin sees the record as left by
the plugins before it. The concept is covered in [[How Widgetizer works]]; the
flags that override these keys live in the [[CLI reference]].
