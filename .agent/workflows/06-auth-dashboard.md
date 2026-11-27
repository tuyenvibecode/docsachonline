# /06-auth-dashboard — Đăng nhập, gửi sách chờ duyệt, kệ chung, dashboard (bước 4)

Điều kiện: bước 3 (UI đọc sách) đã được chủ dự án duyệt **và** `design.md` có phần thiết kế đăng nhập/đăng ký, "Sách của bạn" (tải PDF) và dashboard. Thiếu thì dừng và hỏi. Đọc kỹ `.agent/rules/06-auth-and-security.md` trước.

## A. Chủ dự án chuẩn bị (hướng dẫn từng bước, đừng làm hộ)

1. Tạo project trên supabase.com (gói free).
2. SQL Editor: dán `supabase/schema.sql`, Run.
3. Authentication > Providers: bật Email (nên bật "Confirm email").
4. Settings > API: lấy **Project URL** và **anon key**, đưa cho Antigravity để điền vào `web-config.js`.
5. Đăng ký một tài khoản trên web, rồi chạy trong SQL Editor dòng cuối của `schema.sql` (đổi email) để thành admin đầu tiên.

## B. Việc Antigravity làm (theo thứ tự, xong mỗi mục cho chủ dự án xem)

1. `web-config.js` + khởi tạo `supabase-js` (phiên bản cố định). Trang đăng ký, đăng nhập, đăng xuất theo `design.md`. Màn hình "chờ duyệt" (`pending`) và "bị chặn" (`blocked`).
2. Thư viện chung vẫn đọc từ `books.json` và `chapters/book-N.js` như bước 3, giờ chỉ vào được khi đã đăng nhập và được duyệt. Tiến độ và dấu trang lưu vào `reading_progress`, `bookmarks` với `book_key` = `lib:<id>`.
3. **Kệ sách**: gồm sách gốc của thư viện (từ `books.json`) và sách người dùng đã lên kệ chung (đọc từ `user_books` có `shared = true`, hiện kèm "Đóng góp bởi `contributor`"). Mở sách của người khác: tải `<owner_id>/<id>.json` bằng phiên đăng nhập.
4. **"Sách của bạn"**: nút Thêm sách chọn PDF hoặc txt.
   - PDF: dùng `pdfjs-dist` (phiên bản cố định) lấy chữ từng trang. Gom thành các dòng theo vị trí dọc của từng mảnh chữ, xuống dòng khi vị trí đổi hoặc mảnh chữ báo hết dòng, giữa các trang thêm dòng trống. Không có chữ (PDF scan) thì báo "PDF này là ảnh scan, chưa đọc được". Giới hạn file khoảng 30 MB và báo tiến độ khi đọc.
   - Chữ lấy được đưa qua `convertText` của `lib/clean.js` (PDF/txt thường để `wrapped: true`; thơ thì cho người dùng chọn không gộp dòng).
   - Hiện bản xem trước: số chương, tên chương, vài dòng đầu. Cho sửa tên sách, tác giả, rồi bấm Gửi.
   - Gửi: tạo id sách (uuid), tải `toBookJson(...)` lên bucket `user-books` đường dẫn `<uid>/<id>.json`, rồi thêm dòng vào `user_books` (`id`, `owner_id`, `title`, `author`, `chars`, `chapters`, `size_bytes`; **không** gửi `status` hay `shared`). Nếu thêm dòng lỗi thì xóa file vừa tải lên.
   - Danh sách của người dùng, mỗi sách có nhãn: **Chờ duyệt** (không cho đọc), **Đã duyệt** (cho đọc), **Trên kệ chung**, **Bị từ chối** (hiện `reject_reason`). Xóa được sách chưa lên kệ chung (xóa cả file và dòng).
   - Báo lỗi dễ hiểu khi vượt giới hạn (50 sách, 10 sách chờ duyệt, 3 triệu ký tự).
5. **Dashboard** (`/admin`), chỉ hiện với `role = admin`:
   - **Tài khoản**: danh sách, lọc theo trạng thái, nút Duyệt, Chặn, Bỏ chặn, đổi vai trò. Cảnh báo trước khi hạ quyền admin cuối cùng.
   - **Duyệt sách**: hàng chờ các sách `pending` (huy hiệu số sách đang chờ), xem trước nội dung (tải file chữ), nút **Duyệt**, **Từ chối** (bắt nhập lý do), và **Duyệt và đưa lên kệ chung** (một bước). Sách đã duyệt có nút **Đưa lên kệ chung** hoặc **Gỡ khỏi kệ chung**, ô sửa tên, tác giả, người đóng góp, nút Xóa có xác nhận (xóa cả file).
   - **Sách gốc của thư viện**: chỉ xem (đọc từ `books.json`), quản lý bằng công cụ trên máy.
   - **Thống kê**: số tài khoản theo trạng thái, số sách theo trạng thái, tổng dung lượng `size_bytes` so với giới hạn gói free của Supabase, sách đọc nhiều (đếm theo `book_key` trong `reading_progress`).
5. Chạy `python tools/codemap.py`, `python tools/verify.py`.

## C. Kiểm tra (không bỏ qua)

Dùng 4 tài khoản thử: admin, người dùng A, người dùng B (đã duyệt), một người đang chờ duyệt.

- [ ] Người chờ duyệt: không thêm sách được, không thấy sách nào.
- [ ] A gửi một PDF có chữ: sách hiện "Chờ duyệt", chưa mở đọc được. B không thấy sách đó.
- [ ] Admin xem trước và Duyệt: A mở đọc được. B vẫn không thấy.
- [ ] Admin Đưa lên kệ chung: B thấy, đọc được, có "Đóng góp bởi A". Gỡ khỏi kệ chung: B không còn thấy.
- [ ] A không tự đổi được trạng thái duyệt hay tự bật kệ chung (thử trực tiếp bằng Supabase client). A không xóa được sách đã lên kệ chung.
- [ ] Từ chối kèm lý do: A thấy lý do. PDF scan ảnh báo đúng lỗi. Gửi quá 10 sách chờ duyệt bị chặn với thông báo dễ hiểu.
- [ ] Người dùng tự nâng quyền (`update profiles set role = 'admin'`) bị từ chối. Mở `/admin` bằng tài khoản thường: không có dữ liệu.
- [ ] Xóa sách thì file trong Storage cũng mất. `python tools/verify.py` đạt, không lộ khóa `service_role`.

**DỪNG.** Báo cáo: đã làm gì, mục nào ở phần C đã chạy thật, mục nào chủ dự án phải tự thử (đặc biệt đọc chữ từ vài file PDF thật, vì `pdfjs-dist` chưa được kiểm tra), và lưu ý gói free của Supabase tạm dừng project nếu một tuần không ai dùng.
