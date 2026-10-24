# Quyết định, giả định và điểm Rick cần chọn

Cập nhật lần cuối: 2026-10-22 (bản soạn ban đầu). Claude Code bổ sung khi có phát hiện mới. Nhãn: **MẶC ĐỊNH** = cứ làm theo, Rick đổi được; **CẦN RICK** = chỉ Rick quyết được.

## 1. Các điểm Rick cần chọn (đã có mặc định để không phải chờ)

| # | Câu hỏi | Mặc định đang dùng | Lý do | Trạng thái |
|---|---|---|---|---|
| 1 | Kênh nhận tin | Telegram (cảnh báo tức thời + bản tin) | Cài nhanh, miễn phí, nhận trên điện thoại | MẶC ĐỊNH, CẦN RICK xác nhận quy định nội bộ (mục 2) |
| 2 | Có thêm Email không | Không ở bản đầu; thiết kế sẵn nhánh Gmail/SMTP | Giảm độ phức tạp | MẶC ĐỊNH |
| 3 | Danh sách mã theo dõi | `config/watchlist.example.json` (mã ví dụ) | Chưa có danh sách thật của Rick | **CẦN RICK** cung cấp mã, alias, mức ưu tiên A/B |
| 4 | Chủ đề vĩ mô theo dõi | Danh sách ví dụ trong watchlist | Thường dùng trong công việc tư vấn | MẶC ĐỊNH, Rick chỉnh |
| 5 | Nguồn tin | 16 feed báo chí (CafeF, Vietstock) trong `sources.json`; nguồn chính thức chờ khảo sát | Có tên trên trang RSS chính thức của nhà xuất bản | MẶC ĐỊNH; nguồn chính thức **CẦN RICK** xem kết quả giai đoạn 1 |
| 6 | Nơi chạy n8n | Thử bằng Docker/`npx` bản 2.45.x; chạy thật: chọn giữa n8n Cloud, máy chủ riêng (VPS), máy tính cá nhân | Lịch chỉ chạy khi máy bật liên tục; máy cá nhân ngủ là lỡ lịch | **CẦN RICK** chọn trước giai đoạn 7 |
| 7 | Nhà cung cấp AI | Anthropic (Chat Model có sẵn trong n8n), mô hình nhỏ cho phân loại | Đã có node; chi phí thấp cho tác vụ phân loại | **CẦN RICK**: cần khóa API riêng; gói đăng ký chat không đương nhiên gồm API |
| 8 | Ngân sách AI thử nghiệm | 5 USD cho toàn bộ giai đoạn 4 (GIẢ ĐỊNH) | Đủ chạy bộ mẫu vài lần | **CẦN RICK** xác nhận hoặc đổi |
| 9 | Trần chi phí hằng ngày khi chạy thật | `MAX_AI_ITEMS_PER_DAY = 200` (GIẢ ĐỊNH) | Chặn chi phí chạy ngoài ý muốn | MẶC ĐỊNH, đo lại ở giai đoạn 4 |
| 10 | Lịch chạy | Collector thứ 2–6, mỗi 30 phút 08:00–16:00; Digest 08:15 và 15:30; heartbeat thứ 2 07:55 (giờ Việt Nam) | Bám phiên giao dịch | GIẢ ĐỊNH, đối chiếu giờ giao dịch hiện hành của HOSE/HNX trước khi chốt |
| 11 | Lưu trữ | Data Table của n8n; xuất Google Sheets là tùy chọn | Có sẵn trong n8n, không cần thêm tài khoản | MẶC ĐỊNH |
| 12 | Thời gian giữ dữ liệu | 180 ngày | Đủ tra cứu theo quý | MẶC ĐỊNH |
| 13 | Chế độ thử | `DRY_RUN = true` cho tới khi nghiệm thu | Tránh gửi nhầm | MẶC ĐỊNH |

## 2. Rủi ro tuân thủ cần Rick tự xác nhận

- Quy định của Vietcap về việc đưa nội dung công việc qua Telegram, dịch vụ AI bên ngoài và máy chủ n8n ngoài hệ thống công ty. Chưa có thông tin; **không giả định là được phép**.
- Bản quyền nội dung báo: hệ thống chỉ lưu tiêu đề, URL, đoạn trích ≤ 500 ký tự. Nếu cần lưu nhiều hơn, xem điều khoản từng nguồn.
- Bản tin là công cụ nghiên cứu nội bộ, không gửi khách hàng, không phải khuyến nghị đầu tư.

## 3. Giả định kỹ thuật chưa xác minh

| Giả định | Cách xác minh | Giai đoạn |
|---|---|---|
| Các URL RSS trong `sources.json` trả XML hợp lệ | Tải thử từng URL, lưu mẫu | 1 |
| `pubDate` của từng nguồn có múi giờ rõ ràng | Đọc mẫu, thử chuẩn hóa | 1 |
| Có cách lấy công bố thông tin chính thức hợp lệ (HOSE/HNX/UBCKNN) | Khảo sát, đọc điều khoản và `robots.txt` | 1 |
| Remove Duplicates (lịch sử qua các lần chạy) hoạt động đúng với lịch tự động | Kiểm thử 3 chu kỳ lịch thật, sau khi khởi động lại | 6 |
| Biểu thức cron của Schedule Trigger đúng cú pháp theo phiên bản này | Đọc `ScheduleTrigger.node.ts`, xem "thời điểm chạy kế tiếp" hiển thị trong giao diện | 3 |
| Giờ giao dịch dùng để đặt lịch | Tra trang của HOSE/HNX | 2 |

## 4. Nhật ký quyết định

| Ngày | Quyết định | Người quyết | Lý do |
|---|---|---|---|
| 2026-10-22 | Đặt dự án trong `automation/vn-news-monitor/` thay vì sửa gốc repo | Claude (đề xuất), chờ Rick | Giữ nguyên `AGENTS.md`/`CLAUDE.md` của monorepo n8n; thư mục con có `CLAUDE.md` riêng |
| 2026-10-22 | Ba workflow tách riêng (collector, digest, error handler) | Claude (đề xuất) | Dễ kiểm thử và bật/tắt độc lập |
