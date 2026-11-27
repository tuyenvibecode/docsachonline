# /03-build-ui — Xây giao diện thật

Điều kiện: bước 2 đã được duyệt **và** `design.md` có nội dung thật (không còn dòng `PLACEHOLDER`). Nếu chưa, dừng và hỏi chủ dự án.

1. Đọc kỹ `design.md`. Mơ hồ chỗ nào thì hỏi trước khi làm, đừng tự bịa.
2. Giữ nguyên **hợp đồng dữ liệu** (rule 03). UI chỉ đọc `books.json` và `chapters/book-N.js`, không đổi định dạng dữ liệu.
3. Tải theo nhu cầu: danh sách chỉ tải `books.json` và bìa; chỉ tải `chapters/book-N.js` khi người đọc mở sách.
4. Tính năng lưu cá nhân (dấu trang, vị trí đang đọc, cỡ chữ, chế độ tối) lưu trong `localStorage`, bọc `try/catch` vì trình duyệt có thể chặn.
5. Làm đủ trên điện thoại trước (màn hình hẹp), rồi mới tới máy tính.
6. Chèn chữ vào trang bằng `textContent`, không dùng `innerHTML` với nội dung sách.
7. Làm từng phần nhỏ (trang danh sách, rồi trang đọc, rồi tính năng phụ), mỗi phần xong cho chủ dự án xem trước khi làm tiếp.
8. Giữ `index.html` kiểm tra cũ ở `/check.html` để sau này còn kiểm dữ liệu.
9. Mỗi lần xong một phần: chạy `python tools/verify.py`, `python tools/sync.py`, báo chủ dự án link xem.
