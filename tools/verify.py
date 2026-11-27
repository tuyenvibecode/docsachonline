#!/usr/bin/env python3
"""Kiểm tra toàn bộ dữ liệu. Thoát mã 1 nếu có lỗi (dùng cho GitHub Action).

Lỗi (dừng): file thiếu, chương rỗng, ký tự lỗi, giấy phép lạ,
            books.json lệch với meta, CODEMAP.md lỗi thời, lộ khóa service_role.
Cảnh báo (chỉ nhắc): chương quá ngắn, thiếu bìa, file bìa mồ côi.
"""
import base64
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_index  # noqa: E402
import codemap  # noqa: E402
from common import (  # noqa: E402
    ALLOWED_LICENSES, BOOKS_JSON, CHAPTERS_DIR, COVERS_DIR, ROOT,
    load_all_meta, read_chapter_file,
)

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def main():
    metas = load_all_meta()

    # books.json phải khớp với meta
    expected = build_index.render(build_index.build())
    if not BOOKS_JSON.exists() or BOOKS_JSON.read_text(encoding="utf-8") != expected:
        err("books.json bị lệch so với data/meta. Chạy: python tools/build_index.py")

    # CODEMAP.md phải khớp với code hiện tại
    if not codemap.CODEMAP.exists() or codemap.CODEMAP.read_text(encoding="utf-8") != codemap.render():
        err("CODEMAP.md bị lỗi thời. Chạy: python tools/codemap.py")

    seen = set()
    for m in metas:
        tag = f"book-{m['id']} ({m['title']})"
        key = (m["source"], m["source_id"])
        if key in seen:
            err(f"{tag}: nhập trùng nguồn {key}")
        seen.add(key)

        if m["license"] not in ALLOWED_LICENSES:
            err(f"{tag}: giấy phép '{m['license']}' không được phép")

        path = CHAPTERS_DIR / f"book-{m['id']}.js"
        if not path.exists():
            err(f"{tag}: thiếu {path.name}")
            continue
        try:
            texts, titles = read_chapter_file(path)
        except Exception as e:
            err(f"{tag}: không đọc được {path.name} ({e})")
            continue
        if not texts:
            err(f"{tag}: {path.name} không có window.__BOOK_TEXT__")
            continue

        n = len(texts)
        if sorted(texts, key=int) != [str(i) for i in range(1, n + 1)]:
            err(f"{tag}: khóa chương không liên tục 1..{n}")
        if n != m["chapters"]:
            err(f"{tag}: meta ghi {m['chapters']} chương nhưng file có {n}")
        total = sum(len(t) for t in texts.values())
        if total != m["chars"]:
            err(f"{tag}: meta ghi {m['chars']} ký tự nhưng file có {total}")

        for k, t in texts.items():
            if not t.strip():
                err(f"{tag}: chương {k} rỗng")
            elif len(t) < 200:
                warn(f"{tag}: chương {k} rất ngắn ({len(t)} ký tự)")
            if "�" in t:
                err(f"{tag}: chương {k} có ký tự lỗi (�), có thể sai bảng mã")

        if m.get("cover"):
            if not (ROOT / m["cover"]).exists():
                err(f"{tag}: ghi bìa {m['cover']} nhưng file không có")
        else:
            warn(f"{tag}: chưa có ảnh bìa")

    # File mồ côi
    ids = {m["id"] for m in metas}
    for p in CHAPTERS_DIR.glob("book-*.js") if CHAPTERS_DIR.exists() else []:
        if int(p.stem.split("-")[1]) not in ids:
            err(f"{p.name}: không có meta tương ứng")
    for p in COVERS_DIR.glob("book-*.*") if COVERS_DIR.exists() else []:
        if int(p.stem.split("-")[1]) not in ids:
            warn(f"{p.name}: ảnh bìa mồ côi")

    # Khóa service_role của Supabase tuyệt đối không được nằm trong repo (file .env thật được phép vì đã gitignore)
    gi = ROOT / ".gitignore"
    if (ROOT / ".env").exists() and (not gi.exists() or ".env" not in gi.read_text(encoding="utf-8").splitlines()):
        err(".env có tồn tại nhưng .gitignore chưa có dòng '.env'")
    jwt_rx = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")
    skip_dirs = {".git", "chapters", "covers", "inbox", "pdf", "node_modules", "__pycache__"}
    for p in ROOT.rglob("*"):
        if (not p.is_file() or p.name == ".env" or (set(p.relative_to(ROOT).parts) & skip_dirs)
                or p.stat().st_size > 2_000_000):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for m in jwt_rx.finditer(text):
            seg = m.group(0).split(".")[1]
            try:
                payload = json.loads(base64.urlsafe_b64decode(seg + "=" * (-len(seg) % 4)))
            except Exception:
                continue
            if isinstance(payload, dict) and payload.get("role") == "service_role":
                err(f"{p.relative_to(ROOT)}: có khóa service_role của Supabase trong repo. Xóa và tạo khóa mới ngay.")

    print(f"Đã kiểm tra {len(metas)} sách.")
    for w in warnings:
        print("  CẢNH BÁO:", w)
    for e in errors:
        print("  LỖI:", e)
    if errors:
        print(f"=> {len(errors)} lỗi. Chưa đạt.")
        sys.exit(1)
    print("=> Đạt." + (f" ({len(warnings)} cảnh báo)" if warnings else ""))


if __name__ == "__main__":
    main()
