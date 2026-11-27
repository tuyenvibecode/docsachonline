# Định dạng dữ liệu (không đổi tùy tiện)

## chapters/book-N.js — đúng hai dòng

```js
window.__BOOK_TEXT__ = {"1": "nội dung chương 1", "2": "nội dung chương 2"};
window.__BOOK_TITLES__ = {"1": "Chương 1", "2": "Chương 2"};
```

- Khóa chương là chuỗi số liên tục `"1"` đến `"n"`.
- Trong nội dung chương, các **đoạn văn cách nhau bằng `\n\n`**. Không ngắt dòng cứng theo trang in.
- Ghi bằng `json.dumps(..., ensure_ascii=False)` (tiếng Việt giữ nguyên dấu, không `\uXXXX`).
- Mỗi chương nên khoảng 5.000–20.000 ký tự. Ngắn hơn 200 ký tự là đáng ngờ (có thể là mục lục).

## data/meta/book-N.json — nguồn thật của thông tin sách

```json
{
  "id": 1, "title": "", "author": "", "language": "vi",
  "source": "local|<tên adapter khác>", "source_id": "", "source_url": "",
  "license": "public-domain", "cover": "covers/book-1.webp",
  "chapters": 10, "chars": 138000, "added": "2026-11-26"
}
```

`chapters` và `chars` phải khớp đúng với file chương (verify.py kiểm tra).

## books.json

Chỉ do `tools/build_index.py` tạo. Dạng `{"books": [ ...các meta... ]}`. Không sửa tay.

## Ảnh bìa

`covers/book-N.webp`, rộng tối đa 400px, chất lượng 80. Không có bìa thì để `"cover": null`, UI tự vẽ bìa thay thế.
