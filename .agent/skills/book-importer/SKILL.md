---
name: book-importer
description: Nhập một cuốn sách vào thư viện bằng tools/import_book.py từ file của chủ dự án (txt/docx/pdf). Dùng khi cần thêm sách mới.
---

# Nhập sách

## Lệnh

```bash
# File của chủ dự án (đặt vào inbox/ trước). Hiện chỉ có nguồn "local"
python tools/import_book.py local inbox/sach.pdf --dry-run
# thêm --title "Tên" --author "Tên" nếu muốn; không có thì tự điền
```

Bỏ `--dry-run` để ghi thật. Dùng `--dry-run` trước để xem số chương, số ký tự.

## Tùy chọn hữu ích

| Cờ | Dùng khi |
|---|---|
| `--pattern "<regex>"` | Công cụ không nhận ra dòng tiêu đề chương (ví dụ "Hồi thứ nhất") |
| `--no-unwrap` | Thơ hoặc văn bản đã chia đoạn sẵn, không muốn gộp dòng |
| `--cover <file>` | Nguồn local, kèm ảnh bìa |
| `--force` | Nhập lại cuốn đã có |

## Quy tắc

- Luôn tuân thủ `.agent/rules/02-sources-and-licenses.md`. Giấy phép không hợp lệ thì công cụ tự dừng, không tìm cách vượt qua.
- Nhập theo nhóm 3–5 cuốn rồi `python tools/verify.py`.
- Bìa cần `pip install pillow`. Đọc PDF cần `pip install pypdf` (chỉ PDF có chữ, không phải PDF scan ảnh). Hỏi chủ dự án trước khi cài.
- Sau khi nhập: kiểm tra chất lượng theo skill `data-verifier`, rồi đồng bộ bằng `/05-sync-to-github`.
