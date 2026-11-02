# Hướng dẫn vận hành: chạy hệ thống tin tức 24/7

Cập nhật: 2026-11-02. Viết cho người không lập trình. Bản này bao phần cài đặt trên máy chủ riêng (VPS). Phần lỗi, giám sát và nghiệm thu bổ sung ở giai đoạn 6–8.

## 0. Hệ thống gồm những gì

| Thành phần | Việc làm | Lịch (giờ Việt Nam) |
|---|---|---|
| `VN news - collector` | Đọc 15 nguồn RSS, loại tin trùng, khớp mã theo dõi, AI phân loại (Haiku 5.5) | Thứ 2–6 mỗi 30 phút 08:00–16:30, thêm 18:00 và 21:00; thứ 7, CN 09:00 và 20:00 |
| `VN news - digest` | Gom tin mức ≥ 3, viết "Điểm nhấn", gửi Telegram | Thứ 2–6, 08:15 và 15:30 |
| `VN news - setup tables` | Tạo bảng dữ liệu | Chạy tay một lần |
| `VN news - error handler` | Nhận lỗi của hai workflow trên | Tự chạy khi có lỗi |

Chi phí ước tính mỗi tháng: máy chủ ~4–7 EUR (giá tham khảo từ nguồn thứ cấp, kiểm lại trên trang nhà cung cấp) + AI ≤ ~0,77 USD ở mức trần (`evidence/p4-ai/cost-actual.md`, `evidence/p5-digest/INDEX.md`). Telegram miễn phí.

## 1. Chuẩn bị (làm một lần)

1. **Bot Telegram.** Mở Telegram, tìm `@BotFather`, gửi `/newbot`, đặt tên bot. BotFather trả về một token dạng `123456789:AA...`. Giữ token này riêng tư. Không dán vào chat với Claude.
2. **Khóa Anthropic API.** Vào console.anthropic.com → API keys. Tạo một khóa riêng cho máy chủ. Đặt hạn mức chi tiêu tháng (ví dụ 5 USD) tại mục Limits.
3. **Máy chủ.** Tạo một VPS Ubuntu 24.04, 2 GB RAM trở lên (ví dụ Hetzner CX22/CX23 hoặc tương đương). Chọn đăng nhập bằng SSH key nếu nhà cung cấp hỗ trợ. Ghi lại địa chỉ IP.

## 2. Cài đặt (khoảng 10 phút)

1. Đăng nhập máy chủ: trên máy tính của anh, mở Terminal (macOS) hoặc PowerShell (Windows), gõ `ssh root@<IP>`.
2. Dán hai lệnh sau:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/lilrick23/n8n/claude/vn-news-monitor/automation/vn-news-monitor/deploy/install.sh -o install.sh
   sudo bash install.sh
   ```

3. Script hỏi khóa Anthropic, rồi token Telegram. Ký tự anh dán không hiện ra màn hình. Đó là bình thường.
4. Script nhắc gửi `/start` cho bot. Mở Telegram, gửi `/start` cho bot vừa tạo, rồi nhấn Enter. Script tự lấy chat ID.
5. Script in `{"status":"ok"}` và các bước tiếp theo.

**Sao lưu ngay** tệp `/opt/vn-news-monitor/.env`. Tệp này chứa `N8N_ENCRYPTION_KEY`. Mất tệp này thì mất mọi credential. Cách lấy: `cat /opt/vn-news-monitor/.env`, chép vào trình quản lý mật khẩu.

## 3. Bật hệ thống

1. Mở đường hầm từ máy tính của anh: `ssh -L 5678:127.0.0.1:5678 root@<IP>`. Để cửa sổ này mở.
2. Mở trình duyệt: `http://localhost:5678`. Tạo tài khoản quản trị (email và mật khẩu mạnh).
3. Mở `VN news - setup tables`, bấm **Execute workflow**. Bốn bảng được tạo.
4. Mở `VN news - collector`, bấm **Execute workflow** một lần để kiểm tra. Kết quả xanh là đạt.
5. Mở `VN news - digest`, bấm **Execute workflow**. Anh nhận bản tin gắn nhãn `[THỬ NGHIỆM]` trên Telegram.
6. Bật lịch: ở cả `VN news - collector` và `VN news - digest`, bấm **Publish**.

Từ bước 6, hệ thống chạy liên tục. Máy tính của anh có thể tắt.

## 4. Tắt khẩn cấp

- Tắt một workflow: mở workflow, bấm **Unpublish**.
- Tắt toàn bộ: `ssh root@<IP>`, rồi `cd /opt/vn-news-monitor && docker compose stop`. Bật lại: `docker compose start`.

## 5. Khi nghiệm thu xong

Trong `VN news - digest`, mở node **Config**, đổi `DRY_RUN: true` thành `DRY_RUN: false`. Bản tin không còn nhãn `[THỬ NGHIỆM]`.

## 6. Bảo mật

- Cổng 5678 chỉ mở trên `127.0.0.1` của máy chủ. Từ Internet không vào được giao diện n8n. Anh vào qua đường hầm SSH.
- Bot chỉ **gửi** tới một chat ID. Workflow không nhận lệnh từ Telegram.
- Khóa API và token chỉ nằm trong credential của n8n, mã hóa bằng `N8N_ENCRYPTION_KEY`.
- Quy định nội bộ của Vietcap về Telegram và AI bên ngoài: anh tự xác nhận (`docs/DECISIONS.md` mục 2).

## 7. Chưa kiểm chứng

| Việc | Trạng thái |
|---|---|
| `install.sh` trên VPS thật | CHƯA KIỂM CHỨNG TRỰC TIẾP. Đã chạy thử trong phiên Claude Code: cài, nhập credential và workflow, khởi động, chạy bảng và bản tin đều đạt (`evidence/p7-van-hanh/install-test.log`) |
| Gửi Telegram thật | CHƯA KIỂM CHỨNG TRỰC TIẾP; cần token và chat ID của anh |
| Cảnh báo tức thời mức ≥ 4 | Chưa làm; bản tin 08:15 và 15:30 đã chạy được |
