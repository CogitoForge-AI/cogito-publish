---
title: Cấu hình
order: 2
---

# Cấu hình

pyssg được cấu hình bằng một file Python - mặc định là `pyssg.config.py` - phơi
ra một hàm `config()` trả về một đối tượng `Config`. Dùng Python (thay vì YAML
hay TOML) nghĩa là bạn có thể truyền thẳng các instance plugin và dùng bất kỳ
logic nào bạn muốn, y hệt `webpack.config.js`.

## Hàm `config()`

```python
from pyssg.config import Config
from pyssg_cli.presets import blog


def config() -> Config:
    return Config(
        src="content",
        out="public",
        options={"title": "My Blog", "base_url": "https://example.com"},
        plugins=blog(page_size=10),
    )
```

## Đối tượng `Config`

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `src` | path | Thư mục chứa các nguồn Markdown. |
| `out` | path | Thư mục mà trang đã build được ghi vào. |
| `plugins` | list | Các instance plugin, áp dụng theo thứ tự. |
| `options` | dict | Các giá trị toàn-trang phơi ra cho template dưới dạng `site`. |

`src` và `out` chấp nhận chuỗi hoặc đối tượng `Path`.

## Tùy chọn của site

Bất cứ thứ gì bạn đặt vào `options` đều có sẵn trong template dưới dạng đối tượng
`site`:

```python
Config(..., options={"title": "Docs", "author": "Jane"})
```

```html
<title>{{ site.title }}</title>
<meta name="author" content="{{ site.author }}">
```

## Chọn plugin

Bạn có thể dùng một [preset](/vi/plugins/presets/) hoặc tự ráp plugin bằng tay.
Thứ tự rất quan trọng: plugin chạy theo thứ tự được liệt kê, và bên trong một
lifecycle hook thứ tự được tinh chỉnh thêm theo *stage* của từng plugin. Xem
[Vòng đời](/vi/architecture/lifecycle/) để có bức tranh đầy đủ.

```python
from pyssg_plugins import (
    ReadFile, Frontmatter, Markdown, Template, WriteFile,
)

def config() -> Config:
    return Config(
        src="content",
        out="public",
        plugins=[
            ReadFile(),
            Frontmatter(),
            Markdown(),
            Template(directory="layouts"),
            WriteFile(clean=True),
        ],
    )
```
