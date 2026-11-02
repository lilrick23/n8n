# Bằng chứng giai đoạn 5: bản tin tổng hợp (`news-digest`)

Cập nhật: 2026-11-02. Môi trường thử: n8n 2.45.0 (Docker, `mirror.gcr.io/n8nio/n8n:2.45.0`), phiên Claude Code trên đám mây. Mô hình AI: `claude-haiku-5-5`.

Kết luận: **ĐẠT MỘT PHẦN.** Bản tin dựng đúng từ dữ liệu thật và dữ liệu giả, tách tin dài đúng, ký tự đặc biệt không làm hỏng HTML. Phần gửi Telegram **CHƯA KIỂM CHỨNG TRỰC TIẾP** vì chưa có bot token và chat ID của Rick.

| # | Khẳng định | Nhãn | Bằng chứng | Cách chạy | Giờ UTC / ICT |
|---|---|---|---|---|---|
| 1 | Workflow `news-digest.json` dựng từ `workflows/src/digest/*` và qua kiểm tra cấu trúc | ĐÃ KIỂM CHỨNG | `workflows/news-digest.json`, `scripts/validate-workflows.mjs` (5 tệp, 0 lỗi) | `python3 -I scripts/build_workflows.py` | 11:15 / 18:15 |
| 2 | Bản tin từ dữ liệu thật: 300 tin trong kỳ, 27 tin mức ≥ 3, 3 phần (3.746 / 3.829 / 2.071 ký tự) | ĐÃ KIỂM CHỨNG | `execution-digest-live2.json`, `sample-digest-live2.txt`, `sample-digest.html` | Collector chạy tay (execution 6), rồi digest chạy tay (execution 10) | 11:19 / 18:19 |
| 3 | Tin dài hơn 4 lần giới hạn (16.630 ký tự) được tách thành 5 phần, mỗi phần ≤ 3.753 ký tự, không cắt giữa thẻ `<a>` | ĐÃ KIỂM CHỨNG | `execution-digest-fixture3.json`, `sample-digest-fixture3.txt`, dữ liệu `fixtures/digest/rows.json` | `python3 -I scripts/make_digest_test.py` rồi chạy bản thử (execution 11) | 11:19 / 18:19 |
| 4 | Ký tự đặc biệt `& < > " '` trong tiêu đề, tóm tắt và URL được escape; mỗi phần chỉ có thẻ `b`, `i`, `a`, đóng mở đủ cặp | ĐÃ KIỂM CHỨNG (kiểm bằng script trên đầu ra) | `sample-digest-fixture3.txt` | Kiểm thẻ bằng biểu thức chính quy | 11:19 / 18:19 |
| 5 | Kỳ không có tin vẫn gửi một dòng "Không có tin mức ≥ 3 trong kỳ." kèm dòng miễn trừ | ĐÃ KIỂM CHỨNG | `execution-digest-empty1.json`, `sample-digest-empty1.txt` | Bản thử với 0 tin (execution 9) | 11:19 / 18:19 |
| 6 | `DRY_RUN = true` gắn nhãn `[THỬ NGHIỆM]` ở đầu bản tin | ĐÃ KIỂM CHỨNG | 3 tệp `sample-digest-*.txt` | — | — |
| 7 | Không có `TELEGRAM_CHAT_ID` thì không gửi, ghi `digest_log` với `error = chua_co_chat_id` | ĐÃ KIỂM CHỨNG | `execution-digest-live2.json`, node `Tong ket ban tin` | — | — |
| 8 | AI "Điểm nhấn" chỉ đọc `summary_vi` của tin mức ≥ 4; một lần gọi ~1.340 token vào, ~274 token ra (~0,00027 USD) | ĐÃ KIỂM CHỨNG | `execution-digest-live2.json`, node `Mo hinh Haiku (ban tin)` | — | — |
| 9 | AI lỗi thì bản tin vẫn dựng, chỉ thiếu mục "Điểm nhấn" (`onError = continueRegularOutput`) | CHƯA KIỂM CHỨNG TRỰC TIẾP; mã đã có, thử ở giai đoạn 6 kịch bản (c) | `workflows/src/digest/format.js` | — | — |
| 10 | Gửi Telegram `parse_mode = HTML`, thử lại 3 lần | CHƯA KIỂM CHỨNG TRỰC TIẾP; cần bot token và chat ID của Rick | node `Gui Telegram` | — | — |
| 11 | Mục "Công bố chính thức" ghi rõ "Chưa kết nối nguồn công bố chính thức" | ĐÃ KIỂM CHỨNG | `sample-digest-live2.txt` | — | — |

## Ghi chú

- Lần chạy thật đầu tiên là lần thu thập đầu, nên có tin đăng từ 29–30/10. Khi chạy theo lịch, kỳ bản tin bắt đầu từ lần gửi thành công trước (`digest_log.sent = true`), tối đa 72 giờ.
- Tin không có mã watchlist chia làm hai mục: "Vĩ mô" (chính sách, tín dụng, chủ đề vĩ mô) và "Doanh nghiệp ngoài watchlist". `config/watchlist.example.json` vẫn là danh sách ví dụ, nên phần lớn tin thật rơi vào mục sau.
- Chi phí bản tin: ~44 bản tin/tháng × ~0,00027 USD ≈ 0,012 USD/tháng (tính từ số token đo được, giá Haiku 5.5 kiểm ngày 2026-10-22).
- Tin khớp mã nhưng chưa qua AI (`keyword_only`) được liệt kê riêng ở cuối bản tin để không bỏ sót.
