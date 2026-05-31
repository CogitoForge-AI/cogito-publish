---
title: Kế thừa
order: 1
---

# Kế thừa

Kế thừa template cho phép bạn định nghĩa bộ khung trang một lần và để mỗi layout
điền vào những phần thay đổi. pyssg dùng `{% extends %}` và `{% block %}` native
của Jinja2 - không có gì thêm để học hay bật.

## Một bộ khung gốc

Đặt phần HTML dùng chung trong một template gốc với các block có tên cho những
phần biến thiên:

```html
<!-- layouts/base.html -->
<!doctype html>
<html lang="en">
<head>
  <title>{% block title %}{{ site.title }}{% endblock %}</title>
  <link rel="stylesheet" href="/assets/style.css">
</head>
<body>
  <main>{% block main %}{% endblock %}</main>
</body>
</html>
```

## Mở rộng nó

Một layout cụ thể mở rộng bộ gốc và ghi đè các block:

```html
<!-- layouts/_default/single.html -->
{% extends "base.html" %}

{% block main %}
  <article>{{ content }}</article>
{% endblock %}
```

Bất cứ thứ gì không bị ghi đè sẽ rơi xuống giá trị mặc định của bộ gốc. Bạn có
thể lồng kế thừa sâu tùy thích - một layout section có thể mở rộng một bộ gốc,
bộ này lại mở rộng một bộ khung gốc nữa.

## Quy ước

Layout tham chiếu mà preset `docs()` dùng được tổ chức như sau:

```text
layouts/
  base.html              # the skeleton every page shares
  _default/
    single.html          # extends base.html - normal pages
    list.html            # extends base.html - listing pages
  partials/              # reusable snippets (see Partials)
```

Xem [lookup cascade](/vi/templating/lookup-cascade/) để biết `single.html` và
`list.html` được chọn tự động ra sao.
