# Kỳ vọng và thực tế: news-collector (giai đoạn 3)

Chạy: 2026-10-22, 08:47–08:49 UTC (15:47–15:49 ICT), n8n 2.45.0 (Docker, thư mục dữ liệu mới), workflow `VN news - collector (fixture test)`.
Dữ liệu: 15 fixture trong `fixtures/rss/` (10 tin mỗi nguồn, phục vụ bằng máy chủ tệp cục bộ `127.0.0.1:8099`) và một nguồn cố ý lỗi (`test-missing-feed`, trả 404).

Số kỳ vọng tính bằng `scripts/expected_collector.py`: một bản cài đặt riêng bằng Python, đọc thẳng fixture, không dùng mã JavaScript của workflow. Log gốc: [`expected-vs-actual.log`](expected-vs-actual.log).

## Lần chạy 1 (bảng `news_items` trống)

| Chỉ số | Kỳ vọng | Thực tế (n8n) | Kết quả |
|---|---|---|---|
| Nguồn tải được / lỗi | 15 / 1 (`test-missing-feed`) | 15 / 1 | Đạt |
| Tin đọc từ feed | 150 | 150 | Đạt |
| Sau loại trùng trong lần chạy (cùng URL ở hai feed) | 146 | 146 | Đạt |
| Tập `item_id` (SHA-256 của URL chuẩn hóa) | giống nhau | giống nhau | Đạt |
| Tin mới (chưa có trong bảng) | 146 | 146 | Đạt |
| Tin khớp watchlist/vĩ mô | 6 | 6 | Đạt (cùng 6 tin, cùng mã và chủ đề) |
| `published_at` có `+07:00` và giữ nguyên thời điểm gốc | tất cả | tất cả | Đạt, kiểm cả 15 nguồn, gồm năm 2 chữ số của CafeF |
| Tin đã lưu | 146 | 146 | Đạt |

## Lần chạy 2 (cùng dữ liệu)

| Chỉ số | Kỳ vọng | Thực tế | Kết quả |
|---|---|---|---|
| Tin đọc / sau loại trùng trong lần chạy | 150 / 146 | 150 / 146 | Đạt |
| **Tin mới** | **0** | **0** | **Đạt**: loại trùng qua các lần chạy hoạt động |
| Tin đã lưu | 0 | 0 | Đạt |

Bằng chứng: [`execution-run1.json`](execution-run1.json), [`execution-run2-no-new.json`](execution-run2-no-new.json) (đã rút gọn: trạng thái node, số item, dòng `run_log`, 5 dòng mẫu chỉ gồm tiêu đề và URL).

## Chạy thêm với feed thật (cùng máy n8n, sau hai lần chạy fixture)

| Chỉ số | Lần 1 (15:48 ICT) | Lần 2 (15:48 ICT, 15 giây sau) |
|---|---|---|
| Nguồn tải được / lỗi | 15 / 0 | 15 / 0 |
| Tin đọc / sau loại trùng trong lần chạy | 430 / 424 | 430 / 424 |
| Tin mới | 280 (144 tin còn lại đã có từ fixture) | **0** |
| Tin khớp watchlist ví dụ | 9 | 0 |
| Tin đánh dấu chờ AI (`pending_ai`) | 146 | 0 |
| Thời gian chạy | 13 giây | 9 giây |

Bằng chứng: [`execution-live1.json`](execution-live1.json), [`execution-live2.json`](execution-live2.json).

## Lỗi tìm thấy và đã sửa trong giai đoạn này

| Lỗi | Phát hiện thế nào | Sửa |
|---|---|---|
| Code node không có lớp `URL`: mọi tin bị bỏ (0 tin) | Lần chạy thử đầu tiên | Chuẩn hóa URL bằng biểu thức chính quy |
| Node XML làm mất liên kết với nguồn | Đọc mã `Xml.node.ts` | Chèn `<n8n_source_id>` vào XML trước khi phân tích |
| `Gioi han` (MAX_ITEMS_PER_RUN) đặt trước bước loại trùng: các tin cũ nhất luôn bị cắt và không bao giờ được lưu | Chạy feed thật: 424 tin, giới hạn 300, lần sau vẫn 0 tin mới | Chuyển `Gioi han` ra sau bước kiểm tra `news_items` |
| `n8n execute` (CLI) không dùng được Data Table ("module is disabled") | Chạy workflow tạo bảng | Chạy qua máy chủ n8n (REST `/rest/workflows/:id/run`, giống bấm "Execute workflow") |

## Chưa kiểm ở giai đoạn này

- Nguồn **treo** (quá thời gian chờ 15 giây): mới kiểm nguồn trả 404. `CHƯA KIỂM CHỨNG TRỰC TIẾP`.
- Chạy **theo lịch** (Schedule Trigger) và sau khi khởi động lại: giai đoạn 6.
