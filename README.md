# Book Reader Kit

Gói khởi động cho web đọc sách cá nhân (web tĩnh) làm bằng Antigravity.
Không database, không server: dữ liệu là file JS trong repo, GitHub lưu, Vercel chạy.

## Cách đưa cho Antigravity

1. Giải nén, mở thư mục này làm workspace trong Antigravity.
2. Thư mục `.agent/` chứa rules, workflows, skills (nếu bản Antigravity của anh dùng tên thư mục khác như `.agents/` thì đổi tên cho khớp).
3. Gõ `/01-import-data` để bắt đầu bước 1. Làm xong mỗi bước, Antigravity sẽ dừng chờ anh nói "ok".

## 4 bước

| Bước | Lệnh | Việc |
|---|---|---|
| 1 | `/01-import-data` | Chuẩn bị dữ liệu thật tốt, kiểm tra |
| 2 | `/02-verify-web` | Cho dữ liệu lên trang kiểm tra, xem ổn chưa |
| 3 | `/03-build-ui` | Xây UI theo `design.md` (anh sẽ viết file này sau) |
| 4 | `/06-auth-dashboard` | Đăng nhập, gửi sách chờ duyệt, kệ chung, dashboard (cần Supabase) |

Ngoài ra: `/04-add-source-adapter` thêm nguồn sách mới, `/05-sync-to-github` đẩy sách mới lên web.

## Thêm sách mới thì web tự cập nhật thế nào

```
nhập sách (import_book.py) → verify.py → sync.py → GitHub → Vercel tự deploy → web có sách mới
```

`books.json` luôn sinh tự động từ `data/meta/`, nên không bao giờ bị lệch. `sync.py` chỉ thêm đúng các đường dẫn của dự án vào commit, không đụng tới `inbox/`; PDF để ở `pdf/` thì được thêm.

## Đăng nhập, gửi sách, kệ chung và dashboard (bước 4)

Web dành cho bạn bè đọc nên chỉ cần đăng ký, đăng nhập đơn giản để kiểm soát ai vào. Sách của anh (thư viện chung) vẫn là file tĩnh trên GitHub và Vercel như cũ.

- **Tài khoản**: đăng ký xong ở trạng thái "chờ duyệt", admin duyệt trong dashboard mới vào được (đổi một dòng trong `schema.sql` nếu muốn cho vào luôn).
- **Kệ sách chung**: sách anh upload sẵn, cộng với sách bạn bè đóng góp đã được anh đưa lên kệ chung (hiện "Đóng góp bởi ...").
- **Gửi sách**: ai muốn thêm sách thì tải PDF (hoặc txt) lên mục "Sách của bạn". PDF được chuyển thành chữ **ngay trên trình duyệt** (PDF không gửi đi đâu), chỉ file chữ lưu lên Supabase. Sách mới ở trạng thái **chờ duyệt**; anh duyệt thì họ đọc được, anh bấm **Đưa lên kệ chung** thì mọi người cùng đọc. Giới hạn: 50 sách mỗi người, 10 sách chờ duyệt, 3 triệu ký tự mỗi sách. PDF scan ảnh chưa đọc được.
- **Dashboard**: duyệt hoặc chặn tài khoản; duyệt, từ chối, đưa lên hoặc gỡ khỏi kệ chung, xóa sách người dùng gửi; thống kê dung lượng và sách đọc nhiều.

Cấu trúc dữ liệu: `supabase/schema.sql` (anh dán vào Supabase SQL Editor). Các bước: `.agent/workflows/06-auth-dashboard.md`. Quy tắc: `.agent/rules/06-auth-and-security.md`.

## CODEMAP: tiết kiệm token cho AI

`CODEMAP.md` là bản đồ tự sinh của dự án (việc gì mở file nào, từng hàm kèm số dòng và mô tả). Antigravity đọc nó trước rồi chỉ mở đúng đoạn cần, thay vì quét cả dự án. Rule `.agent/rules/05-token-saving.md` bắt buộc làm vậy, và cấm mở nguyên file sách (`chapters/book-N.js`).

- Cập nhật: `python tools/codemap.py` (sync.py tự chạy). `verify.py` và GitHub Action báo lỗi nếu bản đồ lỗi thời.
- Hàm mới nên có docstring một dòng, bản đồ sẽ tự lấy làm mô tả.

## Lệnh nhanh

```bash
# Nhập sách (xem thêm: python tools/import_book.py --help)
python tools/import_book.py local inbox/sach.pdf          # tên, tác giả, giấy phép không bắt buộc
python tools/import_book.py local inbox/sach.docx --title "Tên" --author "Tên"

python tools/verify.py                 # kiểm tra toàn bộ dữ liệu
python tools/codemap.py                # cập nhật bản đồ code
python -m http.server 8000             # xem thử web ở http://localhost:8000
python tools/sync.py -m "Thêm sách"    # commit + push lên GitHub
```

Cài thêm khi cần (tùy chọn): `pip install pillow pypdf` (pillow cho ảnh bìa, pypdf để đọc PDF có chữ).

## Nguồn dữ liệu

File của anh (PDF, docx, txt): nhập thoải mái, không ràng buộc. Nguồn từ internet: chỉ qua `/04-add-source-adapter` (xem `.agent/rules/02-sources-and-licenses.md`).
Hiện chỉ có một nguồn: `local` (file của anh: txt, docx, pdf có chữ). Muốn thêm nguồn khác thì làm theo `/04-add-source-adapter`; AI sẽ kiểm tra nguồn trước khi viết.

## Lưu ý

- PDF scan ảnh chưa đọc được (cần OCR).
- Repo công khai thì ai có link cũng tải được file sách và PDF. Muốn kín thì để repo private (Vercel vẫn deploy được), nhưng file đã deploy vẫn mở được nếu biết đường dẫn.
