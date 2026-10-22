# Quyết định, giả định và điểm Rick cần chọn

Cập nhật lần cuối: 2026-10-22 (bổ sung sau giai đoạn 1). Claude Code bổ sung khi có phát hiện mới. Nhãn: **MẶC ĐỊNH** = cứ làm theo, Rick đổi được; **CẦN RICK** = chỉ Rick quyết được.

## 1. Các điểm Rick cần chọn (đã có mặc định để không phải chờ)

| # | Câu hỏi | Mặc định đang dùng | Lý do | Trạng thái |
|---|---|---|---|---|
| 1 | Kênh nhận tin | Telegram (cảnh báo tức thời + bản tin) | Cài nhanh, miễn phí, nhận trên điện thoại | MẶC ĐỊNH, CẦN RICK xác nhận quy định nội bộ (mục 2) |
| 2 | Có thêm Email không | Không ở bản đầu; thiết kế sẵn nhánh Gmail/SMTP | Giảm độ phức tạp | MẶC ĐỊNH |
| 3 | Danh sách mã theo dõi | `config/watchlist.example.json` (mã ví dụ) | Chưa có danh sách thật của Rick | **CẦN RICK** cung cấp mã, alias, mức ưu tiên A/B |
| 4 | Chủ đề vĩ mô theo dõi | Danh sách ví dụ trong watchlist | Thường dùng trong công việc tư vấn | MẶC ĐỊNH, Rick chỉnh |
| 5 | Nguồn tin | 15 feed báo chí bật (CafeF, Vietstock, gồm `vietstock-en-stocks` theo lựa chọn của Rick); `vietstock-en-earnings` bỏ; Google News bỏ; nguồn chính thức: dùng feed Vietstock làm tín hiệu, Rick đối chiếu HOSE/HNX | Đã tải thử cả 16 feed ngày 2026-10-22 (`evidence/p1-nguon/source-audit.md`) | MẶC ĐỊNH; Rick chọn bật tin tiếng Anh (2026-10-22). Kênh chính thức: SSI MCP (xem `source-audit.md` mục 6) |
| 6 | Nơi chạy n8n | Thử bằng Docker/`npx` bản 2.45.x; chạy thật: chọn giữa n8n Cloud, máy chủ riêng (VPS), máy tính cá nhân | Lịch chỉ chạy khi máy bật liên tục; máy cá nhân ngủ là lỡ lịch | **CẦN RICK** chọn trước giai đoạn 7 |
| 7 | Nhà cung cấp AI | Anthropic (Chat Model có sẵn trong n8n), mô hình nhỏ cho phân loại | Đã có node; chi phí thấp cho tác vụ phân loại | **CẦN RICK**: cần khóa API riêng; gói đăng ký chat không đương nhiên gồm API |
| 8 | Ngân sách AI thử nghiệm | 5 USD cho toàn bộ giai đoạn 4 (GIẢ ĐỊNH) | Đủ chạy bộ mẫu vài lần | **CẦN RICK** xác nhận hoặc đổi |
| 9 | Trần chi phí hằng ngày khi chạy thật | `MAX_AI_ITEMS_PER_DAY = 200` (GIẢ ĐỊNH) | Chặn chi phí chạy ngoài ý muốn | MẶC ĐỊNH, đo lại ở giai đoạn 4 |
| 10 | Lịch chạy | Collector thứ 2–6, mỗi 30 phút 08:00–16:00; Digest 08:15 và 15:30; heartbeat thứ 2 07:55 (giờ Việt Nam) | Bám phiên giao dịch | GIẢ ĐỊNH, đối chiếu giờ giao dịch hiện hành của HOSE/HNX trước khi chốt |
| 11 | Lưu trữ | Data Table của n8n; xuất Google Sheets là tùy chọn | Có sẵn trong n8n, không cần thêm tài khoản | MẶC ĐỊNH |
| 12 | Thời gian giữ dữ liệu | 180 ngày | Đủ tra cứu theo quý | MẶC ĐỊNH |
| 13 | Chế độ thử | `DRY_RUN = true` cho tới khi nghiệm thu | Tránh gửi nhầm | MẶC ĐỊNH |
| 14 | Phiên bản n8n khi chạy thật | Thử bằng 2.45.0 cho khớp mã repo; chạy thật dùng bản `stable` mới nhất tại thời điểm cài | Ngày 2026-10-22, npm ghi 2.45.x là `beta`, `stable` là 2.44.5 (`evidence/p0-moi-truong/env-report.md`) | MẶC ĐỊNH; kiểm lại tham số node nếu chênh phiên bản |
| 15 | Mạng của phiên Claude Code | Môi trường mới (2026-10-22 07:50 UTC) đã mở CafeF, Vietstock, Telegram, `www.hsx.vn`, UBCKNN, Google News; HNX vẫn lỗi | `evidence/p1-nguon/egress-retest.log` | MẶC ĐỊNH; HNX: **CẦN RICK** thêm `hnx.vn`, `www.hnx.vn` vào danh sách tên miền nếu muốn thử lại |
| 16 | Repo công khai | Chỉ commit tài liệu, workflow, dữ liệu mẫu, bằng chứng đã loại bí mật; watchlist thật không commit | `lilrick23/n8n` là fork công khai: ai cũng đọc được | MẶC ĐỊNH; **CẦN RICK** cân nhắc chuyển sang repo riêng tư |

## 2. Rủi ro tuân thủ cần Rick tự xác nhận

- Quy định của Vietcap về việc đưa nội dung công việc qua Telegram, dịch vụ AI bên ngoài và máy chủ n8n ngoài hệ thống công ty. Chưa có thông tin; **không giả định là được phép**.
- Bản quyền nội dung báo: hệ thống chỉ lưu tiêu đề, URL, đoạn trích ≤ 500 ký tự. Nếu cần lưu nhiều hơn, xem điều khoản từng nguồn.
- Bản tin là công cụ nghiên cứu nội bộ, không gửi khách hàng, không phải khuyến nghị đầu tư.
- Repo `lilrick23/n8n` là **công khai**. Tài liệu hiện có đã nêu tên Rick và nơi làm việc. Danh sách mã theo dõi thật, nhận định riêng, cấu hình kênh nhận tin không được commit vào đây. Nếu muốn giữ kín cả tài liệu, chuyển thư mục này sang một repo riêng tư.

## 3. Giả định kỹ thuật chưa xác minh

| Giả định | Cách xác minh | Giai đoạn |
|---|---|---|
| ~~Các URL RSS trong `sources.json` trả XML hợp lệ~~ ĐÃ KIỂM CHỨNG 2026-10-22 (16/16) | `evidence/p1-nguon/INDEX.md` | 1 |
| ~~`pubDate` của từng nguồn có múi giờ rõ ràng~~ ĐÃ KIỂM CHỨNG: tất cả `+0700`; n8n quy đổi đúng | `evidence/p1-nguon/n8n-live/n8n-rss-live.log` | 1 |
| Có cách lấy công bố thông tin chính thức hợp lệ (HOSE/HNX/UBCKNN): chưa tìm thấy RSS/API công khai; HNX chưa truy cập được | Rick kiểm tra theo `evidence/p1-nguon/INDEX.md` mục hướng dẫn | 1 → mở |
| Nếu dùng HTTP Request thay RSS Read, CafeF cần header User-Agent rõ ràng (chặn `curl/...`) | Đã thấy ở `evidence/p1-nguon/user-agent-test.log`; kiểm lại với UA mặc định của HTTP Request | 2 |
| n8n ngừng chạy quá ~20 giờ sẽ mất tin ở feed nhanh nhất (20 mục phủ ~20 giờ) | Đo lại tần suất sau vài ngày chạy thật | 2, 8 |
| Remove Duplicates (lịch sử qua các lần chạy) hoạt động đúng với lịch tự động | Kiểm thử 3 chu kỳ lịch thật, sau khi khởi động lại | 6 |
| Biểu thức cron của Schedule Trigger đúng cú pháp theo phiên bản này | Đọc `ScheduleTrigger.node.ts`, xem "thời điểm chạy kế tiếp" hiển thị trong giao diện | 3 |
| Giờ giao dịch dùng để đặt lịch | Tra trang của HOSE/HNX | 2 |
| Cú pháp cron `*/30 8-16 * * 1-5` cho lịch collector | Kích hoạt workflow, xem thời điểm chạy kế tiếp | 3 |
| Remove Duplicates giữ lịch sử giống nhau khi chạy tay và chạy theo lịch | Kiểm thử ở giai đoạn 3 (tay) và 6 (lịch) | 3, 6 |
| RSS Read không có timeout: một nguồn treo có thể làm chậm cả lần chạy | Chọn RSS Read hay HTTP Request + phân tích XML ở giai đoạn 2 | 2 |

## 4. Nhật ký quyết định

| Ngày | Quyết định | Người quyết | Lý do |
|---|---|---|---|
| 2026-10-22 | Đặt dự án trong `automation/vn-news-monitor/` thay vì sửa gốc repo | Claude (đề xuất), chờ Rick | Giữ nguyên `AGENTS.md`/`CLAUDE.md` của monorepo n8n; thư mục con có `CLAUDE.md` riêng |
| 2026-10-22 | Ba workflow tách riêng (collector, digest, error handler) | Claude (đề xuất) | Dễ kiểm thử và bật/tắt độc lập |
| 2026-10-22 | Môi trường thử: Docker, image `mirror.gcr.io/n8nio/n8n:2.45.0` | Claude | Docker Hub trả 429; `npx n8n` cần Node ≥ 24, máy có Node 22 |
| 2026-10-22 | Kiểm thử chuỗi thu thập bằng fixture tự dựng, gắn nhãn dữ liệu giả | Claude | Không tải được RSS thật (giai đoạn 0) |
| 2026-10-22 | Telegram node luôn đặt `parse_mode = HTML` và `appendAttribution = false` | Claude | Mặc định của node là Markdown và tự chèn dòng quảng cáo n8n |
| 2026-10-22 | Không thu thập từ API nội bộ của trang HOSE/HNX/UBCKNN; dùng feed Vietstock làm tín hiệu, gắn `reported_fact` | Claude | Không có RSS/API công khai; CLAUDE.md cấm trình thu thập lách luật |
| 2026-10-22 | Bỏ Google News RSS | Claude | robots.txt chặn `/rss` |
| 2026-10-22 | Không commit file RSS đầy đủ; chỉ mẫu 10 mục trong `fixtures/rss/` | Claude | Repo công khai; nội dung thuộc nhà xuất bản |
| 2026-10-22 | Bật `vietstock-en-stocks` | Rick | Trả lời trong luồng |
| 2026-10-22 | SSI MCP là nguồn ưu tiên cho nhóm "Công bố chính thức", gọi bằng node MCP Client; chỉ dùng cho bản tin tổng hợp cho tới khi đo được độ trễ | Claude (đề xuất) | Trả tin HOSE/HNX kèm link gốc; quan sát trễ ~21 giờ |
| 2026-10-22 | Không dùng Vnstock | Claude (đề xuất), chờ Rick | Giấy phép cấm tổ chức dùng thương mại khi chưa có văn bản đồng ý |
| 2026-10-22 | Không tự gọi API nội bộ của Vietcap AI News | Claude | Cần API/export chính thức |
