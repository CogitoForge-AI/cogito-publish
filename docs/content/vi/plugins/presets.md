---
title: Preset
order: 2
---

# Preset

Một preset chỉ là một hàm trả về một danh sách plugin đã được cấu hình. Chúng cho
người mới một thiết lập chạy được trong một dòng, đồng thời để người dùng nâng
cao tự do ráp plugin bằng tay.

```python
from pyssg_cli.presets import docs, blog, site
```

## `docs()`

Tài liệu kỹ thuật: một sidebar dựa trên thư mục với liên kết prev/next.

```python
docs(markdown_extensions=("fenced_code", "tables"))
```

Bộ: `ReadFile`, `Frontmatter`, `Markdown`, `Permalink`, `Collections` (theo thư
mục), `Navigation` (chế độ folder, tuần tự), `Template`, `WriteFile`.

Đây chính là preset dựng nên trang bạn đang đọc.

## `blog()`

Một blog cá nhân: một trang chỉ mục có phân trang, một trang cho mỗi tag, và một
menu trên cùng.

```python
blog(page_size=10)
```

Bộ thêm hai plugin `Listing` (trang chỉ mục blog và các trang tag) cùng một
`Navigation` lấy từ frontmatter.

## `site()`

Một trang công ty hay tổ chức: một menu phẳng ở trên cùng và các trang độc lập.

```python
site()
```

Preset gọn nhẹ nhất - permalink, một menu từ frontmatter, và đường ống tier-1.

## Tùy biến một preset

Mỗi preset chấp nhận các đối số từ khóa cho những núm vặn thông dụng:

| Đối số | Preset | Mặc định |
|--------|--------|----------|
| `markdown_extensions` | tất cả | `()` |
| `template_dir` | tất cả | `"layouts"` |
| `clean` | tất cả | `True` |
| `page_size` | `blog` | `10` |
| `sitemap` | tất cả | `False` |
| `minify` | tất cả | `False` |
| `robots` | tất cả | `False` |
| `markdown_pages` | tất cả | `False` |
| `seo` | tất cả | `True` |
| `rss` | `blog` | `True` |

Ví dụ, một bản build docs cho production có sitemap và HTML đã minify:

```python
docs(sitemap=True, minify=True)
```

Nếu bạn cần kiểm soát nhiều hơn, hãy sao chép phần thân của preset vào cấu hình
của bạn và chỉnh danh sách plugin trực tiếp - nó chỉ là một danh sách.
