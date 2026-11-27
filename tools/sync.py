#!/usr/bin/env python3
"""Đồng bộ lên GitHub: dựng lại books.json và CODEMAP.md, kiểm tra, commit, push.

Vercel nối với GitHub nên sau khi push, web tự cập nhật sau vài chục giây.

Dùng:
    python tools/sync.py                      # commit + push
    python tools/sync.py -m "Thêm 5 sách"     # tự đặt nội dung commit
    python tools/sync.py --no-push            # chỉ commit trên máy
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, load_all_meta  # noqa: E402

PY = sys.executable


def run(cmd, check=True):
    return subprocess.run(cmd, cwd=ROOT, check=check, text=True, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--message")
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    if not (ROOT / ".git").exists():
        sys.exit("Thư mục này chưa là git repo. Chạy: git init && git remote add origin <link repo>")

    subprocess.run([PY, "tools/build_index.py"], cwd=ROOT, check=True)
    subprocess.run([PY, "tools/codemap.py"], cwd=ROOT, check=True)
    ver = subprocess.run([PY, "tools/verify.py"], cwd=ROOT, text=True, capture_output=True)
    print(ver.stdout, end="")
    if ver.returncode != 0:
        sys.exit("Dừng: dữ liệu chưa đạt kiểm tra, không commit.")

    # Chỉ thêm đúng các đường dẫn của dự án (không "git add ." để khỏi đưa nhầm file tạm trong inbox/)
    paths = ["books.json", "chapters", "covers", "pdf", "data", "CODEMAP.md", "tools", ".agent", ".github",
             "lib", "supabase", "web-config.js", "check.html", "KE-SACH-SPEC.md",
             "index.html", "README.md", "design.md", ".gitignore"]
    run(["git", "add"] + [x for x in paths if (ROOT / x).exists()])  # bỏ qua thư mục chưa có
    if not run(["git", "status", "--porcelain"]).stdout.strip():
        print("Không có gì thay đổi.")
        return

    msg = a.message or f"Cập nhật thư viện ({len(load_all_meta())} sách)"
    run(["git", "commit", "-m", msg])
    print("Đã commit:", msg)

    if a.no_push:
        return
    r = run(["git", "push", "-u", "origin", "HEAD"], check=False)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit("Push lỗi. Kiểm tra remote (git remote -v) và quyền truy cập.")
    print("Đã push. Vercel sẽ tự deploy.")


if __name__ == "__main__":
    main()
