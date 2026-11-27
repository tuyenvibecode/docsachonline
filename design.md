# Thiết kế giao diện: Kệ Sách Gáy Đứng & Đọc Sách Lật Trang 3D

## 1. Phong cách & Màu sắc chủ đạo (theo `KE-SACH-SPEC.md`)
- **Nền trang**: `#F3EBD9` (kem giấy ấm), chữ chính `#2B2118`, chữ phụ `#5C4B3B`.
- **Tấm kệ gỗ**: Nền gỗ `#B3844F`, vạch sáng ở mép trên (`#D8AD78`), đổ bóng mềm phía dưới.
- **Chế độ màu**: Hỗ trợ 3 chế độ **Giấy ấm (`warm`)**, **Cổ điển (`sepia`)**, và **Ban đêm (`dark`)**.
- **Font chữ** (Google Fonts hỗ trợ đầy đủ tiếng Việt):
  - **Noto Serif**: Tên sách chữ dọc trên gáy sách và các tiêu đề.
  - **Literata**: Nội dung trang sách (chữ rõ, dấu tiếng Việt tròn trịa, `line-height: 1.78`).
  - **Be Vietnam Pro**: Giao diện điều khiển, tên tác giả và năm xuất bản.

## 2. Màn hình 1: Kệ Sách Gáy Đứng (`Bookshelf View`)
- **Kích thước đồng nhất**: Tất cả gáy sách có cùng kích thước **`116 × 548 px`**, xếp thẳng hàng đáy trên tấm kệ gỗ.
- **Cấu trúc mỗi gáy sách** (`<button>` hỗ trợ bàn phím, `aria-label`, `aria-pressed`):
  1. **Ảnh bìa nhỏ vuông** (`94 × 94 px`) ở đỉnh gáy. Nếu chưa có ảnh bìa thật (`cover`), tự động vẽ hình minh hoạ phong cảnh tối giản từ bộ màu `sky`, `hill`, `sun`.
  2. **Tên sách chữ dọc** (`writing-mode: vertical-rl`, in hoa, font `Noto Serif`), tách sẵn thành 1–2 dòng cân đối (`lines: ['DÒNG 1', 'DÒNG 2']`).
  3. **Tên tác giả** in hoa và **năm xuất bản** đóng khung viền ở chân gáy sách.
- **Kệ thứ hai bên dưới**: Có các ô trống nét đứt `"Chỗ cho sách mới"`.
- **Cuộn ngang**: Kệ sách tự động cuộn ngang mượt mà trên màn hình điện thoại hẹp.
- **Hiệu ứng tương tác**:
  - Rê chuột hoặc focus bàn phím: gáy sách nhích lên `14px` (`translateY(-14px)`).
  - Bấm vào gáy sách: sách được **nhấc/rút ra khỏi kệ** (`translateY(-34px) scale(1.07) rotate(-1.5deg)` kèm bóng đổ lớn trong `0.45s`, easing `cubic-bezier(.2,.8,.2,1)`), sau đó **mở thẳng vào màn hình đọc sách lật trang 3D**.
  - Tôn trọng `prefers-reduced-motion` (tắt animation khi người dùng bật chế độ giảm chuyển động).

## 3. Màn hình 2: Trình Đọc Sách Lật Trang 3D (`3D Flipbook Reader`)
- **Bố cục sách mở**:
  - **Máy tính (`>= 900px`)**: Chế độ **2 trang đối xứng (Dual-page Spread)** với khe bóng gáy sách ở giữa và bìa bọc ngoài. Có nút chuyển nhanh sang **1 trang** hoặc **Cuộn dọc**.
  - **Điện thoại (`< 900px`)**: Tự động hiển thị **1 trang** vừa khít màn hình.
- **Hiệu ứng nắm kéo & lật trang 3D chân thực (`Interactive Page Curl & Drag-to-Flip`)**:
  - Rê chuột vào mép phải/trái của trang sách sẽ thấy **góc giấy dưới quăn nhẹ lên** (`Corner Peel`).
  - Nhấn giữ chuột ở mép trang và kéo ngang (hoặc vuốt ngón tay trên điện thoại): tờ giấy xoay 3D theo đúng vị trí tay kéo (`0° -> -180°`), có độ uốn cong nhẹ, vệt sáng bóng trụ giấy (`Cylindrical Highlight`) và bóng đổ động phủ lên trang giấy nằm bên dưới.
  - Hỗ trợ lật trang bằng: kéo chuột, bấm mép trang, nút `‹ Trang trước` / `Trang sau ›`, và phím mũi tên `←` / `→`.
- **Tiện ích đọc sách**:
  - Ngăn kéo **Mục lục chương** và **Dấu trang** (bấm vào dải ruy-băng đỏ ở góc trên trang sách để lưu dấu trang).
  - Tăng/giảm cỡ chữ (`A-` / `A+`) tự động chia lại số trang vừa khít khung giấy.
  - Tự động lưu chương và trang đang đọc dở vào `localStorage` (bọc `try/catch`).

## 4. Hợp đồng kỹ thuật & Bảo mật
- Bản kiểm tra dữ liệu ban đầu được giữ nguyên tại `/check.html`.
- Chỉ tải `books.json` lúc đầu; chỉ tải `chapters/book-N.js` khi người đọc mở sách.
- Toàn bộ nội dung văn bản sách, tên sách, tác giả, tiêu đề chương được chèn bằng `textContent` (không dùng `innerHTML`).
