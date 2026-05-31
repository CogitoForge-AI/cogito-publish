---
title: Hook
order: 3
---

# Hook

Hệ thống hook là phiên bản Tapable của webpack trong pyssg. Nó cung cấp ba loại
hook đồng bộ - đủ để diễn đạt mọi nhu cầu của một SSG.

## Ba loại hook

### SyncHook

Phát một sự kiện và gọi mọi tap theo thứ tự. Giá trị trả về bị bỏ qua. Dùng cho
các tác dụng phụ (side effect) như ghi file.

```python
builder.hooks.emit.tap("WriteFile", self._emit)
```

### SyncBailHook

Gọi các tap theo thứ tự và dừng lại ở tap đầu tiên trả về giá trị khác `None`,
rồi trả về giá trị đó. Hoàn hảo cho câu hỏi "plugin nào xử lý cái này?".

```python
# "Ai đọc được loại file này?" - reader đầu tiên thắng.
```

### SyncWaterfallHook

Luồn một giá trị qua mọi tap: kết quả của tap này trở thành đầu vào của tap kế
tiếp. Tap trả về `None` nghĩa là "không thay đổi". Đây là trái tim của việc biến
đổi nội dung.

```python
builder.hooks.transform.tap("Markdown", self._render)
# Markdown -> HTML -> thêm anchor -> highlight code -> ...
```

## Sắp thứ tự với `stage`

Mỗi tap mang một `stage` (mặc định `0`). Các tap chạy theo thứ tự stage tăng dần;
trong cùng một stage, thứ tự đăng ký được giữ nguyên. Đây là cách các plugin dùng
chung một hook phối hợp với nhau mà không cần biết nhau.

```python
builder.hooks.transform.tap("base", fn, stage=0)
builder.hooks.transform.tap("wrap", fn, stage=10)   # chạy sau "base"
```

Các plugin tier-2 dùng stage để sắp thứ tự công việc bên trong cùng một pass
`collect`: Permalink (`-200`) gán URL trước, rồi Collections (`-100`) gom nhóm
các trang, rồi Listing (`0`) dựng các trang danh sách, rồi Navigation (`100`)
dựng menu khi mọi trang (kể cả trang sinh ra tự động) đã tồn tại.

## Kiểu (typing)

Hook là generic theo các tham số vị trí của nó nhờ `TypeVarTuple`, cho ra chữ ký
tự nhiên:

```python
self.transform: SyncWaterfallHook[Source, Build]
self.render: SyncHook[Source, Build]
```
