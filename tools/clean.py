"""Làm sạch chữ: gộp dòng bị ngắt theo trang in thành đoạn văn, tách chương."""
import re
import statistics

# Dòng kết thúc bằng các ký tự này thì coi là hết câu
TERMINAL = (".", "!", "?", "…", ":", '"', "”", "’", ")", "»", "]")
# Dòng bắt đầu bằng các ký tự này thì coi là đoạn mới (lời thoại)
DIALOGUE_START = ("-", "–", "—", "“", '"', "‘")

# Dòng tiêu đề chương: "Chương 1", "CHAPTER IV", "Hồi 3 - ..." ...
DEFAULT_CHAPTER_PATTERN = (
    r"^(chương|chuong|hồi|phần|chapter|book|part)\s+(\d+|[ivxlc]+)\b[^\n]{0,70}$"
    r"|^(prologue|epilogue|lời nói đầu|lời tựa|lời kết)\b[^\n]{0,40}$"
)


def normalize(text):
    """Chuẩn hóa xuống dòng: tối đa 1 dòng trống giữa các đoạn, lọc số trang & rác bản in đầu/cuối PDF."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("­", "").replace(" ", " ").replace("​", "")
    # Cắt bỏ phần mục lục cuối sách và trang thông tin nhà in bị lỗi mã VNI
    m_end = re.search(r"\n\s*M\s*Ụ\s*C\s+L\s*Ụ\s*C\s*\n|\nIn\s+\d[\d.]*\s+cuöën", text)
    if m_end and m_end.start() > len(text) * 0.8:
        text = text[:m_end.start()]
    # Cắt bỏ trang thông tin bản quyền nhà xuất bản ở đầu PDF nếu có dòng LỜI GIỚI THIỆU
    m_start = re.search(r"\n\s*LỜI GIỚI THIỆU\s*\n", text)
    if m_start and 0 < m_start.start() < 3000:
        text = text[m_start.start():]
    text = re.sub(r"\bB?elieve that you will succeed", "Believe that you will succeed", text)
    # Lọc các dòng chỉ chứa số trang hoặc tiêu đề trang in lặp lại ở đầu/cuối mỗi trang PDF
    cleaned_lines = []
    for line in text.split("\n"):
        s = line.strip()
        if re.match(r"^\d{1,4}$", s):
            continue
        if s in ("Đ Ắ C   N H Â N   T Â M", "Đ Ắ C N H Â N T Â M", "HOW TO WIN FRIENDS & INFLUENCE PEOPLE"):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]*\n(?:[ \t]*\n)+", "\n\n", text)
    return text.strip()


def unwrap(text):
    """Gộp các dòng bị ngắt cứng (từ PDF, bản in) lại thành đoạn văn.

    Cách đoán: nếu một dòng ngắn hơn nhiều so với dòng bình thường
    và kết thúc bằng dấu câu thì đó là hết đoạn.
    Hạn chế: thơ (dòng ngắn đều nhau) có thể bị gộp sai. Dùng --no-unwrap cho thơ.
    """
    text = normalize(text)
    lines = [l.strip() for l in text.split("\n")]
    lens = [len(l) for l in lines if l]
    if not lens:
        return ""
    median = statistics.median(lens)
    paras, cur = [], []

    def flush():
        if cur:
            paras.append(" ".join(cur))
            cur.clear()

    for l in lines:
        if not l:
            flush()
            continue
        if cur and l.startswith(DIALOGUE_START):
            flush()
        cur.append(l)
        if l.endswith(TERMINAL) and len(l) < 0.7 * median:
            flush()
    flush()
    return "\n\n".join(paras)


def split_chapters(raw, pattern=None, min_chars=200):
    """Tách văn bản thô thành chương theo dòng tiêu đề.

    Trả về (danh sách (tiêu đề, nội dung), số mục đã bỏ vì quá ngắn).
    Mục quá ngắn thường là mục lục hoặc trang bìa.
    Phải gọi TRƯỚC unwrap, vì dòng tiêu đề ngắn sẽ bị gộp nhầm vào đoạn sau.
    """
    rx = re.compile(pattern or DEFAULT_CHAPTER_PATTERN, re.IGNORECASE)
    lines = raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    chapters, title, buf = [], "Mở đầu", []
    for line in lines:
        s = line.strip()
        if s and len(s) <= 90 and rx.match(s):
            chapters.append((title, "\n".join(buf)))
            title, buf = s, []
        else:
            buf.append(line)
    chapters.append((title, "\n".join(buf)))
    kept = [(t, b) for t, b in chapters if len(b.strip()) >= min_chars]
    return kept, len(chapters) - len(kept)


def chunk_by_size(text, target=12000):
    """Không tìm thấy tiêu đề chương: chia theo độ dài, cắt ở ranh giới đoạn."""
    paras = text.split("\n\n")
    chunks, cur, size = [], [], 0
    for p in paras:
        if cur and size + len(p) > target:
            chunks.append("\n\n".join(cur))
            cur, size = [], 0
        cur.append(p)
        size += len(p) + 2
    if cur:
        chunks.append("\n\n".join(cur))
    return [(f"Phần {i}", c) for i, c in enumerate(chunks, 1)]


def convert_text(raw, wrapped=True, pattern=None):
    """Từ văn bản thô ra danh sách chương sạch (tiêu đề, nội dung). Cùng thuật toán với lib/clean.js."""
    found, dropped = split_chapters(raw, pattern)
    if len(found) >= 2:
        chapters = found
    else:
        chapters = chunk_by_size(unwrap(raw) if wrapped else normalize(raw))
        wrapped = False  # đã xử lý xong
    cleaned = []
    for title, body in chapters:
        body = unwrap(body) if wrapped else normalize(body)
        if body:
            cleaned.append((title.strip(), body))
    return cleaned, dropped
