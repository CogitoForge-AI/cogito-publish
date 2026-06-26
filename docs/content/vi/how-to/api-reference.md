---
title: Sinh API reference
nav_title: Sinh API reference
order: 4
---

# Sinh API reference

**Mục tiêu:** xuất bản một mục `References` được dựng tự động từ docstring của một
gói Python - chính là mục bạn thấy trong thanh bên của trang này.

Việc này được làm bằng plugin contrib `apidoc` (`pyssg.contrib.apidoc`). Các plugin
contrib không được tự động re-export vào `pyssg.plugins`; hãy import chúng từ module
của chúng.

## Cách hoạt động

`apidoc` đọc gói của bạn **tĩnh** bằng module `ast` - mã của bạn không bao giờ bị
import hay thực thi. Với mỗi module, nó biến docstring thành một tài liệu Markdown
ảo và đưa qua pipeline thông thường (markdown -> permalink -> nav -> render). Vì
các trang được sinh có chung tiền tố URL (mặc định `/references/`), plugin `nav` tự
động gom chúng vào một mục **References** duy nhất.

Docstring viết theo phong cách **Google**, **NumPy** hoặc **reStructuredText** được
phân tích thành các bảng tham số / giá trị trả về / ngoại lệ có cấu trúc; mọi đoạn
văn khác được giữ nguyên văn. Không có gì bị ghi ngược lại vào thư mục `content/`.

## 1. Thêm plugin

```python
from __future__ import annotations

from pyssg.contrib.apidoc import apidoc
from pyssg.presets import docs

config = docs(
    site={"title": "My Docs"},
    base_url="https://example.com",
    extra_plugins=[
        apidoc(package="../mypackage", route="/references/"),
    ],
)
```

`package` được phân giải so với **thư mục trang**: nếu trang của bạn nằm ở `docs/`
và gói ở `mypackage/` tại gốc kho mã, hãy dùng `"../mypackage"`. Đường dẫn tuyệt
đối cũng được. Bạn cũng có thể trỏ tới một file `.py` đơn lẻ.

## 2. Tùy chọn

| Tùy chọn | Mặc định | Ý nghĩa |
|---|---|---|
| `package` | *(bắt buộc)* | Thư mục gói hoặc file module đơn lẻ (tương đối so với gốc trang, hoặc tuyệt đối). |
| `route` | `"/references/"` | Tiền tố URL cho các trang được sinh. |
| `include_private` | `False` | Bao gồm các thành viên và module dạng `_name`. |
| `include_dunder` | `False` | Bao gồm các thành viên `__dunder__` (`__init__` luôn được hiển thị). |

## 3. Build

```bash
cogito-publish --site docs build
```

Các trang reference xuất hiện dưới route bạn chọn, mỗi module một trang, sắp theo
tên dotted, và được gom vào mục References của thanh bên.

## Lưu ý về build tăng tiến

Các tài liệu ảo được tạo một lần mỗi phiên build (trong hook `make`). Một lần
`build` đầy đủ - và mỗi lần khởi động `serve` - phản ánh trạng thái hiện tại của
các file `.py`. Việc hot-reload trực tiếp khi một file `.py` thay đổi giữa lúc
`serve` được cố ý để ngoài phạm vi: hãy khởi động lại `serve` hoặc chạy `build` để
cập nhật thay đổi trong mã.

## Chính trang này

Trang bạn đang đọc được sinh đúng bằng thiết lập này. Xem
[`docs/pyssg.config.py`](https://github.com/CogitoForge-AI/cogito-publish/blob/main/docs/pyssg.config.py)
- nó thêm `apidoc(package="../pyssg", route="/references/")` lên trên preset `docs`,
và đó chính là thứ tạo ra mục [References](/references/pyssg/) trong thanh bên.
