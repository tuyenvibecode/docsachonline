# Làm từng bước, dừng để chủ dự án duyệt

Dự án chạy theo 4 bước. **Xong mỗi bước phải dừng lại, báo cáo ngắn, chờ chủ dự án nói "ok"** rồi mới sang bước sau. Không tự làm trước.

| Bước | Việc | Workflow | Điều kiện sang bước sau |
|---|---|---|---|
| 1 | Chuẩn bị dữ liệu thật tốt | `/01-import-data` | `python tools/verify.py` đạt và chủ dự án duyệt báo cáo |
| 2 | Cho dữ liệu lên web kiểm tra | `/02-verify-web` | chủ dự án mở web xem và nói ok |
| 3 | Xây giao diện thật | `/03-build-ui` | chỉ bắt đầu khi `design.md` có nội dung thật |
| 4 | Đăng nhập, gửi sách chờ duyệt, kệ chung, dashboard | `/06-auth-dashboard` | bước 3 đã duyệt, `design.md` có phần đăng nhập và dashboard, chủ dự án đã tạo Supabase |

## Quy tắc cứng

- **Không làm UI** (bước 3) khi `design.md` còn dòng `PLACEHOLDER` hoặc chưa tồn tại. Hỏi chủ dự án.
- Ở bước 1, ưu tiên **chất lượng dữ liệu** hơn số lượng: chương tách đúng, đoạn văn liền mạch, không rác, bìa rõ nét.
- Mỗi lần nhập một nhóm nhỏ (3–5 cuốn), kiểm tra, rồi mới nhập tiếp. Không nhập hàng trăm cuốn một lượt.
- Trước mỗi lệnh `git push`, phải chạy `python tools/verify.py` và thấy "Đạt".
- Khi gặp lỗi, đọc thông báo, sửa nguyên nhân gốc. Không tắt kiểm tra để cho qua.
- Báo cáo cuối mỗi bước gồm: đã làm gì, bao nhiêu sách, cảnh báo còn lại, việc cần chủ dự án quyết.
