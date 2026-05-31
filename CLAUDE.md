
# Quy tắc

- Tuân thủ các quy tắc của Python 3.13
- Tuân thủ nghiêm ngặt type checking của Python
- Simple first, performance và clean code
- Không sử dụng emoji, viết code chuẩn design thay vì lạm dụng comment
- Trong code (comment, docstring, tên định danh, chuỗi log/error) chỉ sử dụng tiếng Anh
- Khi phản hồi người dùng chỉ sử dụng tiếng Việt

# Kiến trúc

- Ba package phân lớp trong một wheel: `pyssg` (kernel) <- `pyssg_plugins` <- `pyssg_cli`; ranh giới được enforce bởi test
- Kernel `pyssg` chỉ dùng stdlib, không phụ thuộc bên thứ ba
- Thư viện bên thứ ba thuộc về plugin: khai báo optional extras trong pyproject và import lazy

# Development

- Sử dụng uv - python làm python package manager
- Luôn sử dụng virtualenv thông qua: source .venv/bin/activate
- Hạn chế sử dụng thư viện bên thứ 3 (công cụ dev như coverage không tính là runtime dependency)
- Những tính năng / design mới nên brainstorm trước khi thực hiện
- Trước khi push, chạy đủ các check như CI: `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`

# Testing

- Luôn có unit test cho từng đoạn code tự viết
- Chỉ sư dụng unittest module có săn của Python
- Chạy test: `uv run python -m unittest discover -s tests`
- Tuân thủ test regression
- CI đo branch coverage và fail nếu dưới 85% (ngưỡng `fail_under` trong pyproject)