---
title: Tham chiếu cấu hình
nav_title: Cấu hình
order: 3
---

# Tham chiếu cấu hình

Một trang được cấu hình bằng file `pyssg.config.py` ở gốc trang. Nó phải định nghĩa
một biến cấp module tên `config` trỏ tới một instance `pyssg.config.Config`. Việc
nạp là tất định và không có hiệu ứng phụ: file được import mới mỗi lần gọi và biến
`config` được đọc lại.

## Đối tượng `Config`

```python
from pyssg.config import Config
```

| Trường | Kiểu | Mặc định | Mô tả |
|---|---|---|---|
| `content_dir` | `str` | `"content"` | Thư mục nội dung nguồn, tương đối so với trang. |
| `output_dir` | `str` | `"dist"` | Thư mục đầu ra build, tương đối so với trang. |
| `layout` | `str \| Path \| None` | `None` | Theme. Một `str` là đường dẫn tương đối so với trang; một `Path` tuyệt đối được dùng nguyên trạng (các theme tích hợp phân giải thành đường dẫn tuyệt đối qua `pyssg.themes.theme_path`). |
| `base_url` | `str` | `""` | URL gốc tuyệt đối của trang, dùng cho sitemap, RSS và `hreflang`. |
| `plugins` | `list[Plugin]` | `[]` | Các instance plugin theo **thứ tự apply**. |
| `site` | `dict[str, object]` | `{}` | Các biến template tùy ý (`title`, `description`, ...). |

Các trường thư mục được nối với gốc trang khi engine chạy. Thứ tự danh sách
`plugins` là thứ tự các plugin được apply.

## Preset

Một **preset** là một factory thuần khiết trả về một `Config` đã được điền đầy đủ,
gói sẵn đúng các plugin tích hợp theo đúng thứ tự apply cùng một theme mặc định.
Người dùng cơ bản viết một cấu hình một dòng và không bao giờ phải biết những plugin
nào tồn tại hay chúng phải được sắp ra sao.

### `docs`

```python
from pyssg.presets import docs
```

Một trang tài liệu: điều hướng theo thư mục, taxonomy, wikilink / transclusion, RSS
và sitemap. Theme mặc định: theme `docs` tích hợp.

```python
config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
)
```

Các tham số keyword:

| Tham số | Mặc định | Mô tả |
|---|---|---|
| `site` | `None` | Các biến template. |
| `base_url` | `""` | URL gốc tuyệt đối của trang. |
| `content_dir` | `"content"` | Thư mục nội dung. |
| `output_dir` | `"dist"` | Thư mục đầu ra. |
| `layout` | `None` | Ghi đè theme `docs` mặc định bằng một layout cục bộ của trang. |
| `highlight_style` | `"default"` | Style Pygments để tô màu code. |
| `rss_title` | `None` | Tiêu đề RSS feed (mặc định lấy tiêu đề trang). |
| `extra_plugins` | `None` | Các plugin nối sau phần mặc định (nên chúng chạy sau cùng). |

### `blog`

```python
from pyssg.presets import blog
```

Một blog: bài viết dưới `content/posts/`, danh sách mới-nhất-trước kèm phân trang và
RSS. Theme mặc định: theme `blog` tích hợp.

```python
config = blog(
    site={"title": "My Blog"},
    base_url="https://example.com",
)
```

## Tự dựng cấu hình của bạn

Vì một preset chỉ trả về một `Config`, bạn có thể:

- **Mở rộng** một preset bằng `extra_plugins` (trường hợp phổ biến - xem các hướng
  dẫn [i18n](../how-to/internationalization.md) và
  [API reference](../how-to/api-reference.md)), hoặc
- **Tự dựng một `Config` bằng tay**, tự chọn và sắp thứ tự plugin, khi bạn cần toàn
  quyền kiểm soát.

[Tham chiếu plugin và hook](plugins.md) liệt kê mọi plugin tích hợp bạn có thể lắp
ráp.
