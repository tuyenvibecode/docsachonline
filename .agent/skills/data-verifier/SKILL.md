---
name: data-verifier
description: Kiểm tra chất lượng dữ liệu sách bằng tools/verify.py và đọc thử bằng mắt trước khi sang bước 2 hoặc trước khi push. Dùng sau mỗi lần nhập sách.
---

# Kiểm tra dữ liệu

## 1. Kiểm tra tự động

```bash
python tools/verify.py
```

- **LỖI** (phải sửa): thiếu file, chương rỗng, ký tự `�`, giấy phép lạ, `books.json` lệch, `CODEMAP.md` lỗi thời.
- **CẢNH BÁO** (xem xét): chương dưới 200 ký tự, thiếu bìa, bìa mồ côi.
- Mã thoát 1 khi có lỗi (GitHub Action dựa vào đó).

## 2. Đọc thử bằng mắt (không bỏ qua)

Với mỗi cuốn mới nhập, mở `chapters/book-N.js` hoặc `index.html` rồi xem:

- [ ] Chương đầu: không còn mục lục, lời giới thiệu của nguồn, thông tin bản quyền của trang.
- [ ] Chương giữa: đoạn văn liền mạch, không bị cắt giữa câu, lời thoại tách dòng hợp lý.
- [ ] Chương cuối: không dính chữ "Hết", "THE END", rác của trang, quảng cáo.
- [ ] Số chương hợp lý so với sách thật. Tiêu đề chương đúng.
- [ ] Dấu tiếng Việt đủ (không mất dấu, không chữ lạ).
- [ ] Bìa rõ, đúng sách.

## 3. Báo cáo cho chủ dự án

Mỗi bước 1 báo cáo ngắn gồm: số sách, tổng ký tự, cảnh báo còn lại, 2–3 đoạn trích mẫu (ngắn) để chủ dự án nhìn chất lượng. Đừng dán cả chương.
