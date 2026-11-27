# Giao diện kệ sách — brief cho Antigravity

## Mục tiêu
Làm giao diện **kệ sách** cho web đọc sách cá nhân: sách đứng trên kệ, thấy gáy sách. Bấm vào một cuốn thì cuốn đó được "rút ra" khỏi kệ (để chuẩn bị đọc).

File `index.html` đi kèm là **bản mẫu chạy được** (HTML/CSS/JS thuần, không cần thư viện). Hãy dùng nó làm chuẩn về giao diện và hiệu ứng, rồi tách vào cấu trúc dự án.

## Cần giữ đúng
- Tất cả gáy sách **cùng kích thước**: 116 × 548 px, xếp thẳng hàng đáy trên kệ.
- Mỗi gáy gồm (từ trên xuống): ảnh bìa nhỏ vuông → tên sách **chữ dọc** (`writing-mode: vertical-rl`, in hoa, font serif) → tên tác giả → năm xuất bản trong khung viền.
- Mỗi cuốn có **màu gáy riêng** và màu chữ riêng (đã chọn đủ độ tương phản, đừng đổi tuỳ tiện).
- Tấm kệ gỗ nằm dưới hàng sách (nền gỗ `#B3844F`, vạch sáng ở mép trên).
- Kệ thứ hai bên dưới có vài ô trống nét đứt "Chỗ cho sách mới".
- Kệ cuộn ngang được khi màn hình hẹp (điện thoại).

## Hiệu ứng
- **Rê chuột / focus bàn phím:** sách nhích lên 14px.
- **Bấm vào gáy (sách được rút ra):** `translateY(-34px) scale(1.07) rotate(-1.5deg)` + bóng đổ lớn hơn phía dưới, thời gian 0.45s, easing `cubic-bezier(.2,.8,.2,1)`. Bấm lần nữa thì cất về chỗ cũ.
- Dưới kệ hiện dòng: **Tên sách · Tác giả · Năm** của cuốn đang rút ra.
- Tôn trọng `prefers-reduced-motion` (tắt animation).
- Không dùng hình bàn tay (đã thử, bỏ).

## Dữ liệu (mỗi sách một object)
```js
{ id, lines: ['DÒNG 1','DÒNG 2'], author, year, bg, fg, cover, sky, hill, sun }
```
- `lines`: tên sách tách sẵn thành 1–2 dòng để hiện dọc trên gáy.
- `cover`: đường dẫn ảnh bìa thật. Để trống thì hiện hình minh hoạ tạm (do `sky`/`hill`/`sun` quyết định màu).
- Thêm sách mới = thêm 1 object vào mảng `books`, không phải sửa giao diện.

## Font & màu
- Font: **Noto Serif** (tiêu đề, tên sách), **Be Vietnam Pro** (chữ nhỏ) — Google Fonts, có tiếng Việt.
- Nền trang `#F3EBD9`, chữ `#2B2118`, chữ phụ `#5C4B3B`.

## Truy cập (accessibility)
- Mỗi gáy là `<button>`, có `aria-label` ("Tên sách, tác giả, năm") và `aria-pressed`.
- Có viền focus rõ khi dùng bàn phím.

## Làm sau (chưa làm trong bản mẫu)
- Bấm sách thì mở trang đọc (hiện mới chỉ rút ra).
- Lấy danh sách sách từ dữ liệu của web đọc sách (JSON/JS theo từng sách) thay cho mảng viết tay.
- Thay hình bìa tạm bằng ảnh bìa thật.
