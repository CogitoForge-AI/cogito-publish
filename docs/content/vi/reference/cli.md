---
title: Tham chiếu CLI
nav_title: CLI
order: 2
---

# Tham chiếu CLI

pyssg được gọi như một module: `python -m pyssg [--site PATH] <command> [options]`.
Qua uv là `pyssg ...`.

## Tùy chọn toàn cục

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--site PATH` | `.` | Thư mục trang. Mọi đường dẫn khác trong cấu hình (`content_dir`, `output_dir`, `layout`) đều tương đối so với nó. |

Chạy bất kỳ lệnh nào với `--help` để xem các tùy chọn của nó.

## `init`

Khởi tạo một trang mới cho một preset.

```bash
pyssg --site my-site init --preset docs
```

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--preset {docs,blog}` | `docs` | Preset nào để khởi tạo. |
| `--force` | tắt | Ghi đè `pyssg.config.py` đã tồn tại (nếu không `init` sẽ từ chối để tránh làm hỏng một trang thật). |

Ghi một `pyssg.config.py` một dòng cùng ít nội dung mẫu. Việc khởi tạo là tất định:
ngày tháng mẫu là các hằng cố định, nên chạy hai lần cho ra các file giống hệt.

## `build`

Build đầy đủ ra thư mục đầu ra.

```bash
pyssg --site my-site build
```

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--no-cache` | tắt | Bỏ qua cache bền vững (chứng minh một bản build sạch từ đầu). |
| `--profile` | tắt | In số lượng node "chạm" theo từng pha và số lần trúng cache. |

In ra `build: N pages written`.

## `serve`

Theo dõi nội dung, build lại tăng tiến, và phục vụ kèm tự nạp lại.

```bash
pyssg --site my-site serve
```

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--host HOST` | `127.0.0.1` | Địa chỉ để bind. |
| `--port PORT` | `8000` | Cổng để bind. |
| `--no-cache` | tắt | Bỏ qua cache bền vững. |

Sửa bất kỳ file nào dưới `content/` và trang bị ảnh hưởng sẽ build lại, trình duyệt
tự nạp lại.

## `clean`

Xóa thư mục đầu ra và cache.

```bash
pyssg --site my-site clean
```

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--yes` | tắt | Bỏ qua bước xác nhận tương tác. |

Khi không có `--yes`, `clean` liệt kê những gì sẽ xóa và hỏi xác nhận.

## `eject-layout`

Sao chép một theme tích hợp vào trang để bạn có thể tùy biến.

```bash
pyssg --site my-site eject-layout --theme docs --to layouts/theme
```

| Tùy chọn | Mặc định | Mô tả |
|---|---|---|
| `--theme {docs,blog}` | *(bắt buộc)* | Theme tích hợp để sao chép. |
| `--to DIR` | `layouts/theme` | Thư mục đích, tương đối so với trang. |

Từ chối ghi đè lên một đích đã tồn tại. Sau khi sao chép, đặt `layout="<DIR>"`
trong `pyssg.config.py`. Xem [Tùy biến theme](../how-to/customize-theme.md).
