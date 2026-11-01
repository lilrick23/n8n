# Chi phí AI thực tế (giai đoạn 4)

Đơn giá Haiku 5.5: 0,10 USD / 1 triệu token vào, 0,50 USD / 1 triệu token ra. Tra ngày 2026-10-22 tại `https://platform.claude.com/docs/en/about-claude/pricing.md` (bản lưu: `evidence/p2-thiet-ke/pricing-2026-10-22.txt`). CHƯA KIỂM CHỨNG TRỰC TIẾP lại vào 2026-11-01.
Token lấy từ `tokenUsage` do API trả về, ghi trong dữ liệu chạy của node `Mo hinh Haiku`. Đây là số API tính, không phải ước tính.

## 1. Kết luận

- **ĐÃ KIỂM CHỨNG:** ~0,00016 USD mỗi tin (0,000156–0,000160 ở các lần chạy ổn định), ~0,4 giây mỗi tin.
- Mô hình chi phí giai đoạn 2 dự báo 0,000148 USD/tin. Thực tế cao hơn **6–8%**: token vào gần đúng, token ra cao hơn ~30% (tiếng Việt tốn token hơn giả định 180 token/tin). Mức chênh này nhỏ so với biên độ của số tin mỗi ngày.
- Chạy thật ở trần 200 tin/ngày: **~0,032 USD/ngày, ~0,70 USD/tháng** (22 ngày giao dịch) hoặc ~0,96 USD/tháng nếu chạm trần cả 30 ngày.
- Tổng đã chi trong giai đoạn 4: **~0,11 USD** (bảng mục 3), trong ngân sách thử 5 USD.

## 2. Số đo theo lần chạy

| Lần chạy | Thời điểm (UTC) | Tin | Lần gọi | Token vào | Token ra | USD | USD/tin | Giây/tin (node AI) |
|---|---|---|---|---|---|---|---|---|
| Đánh giá v1 lần 1 | 15:27 | 62 | 8 (1 lần sửa) | 35.152 | 15.049 | 0,01104 | 0,000178 | 0,54 |
| Đánh giá v1 lần 2 | 15:28 | 62 | 7 | 29.344 | 12.979 | 0,00942 | 0,000152 | 0,40 |
| Đánh giá v1 lần 3 | 15:29 | 62 | 7 | 29.344 | 13.067 | 0,00947 | 0,000153 | 0,41 |
| Đánh giá v2 lần 1 | 15:31 | 62 | 7 | 35.287 | 12.749 | 0,00990 | 0,000160 | 0,40 |
| Đánh giá v2 lần 2 | 15:32 | 62 | 7 | 35.287 | 12.810 | 0,00993 | 0,000160 | 0,39 |
| Đánh giá v2 lần 3 | 15:32 | 62 | 7 | 35.287 | 12.696 | 0,00988 | 0,000159 | 0,41 |
| Thu thập thật lần 1 | 15:33 | 167 | 17 | 91.484 | 34.249 | 0,02627 | 0,000157 | — |
| Thu thập thật lần 2 (chạm trần) | 15:35 | 33 | 4 | 20.047 | 7.130 | 0,00557 | 0,000169 | — |
| Thu thập thật lần 3 (n8n mới, mã cuối) | 15:38 | 100 | 10 | 54.589 | 20.286 | 0,01560 | 0,000156 | 0,39 |

Lần chạy "thu thập thật" dùng feed RSS thật và workflow `VN news - collector`; dữ liệu: `execution-collector-live*.json`.
Prompt v2 dài hơn v1 ~850 token vào mỗi lần gọi (định nghĩa loại sự kiện), làm tăng ~0,0000085 USD/tin (~5%). Đổi lại, khớp `event_type` tăng từ 71–77% lên 86–93%.

## 3. Tổng đã chi trong giai đoạn 4

Cộng 9 lần chạy trên: 0,0110 + 0,0094 + 0,0095 + 0,0099 + 0,0099 + 0,0099 + 0,0263 + 0,0056 + 0,0156 = **~0,107 USD**. Thêm một lệnh thử khóa ngày 2026-11-01 (vài chục token, < 0,001 USD).
Đối chiếu với số liệu trên trang Anthropic Console (Usage) là việc Rick nên làm một lần để chắc số khớp hóa đơn (CHƯA KIỂM CHỨNG TRỰC TIẾP).

## 4. So với mô hình chi phí giai đoạn 2

| Thành phần mỗi tin (lô 10 tin) | Giả định (`scripts/cost_model.py`) | Đo được (thu thập lần 3) |
|---|---|---|
| Token vào | (1.200 + 1.106) / 10 + 300 = 531 | 546 |
| Token ra | 100 / 10 + 180 = 190 | 203 |
| USD/tin | 0,000148 | 0,000156 |

Dự báo tháng cập nhật (chỉ phân loại, Haiku 5.5, 22 ngày):

| Kịch bản | Tin vào AI/ngày | USD/tháng (giai đoạn 2) | USD/tháng (đo thật) |
|---|---|---|---|
| Thấp | 30 | 0,10 | 0,10 |
| Vừa | 80 | 0,26 | 0,27 |
| Cao (trần) | 200 | 0,65 | 0,69 |

Bản tin tổng hợp chuyển sang Haiku 5.5 theo quy tắc của Rick (~0,05 USD/tháng theo mô hình giai đoạn 2; đo ở giai đoạn 5). Tổng dự kiến ≤ ~0,75 USD/tháng ở trần, thay cho 1,73 USD/tháng khi bản tin dùng Sonnet.

**Quan sát quan trọng:** lần thu thập đầu có 167 tin cần AI, trong đó chỉ 17 tin khớp watchlist; 150 tin còn lại vào AI chỉ vì nguồn tier 1. Ở chế độ cũ, trần 200 tin bị dùng gần hết ngay lần chạy đầu ngày. Đã sửa: tin khớp được ưu tiên, tin chỉ vì tier 1 chỉ vào AI khi tổng trong ngày < 50% trần (`TIER1_ONLY_AI_SHARE`). Lần 3 xác nhận: 17/17 tin khớp vào AI, 83 tin tier 1 vào AI, 67 tin tier 1 chuyển `keyword_only`.

## 5. Ước tính trong bảng `ai_usage`

Workflow không đọc được `tokenUsage` từ Code node, nên bảng `ai_usage` ghi token **ước tính** (`estimated = true`): token vào = 2.300 × số lần gọi + số ký tự đầu vào / 1,3; token ra = số ký tự đầu ra / 1,9. Hệ số đo từ 3 lần chạy (tiếng Việt ~1,3 ký tự/token vào).
Kiểm ở lần thu thập 3: ước tính 55.478 vào / 19.879 ra (0,015487 USD) so với thật 54.589 / 20.286 (0,015602 USD): lệch **−0,7%** về tiền. Hai lần đầu dùng hệ số cũ (ký tự / 3) và ước tính thấp hơn thật ~41%; đã sửa.
