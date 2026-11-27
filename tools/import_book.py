#!/usr/bin/env python3
"""Nhập một cuốn sách vào thư viện.

Ví dụ:
    python tools/import_book.py local inbox/sach.pdf
    python tools/import_book.py local inbox/sach.docx --title "Tên" --author "Tên"

Xong sẽ tạo: chapters/book-N.js, covers/book-N.webp (nếu có bìa), data/meta/book-N.json
và cập nhật books.json. Sau đó chạy: python tools/verify.py rồi python tools/sync.py
"""
import argparse
import datetime
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import clean  # noqa: E402
import build_index  # noqa: E402
from common import (  # noqa: E402
    ALLOWED_LICENSES, COVERS_DIR, META_DIR, ROOT,
    load_all_meta, next_id, write_chapter_file,
)
from adapters import local  # noqa: E402

# Mỗi nguồn là một file trong tools/adapters/. Hiện chỉ có "local" (file của chủ dự án).
# Thêm nguồn mới: xem .agent/workflows/04-add-source-adapter.md
ADAPTERS = {"local": local}


def save_cover(book_id, data):
    """Lưu bìa nhỏ gọn. Có Pillow thì cắt viền trắng thừa và đổi sang webp 400px; không có thì bỏ qua bìa."""
    if not data:
        return None
    try:
        from PIL import Image, ImageChops
    except ImportError:
        print("(chưa cài Pillow nên bỏ qua ảnh bìa: pip install pillow)")
        return None
    COVERS_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.open(io.BytesIO(data)).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    bbox = ImageChops.difference(img, bg).point(lambda x: 255 if x > 25 else 0).getbbox()
    if bbox:
        img = img.crop(bbox)
    img.thumbnail((400, 600))
    out = COVERS_DIR / f"book-{book_id}.webp"
    img.save(out, "WEBP", quality=80)
    return f"covers/{out.name}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", choices=sorted(ADAPTERS))
    ap.add_argument("ref", help="ID, link hoặc đường dẫn file tùy nguồn")
    ap.add_argument("--title")
    ap.add_argument("--author")
    ap.add_argument("--license")
    ap.add_argument("--language")
    ap.add_argument("--cover", help="đường dẫn ảnh bìa (nguồn local)")
    ap.add_argument("--pattern", help="regex nhận dòng tiêu đề chương (nếu tự nhận chưa đúng)")
    ap.add_argument("--no-unwrap", action="store_true", help="không gộp dòng (dùng cho thơ)")
    ap.add_argument("--dry-run", action="store_true", help="chỉ báo cáo, không ghi file")
    ap.add_argument("--force", action="store_true", help="nhập lại dù đã có")
    a = ap.parse_args()

    book = ADAPTERS[a.source].fetch(
        a.ref, title=a.title, author=a.author, license=a.license,
        language=a.language, cover=a.cover,
    )

    # Cổng giấy phép: không qua được thì dừng, không có ngoại lệ
    if book["license"] not in ALLOWED_LICENSES:
        sys.exit(f"Giấy phép '{book['license']}' không nằm trong danh sách cho phép: {sorted(ALLOWED_LICENSES)}")

    # Chống nhập trùng
    for m in load_all_meta():
        if m["source"] == book["source"] and m["source_id"] == book["source_id"] and not a.force:
            sys.exit(f"Đã có rồi (book-{m['id']}: {m['title']}). Dùng --force nếu muốn nhập lại.")

    wrapped = book["wrapped"] and not a.no_unwrap
    if book["chapters"] is not None:  # nguồn đã chia chương sẵn
        cleaned, dropped = [], 0
        for title, body in book["chapters"]:
            body = clean.unwrap(body) if wrapped else clean.normalize(body)
            if body:
                cleaned.append((title.strip(), body))
    else:
        cleaned, dropped = clean.convert_text(book["raw_text"], wrapped, a.pattern)
    if not cleaned:
        sys.exit("Không có chương nào có chữ. Kiểm tra lại nguồn.")

    chars = sum(len(b) for _, b in cleaned)
    print(f"{book['title']} — {book['author']}")
    print(f"  nguồn: {book['source']} | giấy phép: {book['license']}")
    print(f"  {len(cleaned)} chương, {chars:,} ký tự" + (f", bỏ {dropped} mục quá ngắn (mục lục/trang bìa)" if dropped else ""))
    print(f"  chương đầu: {cleaned[0][0]!r} | chương cuối: {cleaned[-1][0]!r}")
    if a.dry_run:
        print("(dry-run: chưa ghi gì)")
        return

    book_id = next_id()
    write_chapter_file(book_id, cleaned)
    cover = save_cover(book_id, book["cover_bytes"])
    META_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "id": book_id,
        "title": book["title"],
        "author": book["author"],
        "language": book["language"],
        "source": book["source"],
        "source_id": book["source_id"],
        "source_url": book["source_url"],
        "license": book["license"],
        "cover": cover,
        "chapters": len(cleaned),
        "chars": chars,
        "added": datetime.date.today().isoformat(),
    }
    import json
    (META_DIR / f"book-{book_id}.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    build_index.main()
    print(f"Đã ghi book-{book_id}. Tiếp theo: python tools/verify.py")


if __name__ == "__main__":
    main()
