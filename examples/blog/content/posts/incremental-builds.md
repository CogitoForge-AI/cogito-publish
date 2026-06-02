---
title: Incremental builds without the footguns
date: "2024-03-18"
tags: [architecture, performance, caching]
---
A full rebuild is simple to reason about: read everything, render everything,
write everything. The trouble is that "everything" grows, and a thirty-second
build kills the tight edit-preview loop that makes writing pleasant.

Incremental builds fix the speed problem and introduce a correctness problem:
**the incremental result must be byte-for-byte identical to a full rebuild.**
If it ever drifts, you have a generator nobody can trust.

## The rule that keeps you honest

Treat every processing unit as a pure function of its declared inputs:

```python
def render(doc: Document, ctx: Context) -> Page:
    # No clock, no globals, no network. Same inputs -> same bytes.
    ...
```

If a unit reads `datetime.now()` or a global cache, two builds can disagree and
the invariant breaks. Purity is not a style preference here; it is the property
that makes caching *safe*.

## Let the engine own the cache

A tempting mistake is to let each plugin decide what is stale and poke the
cache directly. That scatters the invalidation logic and guarantees subtle
bugs. The better split:

1. Plugins **declare facts** -- "this page depends on that file".
2. The engine **owns the algorithm** -- it propagates dirtiness and decides
   what to rebuild.

With that boundary, you can test one thing: *does an incremental build equal a
full build?* Make it a CI gate and the footguns disappear.

See [[Why static sites won the content war]] for why the rebuild cost is worth
paying in the first place.
