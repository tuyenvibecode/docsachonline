-- Cấu trúc Supabase cho web đọc sách: tài khoản (theo tên đăng nhập username), sách do người dùng tự tải lên, tiến độ đọc, dấu trang, góp ý & phản hồi.
-- CÁCH DÙNG: Supabase > SQL Editor > dán toàn bộ file này > Run. Chạy lại nhiều lần vẫn an toàn.
--
-- Mô hình: sách của chủ dự án (kệ chung gốc) vẫn là file tĩnh trong repo như cũ, không nằm ở đây.
-- Supabase lo: ai được vào, sách người dùng gửi lên (chờ admin duyệt, duyệt xong có thể đưa lên kệ chung), tiến độ, dấu trang, góp ý.
-- Mọi bảng bật RLS: quyền do máy chủ quyết định, ẩn nút trên giao diện không phải là bảo mật.

create extension if not exists pgcrypto with schema extensions;

-- ============ 1. Hồ sơ người dùng (Đăng nhập bằng Tên tài khoản) ============
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  username     text,
  email        text,
  display_name text,
  role         text not null default 'reader'  check (role   in ('reader', 'admin')),
  status       text not null default 'pending' check (status in ('pending', 'approved', 'blocked')),
  created_at   timestamptz not null default now()
);
alter table public.profiles add column if not exists username text;
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

-- Đăng ký xong tự có hồ sơ (lưu username, họ tên display_name; tự xác nhận tài khoản nội bộ không cần xác thực email)
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public, auth as $$
declare
  v_uname text;
  v_dname text;
begin
  v_uname := lower(coalesce(nullif(trim(new.raw_user_meta_data->>'username'), ''), split_part(new.email, '@', 1)));
  v_dname := coalesce(nullif(trim(new.raw_user_meta_data->>'display_name'), ''), v_uname);

  -- Tự động đánh dấu đã xác nhận để người dùng chỉ dùng Tên tài khoản, không bị chặn bởi "Email not confirmed"
  if new.email_confirmed_at is null then
    update auth.users set email_confirmed_at = now() where id = new.id and email_confirmed_at is null;
  end if;

  insert into public.profiles (id, username, email, display_name, role, status)
  values (
    new.id,
    v_uname,
    new.email,
    v_dname,
    case when v_uname = 'admin' then 'admin' else 'reader' end,
    case when v_uname = 'admin' then 'approved' else 'pending' end
  )
  on conflict (id) do update set
    username     = excluded.username,
    display_name = coalesce(nullif(public.profiles.display_name, ''), excluded.display_name);
  return new;
end;
$$;
drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Hàm RPC đăng ký thuần bằng Tên tài khoản + Mật khẩu (không gửi email xác thực, luôn tạo ở trạng thái reader + pending)
create or replace function public.register_account(
  p_username text,
  p_password text,
  p_display_name text default null
) returns uuid
language plpgsql security definer set search_path = public, auth, extensions as $$
declare
  v_uname   text := lower(trim(coalesce(p_username, '')));
  v_dname   text := coalesce(nullif(trim(p_display_name), ''), v_uname);
  v_email   text;
  v_user_id uuid;
begin
  if v_uname !~ '^[a-z0-9._-]{3,32}$' then
    raise exception 'Tên tài khoản phải dài 3–32 ký tự, chỉ gồm chữ không dấu, số và dấu . _ -';
  end if;
  if length(coalesce(p_password, '')) < 6 then
    raise exception 'Mật khẩu quá ngắn.';
  end if;

  v_email := v_uname || '@tusach3d.vn';

  if exists (
    select 1 from public.profiles where lower(username) = v_uname
  ) or exists (
    select 1 from auth.users where lower(email) in (v_email, v_uname || '@tusach.local')
  ) then
    raise exception 'Tên tài khoản này đã có người đăng ký.';
  end if;

  v_user_id := gen_random_uuid();

  insert into auth.users (
    instance_id, id, aud, role, email, encrypted_password,
    email_confirmed_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
    confirmation_token, email_change, email_change_token_new, recovery_token
  ) values (
    '00000000-0000-0000-0000-000000000000',
    v_user_id,
    'authenticated',
    'authenticated',
    v_email,
    extensions.crypt(p_password, extensions.gen_salt('bf')),
    now(),
    '{"provider":"email","providers":["email"]}'::jsonb,
    jsonb_build_object('username', v_uname, 'display_name', v_dname),
    now(),
    now(),
    '', '', '', ''
  );

  insert into auth.identities (
    id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at
  ) values (
    gen_random_uuid(),
    v_user_id,
    v_user_id::text,
    jsonb_build_object('sub', v_user_id::text, 'email', v_email, 'email_verified', true),
    'email',
    now(),
    now(),
    now()
  );

  return v_user_id;
end;
$$;

-- Người dùng đọc hồ sơ của mình và có thể cập nhật Họ tên (display_name) của mình; admin đọc và sửa tất cả.
drop policy if exists profiles_select_own   on public.profiles;
drop policy if exists profiles_select_admin on public.profiles;
drop policy if exists profiles_update_admin on public.profiles;
create policy profiles_select_own   on public.profiles for select using (id = auth.uid());
create policy profiles_select_admin on public.profiles for select using (public.is_admin());
create policy profiles_update_admin on public.profiles for update using (public.is_admin()) with check (public.is_admin());

-- Hàm RPC để Admin reset mật khẩu của bất kỳ User nào về mặc định (123456aA@) ngay trên Dashboard
create or replace function public.admin_reset_user_password(target_user_id uuid, new_pass text default '123456aA@')
returns void
language plpgsql security definer set search_path = public, auth, extensions as $$
begin
  if not public.is_admin() then
    raise exception 'Chỉ Quản trị viên (Admin) mới có quyền reset mật khẩu.';
  end if;

  update auth.users
  set encrypted_password = extensions.crypt(new_pass, extensions.gen_salt('bf')),
      email_confirmed_at = coalesce(email_confirmed_at, now()),
      updated_at = now()
  where id = target_user_id;
end;
$$;

-- ============ 2. Sách người dùng gửi lên: admin duyệt, rồi có thể đưa lên kệ chung ============
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

drop policy if exists ub_select on public.user_books;
drop policy if exists ub_insert on public.user_books;
drop policy if exists ub_update on public.user_books;
drop policy if exists ub_update_admin on public.user_books;
drop policy if exists ub_delete on public.user_books;
create policy ub_select on public.user_books for select using (
  owner_id = auth.uid() or public.is_admin() or (shared and status = 'approved' and public.is_approved()));
create policy ub_insert on public.user_books for insert with check (
  owner_id = auth.uid() and public.is_approved()
  and status = 'pending' and not shared and contributor is null and reject_reason is null and reviewed_at is null);
create policy ub_update on public.user_books for update
  using (owner_id = auth.uid() and public.is_approved()) with check (owner_id = auth.uid());
create policy ub_update_admin on public.user_books for update using (public.is_admin()) with check (public.is_admin());
create policy ub_delete on public.user_books for delete using (
  public.is_admin() or (owner_id = auth.uid() and public.is_approved() and not shared));

insert into storage.buckets (id, name, public, file_size_limit)
  values ('user-books', 'user-books', false, 10485760)        -- riêng tư, tối đa 10 MB mỗi file
  on conflict (id) do update set public = false, file_size_limit = 10485760;

drop policy if exists ub_files_select on storage.objects;
drop policy if exists ub_files_insert on storage.objects;
drop policy if exists ub_files_update on storage.objects;
drop policy if exists ub_files_delete on storage.objects;
create policy ub_files_select on storage.objects for select using (
  bucket_id = 'user-books' and public.can_read_book_file(name));
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
create table if not exists public.reading_progress (
  user_id    uuid not null references auth.users(id) on delete cascade,
  book_key   text not null check (book_key ~ '^(lib:[0-9]+|u:[0-9a-f-]{36})$'),
  chapter    integer not null default 1,
  position   real not null default 0,
  updated_at timestamptz not null default now(),
  primary key (user_id, book_key)
);
alter table public.reading_progress enable row level security;
drop policy if exists progress_own          on public.reading_progress;
drop policy if exists progress_select_admin on public.reading_progress;
create policy progress_own on public.reading_progress for all
  using (user_id = auth.uid() and public.is_approved())
  with check (user_id = auth.uid() and public.is_approved());
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

-- ============ 4. Hộp thư Góp ý & Phản hồi từ Admin (user_feedbacks) ============
create table if not exists public.user_feedbacks (
  id           uuid primary key default gen_random_uuid(),
  user_id      uuid not null references auth.users(id) on delete cascade,
  username     text not null,
  display_name text,
  subject      text not null,
  message      text not null,
  admin_reply  text,
  status       text not null default 'pending' check (status in ('pending', 'replied')),
  replied_at   timestamptz,
  created_at   timestamptz not null default now()
);
alter table public.user_feedbacks enable row level security;

drop policy if exists fb_select_own   on public.user_feedbacks;
drop policy if exists fb_insert_own   on public.user_feedbacks;
drop policy if exists fb_select_admin on public.user_feedbacks;
drop policy if exists fb_update_admin on public.user_feedbacks;
drop policy if exists fb_delete_admin on public.user_feedbacks;

create policy fb_select_own   on public.user_feedbacks for select using (user_id = auth.uid());
create policy fb_insert_own   on public.user_feedbacks for insert with check (user_id = auth.uid() and public.is_approved());
create policy fb_select_admin on public.user_feedbacks for select using (public.is_admin());
create policy fb_update_admin on public.user_feedbacks for update using (public.is_admin()) with check (public.is_admin());
create policy fb_delete_admin on public.user_feedbacks for delete using (public.is_admin());

-- ============ 4B. Thống kê lượt truy cập & tổng thời gian đọc toàn trang ============
create table if not exists public.site_metrics (
  id                 integer primary key default 1 check (id = 1),
  total_visits       bigint not null default 0,
  total_read_seconds bigint not null default 0,
  updated_at         timestamptz not null default now()
);
insert into public.site_metrics (id, total_visits, total_read_seconds)
values (1, 1, 0)
on conflict (id) do nothing;

alter table public.site_metrics enable row level security;
drop policy if exists site_metrics_select_admin on public.site_metrics;
create policy site_metrics_select_admin on public.site_metrics for select using (public.is_admin());

create or replace function public.record_site_activity(p_visit integer default 0, p_read_seconds integer default 0)
returns void
language plpgsql security definer set search_path = public as $$
declare
  v_vis integer := greatest(0, least(coalesce(p_visit, 0), 1));
  v_sec integer := greatest(0, least(coalesce(p_read_seconds, 0), 300));
begin
  update public.site_metrics
  set total_visits       = total_visits + v_vis,
      total_read_seconds = total_read_seconds + v_sec,
      updated_at         = now()
  where id = 1;
end;
$$;

-- ============ 5. Khởi tạo sẵn tài khoản Admin mặc định (TK: admin / MK: admin) ============
-- Lưu ý: Supabase bắt mật khẩu tối thiểu 6 ký tự, nên web tự đệm hậu tố '#TS3D!' cho mật khẩu ngắn hơn 6 ký tự.
-- Vì vậy mật khẩu 'admin' gõ trên web sẽ được gửi lên là 'admin#TS3D!' — dòng dưới lưu đúng giá trị đó.
do $$
declare
  v_admin_id uuid;
begin
  select id into v_admin_id from auth.users where email = 'admin@tusach.local' limit 1;
  if v_admin_id is null then
    v_admin_id := gen_random_uuid();
    insert into auth.users (
      instance_id, id, aud, role, email, encrypted_password,
      email_confirmed_at, raw_app_meta_data, raw_user_meta_data, created_at, updated_at,
      confirmation_token, email_change, email_change_token_new, recovery_token
    ) values (
      '00000000-0000-0000-0000-000000000000',
      v_admin_id,
      'authenticated',
      'authenticated',
      'admin@tusach.local',
      extensions.crypt('admin#TS3D!', extensions.gen_salt('bf')),
      now(),
      '{"provider":"email","providers":["email"]}'::jsonb,
      '{"username":"admin","display_name":"Quản trị viên"}'::jsonb,
      now(),
      now(),
      '', '', '', ''
    );

    insert into auth.identities (
      id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at
    ) values (
      gen_random_uuid(),
      v_admin_id,
      v_admin_id::text,
      jsonb_build_object('sub', v_admin_id::text, 'email', 'admin@tusach.local', 'email_verified', true),
      'email',
      now(),
      now(),
      now()
    );
  else
    update auth.users
    set encrypted_password = extensions.crypt('admin#TS3D!', extensions.gen_salt('bf')),
        email_confirmed_at = coalesce(email_confirmed_at, now()),
        updated_at = now()
    where id = v_admin_id;
  end if;

  insert into public.profiles (id, username, email, display_name, role, status)
  values (v_admin_id, 'admin', 'admin@tusach.local', 'Quản trị viên', 'admin', 'approved')
  on conflict (id) do update
  set username = 'admin', display_name = 'Quản trị viên', role = 'admin', status = 'approved';
end $$;

-- ============ 6. Cấp quyền cho web (dự án Supabase mới không tự cấp) ============
grant usage on schema public to anon, authenticated;

grant select, insert, update, delete on
  public.profiles,
  public.user_books,
  public.reading_progress,
  public.bookmarks,
  public.user_feedbacks,
  public.site_metrics
to authenticated;

grant usage, select on all sequences in schema public to authenticated;

grant execute on function public.is_approved()                          to anon, authenticated;
grant execute on function public.is_admin()                             to anon, authenticated;
grant execute on function public.can_read_book_file(text)               to anon, authenticated;
grant execute on function public.file_is_shared(text)                   to anon, authenticated;
grant execute on function public.register_account(text, text, text)     to anon, authenticated;
grant execute on function public.record_site_activity(integer, integer) to anon, authenticated;
grant execute on function public.admin_reset_user_password(uuid, text)  to authenticated;

-- Báo cho Data API nạp lại cấu hình
notify pgrst, 'reload schema';

