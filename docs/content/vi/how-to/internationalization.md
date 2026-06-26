---
title: Thêm quốc tế hóa (i18n)
nav_title: Quốc tế hóa
order: 2
---

# Thêm quốc tế hóa (i18n)

**Mục tiêu:** phục vụ cùng một trang ở nhiều ngôn ngữ, kèm bộ chuyển ngôn ngữ và
thẻ `hreflang` đúng, mà không bao giờ liên kết tới một bản dịch thiếu.

## 1. Thêm plugin

Plugin `i18n` được tích hợp sẵn. Thêm nó vào một preset qua `extra_plugins`:

```python
from __future__ import annotations

from pyssg.presets import docs
from pyssg.plugins import i18n

config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
    extra_plugins=[i18n(default_locale="en", locales=["en", "vi"])],
)
```

## 2. Sắp xếp nội dung mỗi locale một thư mục

Locale là **thư mục cấp cao nhất** dưới `content/` - không có cách ghi đè bằng
frontmatter:

```
content/
  en/index.md          ->  /            (locale mặc định, phục vụ ở gốc)
  en/guide/intro.md    ->  /guide/intro/
  vi/index.md          ->  /vi/
  vi/guide/intro.md    ->  /vi/guide/intro/
```

Các quy tắc được giữ đơn giản có chủ đích:

- **Locale mặc định** được phục vụ ở gốc trang (tiền tố bị lược bỏ); mọi locale
  khác giữ tiền tố `/<locale>/` của nó.
- Nội dung **nằm ngoài** mọi thư mục locale sẽ không sinh trang.
- Trang chỉ được sinh cho những locale **thực sự có file** - không có cơ chế dự
  phòng nội dung, nên bộ chuyển ngôn ngữ không bao giờ trỏ tới bản dịch thiếu.

## 3. Dùng các biến template

Plugin cấp cho mỗi trang ba biến template bổ sung:

- `lang` - locale của trang hiện tại.
- `translations` - chính trang đó ở các locale khác, mỗi mục `{lang, url, title}`.
- `languages` - tất cả locale đã cấu hình.

Các theme tích hợp `docs` và `blog` đã dùng chúng để render `<html lang>`, các bản
thay thế `hreflang` và một bộ chuyển ở header, nên với bố cục trên bạn có ngay một
trang song ngữ chạy được.

## 4. Build và kiểm tra

```bash
cogito-publish --site my-site build
```

Trang tiếng Anh xuất hiện ở gốc và trang tiếng Việt nằm dưới `/vi/`. Xem
`examples/docs/` trong kho mã để có một ví dụ song ngữ hoàn chỉnh.
