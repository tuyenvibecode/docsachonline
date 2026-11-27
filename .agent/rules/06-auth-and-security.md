# Đăng nhập, gửi sách chờ duyệt, kệ chung và dashboard (bước 4)

## Mức độ bảo vệ (chủ dự án đã chốt)

Web dành cho bạn bè đọc. **Không cần bảo vệ nội dung của thư viện chung**: sách của chủ dự án vẫn là file tĩnh (`books.json`, `chapters/book-N.js`) đẩy lên GitHub và Vercel như cũ qua `tools/sync.py`. Đăng ký và đăng nhập chỉ để **kiểm soát ai vào**, không cố giấu file. Đừng đề xuất chuyển sách lên kho riêng, cũng đừng chặn `chapters/` khỏi GitHub.

Supabase (gói free) lo: tài khoản, **sách người dùng gửi lên (chờ duyệt, kệ chung)**, tiến độ đọc, dấu trang. Cấu trúc ở `supabase/schema.sql`.

## Sách người dùng gửi lên, duyệt, kệ chung

Luồng chủ dự án đã chốt: **gửi sách, chờ admin duyệt, duyệt xong có thể đưa lên kệ chung cho mọi người đọc** (đóng góp tài nguyên).

1. Người dùng chọn **PDF** (hoặc txt) trong "Sách của bạn". Việc chuyển thành chữ làm **ngay trên trình duyệt**; PDF không bị gửi đi đâu. Chỉ file chữ (JSON) lên Supabase Storage bucket `user-books`, đường dẫn `<id người dùng>/<id sách>.json`, kèm một dòng trong bảng `user_books`. Sách mới luôn ở trạng thái `pending` (schema ép như vậy, không tự duyệt được).
2. Admin xem và **Duyệt** (`approved`) hoặc **Từ chối** (`rejected` kèm lý do). Sách `pending` hoặc `rejected`: giao diện hiện nhãn trạng thái, **không cho mở đọc**. Sách `approved`: chủ sách mở đọc được. (Chặn mở đọc ở khâu này do giao diện lo; quyền đọc của người khác thì do schema chặn.)
3. Admin có thêm nút **Đưa lên kệ chung** (`shared = true`, chỉ làm được khi đã `approved`, ghi tên người đóng góp vào `contributor`). Khi đó mọi tài khoản đã được duyệt thấy và đọc được sách ấy, hiển thị kèm "Đóng góp bởi ...". Có nút **Gỡ khỏi kệ chung**.
4. Sách đã lên kệ chung: chủ sách không tự xóa hay sửa tên được (nhờ admin); admin sửa và xóa được.

Giới hạn có sẵn trong schema: 50 sách mỗi người, tối đa 10 sách đang chờ duyệt, 3 triệu ký tự mỗi sách, 10 MB mỗi file. Giao diện báo lỗi dễ hiểu khi vượt. PDF scan ảnh (không có chữ) chưa hỗ trợ: báo rõ, đừng cố đoán.

Thuật toán tách chương và gộp dòng dùng **`lib/clean.js`** (đã kiểm tra khớp `tools/clean.py`). Không viết lại thuật toán khác. Sửa một bên thì phải sửa bên kia.

Tiến độ đọc và dấu trang dùng `book_key`: `lib:<id>` cho sách gốc của thư viện, `u:<id>` cho sách người dùng (kể cả sách trên kệ chung).

## Khóa bí mật và code

- Trong code web chỉ có **URL dự án và anon key** (công khai theo thiết kế), đặt trong `web-config.js`. Tính năng nào cũng không cần service role key; nếu thấy cần thì dừng và hỏi.
- **Service role key không bao giờ** vào repo, code web, log. `tools/verify.py` báo lỗi nếu thấy.
- Không tự tạo tài khoản hay project Supabase, không tự đăng nhập hộ. Chủ dự án tự tạo project, chạy `supabase/schema.sql`, đưa URL và anon key.
- Quyền hạn do RLS trong `schema.sql` quyết định, không phải giao diện. Bảng mới phải bật RLS và có policy. Người dùng không được tự sửa `role` hay `status`.
- Chèn chữ sách, tên sách, email vào trang bằng `textContent`, không `innerHTML`.
- Tải thư viện bên ngoài bằng **phiên bản cố định** (`supabase-js`, `pdfjs-dist` từ jsdelivr hoặc cdnjs), không dùng `@latest`. Hỏi chủ dự án trước khi thêm thư viện khác.
- Đăng ký: tài khoản mới mặc định `pending`, admin duyệt thì mới vào được. Muốn cho vào luôn thì đổi `default 'pending'` thành `'approved'` trong `schema.sql` (hỏi chủ dự án).
- Không ghi mật khẩu, token vào log. Lỗi đăng nhập hiện thông báo chung.

## Báo cáo trung thực

`schema.sql` và `lib/clean.js` đã được kiểm tra (xem đầu file schema); phần đọc chữ từ PDF bằng `pdfjs-dist` và việc nối Supabase thật **chưa kiểm tra**. Khi báo xong bước 4, nói rõ đã chạy thử gì, chưa thử gì, chủ dự án tự thử gì (xem mục "Kiểm tra" của workflow 06).
