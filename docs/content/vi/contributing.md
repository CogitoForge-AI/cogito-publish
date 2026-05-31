---
title: Đóng góp
order: 5
---

# Đóng góp

Cảm ơn bạn đã quan tâm đến việc cải thiện pyssg. Trang này là một định hướng ngắn
gọn; danh sách kiểm tra chính thức nằm trong
[`CONTRIBUTING.md`](https://github.com/magiskboy/pyssg/blob/main/CONTRIBUTING.md)
tại repository.

## Thiết lập môi trường phát triển

pyssg dùng [uv](https://docs.astral.sh/uv/) và nhắm tới Python 3.13.

```bash
git clone https://github.com/magiskboy/pyssg.git
cd pyssg
uv sync --all-extras      # runtime extras + dev tools (ruff, mypy, types)
source .venv/bin/activate
```

`--all-extras` kéo về mọi phụ thuộc tùy chọn (markdown, jinja2, pyyaml, pygments,
watchdog) để bộ test đầy đủ và kiểm tra kiểu chạy được.

## Các bước kiểm tra

Cả bốn đều phải qua trước khi một pull request được merge; CI chạy đúng những
lệnh này trên Linux, macOS và Windows.

```bash
ruff check .              # lint
ruff format --check .     # formatting
mypy                      # strict type checking
python -m unittest discover -s tests
```

## Quy ước

- **Python 3.13** với kiểu nghiêm ngặt. `mypy` chạy ở chế độ `strict`.
- **Chỉ tiếng Anh trong code** - định danh, comment, docstring, chuỗi log và lỗi.
- **Giữ kernel không phụ thuộc.** Các phụ thuộc bên thứ ba thuộc về plugin trong
  `pyssg_plugins`, khai báo dưới dạng extras tùy chọn và import lười.
- **Ưu tiên đơn giản hơn khôn lỏi.** Chuộng code rõ ràng hơn comment chỉ để lặp
  lại điều code đã nói.
- **Mỗi thay đổi đi kèm test** dùng module `unittest` của stdlib. Phòng ngừa hồi
  quy (regression).
- Với tính năng mới hay thay đổi thiết kế, mở một issue để bàn cách tiếp cận
  trước.

## Pull request

1. Tách nhánh từ `dev`.
2. Thực hiện thay đổi kèm test và các bước kiểm tra đều qua.
3. Mở một PR nhắm vào `dev` và điền vào checklist trong template.

Để hiểu codebase trước khi lao vào, hãy đọc mục
[Kiến trúc](/vi/architecture/) - nó dẫn bạn qua kernel, vòng đời và hệ thống hook
mà mọi plugin xây dựng dựa trên đó.
