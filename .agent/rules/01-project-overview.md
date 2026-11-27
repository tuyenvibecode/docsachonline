# Tổng quan dự án

Web đọc sách / truyện cá nhân, **web tĩnh**: không backend, không database.
Chủ dự án là designer, biết code ở mức nghiệp dư, làm web cho nhu cầu cá nhân (phi thương mại).

## Cách hoạt động

- Mỗi cuốn sách là một file `chapters/book-N.js` chứa `window.__BOOK_TEXT__` (xem rule 03).
- `books.json` là danh sách sách, **sinh tự động** từ `data/meta/`. Không sửa tay.
- Web chỉ tải `books.json` lúc đầu, và chỉ tải `chapters/book-N.js` khi người đọc mở sách đó.
- Code nằm trên GitHub, Vercel tự deploy mỗi lần push. Thêm sách = nhập, kiểm tra, `git push`.

## Cấu trúc thư mục

```
CODEMAP.md            bản đồ code tự sinh. ĐỌC TRƯỚC (rule 05)
index.html            trang kiểm tra dữ liệu tạm; UI thật làm sau theo design.md
books.json            sinh tự động
chapters/book-N.js    nội dung chữ
covers/book-N.webp    ảnh bìa nhỏ
data/meta/book-N.json thông tin từng sách (nguồn thật của books.json)
inbox/                file đầu vào tạm (PDF, docx, txt). Bị gitignore
pdf/                  (tùy chọn) PDF muốn đưa lên GitHub, tên pdf/book-N.pdf
tools/                công cụ Python nhập, kiểm tra, đồng bộ
supabase/schema.sql   tài khoản, sách người dùng gửi (duyệt, kệ chung), phân quyền (bước 4, rule 06)
lib/clean.js          tách chương, gộp dòng ngay trên trình duyệt (khớp tools/clean.py)
.agent/               rules, workflows, skills cho Antigravity
design.md             thiết kế UI do chủ dự án cung cấp
```

## Ngôn ngữ và phong cách

- Trả lời chủ dự án bằng tiếng Việt, giản dị, tránh thuật ngữ khi không cần.
- Chủ dự án không phải lập trình viên chuyên nghiệp: comment trong code bằng tiếng Việt, giải thích ngắn "để làm gì".
- Công cụ dữ liệu viết bằng Python chuẩn (stdlib). Không thêm thư viện hay framework mới khi chưa hỏi.
- Web: HTML/CSS/JS thuần, không build step, trừ khi design.md hoặc chủ dự án yêu cầu khác.
