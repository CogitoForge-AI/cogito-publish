---
title: Vòng đời
order: 2
---

# Vòng đời

Một lần build chạy như một chuỗi **pass theo từng giai đoạn**: mỗi pass quét toàn
bộ tập source trước khi pass kế tiếp bắt đầu. Điều này phản chiếu cách webpack
build mọi module trước khi "seal", và chính nó cho phép một plugin nhìn thấy toàn
bộ trang - thiết yếu cho navigation, collection và các trang dẫn xuất.

```text
initialize                       (after every plugin is applied)
before_run
  discover                       (collect Sources)
  load       (each source)       (read raw content)        [bail]
  parse      (each source)       (split frontmatter/body)
  collect    (whole build)       (build site-wide context -> build.meta)
  transform  (each source)       (body -> content)         [waterfall]
  render     (each source)       (emit Output; sees whole site)
  generate   (whole build)       (derived pages: rss, extra files)
  optimize   (whole build)       (minify, optimize)        [stage ordering]
  emit       (whole build)       (write to disk)
  after_emit (whole build)       (sitemap, graph, report)
done | failed
```

## Vì sao theo giai đoạn, không theo từng source

Nếu mỗi source được xử lý trọn vẹn một cách biệt lập, một trang sẽ không thể biết
về các trang khác khi đang render - khiến navigation, "bài viết liên quan" hay
chỉ mục tag trở nên bất khả thi. Bằng cách hoàn tất `parse` cho *tất cả* source
trước khi `collect` chạy, plugin có thể dựng nên bức tranh đầy đủ về trang trước.

## Hai điểm mở rộng cho công việc toàn-trang

- **`collect`** chạy *trước* `render`. Chỉ đọc đối với output: nó tập hợp ngữ
  cảnh toàn-trang vào `build.meta` (collection, navigation) để mọi trang dùng
  được. Các plugin tier-2 tạo ra trang nhân tạo (như listing) cũng nối thêm
  `Source` của chúng tại đây, để các trang đó chảy tự nhiên qua `transform` và
  `render`.
- **`generate`** chạy *sau* `render`. Nó tổng hợp trực tiếp các file `Output` -
  những thứ không bao giờ đi qua template, như `sitemap.xml` hay một RSS feed.

## `build.meta`

`build.meta` là một túi ngữ cảnh dùng chung (một `dict`). Pass `collect` ghi vào
nó; `render`, `generate` và template đọc từ nó. Các plugin tier-2 thống nhất một
tập khóa nhỏ - `site`, `collections`, `menus` - và chính điều đó giữ cho hệ sinh
thái không bị phân mảnh.

Xem [Hook](/vi/architecture/hooks/) để biết thứ tự bên trong một pass hoạt động
ra sao.
