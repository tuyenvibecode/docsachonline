"""Mỗi file trong thư mục này là một "nguồn sách" (adapter).

Hợp đồng chung: mỗi adapter có hàm

    fetch(ref, **opts) -> dict

Dict trả về có các khóa:
    title, author, language          chuỗi
    source, source_id, source_url    nguồn gốc (để chống nhập trùng)
    license                          phải nằm trong ALLOWED_LICENSES (xem common.py)
    wrapped                          True nếu chữ bị ngắt dòng cứng cần gộp lại
    chapters                         danh sách (tiêu đề, nội dung) nếu nguồn đã chia chương, hoặc None
    raw_text                         văn bản thô nếu chapters là None
    cover_bytes                      bytes ảnh bìa hoặc None

Thêm nguồn mới: xem .agent/workflows/04-add-source-adapter.md
"""
