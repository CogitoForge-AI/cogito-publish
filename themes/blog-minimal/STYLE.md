# blog-minimal stylesheet provenance

`assets/style.css` is generated offline from [hugo-coder](https://github.com/luizdepra/hugo-coder)
(MIT). The pyssg build does not compile SCSS; only the resulting static CSS is
shipped. To regenerate after updating the subset:

- Source: hugo-coder at commit `3d3bbd75d7bb46a4670af89442cf0b961440bd4e`
- Entry: a custom SCSS file importing only the minimal core partials (normalize,
  variables, base, content, navigation, pagination, taxonomies, footer, syntax,
  plus their `_*_dark` counterparts). Excludes font-awesome, notices, tabs,
  float, mastodon. The single font-awesome reference in `_content.scss`
  (external-link marker) is shimmed to empty so no icon font is required.
- Command (run from coder's `assets/scss/`, with the entry on the load path):

  ```sh
  npx sass --no-source-map --style=expanded --load-path=. entry.scss style.css
  ```

  then drop the leading `@charset` line and prepend the attribution header.
