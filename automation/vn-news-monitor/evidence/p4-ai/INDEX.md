# Bằng chứng giai đoạn 4 — Phân loại tin bằng AI và bộ mẫu đánh giá

Phiên: 2026-11-01, 15:20–15:45 UTC (22:20–22:45 ICT). n8n 2.45.0, image `mirror.gcr.io/n8nio/n8n:2.45.0`, thư mục dữ liệu mới. Mô hình duy nhất: `claude-haiku-5-5` (quy tắc của Rick ngày 2026-11-01). Gọi API Anthropic thật bằng khóa trong biến môi trường `N8N_ANTHROPIC_API_KEY`, nạp vào kho credential của n8n; khóa không xuất hiện trong file nào của repo.
Kết quả: **ĐẠT có điều kiện**. 100% đầu ra đúng lược đồ, 6/6 mẫu chèn lệnh đạt, chi phí thật nằm trong mô hình (+6–8%). Điều kiện: bộ nhãn **CHƯA DUYỆT**, và recall mức 4–5 (0,62) cần Rick chọn cách xử lý (`eval-report.md` mục 5).

## Sản phẩm

| File | Vai trò |
|---|---|
| `docs/AI-PROMPT.md` | Prompt chính thức (v2), lược đồ, quy tắc kiểm tra sau AI, hạn mức, nhật ký thay đổi |
| `workflows/news-collector.json` | Thêm nhánh AI: `Doc ai_usage` → `Chon tin cho AI` → `Vao AI?` → `Gom lo` → `Phan loai AI` (+ `Mo hinh Haiku`) → `Kiem tra luoc do` → `Luu tin`; `Tinh ai_usage` → `Ghi ai_usage` |
| `workflows/news-ai-eval.json` | Workflow chạy tay: nạp bộ mẫu, dùng đúng các node AI của collector, không ghi Data Table |
| `workflows/src/collector/ai-*.{js,txt,json}`, `gom-lo.js`, `kiem-tra.js` | Mã các node mới |
| `fixtures/eval/labeled.jsonl`, `scripts/make_eval_set.py` | 56 tiêu đề thật + 6 mẫu chèn lệnh, nhãn CHƯA DUYỆT |
| `scripts/eval_report.py` | Chấm điểm từ dữ liệu chạy (không gọi API) |
| `scripts/n8n_rest.py`, `scripts/inspect_collector_exec.py` | Chạy workflow qua REST trên n8n cục bộ; tóm tắt một lần chạy collector |
| `scripts/test-kiem-tra.mjs`, `scripts/test-ai-select.mjs` | Chạy lại mã Code node ngoài n8n |

## Khẳng định và bằng chứng

| # | Khẳng định | Nhãn | Bằng chứng | Lệnh | Thời điểm (UTC / ICT) |
|---|---|---|---|---|---|
| 1 | 4 workflow qua kiểm tra cấu trúc, không bí mật | ĐÃ KIỂM CHỨNG | `validate.log`, `scan-secrets.log` | `node scripts/validate-workflows.mjs`; `bash scripts/scan-secrets.sh` | 15:44 / 22:44 |
| 2 | Import 4 workflow và credential vào n8n 2.45.0 thành công | ĐÃ KIỂM CHỨNG | `import.log` | `n8n import:workflow`, `n8n import:credentials` | 15:38 / 22:38 |
| 3 | Haiku 5.5 chạy với `Thinking Mode = disabled` qua node Anthropic Chat Model 1.6 | ĐÃ KIỂM CHỨNG | `execution-eval-run4.json` (node `Mo hinh Haiku`) | REST run | 15:31 / 22:31 |
| 4 | Khớp `event_type` 86–93%, precision mức 4–5 0,81–0,93, recall 0,62 (prompt v2, nhãn CHƯA DUYỆT) | ĐÃ KIỂM CHỨNG (số đo); nhãn chưa duyệt | `eval-report.md`, `eval-metrics.json`, `eval-raw-outputs.jsonl`, `eval-report.log` | `python3 -I scripts/eval_report.py ...` | 15:31–15:33 / 22:31–22:33 |
| 5 | 100% đầu ra cuối cùng đúng lược đồ; tin sai được `fallback` từng tin, không mất cả lô | ĐÃ KIỂM CHỨNG | `eval-report.md` mục 4; `test-kiem-tra.log` | `node scripts/test-kiem-tra.mjs ...` | 15:43 / 22:43 |
| 6 | 6/6 mẫu chèn lệnh đạt ở 6/6 lần chạy | ĐÃ KIỂM CHỨNG | `injection-test.md` | như #4 | 15:27–15:33 |
| 7 | Chi phí thật ~0,00016 USD/tin, ~0,4 giây/tin; tổng giai đoạn 4 ~0,11 USD | ĐÃ KIỂM CHỨNG (theo `tokenUsage` API trả về) | `cost-actual.md` | như #4 | 15:27–15:39 |
| 8 | Collector thật: 15/15 nguồn, nhánh AI phân loại 167 tin, ghi `run_log` (`ai_calls`, `ai_failures`) và `ai_usage` | ĐÃ KIỂM CHỨNG | `execution-collector-live1.json`, `.log` | REST run, feed thật | 15:33 / 22:33 |
| 9 | Trần `MAX_AI_ITEMS_PER_DAY` hoạt động: lần 2 chỉ 33 tin vào AI (đủ 200), 35 tin `keyword_only`, `cap_reached_at` được ghi | ĐÃ KIỂM CHỨNG | `execution-collector-live2.json`, `.log` | REST run | 15:35 / 22:35 |
| 10 | Tin khớp watchlist được ưu tiên; tin chỉ vì tier 1 dừng ở 50% trần | ĐÃ KIỂM CHỨNG (n8n + 3 ca ngoài n8n) | `execution-collector-live3.json`, `.log`; `test-ai-select.log` | REST run; `node scripts/test-ai-select.mjs` | 15:38 / 22:38 |
| 11 | Ước tính token trong `ai_usage` lệch −0,7% về tiền so với số API | ĐÃ KIỂM CHỨNG (lần chạy 3) | `cost-actual.md` mục 5 | như #10 | 15:38 / 22:38 |
| 12 | Mô hình không có công cụ; đầu ra AI chỉ ghi vào cột dữ liệu | ĐÃ KIỂM CHỨNG (đọc cấu hình) | `workflows/news-collector.json`: node `Phan loai AI` chỉ có kết nối `ai_languageModel` | đọc JSON | — |
| 13 | Rick đã duyệt ≥ 20 nhãn | CHƯA | `fixtures/eval/labeled.jsonl` (`label_status = CHUA_DUYET`) | — | — |
| 14 | Lỗi khóa API sai/hết hạn mức chuyển sang `keyword_only` | CHƯA KIỂM CHỨNG TRỰC TIẾP; mã đã có (`kiem-tra.js`), thử ở giai đoạn 6 kịch bản (c) | — | — | — |

## Lưu ý về file chạy

Các file `execution-*.json` là bản **rút gọn** của `GET /rest/executions/:id`: giữ đầy đủ dữ liệu các node AI và tổng kết; các node tải feed chỉ giữ số item, không giữ toàn văn bài (repo công khai). `eval_report.py` đọc được cả bản đầy đủ lẫn bản rút gọn.
Lần chạy v1 lần 2–3 chỉ giữ số đo (`eval-metrics-prompt-v1.json`, `eval-raw-outputs-prompt-v1.jsonl`), không giữ file chạy.

## Cách Rick tự kiểm tra (5 bước)

1. Trong n8n, vào **Credentials → Add credential → Anthropic**, dán khóa API, đặt tên `Anthropic (vn-news)`.
2. Import `workflows/news-ai-eval.json`. Mở node `Mo hinh Haiku`, chọn credential vừa tạo. Kiểm tra ô Model là `claude-haiku-5-5`.
3. Bấm **Execute workflow**. Sau ~25 giây, mở node `Kiem tra luoc do`: phải có 62 dòng, cột `classified_by` là `ai:claude-haiku-5-5`.
4. Xem 6 dòng có `eval_id` bắt đầu bằng `i`: `importance` không quá 4, `needs_human_check = true`.
5. Duyệt nhãn: mở `fixtures/eval/labeled.jsonl` (hoặc bảng trong `eval-report.md` mục 3), ghi các dòng anh thấy sai nhãn và gửi tôi. Tôi sửa nhãn và chạy lại số đo mà không tốn thêm API.
