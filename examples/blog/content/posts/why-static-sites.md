---
title: Why static sites won the content war
date: "2024-02-04"
tags: [architecture, performance]
---
For a decade the default answer to "I need a website" was a database, an
application server, and a templating layer rendering every page on every
request. For content that rarely changes, that is a lot of moving parts to
keep alive at 3am.

Static site generators flipped the trade. Render the pages **once**, at build
time, and serve plain files afterwards. The result is faster, cheaper, and far
harder to break.

## The numbers that matter

- **Time to first byte** drops to whatever your CDN edge can do, because there
  is no application code in the request path.
- **Operational surface** shrinks to "files in a bucket". There is no runtime
  to patch, no connection pool to exhaust.
- **Scaling** stops being a project. A flat file handles ten requests or ten
  million the same way.

## Where it still hurts

Static is not free of trade-offs. Truly dynamic, per-user pages still need a
server (or an edge function). And a large site can take a while to rebuild from
scratch -- which is exactly why incremental builds matter, a topic for
[[Incremental builds without the footguns]].

The point is not that static beats everything. It is that for the enormous
class of *content that is the same for every visitor*, paying the render cost
once is obviously right.
