---
title: Quick start
tags: [guide]
---
This guide takes you from an empty directory to your first batch of widgets in
about a minute. It assumes you have finished [[Installation]].

## 1. Create an input

Widgetizer reads one file per widget. Make a directory and drop a description
inside:

```bash
mkdir input
echo "shape: hexagon" > input/first.yaml
```

## 2. Build

```bash
widgetizer build ./input --out ./widgets
```

You should see one line per widget produced:

```text
built first -> ./widgets/first.widget
1 widget built in 0.02s
```

## 3. Inspect the result

Each widget is a self-contained file you can ship or open directly. To rebuild
only what changed, add `--incremental`:

```bash
widgetizer build ./input --out ./widgets --incremental
```

## Next steps

- Learn the model behind all of this in [[How Widgetizer works]].
- Tune behavior in the [[Configuration reference]].
- See every flag in the [[CLI reference]].
