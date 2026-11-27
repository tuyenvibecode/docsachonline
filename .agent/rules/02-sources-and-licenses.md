# Nguồn dữ liệu

## File của chủ dự án (PDF, docx, txt): không ràng buộc

- Chủ dự án đưa file nào thì nhập file đó. Không cần khai giấy phép, tên sách hay tác giả: thiếu thì công cụ tự điền (tên theo tên file, tác giả "Không rõ", giấy phép `own`).
- PDF được phép nằm trong repo. Chủ dự án muốn đẩy PDF lên GitHub thì để vào thư mục `pdf/` (đặt tên `pdf/book-N.pdf`); `sync.py` sẽ tự đưa vào commit. Không cần hỏi lại.
- Không chặn, không cảnh báo, không giảng giải về nội dung file chủ dự án tự đưa.

## Nguồn từ internet (trang web, API)

- Chỉ làm khi chủ dự án nêu rõ **một nguồn cụ thể** (tên hoặc link), qua workflow `/04-add-source-adapter`.
- Không tự đi tìm, tự đề xuất, hay tự thêm nguồn bên ngoài.
- Không crawl, scrape, tải hàng loạt từ các trang đăng sách còn bản quyền, hoặc không rõ nguồn và giấy phép. Gặp yêu cầu như vậy: dừng, nói ngắn gọn, đề nghị chủ dự án đưa file của mình hoặc nguồn khác (xem workflow 04).
- Không né rào cản kỹ thuật của một trang (CAPTCHA, chặn tải, đăng nhập, robots.txt).
- Nguồn nào được duyệt thì tải chậm, có nghỉ giữa các request (công cụ có sẵn `pause`), không chạy song song, và ghi đúng `source`, `source_id`, `source_url`.
