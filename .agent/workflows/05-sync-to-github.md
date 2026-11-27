# /05-sync-to-github — Đưa sách mới lên GitHub và web

Dùng mỗi khi vừa nhập sách mới (từ bất kỳ nguồn nào) và muốn web cập nhật.

1. Nhập sách bằng `python tools/import_book.py ...` (hoặc `/01-import-data`).
2. `python tools/verify.py` phải "Đạt".
3. `python tools/sync.py -m "Thêm: <tên các sách>"`
   - Công cụ tự dựng lại `books.json` và `CODEMAP.md`, kiểm tra, `git add` đúng các đường dẫn của dự án (dữ liệu, `tools`, `.agent`, `index.html`, `CODEMAP.md`...), commit, push.
   - Không dùng `git add .` (tránh đưa nhầm file tạm trong `inbox/`). Thư mục `pdf/` được tự thêm nếu có.
4. Vercel nhận push và tự deploy (khoảng vài chục giây). Mở web kiểm tra sách mới đã hiện và mở đọc được.
5. GitHub Action `verify` chạy lại kiểm tra trên GitHub. Nếu đỏ, đọc log và sửa, không tắt Action.

Chưa có git repo hoặc remote: dừng, hướng dẫn chủ dự án `git init`, tạo repo trên GitHub và `git remote add origin <link>`. Không tự tạo hay tự đăng nhập hộ.
