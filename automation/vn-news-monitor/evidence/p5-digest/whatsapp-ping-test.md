# Dòng báo WhatsApp (CallMeBot): thử với máy nhận giả lập, 2026-11-19

Thời điểm: 06:56 UTC (13:56 ICT). n8n 2.45.0 (Docker, phiên Claude Code).
Mục đích: kiểm tra nhánh `Dong bao WhatsApp` → `Co WhatsApp?` → `Gui WhatsApp` mà không gọi CallMeBot thật.

Cách làm:

1. Dựng bản tạm `vnNewsDigestWa01` từ `digest_workflow(chat_id="", wa_phone="+840000000000")`. Số điện thoại giả. URL của `Gui WhatsApp` đổi sang `http://127.0.0.1:5711/whatsapp.php`: một máy chủ Python cục bộ ghi lại tham số nhận được.
2. Nhập credential `vnNewsCallMeBot1` (Query Auth, name `apikey`, value giả `test-key-123`).
3. Chạy trigger `Chay tay`. Execution 14: success. Tất cả node success.

Tham số máy nhận ghi được:

```json
{"phone": ["+840000000000"], "text": ["[THỬ NGHIỆM] Bản tin chạy tay 13:56 19/11: CHƯA gửi được Telegram (0/1 phần). Mở n8n, mục Executions để xem lỗi."], "apikey": ["test-key-123"]}
```

Kết luận: khóa đi từ credential vào tham số `apikey`, không nằm trong workflow. Dòng báo chỉ có nhãn, giờ, trạng thái và số phần. Lượt thử không có chat ID, nên dòng báo ghi đúng là chưa gửi Telegram.

Chưa kiểm chứng: gửi tới WhatsApp thật qua `api.callmebot.com` (chờ Rick lấy khóa).
