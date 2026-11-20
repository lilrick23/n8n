# Báo cáo đánh giá AI phân loại tin (giai đoạn 4)

Phiên: 2026-11-01, 15:27–15:33 UTC (22:27–22:33 ICT). n8n 2.45.0 (Docker), workflow `VN news - AI eval`, mô hình `claude-haiku-5-5`, gọi API Anthropic thật.
Bộ mẫu: `fixtures/eval/labeled.jsonl`, 56 tiêu đề thật (fixture giai đoạn 1, ngày 22/10/2026) + 6 mẫu chèn lệnh tự soạn. Nhãn do Claude đề xuất, **CHƯA DUYỆT** (Rick chưa duyệt dòng nào).

## 1. Kết luận

- **ĐÃ KIỂM CHỨNG:** 100% đầu ra cuối cùng đúng lược đồ (mọi tin đều có giá trị hợp lệ, kể cả tin `fallback`). Với prompt v2, 185/186 tin giữ kết quả AI; 1 tin bị `fallback` vì mô hình viết `trung_lập` có dấu. Bước bỏ dấu đã thêm sau đó; chạy lại mã kiểm tra trên đúng dữ liệu đã ghi: 0 fallback (`test-kiem-tra.log`; chạy bằng Node.js ngoài n8n).
- **ĐÃ KIỂM CHỨNG:** 6/6 mẫu chèn lệnh đạt ở cả 6 lần chạy. Chi tiết: `injection-test.md`.
- **ĐÃ KIỂM CHỨNG:** chi phí thật ~0,00016 USD/tin, ~0,4 giây/tin. Chi tiết: `cost-actual.md`.
- Phân loại `event_type` khớp nhãn 86–93% (prompt v2). Mức quan trọng lệch tối đa 1 mức ở 100% tin thật.
- **Điểm yếu chính:** recall mức 4–5 chỉ 0,62 (13/21). AI chấm 3 cho sự kiện thường lệ của mã trong watchlist (cổ tức nhỏ, kết quả quý của công ty nhỏ), trong khi nhãn đề xuất là 4 theo rubric. Cần Rick quyết định (mục 5).
- Số đo phụ thuộc vào nhãn chưa duyệt. Khi Rick sửa nhãn, chạy lại `scripts/eval_report.py` là có số mới, không cần gọi lại API.

## 2. Số đo (3 lần chạy mỗi phiên bản prompt)

| Chỉ số | v1 lần 1 | v1 lần 2 | v1 lần 3 | **v2 lần 1** | **v2 lần 2** | **v2 lần 3** |
|---|---|---|---|---|---|---|
| Tin qua kiểm tra lược đồ (không fallback), /62 | 52 | 62 | 62 | 61 | 62 | 62 |
| Khớp `event_type`, /56 tin thật | 41/56 (73%) | 43/56 (77%) | 40/56 (71%) | 48/56 (86%) | 52/56 (93%) | 51/56 (91%) |
| Khớp `fact_or_opinion`, /56 | 50/56 (89%) | 51/56 (91%) | 50/56 (89%) | 52/56 (93%) | 51/56 (91%) | 52/56 (93%) |
| Khớp đúng `importance`, /56 | 37/56 (66%) | 38/56 (68%) | 42/56 (75%) | 37/56 (66%) | 36/56 (64%) | 41/56 (73%) |
| `importance` lệch ≤ 1 mức, /56 | 56/56 (100%) | 56/56 (100%) | 54/56 (96%) | 56/56 (100%) | 56/56 (100%) | 56/56 (100%) |
| Precision mức 4–5 | 0.875 | 0.762 | 0.81 | 0.812 | 0.867 | 0.929 |
| Recall mức 4–5 (21 tin nhãn 4–5) | 0.667 | 0.762 | 0.81 | 0.619 | 0.619 | 0.619 |
| `needs_human_check` trên tin thật, /56 | 17 | 8 | 10 | 11 | 11 | 7 |
| Mẫu chèn lệnh đạt, /6 | 6 | 6 | 6 | 6 | 6 | 6 |
| Token vào (API báo) | 35152 | 29344 | 29344 | 35287 | 35287 | 35287 |
| Token ra (API báo) | 15049 | 12979 | 13067 | 12749 | 12810 | 12696 |
| Chi phí lần chạy (USD) | 0.01104 | 0.009424 | 0.009468 | 0.009903 | 0.009934 | 0.009877 |
| Thời gian node AI (giây) | 33.5 | 24.7 | 25.5 | 25.1 | 23.9 | 25.2 |

Định nghĩa: precision mức 4–5 = số tin AI chấm ≥ 4 mà nhãn cũng ≥ 4, chia cho số tin AI chấm ≥ 4. Recall = số tin đó chia cho số tin có nhãn ≥ 4. Mức cuối cùng là mức **sau** quy tắc cứng (mục 5 của `docs/AI-PROMPT.md`). Token lấy từ `tokenUsage` mà API trả về, ghi trong dữ liệu chạy của node `Mo hinh Haiku`.

Độ ổn định (v2): 43/62 tin cho cùng `event_type` và `importance` ở cả 3 lần chạy. Mô hình không nhận tham số nhiệt độ, nên kết quả dao động giữa các lần chạy là bình thường; quy tắc cứng giới hạn biên dao động.

## 3. Sai khác lặp lại (prompt v2)

| Nhóm | Ví dụ | Nhãn đề xuất | AI | Nhận xét |
|---|---|---|---|---|
| Sự kiện thường lệ của mã watchlist bị hạ mức | PHC, CNG chi cổ tức; PGBank, NCT, VEF lãi quý 3; RYG phân phối cổ phiếu | 4 | 3 (3/3 lần) | Gốc của recall thấp. Rubric ghi "cổ tức", "kế hoạch kinh doanh" là mức 4 |
| Tin ngân hàng thương mại bị nâng mức | Techcombank giảm lãi suất cho vay | 3 | 4 (3/3 lần) | Quy tắc "không có mã thì tối đa 3" không áp cho `ngan_hang_tin_dung`; trong bộ mẫu tin này giả lập có mã TCB |
| Niêm yết trái phiếu | SHB niêm yết trái phiếu trên SGX | 3 | 4 (2/3 lần) | Có thể nhãn của Claude quá thấp |
| Đổi trái phiếu lấy cổ phiếu | BNP Paribas, Novaland | `trai_phieu`, 4 | 3 | Tin mơ hồ giữa `trai_phieu`, `ma`, `giao_dich_noi_bo` |
| Tin pháp lý ngoài thị trường | Công an kiểm tra cửa hàng thời trang | `khac`, 1 | `xu_phat_phap_ly`, 1–2 | Prompt v2 đã giới hạn `xu_phat_phap_ly` cho doanh nghiệp niêm yết; AI vẫn chọn |

Danh sách đầy đủ từng tin, từng lần chạy: `eval-metrics.json` (trường `mismatches`), `eval-raw-outputs.jsonl`.

## 4. Lỗi định dạng và cách xử lý

- v1 lần 1: một lô 10 tin bị loại cả lô. Mô hình trả `event_type = "tang_von"` cho tin RYG, lần sửa tự động của node vẫn trả giá trị đó, node báo "Model output doesn't fit required format" (`execution-eval-v1-run1.json`, node `Phan loai AI`, item 3). Xử lý: bỏ `enum` khỏi lược đồ node, đưa danh sách vào prompt, kiểm từng tin ở `Kiem tra luoc do` (v2).
- v2 lần 1: tin r26 có `sentiment = "trung_lập"`. Chỉ tin này bị `fallback`. Xử lý: bỏ dấu trước khi so enum.
- Không có lỗi mạng, 429 hay 5xx trong 9 lần chạy (6 lần đánh giá, 3 lần thu thập thật).

## 5. Đề xuất ngưỡng để Rick chọn (không tự đặt)

| Chỉ số | Hiện đo (v2) | Phương án A (chặt) | Phương án B (cân bằng, đề xuất) |
|---|---|---|---|
| Tin qua kiểm tra lược đồ | 99,5% (100% sau sửa) | ≥ 99% | ≥ 98% |
| Khớp `event_type` | 86–93% | ≥ 90% | ≥ 85% |
| Precision mức 4–5 | 0,81–0,93 | ≥ 0,85 | ≥ 0,75 |
| Recall mức 4–5 | 0,62 | ≥ 0,85 | ≥ 0,75 |
| Mẫu chèn lệnh | 6/6 | 100% | 100% |

Với phương án B, chỉ recall chưa đạt. Hai cách xử lý, Rick chọn sau khi duyệt nhãn:
1. Thêm vào prompt: "Mọi sự kiện cụ thể của mã có trong watchlist (cổ tức, kết quả kinh doanh, phát hành, giao dịch nội bộ) tối thiểu mức 4." Hệ quả: nhiều cảnh báo tức thời hơn.
2. Giữ prompt, hạ nhãn các tin đó xuống 3 nếu Rick thấy cổ tức nhỏ không cần báo ngay. Hệ quả: các tin này chỉ vào bản tin tổng hợp.

Tôi chưa áp cách nào để tránh chỉnh prompt theo nhãn chưa duyệt.

## 6. Cách chạy lại

1. Import `workflows/news-ai-eval.json` vào n8n, chọn credential Anthropic ở node `Mo hinh Haiku`.
2. Bấm **Execute workflow**. Mỗi lần chạy ~25 giây, ~0,01 USD.
3. Tải dữ liệu chạy: `GET /rest/executions/<id>` (hoặc dùng `python3 -I scripts/n8n_rest.py run vnNewsAiEval0001 "Chay tay" out.json` với n8n cục bộ).
4. `python3 -I scripts/eval_report.py evidence/p4-ai out.json` để ra số đo.
5. Sau khi Rick sửa nhãn trong `scripts/make_eval_set.py`: `python3 -I scripts/make_eval_set.py`, rồi chạy lại bước 4 trên dữ liệu cũ (không tốn API) và chạy `build_workflows.py` để cập nhật workflow.

## 7. Bổ sung 2026-11-02: nhãn đã duyệt và prompt v3

Rick duyệt toàn bộ đề xuất lúc 11:06 UTC ngày 02/11/2026: 62 nhãn, phương án B và cách xử lý 1 (nâng mức trong prompt).
Prompt v3 thêm quy tắc: tin có `ticker:` trong dòng khớp, nói về sự kiện cụ thể của chính mã đó, được tối thiểu mức 4. Quy tắc này không áp dụng cho analyst_opinion và rumor.

Kết quả 3 lần chạy thật (ĐÃ KIỂM CHỨNG, `v3/eval-report-v3.log`, `v3/execution-eval-v3-run*.json`):

| Chỉ số | v2 | v3 | Ngưỡng B | Đạt |
|---|---|---|---|---|
| Tin qua kiểm tra lược đồ | 99,5% | 186/186 (100%), 0 fallback | ≥ 98% | Có |
| Khớp `event_type` | 86–93% | 48–49/56 (86–88%) | ≥ 85% | Có |
| Precision mức 4–5 | 0,81–0,93 | 0,81–0,84 | ≥ 0,75 | Có |
| Recall mức 4–5 | 0,62 | 1,0 (21/21) | ≥ 0,75 | Có |
| Mẫu chèn lệnh | 6/6 | 6/6 mỗi lần | 100% | Có |
| Chi phí | ~0,00016 USD/tin | ~0,00016 USD/tin (0,030 USD cho 3 lần) | — | — |

Tin bị chấm 4 nhưng nhãn là 3 (nguồn gốc của precision < 1): r28, r31 (ngân hàng hạ lãi suất cho vay), r30 (1/3 lần), r40 (SHB niêm yết trái phiếu tại SGX), r52 (TVC không hoàn tất mua cổ phiếu TVB). Theo quy tắc v3, r40 và r52 là sự kiện cụ thể của mã nên mức 4 là hợp lý; nhãn 3 của hai dòng này có thể cần sửa ở lần duyệt sau. Đây là suy luận của Claude, chưa sửa nhãn.
