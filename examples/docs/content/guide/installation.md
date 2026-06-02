---
title: Installation
tags: [guide]
---
Widgetizer runs anywhere Python 3.13 runs. Pick the method that matches how you
manage projects.

## Requirements

- Python 3.13 or newer
- A POSIX shell or PowerShell

## Install with pip

```bash
pip install widgetizer
```

## Install from source

```bash
git clone https://github.com/example/widgetizer
cd widgetizer
pip install -e .
```

## Verify the install

```bash
widgetizer --version
```

If that prints a version string, you are ready for the [[Quick start]]. If the
command is not found, make sure your interpreter's `bin/` directory is on your
`PATH`.
