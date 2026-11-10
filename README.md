# Cẩm nang nhà ở xã hội 2026

Trang tham khảo do HS Holding tổng hợp: ai được mua nhà ở xã hội, điều kiện thu nhập và nhà ở, hồ sơ từng nhóm,
biểu mẫu, quy trình xét duyệt, vay ưu đãi, bán lại; kèm một tab riêng cho dự án Khu nhà ở xã hội HUD Thủ Đức
(TP.HCM) theo công bố của chủ đầu tư HUD.

Trang web: https://hsholding.github.io/nha-o-xa-hoi/

Đây không phải trang của cơ quan nhà nước và không phải trang của chủ đầu tư nào.

## Cấu trúc

| Đường dẫn | Nội dung |
|---|---|
| `content/*.md` | Nội dung từng tab, viết bằng Markdown |
| `template.html` | Khung trang, kiểu chữ, màu, phần chuyển tab |
| `build.py` | Dựng `index.html` từ `content/` và `template.html` |
| `assets/bieu-mau/` | Biểu mẫu PDF dùng chung cả nước |
| `assets/img/` | Hình ảnh |
| `index.html` | Trang đã dựng (GitHub Pages phục vụ file này) |

## Cập nhật nội dung

1. Sửa file trong `content/`.
2. Chạy `python3 build.py` (không cần cài thêm thư viện).
3. Commit và push; GitHub Pages tự cập nhật sau khoảng một phút.

Thêm một dự án mới: tạo file `content/<so>-<ten-du-an>.md` và thêm một dòng vào danh sách `TABS` trong `build.py`.
