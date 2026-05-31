---
title: Dev server
order: 3
---

# Dev server

`pyssg serve` build trang của bạn, phục vụ nó cục bộ, và tự động rebuild mỗi khi
một file nguồn thay đổi. Khi live reload bật (mặc định), trình duyệt tự làm mới
sau mỗi lần rebuild.

```bash
pyssg serve
```

```text
pyssg serve serving /path/to/public at http://127.0.0.1:8000/
Watching for changes (watchdog backend)... (Ctrl-C to stop)
Change detected (1 file(s)); rebuilding...
Rebuilt.
```

Mở URL được in ra và bắt đầu chỉnh sửa. Dừng server bằng `Ctrl-C`.

## Tùy chọn

| Cờ | Mặc định | Ý nghĩa |
|----|----------|---------|
| `-c`, `--config` | `pyssg.config.py` | File cấu hình để nạp. |
| `--host` | `127.0.0.1` | Địa chỉ để bind. |
| `--port` | `8000` | Cổng để bind. |
| `--no-livereload` | tắt | Vô hiệu hóa tự động reload trình duyệt. |
| `--open` | tắt | Mở trang trong trình duyệt mặc định khi server khởi động. |

```bash
pyssg serve --port 3000 --open
```

## Cách nó hoạt động

`pyssg serve` không phải là tính năng của kernel - nó là plugin `DevServer`. Vì
một `Builder` có thể tái sử dụng (mỗi `run()` tạo ra một build mới tinh), cả vòng
lặp watch nằm gọn trong một plugin tap vào hook `done`:

1. Lần build đầu tiên hoàn tất và phát `done`.
2. `DevServer` khởi động một thread HTTP server cho thư mục output, rồi vào một
   vòng lặp watch chặn (blocking).
3. Khi có file thay đổi, nó gọi lại `builder.run()` và tăng một token reload.
4. Script live-reload được tiêm vào sẽ poll token đó và reload khi có thay đổi.

Việc theo dõi file dùng [watchdog](https://pypi.org/project/watchdog/) (dựa trên
sự kiện) khi nó được cài đặt - bật nó bằng extra `dev` (`uv sync --extra dev`).
Khi không có watchdog, nó quay về polling mtime bằng thư viện chuẩn, nên kernel
vẫn giữ được bảo đảm chỉ-dùng-stdlib trong cả hai trường hợp. Thư mục output
không bao giờ bị theo dõi (ghi vào nó sẽ lặp vô tận).

## Lưu ý

- **Thay đổi cấu hình cần khởi động lại.** Sửa `pyssg.config.py` có thể đổi danh
  sách plugin, vốn được cố định khi builder được tạo. `pyssg serve` phát hiện
  thay đổi và in lời nhắc; khởi động lại để áp dụng.
- **404 thoáng qua khi rebuild.** Với `clean=True` (mặc định của preset) thư mục
  output được tạo lại trong mỗi lần build, nên một request rơi vào giữa lúc
  rebuild có thể 404 thoáng qua. Live reload sẽ thử lại ở lần poll kế tiếp.
- **Lỗi build vẫn tiếp tục phục vụ.** Nếu một lần rebuild thất bại, lỗi được in
  ra và output tốt cuối cùng được giữ lại; sửa nguồn và lưu lại.

## Dùng trong cấu hình

`pyssg serve` tự nối thêm một `DevServer`, nên thường bạn không phải cấu hình gì.
Để có mặc định tùy chỉnh, bạn có thể tự thêm nó - nó chỉ là một plugin:

```python
from pyssg_plugins import DevServer

# ... DevServer(host="0.0.0.0", port=4000, livereload=False)
```
