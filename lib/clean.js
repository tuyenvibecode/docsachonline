// Mục đích: Chuyển văn bản thô (lấy từ PDF hoặc txt) thành các chương sạch ngay trên trình duyệt. Cùng thuật toán với tools/clean.py.
// Chữ lấy từ PDF thường bị ngắt dòng theo trang in, nên phải gộp lại thành đoạn văn và tách chương theo tiêu đề.
// Không phụ thuộc thư viện nào, không gọi mạng. Dùng: import { convertText, toBookJson } from "./lib/clean.js"
//
// GHI CHÚ: nếu sửa thuật toán ở đây thì phải sửa tools/clean.py cho khớp (và ngược lại).

const TERMINAL = [".", "!", "?", "…", ":", '"', "”", "’", ")", "»", "]"];       // dòng kết thúc bằng các ký tự này là hết câu
const DIALOGUE_START = ["-", "–", "—", "“", '"', "‘"];                          // dòng bắt đầu bằng các ký tự này là đoạn mới (lời thoại)
const DEFAULT_CHAPTER_PATTERN =
  "^(chương|chuong|hồi|phần|chapter|book|part)\\s+(\\d+|[ivxlc]+)\\b[^\\n]{0,70}$" +
  "|^(prologue|epilogue|lời nói đầu|lời tựa|lời kết)\\b[^\\n]{0,40}$";

const len = (s) => Array.from(s).length; // đếm theo ký tự thật, giống Python

function median(nums) {
  const a = [...nums].sort((x, y) => x - y);
  const m = a.length >> 1;
  return a.length % 2 ? a[m] : (a[m - 1] + a[m]) / 2;
}

/** Chuẩn hóa xuống dòng: tối đa 1 dòng trống giữa các đoạn, lọc số trang & rác bản in đầu/cuối PDF. */
export function normalize(text) {
  let t = text
    .replace(/\r\n/g, "\n").replace(/\r/g, "\n")
    .replace(/­/g, "").replace(/ /g, " ").replace(/​/g, "");
  const mEnd = t.match(/\n\s*M\s*Ụ\s*C\s+L\s*Ụ\s*C\s*\n|\nIn\s+\d[\d.]*\s+cuöën/);
  if (mEnd && mEnd.index > t.length * 0.8) {
    t = t.slice(0, mEnd.index);
  }
  const mStart = t.match(/\n\s*LỜI GIỚI THIỆU\s*\n/);
  if (mStart && mStart.index > 0 && mStart.index < 3000) {
    t = t.slice(mStart.index);
  }
  t = t.replace(/\bB?elieve that you will succeed/g, "Believe that you will succeed");
  const lines = t
    .split("\n")
    .filter((line) => {
      const s = line.trim();
      if (/^\d{1,4}$/.test(s)) return false;
      if (s === "Đ Ắ C   N H Â N   T Â M" || s === "Đ Ắ C N H Â N T Â M" || s === "HOW TO WIN FRIENDS & INFLUENCE PEOPLE") return false;
      return true;
    });
  return lines.join("\n")
    .replace(/[ \t]+/g, " ")
    .replace(/\n[ \t]*\n(?:[ \t]*\n)+/g, "\n\n")
    .trim();
}

/** Gộp các dòng bị ngắt cứng (từ PDF, bản in) lại thành đoạn văn. Thơ thì không nên gộp. */
export function unwrap(text) {
  const lines = normalize(text).split("\n").map((l) => l.trim());
  const lens = lines.filter(Boolean).map(len);
  if (!lens.length) return "";
  const med = median(lens);
  const paras = [];
  let cur = [];
  const flush = () => { if (cur.length) { paras.push(cur.join(" ")); cur = []; } };

  for (const l of lines) {
    if (!l) { flush(); continue; }
    if (cur.length && DIALOGUE_START.some((c) => l.startsWith(c))) flush();
    cur.push(l);
    if (TERMINAL.some((c) => l.endsWith(c)) && len(l) < 0.7 * med) flush();
  }
  flush();
  return paras.join("\n\n");
}

/** Tách văn bản thô thành chương theo dòng tiêu đề. Mục quá ngắn (mục lục, trang bìa) bị bỏ. Gọi TRƯỚC unwrap. */
export function splitChapters(raw, pattern = null, minChars = 200) {
  const rx = new RegExp(pattern || DEFAULT_CHAPTER_PATTERN, "iu");
  const lines = raw.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const all = [];
  let title = "Mở đầu";
  let buf = [];
  for (const line of lines) {
    const s = line.trim();
    if (s && len(s) <= 90 && rx.test(s)) {
      all.push([title, buf.join("\n")]);
      title = s;
      buf = [];
    } else {
      buf.push(line);
    }
  }
  all.push([title, buf.join("\n")]);
  const kept = all.filter(([, b]) => b.trim().length >= minChars);
  return { chapters: kept, dropped: all.length - kept.length };
}

/** Không tìm thấy tiêu đề chương: chia theo độ dài, cắt ở ranh giới đoạn. */
export function chunkBySize(text, target = 12000) {
  const chunks = [];
  let cur = [];
  let size = 0;
  for (const p of text.split("\n\n")) {
    if (cur.length && size + len(p) > target) { chunks.push(cur.join("\n\n")); cur = []; size = 0; }
    cur.push(p);
    size += len(p) + 2;
  }
  if (cur.length) chunks.push(cur.join("\n\n"));
  return chunks.map((c, i) => [`Phần ${i + 1}`, c]);
}

/**
 * Từ văn bản thô ra danh sách chương sạch: { chapters: [{title, body}], dropped }.
 * wrapped = true khi chữ bị ngắt dòng cứng (PDF, txt từ bản in); false cho chữ đã chia đoạn sẵn.
 */
export function convertText(raw, { wrapped = true, pattern = null } = {}) {
  const { chapters: found, dropped } = splitChapters(raw, pattern);
  let chapters;
  if (found.length >= 2) {
    chapters = found;
  } else {
    chapters = chunkBySize(wrapped ? unwrap(raw) : normalize(raw));
    wrapped = false; // đã xử lý xong
  }
  const cleaned = [];
  for (const [title, body0] of chapters) {
    const body = wrapped ? unwrap(body0) : normalize(body0);
    if (body) cleaned.push({ title: title.trim(), body });
  }
  return { chapters: cleaned, dropped };
}

/** Đóng gói thành đúng định dạng file chương: { texts: {"1": ...}, titles: {"1": ...} }. */
export function toBookJson(chapters) {
  const texts = {};
  const titles = {};
  chapters.forEach((c, i) => { texts[String(i + 1)] = c.body; titles[String(i + 1)] = c.title; });
  return { texts, titles };
}
