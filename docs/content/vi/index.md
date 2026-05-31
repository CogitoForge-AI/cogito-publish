---
title: pyssg
nav_title: Trang chủ
order: 0
hero_eyebrow: Trình tạo trang tĩnh
---

Một trình tạo trang tĩnh xây quanh một **kernel siêu nhỏ** và kiến trúc
**plugin + lifecycle-hook kiểu webpack**. Kernel không biết gì về Markdown,
HTML hay template: mọi tính năng đều là một plugin tap vào các lifecycle hook.

Chính trang này được tạo bởi pyssg, dùng preset `i18n_docs()` có sẵn để phục vụ
cả tiếng Anh lẫn tiếng Việt từ một cây nguồn duy nhất.

<div class="features">
  <div class="feature">
    <h3>Kernel nhỏ, không phụ thuộc</h3>
    <p>Lõi thuần thư viện chuẩn. Nó chỉ điều phối một vòng đời và để các plugin làm việc.</p>
  </div>
  <div class="feature">
    <h3>Mọi thứ đều là plugin</h3>
    <p>Đọc file, phân tích frontmatter, render Markdown, dựng template, ghi ra đĩa - tất cả là plugin bạn có thể thay hoặc mở rộng.</p>
  </div>
  <div class="feature">
    <h3>Một mô hình nội dung chung</h3>
    <p>Permalink, collection, listing và navigation cùng nói một ngôn ngữ, nên template chỉ cần học site, page, collections và menus.</p>
  </div>
  <div class="feature">
    <h3>Preset thân thiện</h3>
    <p>docs(), blog() và site() cho bạn một bộ chạy được trong một dòng; người dùng nâng cao tự ráp plugin bằng tay.</p>
  </div>
</div>

## Nếm thử

```python
# pyssg.config.py
from pyssg.config import Config
from pyssg_cli.presets import docs


def config() -> Config:
    return Config(src="content", out="public", plugins=docs())
```

```bash
pyssg build
```

Đó là toàn bộ thiết lập đằng sau trang bạn đang đọc.

## Đi tiếp đâu

- **Mới đến?** Bắt đầu với [Bắt đầu nhanh](/vi/guide/getting-started/).
- **Đang dựng trang?** Học [Templating](/vi/templating/) và các [plugin có sẵn](/vi/plugins/built-in/).
- **Muốn hiểu bên trong?** Đọc tổng quan [Kiến trúc](/vi/architecture/) hoặc tìm hiểu [viết plugin](/vi/plugins/writing-plugins/).
