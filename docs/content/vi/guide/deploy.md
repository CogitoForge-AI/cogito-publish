---
title: Triển khai
order: 4
---

# Triển khai

Một bản build pyssg là một thư mục thuần các file tĩnh (mặc định là `public/`),
nên nó host ở đâu cũng được. Hướng dẫn này bao quát các công thức dựng sẵn cho ba
nền tảng miễn phí phổ biến nhất. Cấu hình sao-chép-dán nằm trong
[`recipes/deploy/`](https://github.com/your-org/pyssg/tree/main/recipes/deploy).

## Hai điều cần kiểm tra trước

**Phục vụ từ gốc domain.** pyssg phát ra các liên kết tuyệt-đối-từ-gốc (`/blog/`,
`/style.css`), nên trang phải nằm tại gốc của một domain. Một domain tùy chỉnh,
một trang user/org dạng `<user>.github.io`, một subdomain Netlify và một subdomain
`*.pages.dev` đều thỏa điều kiện. Một **project site** trên GitHub Pages tại
`user.github.io/<repo>/` phục vụ từ một subpath và hiện chưa được hỗ trợ -- điều
đó cần tính năng `base_url`, đang được theo dõi trong roadmap.

**Đặt một URL chính tắc (canonical) cho site** để các plugin Sitemap và RSS phát
ra URL tuyệt đối:

```python
Config(..., options={"base_url": "https://your-domain.example"})
```

## GitHub Pages

1. Sao chép `recipes/deploy/github-pages/deploy.yml` thành
   `.github/workflows/deploy.yml`.
2. Sao chép `recipes/deploy/github-pages/.nojekyll` vào gốc dự án (nó ngăn GitHub
   chạy output qua Jekyll).
3. Trong repo, đặt **Settings -> Pages -> Source** thành "GitHub Actions".
4. Push lên `main`. Workflow build bằng uv và xuất bản artifact:

```yaml
- uses: astral-sh/setup-uv@v5
- run: uv run --python 3.13 --with "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git" pyssg build
- uses: actions/upload-pages-artifact@v3
  with:
    path: public
```

Với một domain tùy chỉnh, thêm một file `CNAME` chứa domain của bạn vào `public/`
(ví dụ bằng một mục `StaticFiles`).

## Netlify

Sao chép `recipes/deploy/netlify/netlify.toml` vào gốc dự án và kết nối repository
trong Netlify. Image của Netlify có sẵn Python nhưng không có uv, nên bản build
dùng pip:

```toml
[build]
  command = "pip install 'pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git' && pyssg build"
  publish = "public"

[build.environment]
  PYTHON_VERSION = "3.13"
```

## Cloudflare Pages

Tạo một dự án Pages từ repository của bạn và đặt:

- **Build command:** `pip install "pyssg[plugins] @ git+https://github.com/magiskboy/pyssg.git" && pyssg build`
- **Build output directory:** `public`
- **Environment variable:** `PYTHON_VERSION = 3.13`

Thích triển khai theo CI hơn? Dùng `recipes/deploy/cloudflare-pages/deploy.yml`,
file này build trong GitHub Actions và upload bằng Wrangler (cần các secret
`CLOUDFLARE_API_TOKEN` và `CLOUDFLARE_ACCOUNT_ID`).

## Các host khác

Mọi host tĩnh đều dùng được: build cục bộ bằng `pyssg build` và upload `public/`.
Các công thức ở trên được mô tả bởi một manifest `deploy.toml` nhỏ cho mỗi đích,
nên thêm nền tảng mới rất dễ -- xem
[README của recipes](https://github.com/your-org/pyssg/tree/main/recipes/deploy).
