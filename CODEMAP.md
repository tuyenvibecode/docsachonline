# CODEMAP

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

## Python (tools/)

### `tools/adapters/__init__.py`  (17 dòng)
Mỗi file trong thư mục này là một "nguồn sách" (adapter).

### `tools/adapters/local.py`  (79 dòng)
Nguồn: file trên máy (txt, docx, pdf có chữ). Dùng cho file của chính anh.
- `fetch(ref, **opts)` (dòng 49)

### `tools/build_index.py`  (29 dòng)
Tạo lại books.json từ data/meta/book-*.json.
- `build()` (dòng 15)
- `render(data)` (dòng 19)
- `main()` (dòng 23)

### `tools/clean.py`  (128 dòng)
Làm sạch chữ: gộp dòng bị ngắt theo trang in thành đoạn văn, tách chương.
Hằng số: `TERMINAL`, `DIALOGUE_START`, `DEFAULT_CHAPTER_PATTERN`
- `normalize(text)` (dòng 17): Chuẩn hóa xuống dòng: tối đa 1 dòng trống giữa các đoạn, lọc số trang & rác bản in đầu/cuối PDF.
- `unwrap(text)` (dòng 45): Gộp các dòng bị ngắt cứng (từ PDF, bản in) lại thành đoạn văn.
- `split_chapters(raw, pattern, min_chars)` (dòng 78): Tách văn bản thô thành chương theo dòng tiêu đề.
- `chunk_by_size(text, target)` (dòng 100): Không tìm thấy tiêu đề chương: chia theo độ dài, cắt ở ranh giới đoạn.
- `convert_text(raw, wrapped, pattern)` (dòng 115): Từ văn bản thô ra danh sách chương sạch (tiêu đề, nội dung). Cùng thuật toán với lib/clean.js.

### `tools/codemap.py`  (181 dòng)
Tạo CODEMAP.md: bản đồ ngắn của dự án để AI đọc thay vì mở từng file (tiết kiệm token).
Hằng số: `CODEMAP`, `HEADER`
- `python_section()` (dòng 83)
- `html_section()` (dòng 108): Liệt kê hàm JS trong index.html và lib/*.js (số dòng + mục đích).
- `agent_section()` (dòng 141)
- `render()` (dòng 163)
- `main()` (dòng 168)

### `tools/common.py`  (80 dòng)
Hàm dùng chung cho các công cụ nhập sách.
Hằng số: `ROOT`, `CHAPTERS_DIR`, `COVERS_DIR`, `META_DIR`, `BOOKS_JSON`, `ALLOWED_LICENSES`, `USER_AGENT`
- `http_get(url, params, binary, timeout, pause)` (dòng 25): Tải một URL. Nghỉ một chút sau mỗi lần để không làm nặng máy chủ người ta.
- `load_all_meta()` (dòng 36)
- `next_id()` (dòng 45)
- `write_chapter_file(book_id, chapters)` (dòng 55): Ghi chapters/book-N.js. chapters là danh sách (tiêu đề, nội dung).
- `read_chapter_file(path)` (dòng 69): Đọc lại file chương, trả về (texts, titles). Dùng cho verify.

### `tools/import_book.py`  (128 dòng)
Nhập một cuốn sách vào thư viện.
Hằng số: `ADAPTERS`
- `save_cover(book_id, data)` (dòng 31): Lưu bìa nhỏ gọn. Có Pillow thì cắt viền trắng thừa và đổi sang webp 400px; không có thì bỏ qua bìa.
- `main()` (dòng 52)

### `tools/sync.py`  (65 dòng)
Đồng bộ lên GitHub: dựng lại books.json và CODEMAP.md, kiểm tra, commit, push.
Hằng số: `PY`
- `run(cmd, check)` (dòng 22)
- `main()` (dòng 26)

### `tools/verify.py`  (136 dòng)
Kiểm tra toàn bộ dữ liệu. Thoát mã 1 nếu có lỗi (dùng cho GitHub Action).
- `err(msg)` (dòng 25)
- `warn(msg)` (dòng 29)
- `main()` (dòng 33)

## Web (JavaScript)

### `index.html`  (4892 dòng)
Giao diện kệ sách gỗ 3D và trình đọc sách lật trang 3D (3D Flipbook Reader).
- `usernameToInternalEmail(rawUsername)` (dòng 1745)
- `normalizeInternalPassword(rawPass)` (dòng 1759)
- `getProfileUsername(p)` (dòng 1765)
- `getProfileFullName(p)` (dòng 1772)
- `showSpineToast(msg)` (dòng 1778)
- `loadPrefs()` (dòng 1798)
- `savePrefs()` (dòng 1808)
- `applyUiTheme(uiTheme)` (dòng 1815)
- `applyPaperTheme(paper)` (dòng 1825)
- `applyFontSize(size)` (dòng 1834)
- `isSinglePageLayout()` (dòng 1840)
- `initLibrary()` (dòng 1845)
- `updateLibraryHeaderCount()` (dòng 1867)
- `splitTitleToLines(rawTitle)` (dòng 1885)
- `toSpecBookObject(b, idx)` (dòng 1905)
- `renderBookshelf()` (dòng 1926)
- `togglePullBook(item)` (dòng 1995)
- `createBookCard(item)` (dòng 2014)
- `loadBookScript(b)` (dòng 2119)
- `openBook(b)` (dòng 2154)
- `closeReader()` (dòng 2180)
- `paginateCurrentChapter()` (dòng 2188)
- `renderPageBlocks(container, blocks)` (dòng 2299)
- `openChapter(chapNum, targetPageIdx = 0)` (dòng 2312)
- `renderCurrentSpread()` (dòng 2339)
- `renderScrollReader()` (dòng 2386)
- `canTurnNext()` (dòng 2407)
- `canTurnPrev()` (dòng 2413)
- `flipNextPage()` (dòng 2419)
- `flipPrevPage()` (dòng 2430)
- `prepareFlipSession(direction)` (dòng 2442)
- `setFlipProgress(session, rawProgress)` (dòng 2552)
- `animateFlipTo(session, targetProgress, shouldCommit)` (dòng 2597)
- `stepFrame(now)` (dòng 2604)
- `finishFlipSession(session, shouldCommit)` (dòng 2623)
- `getBookKey(b)` (dòng 2648)
- `saveReadingProgress()` (dòng 2655)
- `toggleBookmark(e)` (dòng 2682)
- `updateBookmarkRibbon()` (dòng 2709)
- `openDrawer(mode = "toc")` (dòng 2728)
- `closeDrawer()` (dòng 2737)
- `renderDrawerList()` (dòng 2742)
- `updateModeButtons()` (dòng 2797)
- `bindEvents()` (dòng 2803)
- `onPointerDown(e, forcedDir)` (dòng 2864)
- `onPointerMove(e)` (dòng 2891)
- `onPointerUp(e)` (dòng 2911)
- `isSupabaseConfigured()` (dòng 2951)
- `isApprovedUser()` (dòng 2956)
- `isAdminUser()` (dòng 2960)
- `initSupabaseClient()` (dòng 2964)
- `refreshAuthSession()` (dòng 2970)
- `showAuthLoginForm(mode = "login")` (dòng 3054)
- `showAuthStatusGate(kind, title, msg)` (dòng 3066)
- `switchAuthPortalMode(mode)` (dòng 3080)
- `setAuthAlert(type, msg)` (dòng 3099)
- `loadSupabaseBooksAndProgress()` (dòng 3111)
- `loadLocalUserBooks()` (dòng 3152)
- `saveLocalUserBooks()` (dòng 3177)
- `switchMainTab(tab)` (dòng 3187)
- `loadPdfJs()` (dòng 3212)
- `extractTextFromPdfFile(file, onProgress)` (dòng 3230)
- `handleSelectedBookFile(file)` (dòng 3276)
- `submitPendingUserBook()` (dòng 3342)
- `renderMyBooksList()` (dòng 3424)
- `deleteUserBook(b, byAdmin)` (dòng 3537)
- `updateAdminBadgeCount()` (dòng 3560)
- `switchAdminSection(sec)` (dòng 3596)
- `renderAdminDashboard()` (dòng 3613)
- `adminUpdateBook(b, patch)` (dòng 4281)
- `adminUpdateProfile(uid, patch)` (dòng 4297)
- `adminResetPassword(u)` (dòng 4311)
- `setChangePassAlert(type, msg)` (dòng 4326)
- `openChangePassModal()` (dòng 4337)
- `closeChangePassModal()` (dòng 4347)
- `submitChangePassword(e)` (dòng 4351)
- `loadLocalFeedbacks()` (dòng 4388)
- `saveLocalFeedbacks(list)` (dòng 4397)
- `getSeenReplyIds()` (dòng 4401)
- `updateUserFeedbackBadge()` (dòng 4410)
- `markFeedbackRepliesSeen()` (dòng 4418)
- `loadMyFeedbacks()` (dòng 4424)
- `submitUserFeedback(e)` (dòng 4436)
- `formatDateTime(iso)` (dòng 4490)
- `buildFeedbackCard(f, opts)` (dòng 4497)
- `renderMyFeedbacks()` (dòng 4536)
- `renderAdminFeedbacks(list)` (dòng 4551)
- `adminReplyFeedback(f, text)` (dòng 4612)
- `adminDeleteFeedback(f)` (dòng 4633)
- `previewUserBookContent(b)` (dòng 4648)
- `bindStep4Events()` (dòng 4670)

### `lib/clean.js`  (132 dòng)
Chuyển văn bản thô (lấy từ PDF hoặc txt) thành các chương sạch ngay trên trình duyệt. Cùng thuật toán với tools/clean.py.
- `median(nums)` (dòng 15)
- `normalize(text)` (dòng 22)
- `unwrap(text)` (dòng 50)
- `splitChapters(raw, pattern = null, minChars = 200)` (dòng 70)
- `chunkBySize(text, target = 12000)` (dòng 92)
- `convertText(raw, { wrapped = true, pattern = null } = {})` (dòng 109)
- `toBookJson(chapters)` (dòng 127)

## Rules, workflows, skills (.agent/)

**rules**
- `.agent/rules/01-project-overview.md`: Tổng quan dự án
- `.agent/rules/02-sources-and-licenses.md`: Nguồn dữ liệu
- `.agent/rules/03-data-format.md`: Định dạng dữ liệu (không đổi tùy tiện)
- `.agent/rules/04-step-gates.md`: Làm từng bước, dừng để chủ dự án duyệt
- `.agent/rules/05-token-saving.md`: Tiết kiệm token (BẮT BUỘC)
- `.agent/rules/06-auth-and-security.md`: Đăng nhập, gửi sách chờ duyệt, kệ chung và dashboard (bước 4)

**workflows**
- `.agent/workflows/01-import-data.md`: /01-import-data — Chuẩn bị dữ liệu
- `.agent/workflows/02-verify-web.md`: /02-verify-web — Đưa dữ liệu lên web kiểm tra
- `.agent/workflows/03-build-ui.md`: /03-build-ui — Xây giao diện thật
- `.agent/workflows/04-add-source-adapter.md`: /04-add-source-adapter — Thêm một nguồn sách mới
- `.agent/workflows/05-sync-to-github.md`: /05-sync-to-github — Đưa sách mới lên GitHub và web
- `.agent/workflows/06-auth-dashboard.md`: /06-auth-dashboard — Đăng nhập, gửi sách chờ duyệt, kệ chung, dashboard (bước 4)

**skills**
- `.agent/skills/book-importer/SKILL.md`: Nhập một cuốn sách vào thư viện bằng tools/import_book.py từ file của chủ dự án (txt/docx/pdf). Dùng khi cần thêm sách mới.
- `.agent/skills/codemap/SKILL.md`: Dùng CODEMAP.md để tìm đúng file và đúng dòng cần sửa mà không phải mở cả dự án, và cập nhật lại bản đồ sau khi sửa code. Dùng ở đầu mọi ...
- `.agent/skills/data-verifier/SKILL.md`: Kiểm tra chất lượng dữ liệu sách bằng tools/verify.py và đọc thử bằng mắt trước khi sang bước 2 hoặc trước khi push. Dùng sau mỗi lần nhậ...
- `.agent/skills/text-cleaner/SKILL.md`: Xử lý chữ khi nhập sách bị sai: chương tách sai, dòng bị ngắt cứng, rác đầu/cuối, lỗi bảng mã. Dùng khi dry-run hoặc verify báo số chương...
