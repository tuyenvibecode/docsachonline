# Tiết kiệm token (BẮT BUỘC)

Dự án có `CODEMAP.md`: bản đồ tự sinh của toàn bộ code, kèm số dòng và mô tả một dòng cho từng hàm. Dùng nó để không phải mở cả dự án.

## Cách làm việc

1. **Đọc `CODEMAP.md` trước tiên**, trước khi mở bất kỳ file code nào. Thường đủ để biết cần sửa ở đâu.
2. Mở file bằng Read với `offset` và `limit` theo số dòng trong bản đồ. Chỉ đọc cả file khi file nhỏ hoặc sắp sửa gần hết file.
3. Không dùng lệnh tìm kiếm quét cả thư mục để "làm quen dự án". Tra bản đồ.
4. Làm xong thì chạy lại `python tools/codemap.py` nếu đã thêm, xóa, đổi tên file hay hàm, hoặc code bị lệch số dòng. (`verify.py` và GitHub Action sẽ báo lỗi nếu quên; `sync.py` tự cập nhật.)

## Không bao giờ mở nguyên file

| File | Vì sao | Xem bằng cách nào |
|---|---|---|
| `chapters/book-N.js` | Cả cuốn sách trên vài dòng cực dài | Dùng lệnh nhỏ trong `CODEMAP.md` để in 800 ký tự đầu một chương |
| `books.json`, `data/meta/*.json` | Lớn dần theo số sách | `python tools/verify.py` đã tóm tắt |
| `covers/`, `inbox/` | Nhị phân, file đầu vào | Không đọc |

## Thói quen khác

- Dùng `--dry-run` của `import_book.py` để xem tóm tắt (số chương, số ký tự) thay vì mở file kết quả.
- Khi báo cáo cho chủ dự án, trích tối đa 2–3 đoạn ngắn làm mẫu, không dán cả chương.
- Đừng đọc lại file vừa tự ghi: ghi thành công là đủ, kiểm tra bằng `verify.py`.
- Đừng chép nội dung rules hay docs vào câu trả lời; chỉ nêu tên file.
