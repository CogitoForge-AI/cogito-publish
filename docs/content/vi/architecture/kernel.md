---
title: Kernel
order: 1
---

# Kernel

Kernel được thiết kế nhỏ một cách có chủ ý và **không có bất kỳ phụ thuộc bên thứ
ba nào** - nó thuần thư viện chuẩn. Mọi thứ trong đó đều rơi vào một trong số ít
module sau.

| Module | Trách nhiệm |
|--------|-------------|
| `hooks.py` | `SyncHook`, `SyncBailHook`, `SyncWaterfallHook`. |
| `builder.py` | `Builder` (bộ điều phối vòng đời) và `BuilderHooks`. |
| `build.py` | `Build`, trạng thái của một lần chạy. |
| `models.py` | `Source` và `Output`, các túi dữ liệu trung tính. |
| `plugin.py` | Protocol `Plugin`. |
| `config.py` | `Config` và việc nạp `pyssg.config.py`. |
| `cli.py` | Điểm vào `pyssg build`. |

## Không phụ thuộc theo thiết kế

Quy tắc rất đơn giản: **kernel chỉ dùng thư viện chuẩn; plugin được dùng bất cứ
thứ gì chúng cần.** Điều này hóa giải mâu thuẫn giữa "giữ phụ thuộc tối thiểu" và
"chúng ta cần một bộ phân tích Markdown thực thụ". Kernel luôn sạch sẽ, trong khi
một plugin như `Markdown` thoải mái phụ thuộc vào `python-markdown`, được import
lười (lazy) nên chi phí chỉ phải trả khi plugin thực sự được dùng.

## Protocol plugin

Một plugin là bất kỳ đối tượng nào có phương thức `apply`:

```python
class Plugin(Protocol):
    def apply(self, builder: Builder) -> None: ...
```

Bên trong `apply`, plugin tap vào những hook nó quan tâm. Đó là toàn bộ hợp đồng
giữa kernel và các phần mở rộng của nó.

## Builder

`Builder` được tạo từ một `Config`. Khi khởi tạo, nó áp dụng mọi plugin (gọi
`apply`), rồi phát hook `initialize`. Gọi `run()` sẽ thực thi trọn một
[vòng đời](/vi/architecture/lifecycle/) và trả về `Build` thu được.

Vì builder là một đối tượng sống lâu, nó là nơi tự nhiên cho một chế độ watch
trong tương lai - rebuild khi file thay đổi - mà không phải sửa bất kỳ plugin nào.
