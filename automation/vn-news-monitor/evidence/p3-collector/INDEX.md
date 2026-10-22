# Bằng chứng giai đoạn 3 — Workflow thu thập (`news-collector`)

Phiên: 2026-10-22, 08:30–08:50 UTC (15:30–15:50 ICT). n8n 2.45.0, image `mirror.gcr.io/n8nio/n8n:2.45.0`, thư mục dữ liệu mới cho lần chạy cuối.
Kết quả: **ĐẠT** theo tiêu chí giai đoạn 3: validate 0 lỗi; import thành công; chạy fixture đúng kỳ vọng; chạy lần hai ra 0 tin mới. Chưa có nhánh AI và cảnh báo (giai đoạn 4–5). Chưa chạy theo lịch (giai đoạn 6).

## Sản phẩm

| File | Vai trò |
|---|---|
| `workflows/news-setup.json` | Chạy một lần: tạo bảng `news_items`, `run_log`, `ai_usage` |
| `workflows/news-collector.json` | Thu thập 15 feed, chuẩn hóa, loại trùng, khớp watchlist, lưu, ghi `run_log` |
| `workflows/news-error-handler.json` | Bản tối thiểu để `errorWorkflow` có đích; giai đoạn 6 hoàn thiện |
| `workflows/src/collector/*.js` | Mã của các Code node (đọc và so sánh dễ hơn JSON) |
| `scripts/build_workflows.py` | Ghép mã và cấu hình thành các file JSON trên |
| `scripts/validate-workflows.mjs`, `scripts/scan-secrets.sh` | Kiểm tra workflow và quét bí mật |
| `scripts/test-match.mjs`, `fixtures/match/match-cases.jsonl` | 18 ca kiểm thử khớp mã và chủ đề |
| `scripts/expected_collector.py`, `scripts/n8n_exec.py` | Tính số kỳ vọng độc lập; đọc kết quả execution của n8n |

## Khẳng định và bằng chứng

| # | Khẳng định | Nhãn | Bằng chứng | Lệnh | Thời điểm (UTC / ICT) |
|---|---|---|---|---|---|
| 1 | 3 workflow (và bản thử fixture) qua kiểm tra: JSON hợp lệ, không node mồ côi, timezone, `errorWorkflow`, không bí mật | ĐÃ KIỂM CHỨNG | `validate.log` | `node scripts/validate-workflows.mjs` | 08:48 / 15:48 |
| 2 | Không có chuỗi giống bí mật trong `evidence/`, `workflows/` | ĐÃ KIỂM CHỨNG | `scan-secrets.log` | `bash scripts/scan-secrets.sh` | 08:49 / 15:49 |
| 3 | Import 4 workflow vào n8n 2.45.0 thành công, ở trạng thái không hoạt động | ĐÃ KIỂM CHỨNG | `import.log` | `n8n import:workflow --input=...` | 08:47 / 15:47 |
| 4 | Workflow tạo bảng tạo được 3 bảng Data Table | ĐÃ KIỂM CHỨNG | `execution-setup.json`, `.log` | REST `POST /rest/workflows/vnNewsSetup00001/run` | 08:47 / 15:47 |
| 5 | Chạy fixture lần 1: 150 tin đọc, 146 sau loại trùng, 146 lưu, 6 khớp watchlist; khớp 10/10 chỉ số kỳ vọng | ĐÃ KIỂM CHỨNG | `expected-vs-actual.md`, `.log`, `execution-run1.json` | REST run + `python3 -I scripts/expected_collector.py` | 08:47 / 15:47 |
| 6 | Chạy fixture lần 2 cùng dữ liệu: 0 tin mới | ĐÃ KIỂM CHỨNG (chạy tay) | `execution-run2-no-new.json`, `.log` | REST run | 08:47 / 15:47 |
| 7 | Nguồn trả 404 đi ra nhánh lỗi, được ghi vào `run_log`; 15 nguồn khác chạy bình thường | ĐÃ KIỂM CHỨNG | `execution-run1.json` (node `Loi tai feed`, `Tong ket`) | REST run | 08:47 / 15:47 |
| 8 | Chạy feed thật: 15/15 nguồn, 430 tin, 280 mới; lần hai 0 tin mới | ĐÃ KIỂM CHỨNG | `execution-live1.json`, `execution-live2.json`, `.log` | REST run, mạng qua proxy của phiên | 08:48 / 15:48 |
| 9 | Khớp mã/alias/chủ đề: 18/18 ca đúng, gồm USD/GDP/CPI/ETF/IPO không bị nhận là mã | ĐÃ KIỂM CHỨNG (mã Code node chạy bằng Node.js 22, ngoài n8n) | `test-match.log` | `node scripts/test-match.mjs` | 08:44 / 15:44 |
| 10 | Nguồn treo quá 15 giây bị cắt và đi nhánh lỗi | CHƯA KIỂM CHỨNG TRỰC TIẾP | — | — | — |
| 11 | Lịch cron chạy đúng giờ ICT; loại trùng đúng khi chạy theo lịch và sau khởi động lại | GIẢ ĐỊNH, kiểm ở giai đoạn 6 | — | — | — |

## Cách Rick tự kiểm tra (5 bước)

1. Mở n8n, vào **Workflows → Import from file**, lần lượt chọn `news-error-handler.json`, `news-setup.json`, `news-collector.json` trong thư mục `workflows/`.
2. Mở `VN news - setup tables`, bấm **Execute workflow**. Vào mục **Data tables**: phải thấy 3 bảng `news_items`, `run_log`, `ai_usage`.
3. Mở `VN news - collector`, bấm **Execute workflow** (node `Chay tay`). Chờ khoảng 15 giây.
4. Mở bảng `news_items`: phải có vài trăm dòng, cột `published_at` có giờ, cột `tickers` có mã khi tin nhắc tới mã trong watchlist. Mở `run_log`: một dòng, `sources_failed = 0`.
5. Bấm **Execute workflow** lần nữa: dòng mới trong `run_log` phải có `items_new` bằng 0 hoặc rất nhỏ (chỉ tin mới đăng trong vài phút đó).

Không bật (Activate/Publish) workflow ở bước này: lịch tự chạy chỉ bật sau khi có nhánh AI, cảnh báo và Rick đồng ý.

## Ghi chú dữ liệu

- File execution đầy đủ (1–4 MB, chứa đoạn trích báo) **không commit**. Bản trong thư mục này đã rút gọn: trạng thái node, số item, dòng `run_log`, 5 dòng mẫu chỉ gồm tiêu đề và URL.
- Tài khoản chủ của bản n8n thử là `owner@example.com` với mật khẩu ngẫu nhiên lưu ngoài repo; khóa mã hóa là chuỗi thử không dùng ở đâu khác.
