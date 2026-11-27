# /02-verify-web — Đưa dữ liệu lên web kiểm tra

Điều kiện: bước 1 đã được chủ dự án duyệt.

1. Chạy `python tools/verify.py`, phải "Đạt".
2. Chạy máy chủ thử trên máy: `python -m http.server 8000`, mở `http://localhost:8000` (mở file trực tiếp bằng đôi bấm sẽ không chạy vì trình duyệt chặn).
3. Trang `index.html` hiện tại chỉ là **trang kiểm tra dữ liệu**, không phải UI thật. Dùng nó để kiểm:
   - Danh sách sách hiện đủ, bìa hiện đúng.
   - Mở từng sách: chọn chương, chuyển chương, chữ hiện đủ dấu tiếng Việt, đoạn văn liền mạch.
   - Mở trình duyệt DevTools, tab Console: không có lỗi đỏ.
   - Thử trên khung điện thoại (DevTools, chế độ thiết bị).
4. Nếu có git repo và remote: `python tools/sync.py` để đẩy lên GitHub. Nếu chưa có repo, **dừng và hướng dẫn chủ dự án** tạo repo rồi tự đưa link (không tự tạo repo hay tự đăng nhập hộ).
5. Nếu đã nối Vercel: đợi deploy xong, kiểm tra lại trên link thật (tốc độ tải, bìa, chương).
6. **DỪNG.** Báo cáo những gì đã kiểm, lỗi phát hiện, link web (nếu có). Chờ chủ dự án nói ok mới sang bước 3.
