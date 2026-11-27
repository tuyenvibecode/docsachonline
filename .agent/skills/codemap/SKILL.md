---
name: codemap
description: Dùng CODEMAP.md để tìm đúng file và đúng dòng cần sửa mà không phải mở cả dự án, và cập nhật lại bản đồ sau khi sửa code. Dùng ở đầu mọi việc liên quan tới code.
---

# Codemap

`CODEMAP.md` ở thư mục gốc là bản đồ tự sinh của dự án.

## Đọc bản đồ

1. Mở `CODEMAP.md`, nhìn bảng "Việc gì thì mở file nào".
2. Tìm hàm cần sửa trong mục Python hoặc Web, ghi lại số dòng.
3. Read file đó với `offset` = số dòng, `limit` khoảng 40–80 dòng.
4. Cần xem dữ liệu sách thì dùng lệnh nhỏ in vài trăm ký tự (có trong bản đồ), không mở nguyên file.

## Cập nhật bản đồ

```bash
python tools/codemap.py          # ghi lại CODEMAP.md
python tools/codemap.py --check  # chỉ kiểm tra có lỗi thời không
```

Chạy sau khi: thêm hoặc xóa file, thêm hoặc đổi hàm, sửa làm lệch số dòng, thêm rule/workflow/skill.
`python tools/verify.py` cũng kiểm tra bản đồ và báo lỗi nếu lỗi thời. `python tools/sync.py` tự cập nhật trước khi commit.

## Mô tả hàm lấy từ đâu

Bản đồ lấy mô tả từ dòng đầu của docstring. Viết hàm mới thì cho nó một docstring một dòng (tiếng Việt, nói hàm làm gì), bản đồ sẽ tự có mô tả.
Không sửa `CODEMAP.md` bằng tay; muốn đổi bảng "Việc gì thì mở file nào" thì sửa `HEADER` trong `tools/codemap.py`.
