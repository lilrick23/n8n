# Checklist nghiệm thu

Đánh dấu bằng: `[x] ĐÃ KIỂM CHỨNG` (kèm đường dẫn bằng chứng), `[~] CHƯA KIỂM CHỨNG TRỰC TIẾP`, `[ ]` chưa làm, `[n/a]` không áp dụng (kèm lý do). Một dòng không có đường dẫn bằng chứng thì không được đánh `[x]`.

## A. Môi trường và nguồn
- [ ] Ghi phiên bản Node, pnpm, n8n, hệ điều hành → `evidence/p0-*/env-report.md`
- [ ] Kiểm tra truy cập mạng ra ngoài, ghi mã trả về → `egress-test.log`
- [ ] n8n khởi động được (hoặc ghi rõ vì sao không) → `n8n-start.log`
- [ ] Mỗi nguồn trong `sources.json` đã tải thử, có mẫu XML và thời điểm tải → `fixtures/rss/`
- [ ] Mỗi nguồn có kết luận giữ/bỏ/chờ
- [ ] Mục nguồn chính thức có kết luận và dẫn chiếu điều khoản/robots

## B. Workflow thu thập
- [ ] `validate-workflows.mjs` báo 0 lỗi (JSON hợp lệ, không node mồ côi, timezone `Asia/Ho_Chi_Minh`, có `errorWorkflow`, không bí mật)
- [ ] Import thành công vào n8n 2.45.x
- [ ] Chạy với fixture: số tin vào / sau loại trùng / khớp watchlist đúng kỳ vọng
- [ ] Chạy lần hai cùng dữ liệu: 0 tin mới
- [ ] Một nguồn lỗi (404/timeout) không làm hỏng cả lần chạy
- [ ] Khớp mã: không nhận nhầm từ phổ biến (USD, GDP, CPI, ETF, IPO); khớp alias có/không dấu
- [ ] Ngày giờ về đúng ICT (+07:00), kiểm tra với ít nhất một tin ở mỗi nguồn
- [ ] Liên kết chuẩn hóa (bỏ `utm_*`) và id ổn định giữa các lần chạy

## C. AI
- [ ] Bộ mẫu ≥ 40 tiêu đề có nhãn; Rick duyệt ≥ 20 dòng (hoặc ghi `CHƯA DUYỆT`)
- [ ] Báo cáo: khớp `event_type`, precision/recall mức 4–5, tỉ lệ `needs_human_check`
- [ ] 100% đầu ra qua kiểm tra lược đồ; trường hợp sai có xử lý thử lại và dự phòng
- [ ] 5 mẫu chèn lệnh không làm đổi kết quả sai
- [ ] Không có công cụ nào cấp cho mô hình ở bước phân loại
- [ ] Chi phí thực tế mỗi tin đã đo; so với mô hình chi phí, có giải trình chênh lệch
- [ ] Đơn giá có ngày tra và URL; trần `MAX_AI_ITEMS_PER_DAY` hoạt động (thử vượt trần)

## D. Bản tin và gửi
- [ ] Mẫu bản tin có đủ nhóm: chính thức / báo chí xác nhận / ý kiến / tin đồn, mỗi dòng có nguồn, URL, giờ đăng
- [ ] Có dòng miễn trừ trách nhiệm
- [ ] Tin dài gấp 3 lần 4096 ký tự được tách đúng, không cắt giữa URL
- [ ] Tiêu đề chứa `_ * [ < > &` gửi không lỗi (HTML, đã escape)
- [ ] `DRY_RUN` hoạt động: gửi đúng kênh thử, gắn nhãn thử nghiệm
- [ ] Ngày không có tin vẫn có thông báo "không có tin mức ≥ 3"

## E. Lỗi và vận hành
- [ ] Ma trận 7 kịch bản lỗi có bằng chứng từng dòng
- [ ] Chạy theo lịch thật ≥ 3 chu kỳ, không gửi trùng
- [ ] Khởi động lại n8n, lịch sử loại trùng còn nguyên
- [ ] Báo lỗi có chống bão (1 lỗi giống nhau / 30 phút)
- [ ] Heartbeat hằng tuần hoạt động
- [ ] Lịch xóa dữ liệu cũ và cấu hình giữ execution đã thiết lập

## F. Bảo mật
- [ ] Không có bí mật trong repo, workflow JSON, evidence (`scan-secrets.sh` sạch)
- [ ] Credential chỉ trong kho credential của n8n
- [ ] `N8N_ENCRYPTION_KEY` đã được Rick sao lưu riêng (nhắc trong RUNBOOK)
- [ ] n8n có xác thực người dùng; cổng 5678 không mở ra Internet khi chưa có HTTPS
- [ ] Telegram bot chỉ gửi tới một chat ID, không nhận lệnh
- [ ] Khóa API có hạn mức chi tiêu tại nhà cung cấp
- [ ] Không có thông tin khách hàng/tài khoản trong watchlist, log, bằng chứng

## G. Tài liệu và bàn giao
- [ ] `RUNBOOK.md` tiếng Việt, người không lập trình làm theo được
- [ ] `FINAL-REPORT.md`: mỗi khẳng định → nhãn → file bằng chứng
- [ ] Giả định chưa xác minh được liệt kê rõ
- [ ] Chi phí tháng ước tính, có công thức và ngày tra giá
- [ ] PR nháp mở, mô tả đúng phạm vi; chỉ thay đổi trong `automation/vn-news-monitor/`
- [ ] `LESSONS.md` có bài học và tối đa 3 đề xuất tiếp theo

## H. Kịch bản nghiệm thu 3 ngày (Rick)
Mỗi ngày giao dịch, ghi 5 dòng: (1) tin quan trọng Rick tự thấy mà hệ thống bỏ sót; (2) tin hệ thống báo nhưng không quan trọng; (3) tin bị phân loại sai mức; (4) tin trùng gửi nhiều lần; (5) bản tin có đúng giờ không. Kết thúc 3 ngày, Claude Code tổng hợp thành số đo và đề xuất chỉnh rubric hoặc watchlist.
