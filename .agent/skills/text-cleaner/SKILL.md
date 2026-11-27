---
name: text-cleaner
description: Xử lý chữ khi nhập sách bị sai: chương tách sai, dòng bị ngắt cứng, rác đầu/cuối, lỗi bảng mã. Dùng khi dry-run hoặc verify báo số chương lạ hoặc đọc thử thấy chữ xấu.
---

# Làm sạch chữ

Mã nằm ở `tools/clean.py`; bản cho trình duyệt là `lib/clean.js` (cùng thuật toán, sửa một bên thì sửa bên kia). Các bước xử lý theo thứ tự:

1. **Tách chương trước** (`split_chapters`): nhận dòng ngắn (tối đa 90 ký tự) dạng "Chương 3", "CHAPTER IV", "Hồi 2", "Phần 1", "Part 2". Mục dưới 200 ký tự bị bỏ (thường là mục lục, trang bìa).
2. **Gộp dòng** (`unwrap`) từng chương: gộp dòng bị ngắt theo trang in thành đoạn; dòng bắt đầu bằng `-`, `–`, `—`, `“`, `"` là đoạn mới (lời thoại).
3. Không tìm được chương nào: chia theo độ dài ~12.000 ký tự (`chunk_by_size`), tên "Phần 1", "Phần 2"...

## Chẩn đoán nhanh

| Triệu chứng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Chỉ ra 1–2 chương, hoặc "Phần 1...n" | Tiêu đề chương dạng lạ ("Hồi thứ nhất", "I.", "Mười") | Dùng `--pattern` với regex khớp tiêu đề; thử trên văn bản thô trước |
| Hàng trăm chương | Regex khớp nhầm các dòng thường | Siết `--pattern` (ví dụ thêm `^...$`) |
| Cả chương dính thành một đoạn dài | Thơ, hoặc đã chia đoạn sẵn mà vẫn gộp | `--no-unwrap` |
| Đoạn văn bị cắt giữa câu | PDF xuống dòng lạ, dòng quá ngắn | Kiểm tra bằng mắt vài chương; chỉnh `unwrap` nếu lặp lại, hỏi chủ dự án trước khi đổi hành vi chung |
| Có ký tự `�` | Sai bảng mã file nguồn | Thử bảng mã khác (adapter local thử utf-8, cp1258, cp1252); hoặc báo chủ dự án |
| Dòng phụ đề ngay sau tiêu đề chương dính vào đoạn đầu | Không có dòng trống giữa phụ đề và đoạn đầu | Chấp nhận được; nếu muốn tách thì thêm quy tắc trong `unwrap`, thử lại ít nhất 2 cuốn |
| Số trang rơi vào giữa đoạn | PDF | Thêm bước lọc dòng chỉ gồm số trong `clean.py` (giữ đơn giản, có chú thích) |

## Nguyên tắc

- Sửa quy tắc chung trong `clean.py` thì phải thử lại ít nhất 2 cuốn đã nhập trước (đảm bảo không làm hỏng cuốn khác).
- Không sửa nội dung văn bản (không "sửa chính tả", không viết lại câu). Chỉ làm sạch cấu trúc.
