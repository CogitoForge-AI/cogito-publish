---
title: Viết plugin
order: 3
---

# Viết plugin

Một plugin là bất kỳ đối tượng nào có phương thức `apply(builder)`. Bên trong nó,
hãy tap vào những hook bạn quan tâm.

## Một plugin tối giản

Plugin này thêm ước lượng thời gian đọc vào metadata của mỗi trang:

```python
from pyssg.builder import Builder
from pyssg.build import Build
from pyssg.models import Source


class ReadingTime:
    def __init__(self, wpm: int = 200) -> None:
        self._wpm = wpm

    def apply(self, builder: Builder) -> None:
        builder.hooks.parse.tap("ReadingTime", self._estimate)

    def _estimate(self, source: Source, build: Build) -> None:
        words = len(source.body.split())
        source.meta["reading_time"] = max(1, round(words / self._wpm))
```

Dùng nó như bất kỳ plugin có sẵn nào:

```python
plugins = [..., ReadingTime(wpm=180), ...]
```

Và đọc nó trong một template:

```html
<span>{{ page.reading_time }} min read</span>
```

## Chọn một hook

| Bạn muốn... | Tap |
|-------------|-----|
| Phát hiện hoặc đọc file nguồn | `discover`, `load` |
| Phân tích hoặc chú thích một trang đơn lẻ | `parse` |
| Dựng dữ liệu toàn-trang (nav, group) | `collect` |
| Biến đổi nội dung body | `transform` (waterfall) |
| Tạo output từ một trang | `render` |
| Tạo các file dẫn xuất (rss, sitemap) | `generate` |
| Hậu xử lý mọi output | `optimize` |
| Ghi ra đĩa | `emit` |
| Báo cáo sau khi ghi | `after_emit` |

## Quy ước

- **Sắp thứ tự với `stage`.** Nếu plugin của bạn phải chạy trước hoặc sau một
  plugin khác trên cùng một hook, hãy đặt `stage` của nó. Số nhỏ hơn chạy trước.
- **Import lười các phụ thuộc nặng.** Import thư viện bên thứ ba bên trong phương
  thức dùng đến nó, không phải ở đầu module, để plugin có thể được cài đặt và soi
  xét mà không cần phụ thuộc đó hiện diện.
- **Tái dùng mô hình nội dung.** Đọc và ghi `build.meta["collections"]`,
  `["menus"]` và `["site"]` (xem `pyssg.content`) thay vì tự nghĩ ra khóa riêng,
  để plugin của bạn ghép được với các plugin có sẵn.
- **Đánh dấu trang nhân tạo.** Nếu bạn nối thêm một `Source` được sinh ra trong
  `collect`, hãy đặt `source.meta["generated"] = True` để các plugin khác phân
  biệt được nó với file thật.

## Plugin waterfall

Với `transform`, hãy trả về giá trị (có thể đã sửa đổi) để tap kế tiếp tiếp tục
đường ống:

```python
def apply(self, builder: Builder) -> None:
    builder.hooks.transform.tap("Anchors", self._add_anchors, stage=10)

def _add_anchors(self, source: Source, build: Build) -> Source:
    source.content = inject_heading_anchors(source.content)
    return source
```
