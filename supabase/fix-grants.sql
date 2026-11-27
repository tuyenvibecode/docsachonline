-- SỬA LỖI "permission denied for table ...": cấp quyền cho web (vai trò anon / authenticated) dùng các bảng.
-- Quyền xem/sửa từng dòng vẫn do RLS (policy) trong schema.sql quyết định, nên cấp quyền ở đây vẫn an toàn.
-- CÁCH DÙNG: Supabase > SQL Editor > dán file này > Run. Chạy lại nhiều lần vẫn an toàn.

grant usage on schema public to anon, authenticated;

grant select, insert, update, delete on
  public.profiles,
  public.user_books,
  public.reading_progress,
  public.bookmarks,
  public.user_feedbacks
to authenticated;

grant usage, select on all sequences in schema public to authenticated;

grant execute on function public.is_approved()                          to anon, authenticated;
grant execute on function public.is_admin()                             to anon, authenticated;
grant execute on function public.can_read_book_file(text)               to anon, authenticated;
grant execute on function public.file_is_shared(text)                   to anon, authenticated;
grant execute on function public.admin_reset_user_password(uuid, text)  to authenticated;

-- Báo cho Data API nạp lại cấu hình
notify pgrst, 'reload schema';
