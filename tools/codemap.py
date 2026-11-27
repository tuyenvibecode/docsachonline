#!/usr/bin/env python3
"""Tạo CODEMAP.md: bản đồ ngắn của dự án để AI đọc thay vì mở từng file (tiết kiệm token).

Bản đồ liệt kê: việc gì thì mở file nào, từng hàm Python (kèm số dòng và mô tả một dòng),
các hàm trong index.html, và các rules/workflows/skills. Tất cả sinh tự động từ code,
nên luôn đúng. Không có ngày giờ hay số liệu sách để tránh đổi liên tục.

Dùng:
    python tools/codemap.py           # ghi lại CODEMAP.md
    python tools/codemap.py --check   # chỉ kiểm tra có lỗi thời không (thoát mã 1 nếu lệch)
"""
import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402

CODEMAP = ROOT / "CODEMAP.md"

HEADER = """# CODEMAP

> File này **tự sinh** bởi `python tools/codemap.py`. Không sửa tay.
> **AI: đọc file này TRƯỚC.** Chỉ mở file khi thật cần, và dùng số dòng bên dưới để đọc đúng đoạn (Read với offset/limit).

## Việc gì thì mở file nào

| Muốn... | Mở |
|---|---|
| Nhập thêm sách từ file của chủ dự án | `tools/import_book.py` (lệnh), `tools/adapters/local.py` |
| Sửa cách tách chương, gộp dòng | `tools/clean.py` |
| Thêm nguồn sách mới | `tools/adapters/__init__.py` (hợp đồng) và `.agent/workflows/04-add-source-adapter.md` |
| Đổi cách kiểm tra dữ liệu | `tools/verify.py` |
| Đẩy lên GitHub | `tools/sync.py` |
| Biết định dạng file chương, meta | `.agent/rules/03-data-format.md` |
| Biết quy định giấy phép, nguồn | `.agent/rules/02-sources-and-licenses.md` |
| Đăng nhập, gửi sách chờ duyệt, kệ chung, dashboard | `supabase/schema.sql`, `.agent/rules/06-auth-and-security.md`, `.agent/workflows/06-auth-dashboard.md` |
| Chuyển PDF/txt thành chương trên trình duyệt | `lib/clean.js` (khớp `tools/clean.py`) |
| Giao diện (bản kiểm tra tạm) | `index.html`; UI thật làm theo `design.md` |

## Luồng dữ liệu

```
inbox/ (file của chủ dự án) → import_book.py → chapters/book-N.js + data/meta/book-N.json (+ covers/)
        → build_index.py → books.json → verify.py → sync.py → GitHub → Vercel
```

## KHÔNG mở nguyên file (rất tốn token)

- `chapters/book-N.js`: mỗi file là cả cuốn sách (hàng trăm KB, dòng rất dài). Xem một đoạn nhỏ bằng:
  `python -c "import sys; sys.path.insert(0,'tools'); from common import read_chapter_file as r; t,ti=r('chapters/book-1.js'); print(ti); print(t['1'][:800])"`
- `books.json`, `data/meta/*.json`: `python tools/verify.py` đã tóm tắt; chỉ mở khi sửa định dạng.
- `covers/`, `inbox/`: không đọc.
- Python và HTML: dùng số dòng trong bản đồ dưới đây để đọc từng đoạn.
"""


def _first_line(text):
    if not text:
        return ""
    for line in text.strip().splitlines():
        if line.strip():
            return line.strip()
    return ""


def _cell(s):
    return s.replace("|", "/").replace("\n", " ").strip()


def _signature(node):
    a = node.args
    parts = [x.arg for x in a.posonlyargs + a.args]
    if a.vararg:
        parts.append("*" + a.vararg.arg)
    parts += [x.arg for x in a.kwonlyargs]
    if a.kwarg:
        parts.append("**" + a.kwarg.arg)
    return f"{node.name}({', '.join(parts)})"


def python_section():
    out = ["## Python (tools/)", ""]
    files = sorted(p for p in (ROOT / "tools").rglob("*.py") if "__pycache__" not in p.parts)
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        src = p.read_text(encoding="utf-8")
        tree = ast.parse(src)
        out.append(f"### `{rel}`  ({len(src.splitlines())} dòng)")
        doc = _first_line(ast.get_docstring(tree))
        if doc:
            out.append(doc)
        consts = [t.id for n in tree.body if isinstance(n, ast.Assign)
                  for t in n.targets if isinstance(t, ast.Name) and t.id.isupper()]
        if consts:
            out.append(f"Hằng số: {', '.join(f'`{c}`' for c in consts)}")
        funcs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for n in funcs:
            if n.name.startswith("_") and not ast.get_docstring(n):
                continue
            d = _first_line(ast.get_docstring(n))
            out.append(f"- `{_signature(n)}` (dòng {n.lineno})" + (f": {d}" if d else ""))
        out.append("")
    return "\n".join(out)


def html_section():
    """Liệt kê hàm JS trong index.html và lib/*.js (số dòng + mục đích)."""
    files = [ROOT / "index.html"] + sorted((ROOT / "lib").glob("*.js")) if (ROOT / "lib").exists() else [ROOT / "index.html"]
    rx = re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)")
    out = ["## Web (JavaScript)", ""]
    for p in files:
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8").splitlines()
        purpose = next((l.split(":", 1)[1].strip() for l in lines[:6] if l.startswith("// Mục đích:")), "")
        out.append(f"### `{p.relative_to(ROOT).as_posix()}`  ({len(lines)} dòng)")
        if purpose:
            out.append(purpose)
        for i, line in enumerate(lines, 1):
            m = rx.match(line)
            if m:
                out.append(f"- `{m.group(1)}({m.group(2).strip()})` (dòng {i})")
        out.append("")
    return "\n".join(out)


def _md_title(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _skill_desc(path):
    m = re.search(r"^description:\s*(.+)$", path.read_text(encoding="utf-8"), re.M)
    return m.group(1).strip() if m else ""


def agent_section():
    base = ROOT / ".agent"
    out = ["## Rules, workflows, skills (.agent/)", ""]
    for kind in ("rules", "workflows"):
        d = base / kind
        if d.exists():
            out.append(f"**{kind}**")
            for p in sorted(d.glob("*.md")):
                out.append(f"- `.agent/{kind}/{p.name}`: {_cell(_md_title(p))}")
            out.append("")
    d = base / "skills"
    if d.exists():
        out.append("**skills**")
        for p in sorted(d.glob("*/SKILL.md")):
            desc = _cell(_skill_desc(p))
            if len(desc) > 140:
                desc = desc[:137] + "..."
            out.append(f"- `.agent/skills/{p.parent.name}/SKILL.md`: {desc}")
        out.append("")
    return "\n".join(out)


def render():
    parts = [HEADER, python_section(), html_section(), agent_section()]
    return "\n".join(x for x in parts if x).rstrip() + "\n"


def main():
    text = render()
    if "--check" in sys.argv:
        if not CODEMAP.exists() or CODEMAP.read_text(encoding="utf-8") != text:
            print("CODEMAP.md bị lỗi thời. Chạy: python tools/codemap.py")
            sys.exit(1)
        print("CODEMAP.md còn đúng.")
        return
    CODEMAP.write_text(text, encoding="utf-8")
    print(f"CODEMAP.md: {len(text.splitlines())} dòng, khoảng {len(text) // 3} token")


if __name__ == "__main__":
    main()
