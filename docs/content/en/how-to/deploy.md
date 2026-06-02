---
title: Deploy a built site
nav_title: Deploy
order: 6
---

# Deploy a built site

**Goal:** publish the static output produced by `build`.

## 1. Produce a clean build

```bash
pyssg --site my-site build
```

Everything to deploy is now in the output directory (`dist/` by default; set
`output_dir` in your config to change it). The output is a plain tree of HTML,
CSS, and assets - no server runtime is required.

## 2. Set `base_url`

If your site is served from a subpath (for example a GitHub Pages project site at
`https://user.github.io/repo`), set `base_url` so generated absolute URLs - the
sitemap, RSS feed, and `hreflang` tags - are correct:

```python
config = docs(
    site={"title": "My Docs"},
    base_url="https://user.github.io/repo",
)
```

## 3. Upload `dist/`

Point any static host at the output directory. A few common targets:

- **GitHub Pages** - push the `dist/` contents to the `gh-pages` branch, or use a
  Pages action that uploads the directory as the artifact.
- **Netlify / Cloudflare Pages / Vercel** - set the build command to
  `pyssg --site my-site build` and the publish directory to
  `my-site/dist`.
- **Any web server / object storage** - copy `dist/` to the document root or
  bucket.

## 4. Keep builds reproducible in CI

pyssg builds are deterministic: given the same inputs, two builds produce
byte-identical output. In CI, run a full `build` (the cache is an optimization,
not a correctness requirement) - pass `--no-cache` if you want to prove a clean
build from scratch:

```bash
pyssg --site my-site build --no-cache
```

To remove the output directory and cache locally, use `clean`:

```bash
pyssg --site my-site clean --yes
```
