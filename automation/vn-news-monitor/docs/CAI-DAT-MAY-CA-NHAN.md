# Cài hệ thống tin tức trên máy tính của anh (Windows hoặc macOS)

Cập nhật: 2026-11-17. Viết cho người không lập trình. Làm một lần, khoảng 20 phút.

Hệ thống chạy trong **Docker Desktop**. Docker Desktop là phần mềm chạy các ứng dụng đóng gói sẵn (gọi là *container*) trên máy của anh. n8n chạy bên trong nó.

**Điều kiện để bản tin đến đúng giờ:** máy bật, không ngủ, có Internet, Docker Desktop đang chạy. Máy tắt hoặc ngủ lúc 08:15 thì lỡ bản tin sáng hôm đó. Lần quét tin sau sẽ gom bù tin bị lỡ (tối đa 72 giờ).

## 1. Chuẩn bị

1. **Gói cài đặt.** Tải tệp `vn-news-monitor-may-ca-nhan.zip` Claude gửi. Giải nén vào thư mục **Tài liệu** (Documents). Anh có thư mục `vn-news-monitor`.
2. **Khóa Anthropic API.** Vào console.anthropic.com, mục API keys. Tạo một khóa mới tên `may-ca-nhan`. Ở mục Limits, đặt hạn mức chi tiêu tháng, ví dụ 5 USD.
3. **Token bot Telegram.** Anh đã có bot `@Rickbriefbot`. Lấy lại token: mở `@BotFather`, gửi `/mybots`, chọn bot, bấm **API Token**.

Không dán khóa hay token vào chat với Claude.

## 2. Cài Docker Desktop

1. Tải tại docker.com/products/docker-desktop. Chọn bản cho Windows, hoặc cho Mac (chip Apple hoặc Intel, xem ở menu Apple → Giới thiệu máy Mac này).
2. Cài như phần mềm thường. Windows có thể yêu cầu khởi động lại máy và bật WSL 2: bấm đồng ý.
3. Mở Docker Desktop. Bỏ qua bước đăng nhập nếu được hỏi.
4. Vào **Settings → General**, bật **Start Docker Desktop when you sign in to your computer**. Bấm **Apply**.

## 3. Điền khóa

1. Trong thư mục `vn-news-monitor`, đổi tên tệp `khoa-mau.txt` thành `khoa.txt`.
2. Mở `khoa.txt` bằng Notepad (Windows) hoặc TextEdit (Mac).
3. Dán khóa Anthropic sau `ANTHROPIC_KEY=` và token Telegram sau `TELEGRAM_TOKEN=`. Không thêm dấu cách hay dấu ngoặc. Để trống `CHAT_ID=`.
4. Lưu tệp. Trên Mac, nếu TextEdit hỏi định dạng, chọn **văn bản thuần** (Format → Make Plain Text).

## 4. Chạy cài đặt

1. Mở Telegram, gửi `/start` cho `@Rickbriefbot`. Làm ngay trước bước 3 dưới đây: máy tìm địa chỉ chat của anh từ tin này.
2. Mở cửa sổ lệnh trong thư mục:
   - **Windows:** mở thư mục `vn-news-monitor` trong File Explorer. Bấm vào thanh địa chỉ, gõ `powershell`, nhấn Enter.
   - **Mac:** mở ứng dụng Terminal, gõ `cd ~/Documents/vn-news-monitor`, nhấn Enter.
3. Gõ lệnh sau, nhấn Enter:

   ```
   docker compose up -d
   ```

4. Lần đầu máy tải n8n khoảng 300 MB, mất vài phút. Xong khi thấy `Container ...-n8n-1 Started`.
5. Kiểm tra: gõ `docker compose logs cai-dat`. Dòng cuối phải là `Xong. Mo http://localhost:5678`. Nếu có dòng `Chua thay tin /start`, xem mục 8.

## 5. Bật hệ thống

1. Mở trình duyệt, vào `http://localhost:5678`. Tạo tài khoản quản trị (email và mật khẩu mạnh). Tài khoản này chỉ nằm trên máy anh.
2. Mở workflow `VN news - setup tables`, bấm **Execute workflow** một lần. Bốn bảng dữ liệu được tạo.
3. Mở `VN news - collector`, bấm **Execute workflow**. Chờ khoảng 1 phút. Các bước chuyển xanh là đạt.
4. Mở `VN news - digest`, bấm **Execute workflow**. Telegram của anh nhận bản tin gắn nhãn `[THỬ NGHIỆM]`.
5. Bật lịch: ở `VN news - collector` và `VN news - digest`, bấm **Publish**.

## 6. Việc bảo mật ngay sau khi cài

1. Mở lại `khoa.txt`, xóa khóa sau `ANTHROPIC_KEY=` và `TELEGRAM_TOKEN=`, lưu. Khóa đã nằm trong n8n, được mã hóa.
2. Mở thư mục `sao-luu`, mở `khoa-ma-hoa-n8n.txt`. Chép dòng trong đó vào trình quản lý mật khẩu. Sau đó xóa tệp. Mất khóa này thì mất mọi credential khi cài lại.

## 7. Giữ máy không ngủ

**Windows**

1. Settings → System → Power & battery (Windows 11) hoặc Power & sleep (Windows 10).
2. Ở mục khi cắm sạc (Plugged in), đặt **Sleep** thành **Never**. Màn hình được phép tắt.
3. Laptop: Control Panel → Power Options → Choose what closing the lid does → khi cắm sạc chọn **Do nothing**, nếu anh hay gập máy.

**macOS**

1. System Settings → Battery (laptop) hoặc Energy (máy để bàn).
2. Bật **Prevent automatic sleeping on power adapter when the display is off**.
3. Laptop Mac gập nắp sẽ ngủ, trừ khi nối màn hình ngoài. Để máy mở nắp khi cần nhận bản tin.

## 8. Khi có sự cố

| Hiện tượng | Cách xử lý |
|---|---|
| Log có `Chua thay tin /start` | Gửi `/start` cho bot. Mở `http://localhost:5678`, workflow `VN news - digest`, node **Config**, điền chat ID vào `TELEGRAM_CHAT_ID`. Hoặc nhờ Claude hướng dẫn lấy chat ID |
| `docker: command not found` hoặc `cannot connect` | Docker Desktop chưa mở. Mở Docker Desktop, chờ biểu tượng cá voi ngừng nhấp nháy, chạy lại lệnh |
| Không vào được `localhost:5678` | Gõ `docker compose ps` trong thư mục. Nếu n8n không ở trạng thái `running`, gõ `docker compose up -d` |
| Không nhận bản tin sáng | Máy có ngủ lúc 08:15 không? Xem lịch sử ở mục **Executions** trong n8n |

## 9. Tắt và bật

- Tạm dừng một workflow: mở workflow, bấm **Unpublish**.
- Tắt toàn bộ: trong thư mục, gõ `docker compose stop`. Bật lại: `docker compose start`.
- Khi máy khởi động lại: Docker Desktop tự mở, n8n tự chạy lại. Không cần làm gì.

## 10. Khi nghiệm thu xong

Trong `VN news - digest`, node **Config**, đổi `DRY_RUN: true` thành `DRY_RUN: false`. Bản tin không còn nhãn `[THỬ NGHIỆM]`.

## 11. Trạng thái kiểm chứng

| Việc | Trạng thái |
|---|---|
| Gói cài đặt chạy bằng `docker compose up -d`: nhập 2 credential, 4 workflow, tìm chat ID, lưu khóa mã hóa; chạy lại thì bỏ qua | ĐÃ KIỂM CHỨNG trên Linux trong phiên Claude Code (`evidence/p7-van-hanh/pc-install-test.md`) |
| Gửi bản tin thật tới Telegram của anh | ĐÃ KIỂM CHỨNG 2026-11-17 (`evidence/p5-digest/telegram-live/run-log.md`) |
| Cài trên Windows và macOS thật | CHƯA KIỂM CHỨNG TRỰC TIẾP. Cách kiểm: làm mục 4 và 5; đạt khi bản tin `[THỬ NGHIỆM]` đến Telegram |
| Tự chạy lại sau khi khởi động lại máy | CHƯA KIỂM CHỨNG TRỰC TIẾP. Cách kiểm: khởi động lại máy, mở `http://localhost:5678` sau 2 phút |
