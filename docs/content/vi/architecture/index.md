---
title: Kiến trúc
order: 4
---

# Kiến trúc

pyssg mượn thiết kế lõi từ webpack. Bốn ý tưởng cốt lõi chống đỡ cả hệ thống:

| webpack | pyssg | Vai trò |
|---------|-------|---------|
| Tapable | hệ thống hook | Hệ thần kinh: các lifecycle hook có kiểu rõ ràng. |
| Compiler | `Builder` | Bộ điều phối sống lâu; sở hữu các hook. |
| Compilation | `Build` | Trạng thái của một lần build. |
| Plugin | `Plugin` | Một đối tượng có `apply(builder)` để tap vào hook. |

Đặc tính then chốt: **kernel chỉ phát ra sự kiện tại các cột mốc của vòng đời.**
Plugin đăng ký listener và làm phần việc thực sự - kể cả các tác vụ "lõi" như
đọc file hay render Markdown cũng là plugin.

## Trong mục này

- [Kernel](/vi/architecture/kernel/) - những gì nằm trong lõi và vì sao nó lại
  nhỏ đến vậy.
- [Vòng đời](/vi/architecture/lifecycle/) - các pass theo từng giai đoạn mà một
  lần build đi qua.
- [Hook](/vi/architecture/hooks/) - ba loại hook và cách thứ tự `stage` hoạt động.

## Mô hình dữ liệu

Hai túi dữ liệu trung tính chảy qua vòng đời:

- **`Source`** - một file đầu vào. Plugin lần lượt điền `raw`, `body`,
  `frontmatter`, `content` và `meta` khi nó đi qua các pass.
- **`Output`** - một file sẽ được ghi ra. Có `path` (tương đối với `out`) và
  `content`.

Kernel không bao giờ soi vào nội dung của chúng ngoài việc chuyển chúng giữa các
hook; ý nghĩa của chúng hoàn toàn do plugin quyết định.
