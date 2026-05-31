---
title: Partial
order: 2
---

# Partial

Partial là các đoạn template tái dùng được - một header, một card, một thanh phân
trang. pyssg bổ sung một hàm `partial()`, mô phỏng theo Hugo, bên cạnh
`{% include %}` và macro native của Jinja2.

## Hàm `partial()`

```html
{{ partial("partials/card.html", {"item": entry}) }}
```

`partial(name, context=None)`:

- render template có tên với một ngữ cảnh **tường minh**;
- tự động gộp vào `site`, `menus` và `collections`, nên một partial luôn vươn tới
  được dữ liệu toàn-trang;
- trả về markup an toàn, nên kết quả không bị escape hai lần;
- chấp nhận một tên có hoặc không có hậu tố `.html`.

Đây là cách được khuyến nghị để dựng component, vì dữ liệu một partial nhìn thấy
đúng bằng những gì bạn truyền vào nó - không có bất ngờ từ scope kế thừa.

## Ví dụ: một component có tham số

```html
<!-- layouts/partials/badge.html -->
<span class="badge badge-{{ kind }}">{{ label }}</span>
```

```html
{{ partial("partials/badge.html", {"label": "New", "kind": "info"}) }}
```

## Quy ước

Giữ các đoạn mã dưới `layouts/partials/`. Trang tham chiếu tách phần "khung viền"
của nó thành các partial để mỗi layout luôn nhỏ gọn:

```text
layouts/partials/
  topbar.html
  sidebar.html
  prevnext.html
  footer.html
  entry.html       # one item in a listing
```

Một layout khi đó đọc gần như một bản phác thảo (outline):

```html
{% extends "base.html" %}
{% block main %}
  <article>{{ content }}</article>
  {{ partial("partials/prevnext.html", {"prev": page.prev, "next": page.next}) }}
{% endblock %}
```

## Jinja2 native vẫn dùng được

Nếu bạn thích các tính năng dựng sẵn của Jinja2, chúng vẫn có sẵn nguyên vẹn:

```html
{% include "partials/topbar.html" %}

{% from "partials/macros.html" import card %}
{{ card(entry) }}
```

Dùng `{% include %}` cho các đoạn tĩnh, macro cho component có tham số, hoặc
`partial()` khi bạn muốn ngữ cảnh tường minh kiểu Hugo kèm dữ liệu site.
