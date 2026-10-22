# Quyết định, giả định và điểm Rick cần chọn

Cập nhật lần cuối: 2026-10-22 (bổ sung sau giai đoạn 3). Claude Code bổ sung khi có phát hiện mới. Nhãn: **MẶC ĐỊNH** = cứ làm theo, Rick đổi được; **CẦN RICK** = chỉ Rick quyết được.

## 1. Các điểm Rick cần chọn (đã có mặc định để không phải chờ)

| # | Câu hỏi | Mặc định đang dùng | Lý do | Trạng thái |
|---|---|---|---|---|
| 1 | Kênh nhận tin | Telegram (cảnh báo tức thời + bản tin) | Cài nhanh, miễn phí, nhận trên điện thoại | MẶC ĐỊNH, CẦN RICK xác nhận quy định nội bộ (mục 2) |
| 2 | Có thêm Email không | Không ở bản đầu; thiết kế sẵn nhánh Gmail/SMTP | Giảm độ phức tạp | MẶC ĐỊNH |
| 3 | Danh sách mã theo dõi | `config/watchlist.example.json` (mã ví dụ) | Chưa có danh sách thật của Rick | **CẦN RICK** cung cấp mã, alias, mức ưu tiên A/B |
| 4 | Chủ đề vĩ mô theo dõi | Danh sách ví dụ trong watchlist | Thường dùng trong công việc tư vấn | MẶC ĐỊNH, Rick chỉnh |
| 5 | Nguồn tin | 15 feed báo chí bật (CafeF, Vietstock, gồm `vietstock-en-stocks` theo lựa chọn của Rick); `vietstock-en-earnings` bỏ; Google News bỏ; nguồn chính thức: dùng feed Vietstock làm tín hiệu, Rick đối chiếu HOSE/HNX | Đã tải thử cả 16 feed ngày 2026-10-22 (`evidence/p1-nguon/source-audit.md`) | MẶC ĐỊNH; Rick chọn bật tin tiếng Anh (2026-10-22). Kênh chính thức: SSI MCP (xem `source-audit.md` mục 6) |
| 6 | Nơi chạy n8n | Thử bằng Docker/`npx` bản 2.45.x; chạy thật: chọn giữa n8n Cloud, máy chủ riêng (VPS), máy tính cá nhân | Lịch chỉ chạy khi máy bật liên tục; máy cá nhân ngủ là lỡ lịch | **CẦN RICK** chọn trước giai đoạn 7 |
| 7 | Nhà cung cấp AI | Anthropic (Chat Model có sẵn trong n8n): `claude-haiku-5-5` cho phân loại, `claude-sonnet-5-5` cho bản tin (Rick đổi được sang Haiku 5.5) | Đã có node; chi phí thấp cho tác vụ phân loại | **CẦN RICK**: cần khóa API riêng; gói đăng ký chat không đương nhiên gồm API |
| 8 | Ngân sách AI thử nghiệm | 5 USD cho toàn bộ giai đoạn 4 (GIẢ ĐỊNH) | Chạy thật ước tính 1,2–1,7 USD/tháng (`evidence/p2-thiet-ke/cost-model.md`); 5 USD đủ chạy bộ mẫu hàng chục lần | **CẦN RICK** xác nhận hoặc đổi |
| 9 | Trần chi phí hằng ngày khi chạy thật | `MAX_AI_ITEMS_PER_DAY = 200` (GIẢ ĐỊNH) | Chặn chi phí chạy ngoài ý muốn | MẶC ĐỊNH, đo lại ở giai đoạn 4 |
| 10 | Lịch chạy | Collector thứ 2–6 mỗi 30 phút 08:00–16:30, thêm 18:00 và 21:00; thứ 7, CN 09:00 và 20:00. Digest 08:15 và 15:30 thứ 2–6; heartbeat thứ 2 07:55. Ngoài giờ chỉ cảnh báo mức 5 (giờ Việt Nam) | Bám phiên giao dịch; quét cuối tuần vì feed nhanh nhất chỉ giữ ~20,5 giờ (`docs/DESIGN.md` mục 1.3) | GIẢ ĐỊNH; giờ giao dịch lấy từ nguồn thứ cấp, Rick đối chiếu quy chế HOSE/HNX |
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
| HTTP Request + XML node đọc đúng 16 feed (BOM, CDATA); đặt UA trình duyệt vì CafeF chặn `curl/...` | Chạy với `fixtures/rss/` | 3 |
| n8n ngừng chạy quá ~20 giờ sẽ mất tin ở feed nhanh nhất (20 mục phủ ~20 giờ) | Đo lại tần suất sau vài ngày chạy thật | 2, 8 |
| Remove Duplicates (lịch sử qua các lần chạy) hoạt động đúng với lịch tự động | Kiểm thử 3 chu kỳ lịch thật, sau khi khởi động lại | 6 |
| Biểu thức cron của Schedule Trigger đúng cú pháp theo phiên bản này: import thành công, chưa kích hoạt | Kích hoạt trên máy thật, xem "thời điểm chạy kế tiếp" | 6 |
| Cổng vào AI "khớp watchlist **hoặc** nguồn tier 1" quá rộng: lần chạy feed thật có 146/280 tin chờ AI, chủ yếu do tier 1 | Đo lại ở giai đoạn 4; phương án: tier 1 chỉ vào AI khi tiêu đề có từ khóa sự kiện (cổ tức, phát hành, giao dịch nội bộ, kết quả kinh doanh...) | 4 |
| Giờ giao dịch dùng để đặt lịch: đã lấy từ nguồn thứ cấp (DESIGN mục 1.3), chưa đọc quy chế gốc | Rick xem quy chế giao dịch HOSE/HNX | 2 → mở |
| Cú pháp cron `*/30 8-16 * * 1-5` cho lịch collector | Kích hoạt workflow, xem thời điểm chạy kế tiếp | 3 |
| Remove Duplicates giữ lịch sử giống nhau khi chạy tay và chạy theo lịch | Kiểm thử ở giai đoạn 3 (tay) và 6 (lịch) | 3, 6 |
| ~~RSS Read không có timeout~~ ĐỌC MÃ, xác nhận; đã chọn HTTP Request (timeout 15 giây) + XML | `docs/DESIGN.md` mục 1.1 | 2 |
| Haiku 5.5 nhận `Thinking Mode = Disabled`; không đặt được nhiệt độ (mô hình mới bỏ `temperature`) | Gọi thử ở giai đoạn 4 | 4 |
| Độ trễ của SSI MCP; cách n8n xác thực với SSI MCP | Đo 5 ngày; hỏi SSI | 5, 6 |

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
| 2026-10-22 | Tải feed bằng HTTP Request (timeout 15 giây, thử lại 2 lần) + XML node; RSS Read là phương án dự phòng | Claude | RSS Read không có timeout (đọc mã) |
| 2026-10-22 | Loại trùng bằng Data Table `rowNotExists`, lưu mọi tin mới | Claude | Tin chỉ được đánh dấu đã thấy sau khi lưu; chạy hỏng giữa chừng không mất tin |
| 2026-10-22 | Gom 10 tin vào một văn bản cho mỗi lần gọi AI | Claude | Batching của Information Extractor vẫn gọi một lần mỗi tin; gom lô giảm 63% chi phí phân loại |
| 2026-10-22 | Đặt Thinking Mode = Disabled; bỏ yêu cầu nhiệt độ ≤ 0,2 của PROMPTS | Claude | Haiku 5.5 không nhận `temperature`; node n8n tự bỏ tham số này |
| 2026-10-22 | Thêm lịch quét tối và cuối tuần | Claude (đề xuất), chờ Rick | Khoảng nghỉ cuối tuần ~63 giờ > ~20,5 giờ feed giữ tin |
| 2026-10-22 | Cột khóa của `news_items` là `item_id` (không phải `id`) | Claude | Data Table đã có cột hệ thống `id` |
| 2026-10-22 | `MAX_ITEMS_PER_RUN` áp dụng sau bước kiểm tra trùng | Claude | Đặt trước thì các tin cũ nhất bị cắt ở mọi lần chạy (đã thấy khi chạy feed thật) |
| 2026-10-22 | Workflow JSON tạo từ `scripts/build_workflows.py`; mã Code node nằm ở `workflows/src/collector/*.js` | Claude | Dễ đọc, dễ so sánh thay đổi; Rick vẫn import một file JSON |
