# /04-add-source-adapter — Thêm một nguồn sách mới

Dùng khi chủ dự án muốn lấy sách từ một nguồn chưa có trong `tools/adapters/`. Nguồn mới thì dữ liệu mới tự nhập, tự cập nhật lên web qua `sync.py` (không cần sửa web).

## A. Kiểm tra nguồn trước (không bỏ qua)

1. Hỏi chủ dự án: tên nguồn, link, và **vì sao biết nguồn này được phép** (phi bản quyền, giấy phép CC, API chính thức cho phép, hay của chủ dự án).
2. Tự kiểm tra: trang có ghi giấy phép/điều khoản không, có API chính thức không, robots.txt và điều khoản có cho tải không.
3. **Dừng và từ chối** nếu nguồn đăng sách còn bản quyền hoặc không rõ nguồn gốc, hoặc muốn né CAPTCHA/đăng nhập/chặn tải. Giải thích ngắn, đề nghị nguồn thay thế (file của chủ dự án, hoặc nội dung tác giả cho phép bằng văn bản). Không viết thử, không "làm demo".

## B. Viết adapter (khi nguồn hợp lệ)

4. Tạo `tools/adapters/<ten_nguon>.py` theo hợp đồng trong `tools/adapters/__init__.py`. Tham khảo `local.py` để thấy dạng dữ liệu trả về.
5. Ưu tiên API chính thức hơn bóc HTML. Dùng `common.http_get` (có nghỉ giữa các lần gọi).
6. `license` trả về chỉ được là giá trị trong `ALLOWED_LICENSES`; nếu nguồn không cho biết rõ giấy phép từng sách thì **đọc từ dữ liệu của nguồn** và dừng khi không rõ.
7. Đăng ký adapter trong `tools/import_book.py` (dòng `ADAPTERS`).
8. Thử một cuốn với `--dry-run`, rồi nhập thật một cuốn. Chạy `python tools/codemap.py` để bản đồ có adapter mới, rồi `python tools/verify.py`.
9. Báo chủ dự án cách dùng: ví dụ lệnh nhập và cách chạy `python tools/sync.py` để lên web.
