---
title: Templating
order: 2
---

# Templating

Plugin `Template` render trang bằng [Jinja2](https://jinja.palletsprojects.com/),
và bổ sung thêm hai tiện ích lấy cảm hứng từ Hugo lên trên đó.

- [Kế thừa](/vi/templating/inheritance/) - dùng chung một bộ khung gốc với
  `{% extends %}` và `{% block %}`.
- [Partial](/vi/templating/partials/) - tái dùng đoạn mã và component với hàm
  `partial()`.
- [Lookup cascade](/vi/templating/lookup-cascade/) - để các trang tự phân giải
  template theo type, section và kind, thay vì khai báo `layout` ở khắp nơi.

Mọi thứ ở đây nằm trong plugin `Template` và Jinja2 chuẩn - kernel không bị đụng
tới. Chính trang này dùng cả ba tính năng; thư mục `layouts/` của nó là một tham
chiếu đang hoạt động.

## Ngữ cảnh template

Mỗi template nhận:

| Biến | Nó là gì |
|------|----------|
| `content` | Phần thân HTML đã render (markup an toàn). |
| `page` | Frontmatter của trang gộp với `meta` của nó (`url`, `prev`, ...). |
| `site` | Các tùy chọn toàn-trang từ `Config.options`. |
| `collections` | Các nhóm trang có tên (khi dùng `Collections`). |
| `menus` | Các cây navigation có tên (khi dùng `Navigation`). |
| `partial` | Hàm render partial. |
