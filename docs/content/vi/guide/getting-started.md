---
title: Bắt đầu nhanh
order: 1
---

# Bắt đầu nhanh

Hướng dẫn này đưa bạn từ một thư mục rỗng đến một trang đã build xong.

## Yêu cầu

- Python 3.13 trở lên
- [uv](https://github.com/astral-sh/uv) (khuyến nghị) hoặc pip

## Cài đặt

pyssg cài trực tiếp từ GitHub - chưa publish lên PyPI. Kernel không có phụ thuộc;
các plugin có sẵn `Markdown`, `Template` và `Highlight` cần thư viện bên thứ ba,
gói trong extra `plugins`:

```bash
# uv (khuyến nghị)
uv add "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git"
# pip
pip install "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git"
```

Ghim vào một tag đã phát hành bằng cách thêm `@v0.1.0` vào URL.

## Bố cục dự án

Một dự án điển hình trông như sau:

```text
my-site/
  content/            # nguồn Markdown của bạn
    index.md
    guide/
      intro.md
  layouts/            # template Jinja2
    default.html
    list.html
  pyssg.config.py     # cấu hình
  public/             # output build (tự sinh)
```

Thư mục `layouts/` nằm cạnh `content/`. Plugin `Template` mặc định tìm template
trong `<src>/../layouts`.

## Viết nội dung

```text
---
title: Hello
---
# Hello world

This is **Markdown**.
```

Khối giữa hai hàng `---` là *frontmatter*: metadata cho từng trang mà template và
plugin có thể đọc.

## Thêm một layout

```html
<!-- layouts/default.html -->
<!doctype html>
<title>{{ page.title }}</title>
<main>{{ content }}</main>
```

`content` là phần thân HTML đã render; `page` lộ ra frontmatter.

## Cấu hình

```python
# pyssg.config.py
from pyssg.config import Config
from pyssg_cli.presets import docs


def config() -> Config:
    return Config(src="content", out="public", plugins=docs())
```

## Build

```bash
pyssg build
```

Trang của bạn giờ nằm trong `public/`. Để dùng file cấu hình ở vị trí khác:

```bash
pyssg build -c path/to/pyssg.config.py
```

Tiếp theo: tìm hiểu chi tiết các tùy chọn [cấu hình](/en/guide/configuration/)
(bản tiếng Việt sẽ bổ sung sau).
