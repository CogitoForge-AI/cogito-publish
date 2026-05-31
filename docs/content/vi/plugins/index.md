---
title: Plugin
order: 3
---

# Plugin

Plugin là nơi mọi việc thực sự diễn ra. pyssg đi kèm hai tier plugin có sẵn cộng
với một cách để tự viết plugin của riêng bạn.

- [Plugin có sẵn](/vi/plugins/built-in/) - các plugin tier-1 và tier-2 đi kèm
  pyssg.
- [Viết plugin](/vi/plugins/writing-plugins/) - phương thức `apply`, tap vào hook,
  và các quy ước cần theo.
- [Preset](/vi/plugins/presets/) - các bộ plugin dựng sẵn cho docs, blog và trang
  công ty.

## Hai tier

**Tier 1** biến Markdown thành HTML, một-đối-một:

`ReadFile` -> `Frontmatter` -> `Markdown` -> `Template` -> `WriteFile`

**Tier 2** bổ sung cấu trúc linh hoạt - URL, gom nhóm, trang danh sách và
navigation - để cây nguồn và cây output không nhất thiết phải trùng nhau:

`Permalink`, `Collections`, `Listing`, `Navigation`

Mọi plugin tier-2 dùng chung một [mô hình nội dung](/vi/architecture/lifecycle/),
nên một template chỉ bao giờ phải học `site`, `page`, `collections` và `menus`.
