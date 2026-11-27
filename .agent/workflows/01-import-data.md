# /01-import-data — Chuẩn bị dữ liệu

Mục tiêu: có một thư viện dữ liệu sạch, đã kiểm tra, từ các nguồn hợp lệ (rule 02).

1. Đọc `CODEMAP.md` trước, rồi `.agent/rules/` (đặc biệt 02, 03, 04, 05). Chỉ mở thêm file khi thật cần.
2. Hỏi chủ dự án sách nào cần nhập: file trong `inbox/` (txt, docx, pdf có chữ), (tên sách, tác giả, giấy phép không bắt buộc, thiếu thì tự điền). **Chỉ nhập những gì chủ dự án đưa hoặc đã chỉ định rõ; không tự đi tìm, tự tải, hay tự đề xuất nguồn bên ngoài để lấy sách.**
3. Với **từng nguồn chưa chắc hợp lệ** hoặc nguồn chưa có adapter: dừng, dùng `/04-add-source-adapter`.
4. Cài thư viện tùy chọn nếu cần: `pip install pillow pypdf` (hỏi trước).
5. Nhập thử từng cuốn bằng `--dry-run` để xem số chương, số ký tự, tên chương đầu/cuối:
   `python tools/import_book.py <nguồn> <ref> --dry-run`
   - Số chương lạ (1 chương hoặc hàng trăm) thì xem skill `text-cleaner`, thử `--pattern` hoặc `--no-unwrap`.
6. Nhập thật (bỏ `--dry-run`). Mỗi nhóm 3–5 cuốn.
7. Mở vài chương bất kỳ trong `chapters/book-N.js`, đọc thử: đoạn văn có liền mạch, có chương nào bị cắt giữa chừng, có rác đầu/cuối không (skill `data-verifier`).
8. Chạy `python tools/verify.py` cho đến khi "Đạt". Sửa nguyên nhân, không bỏ qua.
9. **DỪNG.** Báo cáo cho chủ dự án: danh sách sách đã nhập, cảnh báo còn lại, 2–3 đoạn mẫu để chủ dự án xem chất lượng chữ. Chờ "ok".
