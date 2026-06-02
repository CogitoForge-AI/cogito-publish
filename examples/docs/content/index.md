---
title: Widgetizer
tags: [overview]
---
**Widgetizer** is a fictional toolkit used to demonstrate the pyssg `docs`
preset. It turns raw inputs into polished widgets with a single command. This
site is the kind of documentation the preset produces out of the box: a
sidebar grouped by section, breadcrumbs, per-page tables of contents, tag
archives, and a sitemap.

## Where to start

- New here? Read [[Installation]], then [[Quick start]].
- Want the concepts? See [[How Widgetizer works]].
- Looking for specifics? Jump to the [[Configuration reference]] or the
  [[CLI reference]].

## At a glance

```bash
pip install widgetizer
widgetizer build ./input --out ./widgets
```

That command reads everything under `./input`, builds a widget for each entry,
and writes the results to `./widgets`. The rest of these docs explain each step
in detail.
