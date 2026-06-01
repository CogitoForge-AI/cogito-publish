---
title: Triển khai trang đã build
nav_title: Triển khai
order: 6
---

# Triển khai trang đã build

**Mục tiêu:** xuất bản đầu ra tĩnh do `build` tạo ra.

## 1. Tạo một bản build sạch

```bash
uv run python -m pyssg --site my-site build
```

Mọi thứ cần triển khai giờ nằm trong thư mục đầu ra (mặc định `dist/`; đặt
`output_dir` trong cấu hình để đổi). Đầu ra là một cây HTML, CSS và asset thuần -
không cần runtime máy chủ nào.

## 2. Đặt `base_url`

Nếu trang của bạn được phục vụ từ một đường dẫn con (ví dụ một trang dự án GitHub
Pages tại `https://user.github.io/repo`), hãy đặt `base_url` để các URL tuyệt đối
được sinh - sitemap, RSS feed và thẻ `hreflang` - đều chính xác:

```python
config = docs(
    site={"title": "My Docs"},
    base_url="https://user.github.io/repo",
)
```

## 3. Tải `dist/` lên

Trỏ bất kỳ host tĩnh nào vào thư mục đầu ra. Một vài đích phổ biến:

- **GitHub Pages** - đẩy nội dung `dist/` lên nhánh `gh-pages`, hoặc dùng một Pages
  action tải thư mục lên làm artifact.
- **Netlify / Cloudflare Pages / Vercel** - đặt lệnh build là
  `uv run python -m pyssg --site my-site build` và thư mục xuất bản là
  `my-site/dist`.
- **Bất kỳ web server / object storage nào** - sao chép `dist/` vào document root
  hoặc bucket.

## 4. Giữ build có thể tái lập trong CI

Build của pyssg là tất định: với cùng đầu vào, hai lần build cho ra kết quả giống
nhau từng byte. Trong CI, hãy chạy một lần `build` đầy đủ (cache là tối ưu, không
phải yêu cầu về tính đúng đắn) - truyền `--no-cache` nếu bạn muốn chứng minh một
bản build sạch từ đầu:

```bash
uv run python -m pyssg --site my-site build --no-cache
```

Để xóa thư mục đầu ra và cache ở máy cục bộ, dùng `clean`:

```bash
uv run python -m pyssg --site my-site clean --yes
```
