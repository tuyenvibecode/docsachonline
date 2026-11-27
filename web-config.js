// Mục đích: Cấu hình kết nối Supabase (URL dự án và anon key công khai) cho Bước 4.
// Khi chưa điền SUPABASE_URL và SUPABASE_ANON_KEY, web vẫn cho đọc thư viện chung bình thường và cho dùng thử mục "Sách của bạn" ngay trên trình duyệt (lưu cục bộ).
window.__WEB_CONFIG__ = {
  SUPABASE_URL: "",
  SUPABASE_ANON_KEY: "",
  // Đặt REQUIRE_AUTH = true nếu muốn bắt buộc đăng nhập và được admin duyệt mới thấy kệ sách chung
  REQUIRE_AUTH: false
};
