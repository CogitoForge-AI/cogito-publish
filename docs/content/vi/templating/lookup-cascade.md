---
title: Lookup cascade
order: 3
---

# Lookup cascade

Thay vì bắt mỗi trang khai báo dùng template nào, pyssg phân giải template tự
động từ type, section và kind của trang - cùng một ý tưởng với template lookup
của Hugo. Thả một `blog/single.html` vào layouts của bạn và mọi bài blog dùng nó,
không cần frontmatter.

## Thứ tự

Với mỗi trang, plugin thử các tên sau theo thứ tự và dùng tên đầu tiên tồn tại:

```text
1. <frontmatter layout>        explicit override, always wins
2. <type>/<kind>.html          e.g. blog/single.html
3. <section>/<kind>.html       e.g. <top folder>/list.html
4. _default/<kind>.html        e.g. _default/single.html
5. <kind>.html                 e.g. list.html
6. <default_layout>            final fallback (default.html)
```

## Các biến

- **`kind`** là `list` cho các trang listing được sinh ra (trang tag, chỉ mục
  blog) và `single` cho mọi thứ còn lại. pyssg đặt nó từ cờ `generated` của trang,
  nên bạn không phải quản lý nó bằng tay.
- **`type`** đến từ frontmatter `type`. Dùng nó để gán cho một nhóm trang một
  template riêng biệt bất kể chúng nằm ở đâu: `type: tutorial` ->
  `tutorial/single.html`.
- **`section`** là thư mục cấp cao nhất của đường dẫn nguồn. Một file tại
  `blog/hello.md` có section là `blog`.

## Ví dụ

| Trang | Template được phân giải (tên đầu tiên tồn tại) |
|-------|-----------------------------------------------|
| `blog/hello.md` | `blog/single.html` -> `_default/single.html` -> `default.html` |
| `blog/hello.md` với `type: featured` | `featured/single.html` -> `blog/single.html` -> ... |
| một trang tag được sinh ra trong `tags/` | `tags/list.html` -> `_default/list.html` -> ... |
| `about.md` (gốc) | `_default/single.html` -> `single.html` -> `default.html` |
| bất kỳ trang nào có `layout: special.html` | `special.html` trước tiên |

## Vì sao nó quan trọng

Cascade là thứ biến một thư mục layout thành một *theme* tái dùng được. Một trang
chỉ cần `layout` cho những trường hợp thực sự cá biệt; trường hợp thông dụng -
"mọi bài viết trông như thế này, mọi trang danh sách trông như thế kia" - được
diễn đạt một lần trong `_default/single.html` và `_default/list.html`. Trang này
không khai báo `layout` trong bất kỳ file nội dung nào; nó hoàn toàn được điều
khiển bởi cascade.
