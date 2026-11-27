-- Cấu trúc Supabase cho web đọc sách: tài khoản, sách do người dùng tự tải lên, tiến độ đọc, dấu trang.
-- CÁCH DÙNG: Supabase > SQL Editor > dán toàn bộ file này > Run. Chạy lại nhiều lần vẫn an toàn.
--
-- ĐÃ THỬ: chạy trên PostgreSQL 16 thật (có giả lập schema auth và storage của Supabase), chạy 2 lần không lỗi,
--         phân quyền đúng với 3 tài khoản thử (admin, người dùng đã duyệt, người dùng chờ duyệt).
-- CHƯA THỬ: trên Supabase thật. Sau khi chạy hãy làm mục "Kiểm tra" trong .agent/workflows/06-auth-dashboard.md.
--
-- Mô hình: sách của chủ dự án (kệ chung gốc) vẫn là file tĩnh trong repo như cũ, không nằm ở đây.
-- Supabase lo: ai được vào, sách người dùng gửi lên (chờ admin duyệt, duyệt xong có thể đưa lên kệ chung), tiến độ, dấu trang.
-- Mọi bảng bật RLS: quyền do máy chủ quyết định, ẩn nút trên giao diện không phải là bảo mật.

-- ============ 1. Hồ sơ người dùng ============
-- Muốn cho ai đăng ký cũng vào luôn (không cần duyệt): đổi default 'pending' thành 'approved' ở dòng status bên dưới.
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  email        text,
  display_name text,
  role         text not null default 'reader'  check (role   in ('reader', 'admin')),
  status       text not null default 'pending' check (status in ('pending', 'approved', 'blocked')),
  created_at   timestamptz not null default now()
);
alter table public.profiles enable row level security;

-- security definer để đọc được bảng profiles bên trong policy mà không bị lặp vô hạn
create or replace function public.is_approved() returns boolean
language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.profiles where id = auth.uid() and status = 'approved');
$$;

create or replace function public.is_admin() returns boolean
language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.profiles where id = auth.uid() and role = 'admin' and status = 'approved');
$$;

-- Đăng ký xong tự có hồ sơ (lưu luôn display_name nếu có trong metadata)
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, email, display_name)
  values (new.id, new.email, new.raw_user_meta_data->>'display_name');
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Người dùng chỉ đọc hồ sơ của mình; admin đọc và sửa tất cả.
-- Cố ý KHÔNG cho người dùng tự sửa profiles, để không ai tự nâng quyền hay tự duyệt mình.
drop policy if exists profiles_select_own   on public.profiles;
drop policy if exists profiles_select_admin on public.profiles;
drop policy if exists profiles_update_admin on public.profiles;
create policy profiles_select_own   on public.profiles for select using (id = auth.uid());
create policy profiles_select_admin on public.profiles for select using (public.is_admin());
create policy profiles_update_admin on public.profiles for update using (public.is_admin()) with check (public.is_admin());

-- ============ 2. Sách người dùng gửi lên: admin duyệt, rồi có thể đưa lên kệ chung ============
-- Quy trình:  người dùng gửi sách (pending)
--             -> admin duyệt (approved) hoặc từ chối (rejected, kèm lý do)
--             -> sách đã duyệt: giao diện cho chủ sách mở đọc
--             -> admin bật "kệ chung" (shared): mọi tài khoản đã được duyệt đều đọc được (đóng góp tài nguyên)
-- PDF được chuyển thành chữ ngay trên trình duyệt; chỉ file chữ (JSON) được gửi lên, PDF không rời máy người dùng.
-- Chữ nằm ở Storage: bucket 'user-books', đường dẫn <id chủ sách>/<id sách>.json
create table if not exists public.user_books (
  id            uuid primary key default gen_random_uuid(),
  owner_id      uuid not null references auth.users(id) on delete cascade,
  title         text not null,
  author        text not null default 'Không rõ',
  chapters      integer not null default 0,
  chars         integer not null check (chars between 1 and 3000000),   -- tối đa 3 triệu ký tự mỗi sách
  size_bytes    integer not null default 0,
  status        text not null default 'pending' check (status in ('pending', 'approved', 'rejected')),
  shared        boolean not null default false,        -- true = nằm trên kệ chung
  contributor   text,                                  -- tên người đóng góp, admin điền khi đưa lên kệ chung
  reject_reason text,
  reviewed_at   timestamptz,
  created_at    timestamptz not null default now(),
  constraint shared_needs_approved check (not shared or status = 'approved')
);
alter table public.user_books enable row level security;

-- Giới hạn: tối đa 50 sách mỗi người, và tối đa 10 sách đang chờ duyệt (để khỏi dồn việc cho admin)
create or replace function public.enforce_user_book_limits() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if (select count(*) from public.user_books where owner_id = new.owner_id) >= 50 then
    raise exception 'Đã đạt giới hạn 50 sách của bạn. Hãy xóa bớt sách cũ.';
  end if;
  if (select count(*) from public.user_books where owner_id = new.owner_id and status = 'pending') >= 10 then
    raise exception 'Bạn đang có 10 sách chờ duyệt. Hãy đợi admin duyệt bớt rồi gửi tiếp.';
  end if;
  return new;
end;
$$;
drop trigger if exists user_books_limits on public.user_books;
create trigger user_books_limits before insert on public.user_books
  for each row execute function public.enforce_user_book_limits();

-- Chủ sách chỉ được sửa tên/tác giả; trạng thái duyệt, kệ chung, lý do, người đóng góp chỉ admin đổi được.
-- (Chạy từ SQL Editor thì auth.uid() rỗng nên được phép.) Đổi trạng thái thì tự ghi thời điểm duyệt.
create or replace function public.guard_user_book_update() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is not null and not public.is_admin() then
    if new.owner_id <> old.owner_id or new.status <> old.status or new.shared <> old.shared
       or new.reviewed_at is distinct from old.reviewed_at
       or new.reject_reason is distinct from old.reject_reason
       or new.contributor is distinct from old.contributor then
      raise exception 'Bạn không có quyền đổi thông tin duyệt sách.';
    end if;
    if old.shared and (new.title <> old.title or new.author <> old.author) then
      raise exception 'Sách đã lên kệ chung, hãy nhờ admin sửa tên giúp bạn.';
    end if;
  end if;
  if new.status is distinct from old.status then new.reviewed_at := now(); end if;
  return new;
end;
$$;
drop trigger if exists user_books_guard on public.user_books;
create trigger user_books_guard before update on public.user_books
  for each row execute function public.guard_user_book_update();

-- Hai hàm kiểm tra file chữ (security definer để không dính policy của bảng user_books)
create or replace function public.can_read_book_file(file_name text) returns boolean
language sql security definer set search_path = public stable as $$
  select public.is_admin() or (
    public.is_approved() and (
      split_part(file_name, '/', 1) = auth.uid()::text            -- file trong thư mục của chính mình
      or exists (
        select 1 from public.user_books b
        where b.owner_id::text = split_part(file_name, '/', 1)
          and b.id::text || '.json' = split_part(file_name, '/', 2)
          and b.status = 'approved' and b.shared)));              -- hoặc sách đã duyệt và đã lên kệ chung
$$;
create or replace function public.file_is_shared(file_name text) returns boolean
language sql security definer set search_path = public stable as $$
  select exists (select 1 from public.user_books b
    where b.owner_id::text = split_part(file_name, '/', 1)
      and b.id::text || '.json' = split_part(file_name, '/', 2) and b.shared);
$$;

-- Ai thấy dòng sách nào: chủ sách (mọi trạng thái), admin (tất cả), người đã duyệt (chỉ sách trên kệ chung)
drop policy if exists ub_select on public.user_books;
drop policy if exists ub_insert on public.user_books;
drop policy if exists ub_update on public.user_books;
drop policy if exists ub_update_admin on public.user_books;
drop policy if exists ub_delete on public.user_books;
create policy ub_select on public.user_books for select using (
  owner_id = auth.uid() or public.is_admin() or (shared and status = 'approved' and public.is_approved()));
-- Gửi sách mới: luôn ở trạng thái chờ duyệt, không tự duyệt, không tự đưa lên kệ chung
create policy ub_insert on public.user_books for insert with check (
  owner_id = auth.uid() and public.is_approved()
  and status = 'pending' and not shared and contributor is null and reject_reason is null and reviewed_at is null);
create policy ub_update on public.user_books for update
  using (owner_id = auth.uid() and public.is_approved()) with check (owner_id = auth.uid());
create policy ub_update_admin on public.user_books for update using (public.is_admin()) with check (public.is_admin());
-- Sách đã lên kệ chung thì chủ sách không tự xóa được (nhờ admin gỡ), admin xóa được tất cả
create policy ub_delete on public.user_books for delete using (
  public.is_admin() or (owner_id = auth.uid() and public.is_approved() and not shared));

insert into storage.buckets (id, name, public, file_size_limit)
  values ('user-books', 'user-books', false, 10485760)        -- riêng tư, tối đa 10 MB mỗi file
  on conflict (id) do update set public = false, file_size_limit = 10485760;

drop policy if exists ub_files_select on storage.objects;
drop policy if exists ub_files_insert on storage.objects;
drop policy if exists ub_files_update on storage.objects;
drop policy if exists ub_files_delete on storage.objects;
-- Đọc file: admin luôn đọc được. Chủ sách đọc được file trong thư mục của mình (kể cả khi đang chờ duyệt, vì chính họ
-- gửi lên; giao diện chỉ cho mở đọc khi đã duyệt). Người khác chỉ đọc được sách đã duyệt VÀ đã lên kệ chung.
create policy ub_files_select on storage.objects for select using (
  bucket_id = 'user-books' and public.can_read_book_file(name));
-- Ghi file: chỉ vào thư mục mang id của chính mình
create policy ub_files_insert on storage.objects for insert with check (
  bucket_id = 'user-books' and split_part(name, '/', 1) = auth.uid()::text and public.is_approved());
create policy ub_files_update on storage.objects for update
  using (bucket_id = 'user-books' and split_part(name, '/', 1) = auth.uid()::text and public.is_approved()
         and not public.file_is_shared(name))
  with check (bucket_id = 'user-books' and split_part(name, '/', 1) = auth.uid()::text);
create policy ub_files_delete on storage.objects for delete using (
  bucket_id = 'user-books' and (public.is_admin() or
    (split_part(name, '/', 1) = auth.uid()::text and public.is_approved() and not public.file_is_shared(name))));

-- ============ 3. Tiến độ đọc và dấu trang (của riêng từng người) ============
-- book_key: 'lib:3' là sách số 3 của thư viện chung (books.json), 'u:<id>' là sách người dùng gửi lên (kể cả sách đã lên kệ chung)
create table if not exists public.reading_progress (
  user_id    uuid not null references auth.users(id) on delete cascade,
  book_key   text not null check (book_key ~ '^(lib:[0-9]+|u:[0-9a-f-]{36})$'),
  chapter    integer not null default 1,
  position   real not null default 0,                -- vị trí cuộn trong chương, 0 đến 1
  updated_at timestamptz not null default now(),
  primary key (user_id, book_key)
);
alter table public.reading_progress enable row level security;
drop policy if exists progress_own          on public.reading_progress;
drop policy if exists progress_select_admin on public.reading_progress;
create policy progress_own on public.reading_progress for all
  using (user_id = auth.uid() and public.is_approved())
  with check (user_id = auth.uid() and public.is_approved());
-- Admin chỉ ĐỌC (để làm thống kê "sách đọc nhiều"), không sửa được
create policy progress_select_admin on public.reading_progress for select using (public.is_admin());

create table if not exists public.bookmarks (
  id         bigint generated always as identity primary key,
  user_id    uuid not null references auth.users(id) on delete cascade,
  book_key   text not null check (book_key ~ '^(lib:[0-9]+|u:[0-9a-f-]{36})$'),
  chapter    integer not null,
  note       text,
  created_at timestamptz not null default now()
);
alter table public.bookmarks enable row level security;
drop policy if exists bookmarks_own on public.bookmarks;
create policy bookmarks_own on public.bookmarks for all
  using (user_id = auth.uid() and public.is_approved())
  with check (user_id = auth.uid() and public.is_approved());

-- ============ 4. Tạo admin đầu tiên (làm tay, một lần) ============
-- Đăng ký tài khoản của anh trên web trước, rồi chạy dòng dưới (đổi email):
--   update public.profiles set role = 'admin', status = 'approved' where email = 'email-cua-anh@example.com';
