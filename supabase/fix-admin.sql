-- SỬA NHANH: biến tài khoản "admin" thành Quản trị viên (đã duyệt).
-- Dùng khi đăng nhập admin/admin mà web báo "Tài khoản đang chờ Admin phê duyệt".
-- CÁCH DÙNG: chạy supabase/schema.sql TRƯỚC (một lần), rồi dán file này vào SQL Editor > Run.

insert into public.profiles (id, username, email, display_name, role, status)
select id, 'admin', email, 'Quản trị viên', 'admin', 'approved'
from auth.users
where email = 'admin@tusach.local'
on conflict (id) do update
set username = 'admin', role = 'admin', status = 'approved';

-- Kiểm tra: dòng kết quả phải có role = admin, status = approved
select id, username, email, role, status from public.profiles where email = 'admin@tusach.local';
