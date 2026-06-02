---
title: Markdown is enough (and that is the point)
date: "2024-04-22"
tags: [authoring, markdown]
---
Every few years a new authoring format promises to replace Markdown. None of
them stick, and the reason is boring: Markdown is *almost good enough* and
trivially learnable. Authors want to write, not to learn a DSL.

## What plain Markdown gives you

A surprising amount:

| Feature        | Syntax              |
| -------------- | ------------------- |
| Headings       | `# Title`           |
| Emphasis       | `*italic*`          |
| Code           | `` `inline` ``      |
| Lists          | `- item`            |
| Links          | `[text](url)`       |

That table itself is Markdown. So is this list. So is the fenced code block
below.

```python
print("rendered at build time, served as plain HTML")
```

## Extend, do not replace

The right move is to keep the core readable and add power through extensions:
tables, footnotes, table-of-contents, syntax highlighting, and `[[wikilinks]]`
for cross-references. Each is opt-in and degrades gracefully -- open the raw
file and it still reads like prose.

That is the whole philosophy: the source should be pleasant to read *before* it
is rendered. Tooling that forgets this trades author happiness for features
nobody asked for.
