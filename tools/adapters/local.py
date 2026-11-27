"""Nguồn: file trên máy (txt, docx, pdf có chữ). Dùng cho file của chính anh.

Dùng: python tools/import_book.py local inbox/sach-cua-toi.pdf
      (thêm --title, --author, --cover, --license nếu muốn; không có thì tự điền)

Không bắt buộc tham số nào: thiếu tên sách thì lấy theo tên file, thiếu tác giả thì ghi "Không rõ",
thiếu giấy phép thì ghi "own". PDF scan ảnh chưa hỗ trợ (cần OCR).
"""
import re
import sys
import zipfile
from html import unescape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _read_txt(path):
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-8", "cp1258", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def _read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    xml = re.sub(r"</w:p>", "\n\n", xml)
    xml = re.sub(r"<w:tab/>", " ", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return unescape(xml)


def _read_pdf(path):
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit("Đọc PDF cần pypdf: pip install pypdf")
    reader = PdfReader(str(path))
    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    if len(text.strip()) < 200:
        raise SystemExit("PDF này gần như không có chữ (có thể là PDF scan ảnh). Cần OCR, chưa hỗ trợ.")
    return text


def fetch(ref, **opts):
    path = Path(ref)
    if not path.exists():
        raise SystemExit(f"Không thấy file: {path}")
    ext = path.suffix.lower()
    if ext == ".txt":
        text, wrapped = _read_txt(path), True
    elif ext == ".docx":
        text, wrapped = _read_docx(path), False  # docx đã chia đoạn sẵn
    elif ext == ".pdf":
        text, wrapped = _read_pdf(path), True
    else:
        raise SystemExit("Chỉ hỗ trợ .txt, .docx, .pdf")

    cover = None
    if opts.get("cover"):
        cover = Path(opts["cover"]).read_bytes()

    return {
        "title": opts.get("title") or path.stem.replace("_", " ").replace("-", " ").strip(),
        "author": opts.get("author") or "Không rõ",
        "language": opts.get("language") or "vi",
        "source": "local",
        "source_id": path.name,
        "source_url": "",
        "license": opts.get("license") or "own",
        "wrapped": wrapped,
        "chapters": None,
        "raw_text": text,
        "cover_bytes": cover,
    }
