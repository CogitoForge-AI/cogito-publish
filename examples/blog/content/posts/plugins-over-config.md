---
title: Prefer plugins over a thousand config options
date: "2024-05-30"
tags: [architecture, design]
---
There are two ways a tool grows to meet new needs. It can sprout a new config
flag for every request, until the options reference reads like tax law. Or it
can expose a small, stable extension point and let features live as plugins.

The second path ages better.

## Why config sprawl rots

Each flag is a permanent promise. It interacts with every other flag, multiplies
the test matrix, and can never quite be removed. Five years in, nobody knows
which combinations actually work.

## A small kernel, many plugins

Keep the core tiny and lifecycle-driven. A plugin taps a hook, declares what it
contributes, and stays out of the engine's algorithms:

```python
def my_plugin() -> Plugin:
    def on_page(page, ctx):
        # contribute a fact; the engine decides what to do with it
        return page
    return Plugin(name="my-plugin", page=on_page)
```

The kernel never grows to know about your feature. Your feature never has to
fork the kernel. New behavior is *added*, not *configured into existence*.

## The honest cost

Plugins demand a well-designed hook contract, and a bad one leaks the engine's
internals everywhere. That design work is real -- but you pay it once, instead
of paying interest on config debt forever. It pairs naturally with the
build-time purity argued in [[Incremental builds without the footguns]].
