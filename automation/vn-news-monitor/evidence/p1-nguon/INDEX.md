# Bằng chứng giai đoạn 1 — Khảo sát nguồn tin

Phiên chạy: 2026-10-22, 07:53–08:05 UTC (14:53–15:05 ICT). Máy: container đám mây của phiên Claude Code, môi trường mới Rick tạo lúc 07:50 UTC (đã mở tên miền tin tức).
Kết quả: **ĐẠT MỘT PHẦN.** 16/16 feed báo chí đã khảo sát bằng dữ liệu thật, có kết luận giữ/bỏ/chờ. Nguồn chính thức đã có kết luận (chưa có kênh tự động hợp lệ), riêng HNX chưa truy cập được.

Báo cáo chính: [`source-audit.md`](source-audit.md).

## Khẳng định và bằng chứng

| # | Khẳng định | Nhãn | Bằng chứng | Lệnh | Thời điểm (UTC / ICT) |
|---|---|---|---|---|---|
| 1 | Môi trường mới đã mở mạng tới CafeF, Vietstock (VN và EN), `api.telegram.org`, `www.hsx.vn`, `ssc.gov.vn`, `news.google.com`. Chưa tới được `hsx.vn` (không www, bị ngắt kết nối) và `hnx.vn`/`www.hnx.vn` (lỗi chứng chỉ qua proxy, đi thẳng 503) | ĐÃ KIỂM CHỨNG | `egress-retest.log`, `robots/robots-fetch.log` | `curl -sS -o /dev/null -m 20 -L -w ...` | 07:53 / 14:53 |
| 2 | 16/16 feed trả HTTP 200, XML hợp lệ, UTF-8 | ĐÃ KIỂM CHỨNG | `fetch-<source_id>.log` (16 file, có header HTTP gốc), `survey-run.log` | `curl -sS -L -m 20 -A '<UA trình duyệt>' -D - -o ...` | 07:54 / 14:54 |
| 3 | Số mục, khoảng phủ, tần suất, định dạng ngày, múi giờ, tham số theo dõi, trùng giữa nguồn của từng feed | ĐÃ KIỂM CHỨNG (ảnh chụp một thời điểm) | `survey.json`, `source-audit.md` mục 2 và 4 | `python3 -I scripts/survey_rss.py evidence/p1-nguon/raw config/sources.json evidence/p1-nguon/survey.json` | 07:55 / 14:55 |
| 4 | CafeF chặn User-Agent `curl/...`, chấp nhận `rss-parser` (UA của node RSS Read) và UA trình duyệt; Vietstock chấp nhận tất cả | ĐÃ KIỂM CHỨNG | `user-agent-test.log` | `curl ... -A "<UA>"` × 4 UA × 4 feed | 07:56 / 14:56 |
| 5 | n8n 2.45.0 (Docker) đọc feed thật bằng node RSS Read 1.2: 5 feed, 170 mục (50+50+20+20+30), 0 lỗi; `isoDate` đúng, đổi sang ICT đúng, kể cả năm 2 chữ số của CafeF và BOM của feed tiếng Anh | ĐÃ KIỂM CHỨNG | `n8n-live/p1-rss-live-workflow.json`, `n8n-live/n8n-rss-live.log` | `n8n import:workflow`, `n8n execute --id=p1rsslive0000001` | 08:03 / 15:03 |
| 6 | Mẫu XML thu gọn 10 mục/nguồn cho kiểm thử ngoại tuyến, dòng đầu ghi thời điểm tải | ĐÃ KIỂM CHỨNG | `fixtures/rss/*.xml` (16 file, đã kiểm tra phân tích được, mỗi file đúng 10 mục) | script Python tạo fixture (chạy một lần trong phiên) | 08:04 / 15:04 |
| 7 | robots.txt: CafeF cho phép tất cả; Vietstock chỉ chặn `/manager`, `/export`, `/cache`, file js/css; HOSE cho phép tất cả; UBCKNN không có robots.txt; Google News chặn `/rss` | ĐÃ KIỂM CHỨNG | `robots/*.robots.txt`, `robots/robots-fetch.log` | `curl ... https://<host>/robots.txt` | 07:56 / 14:56 |
| 8 | Không tìm thấy RSS/API công khai của HOSE, UBCKNN | ĐÃ KIỂM CHỨNG một phần: chỉ xem trang chủ và 80 KB đầu gói mã HOSE (bị cắt kết nối) | `source-audit.md` mục 3 | `curl` trang chủ, tìm chuỗi `rss` | 07:58 / 14:58 |
| 9 | HNX: chưa biết có RSS/API, chưa đọc robots/điều khoản | CHƯA KIỂM CHỨNG TRỰC TIẾP | `egress-retest.log` | — | — |
| 10 | Điều khoản sử dụng (Terms of Use) của CafeF, Vietstock, HOSE | CHƯA KIỂM CHỨNG TRỰC TIẾP: chưa đọc. robots.txt cho phép, và hệ thống chỉ lưu tiêu đề, URL, đoạn trích ngắn | — | — | — |
| 11 | Chu kỳ 30 phút đủ trong giờ giao dịch; ngừng quá ~20 giờ sẽ mất tin ở feed nhanh nhất | ĐÃ KIỂM CHỨNG cho số đo một ngày; khuyến nghị lịch là GIẢ ĐỊNH | `source-audit.md` mục 4.9 | — | — |

## Hướng dẫn Rick tự kiểm tra (cho mục 9 và 10)

1. Mở `https://www.hnx.vn` trên máy tính ở công ty, tìm biểu tượng RSS ở chân trang hoặc mục "Tin công bố".
2. Mở `https://www.hnx.vn/robots.txt` và chụp màn hình.
3. Tìm mục "Điều khoản sử dụng" ở chân trang HOSE, HNX, CafeF, Vietstock; xem có cấm thu thập tự động hoặc dùng lại tiêu đề không.
4. Nếu Vietcap có thuê bao dữ liệu chính thức (sở giao dịch hoặc nhà cung cấp dữ liệu), hỏi bộ phận phụ trách có cho dùng trong công cụ nội bộ không.
5. Gửi kết quả (ảnh hoặc ghi chú) vào luồng này; Claude cập nhật `sources.json` và mục 3 của `source-audit.md`.

## Ghi chú về dữ liệu

- File XML đầy đủ (`raw/`, khoảng 500 KB) **không commit**: repo công khai, và đó là nội dung của nhà xuất bản. Chỉ giữ mẫu 10 mục trong `fixtures/rss/` để kiểm thử. Có thể tải lại bằng lệnh ở mục 2.
- Không có bí mật trong thư mục này: `resumeToken` của execution đã thay bằng `<redacted>`, khóa mã hóa dùng thử là chuỗi giả không dùng ở đâu khác, địa chỉ proxy của phiên được ghi dạng `<session egress proxy>`.
- Code node trả `workflow_tz: null` vì `$workflow.timezone` không phải thuộc tính có sẵn; múi giờ của workflow đã kiểm ở giai đoạn 0. Không ảnh hưởng kết luận.
