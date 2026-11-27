"""Hàm dùng chung cho các công cụ nhập sách.

Chỉ dùng thư viện có sẵn của Python (không cần cài thêm gì),
trừ ảnh bìa (Pillow) và PDF (pypdf) là tùy chọn.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHAPTERS_DIR = ROOT / "chapters"
COVERS_DIR = ROOT / "covers"
META_DIR = ROOT / "data" / "meta"
BOOKS_JSON = ROOT / "books.json"

# Giấy phép được phép nhập. Muốn thêm loại mới phải hỏi chủ dự án.
ALLOWED_LICENSES = {"public-domain", "cc0", "cc-by", "cc-by-sa", "own"}

USER_AGENT = "BookReaderKit/1.0 (personal reading project)"


def http_get(url, params=None, binary=False, timeout=30, pause=0.5):
    """Tải một URL. Nghỉ một chút sau mỗi lần để không làm nặng máy chủ người ta."""
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    time.sleep(pause)
    return data if binary else data.decode("utf-8", errors="replace")


def load_all_meta():
    metas = []
    if META_DIR.exists():
        for p in sorted(META_DIR.glob("book-*.json")):
            metas.append(json.loads(p.read_text(encoding="utf-8")))
    metas.sort(key=lambda m: m["id"])
    return metas


def next_id():
    ids = [m["id"] for m in load_all_meta()]
    return (max(ids) + 1) if ids else 1


def _js_safe(s):
    # Hai ký tự này làm hỏng chuỗi JS ở trình duyệt cũ
    return s.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def write_chapter_file(book_id, chapters):
    """Ghi chapters/book-N.js. chapters là danh sách (tiêu đề, nội dung)."""
    texts = {str(i): t for i, (_, t) in enumerate(chapters, 1)}
    titles = {str(i): ti for i, (ti, _) in enumerate(chapters, 1)}
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    path = CHAPTERS_DIR / f"book-{book_id}.js"
    out = (
        "window.__BOOK_TEXT__ = " + _js_safe(json.dumps(texts, ensure_ascii=False)) + ";\n"
        "window.__BOOK_TITLES__ = " + _js_safe(json.dumps(titles, ensure_ascii=False)) + ";\n"
    )
    path.write_text(out, encoding="utf-8")
    return path


def read_chapter_file(path):
    """Đọc lại file chương, trả về (texts, titles). Dùng cho verify."""
    texts, titles = None, {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"^window\.__BOOK_(TEXT|TITLES)__\s*=\s*(.*);\s*$", line)
        if m:
            data = json.loads(m.group(2))
            if m.group(1) == "TEXT":
                texts = data
            else:
                titles = data
    return texts, titles
