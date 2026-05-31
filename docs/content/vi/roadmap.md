---
title: Lộ trình
order: 6
---

# Lộ trình

pyssg đang hướng tới đâu. Đây là một tài liệu sống - các mục dịch chuyển và ưu
tiên thay đổi khi dự án lớn lên. Để có bức tranh đầy đủ về những gì đã chạy được,
hãy duyệt phần còn lại của tài liệu này.

Muốn giúp một việc gì đó ở đây, hoặc đề xuất một mục? Hãy mở một issue hoặc pull
request trên [GitHub](https://github.com/magiskboy/pyssg).

## Đã có ngay bây giờ

- Kernel không phụ thuộc với thiết kế plugin và lifecycle-hook kiểu webpack.
- `pyssg build` và `pyssg serve` (watch + live reload).
- Các preset `docs()`, `blog()` và `site()`.
- Templating với lookup cascade kiểu Hugo và `partial()`.
- Tạo khung `pyssg new` với theme offline và theme host trên GitHub.
- Tô màu cú pháp, fingerprint asset, thẻ SEO / Open Graph, `robots.txt` và
  redirect.
- Sitemap, RSS, và output Markdown thô song song với HTML.

## Tiếp theo

Nhắm cho bản phát hành 1.0.

- **File dữ liệu** - nạp `data/*.toml|json|yaml` vào template của bạn.
- **Hai theme được trau chuốt** - một theme docs OSS và một theme blog cá nhân,
  không cần Node hay bước build nào.
- **Tìm kiếm phía client** - một chỉ mục được sinh ra cùng một widget tìm kiếm
  nhỏ.

## Sau này

- **Shortcode & admonition** - callout, embed, và nhóm tab.
- **Mục lục cho từng trang**, thời gian đọc, và đếm từ.
- **Phân giải liên kết nội bộ** kèm báo cáo liên kết hỏng.
- **Wikilink kiểu Obsidian** (`[[...]]`) và backlink.
- **Lint Markdown** để bắt lỗi ngay lúc build.
- **Feed mở rộng** - JSON Feed và Atom, cùng feed cho từng tag.
- **Plugin bên thứ ba** phân phối dưới dạng các gói Python thuần.
- **Build tăng dần (incremental)** để rebuild nhanh hơn trên các trang lớn.
