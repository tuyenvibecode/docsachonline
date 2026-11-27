#!/usr/bin/env python3
"""Tạo lại books.json từ data/meta/book-*.json.

books.json không bao giờ sửa tay: nó luôn sinh ra từ thư mục meta,
nên thêm sách mới không bao giờ làm lệch danh sách.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import BOOKS_JSON, load_all_meta  # noqa: E402


def build():
    return {"books": load_all_meta()}


def render(data):
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main():
    BOOKS_JSON.write_text(render(build()), encoding="utf-8")
    print(f"books.json: {len(load_all_meta())} sách")


if __name__ == "__main__":
    main()
