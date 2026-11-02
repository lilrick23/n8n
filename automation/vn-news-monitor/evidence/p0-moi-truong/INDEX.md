# Bằng chứng giai đoạn 0 — Môi trường

Phiên chạy: 2026-10-22, 04:31–04:42 UTC (11:31–11:42 ICT). Máy: container đám mây của phiên Claude Code (Ubuntu 24.04).
Kết quả: **ĐẠT MỘT PHẦN.** Chạy được n8n; không ra được mạng tới nguồn tin và Telegram.

## Ba câu hỏi của tiêu chí hoàn thành

| Câu hỏi | Trả lời | Nhãn | Bằng chứng |
|---|---|---|---|
| (i) Có chạy được n8n không, bằng cách nào? | Có. Docker, image `mirror.gcr.io/n8nio/n8n:2.45.0` (bản sao của Docker Hub; Docker Hub trả 429). `healthz` = ok sau khoảng 10 giây; `n8n --version` = 2.45.0; import và thực thi workflow bằng CLI thành công. `npx n8n` không dùng được vì Node trên máy là 22, n8n 2.45 cần ≥ 24. | ĐÃ KIỂM CHỨNG | `n8n-start.log`, `docker-pull.log`, `n8n-smoke-execute.log`, `smoke-workflow.json` |
| (ii) Có ra được mạng không? | Không tới nguồn tin: 16/16 feed CafeF/Vietstock, `api.telegram.org`, HOSE, HNX, UBCKNN, Google News đều bị proxy trả 403. Ra được: `api.anthropic.com`, npm, nodejs.org, mirror.gcr.io. Bên trong container n8n: RSS và Telegram lỗi `ENOTFOUND`. | ĐÃ KIỂM CHỨNG | `egress-test.log`, `n8n-smoke-execute.log` (node "Thu tai RSS CafeF") |
| (iii) Kế hoạch kiểm thử cho từng trường hợp | Xem bảng dưới. | — | — |

## Kế hoạch kiểm thử

| Hạng mục | Làm trong phiên này | Nhãn dự kiến | Phần Rick tự thử |
|---|---|---|---|
| Cấu trúc workflow (JSON, kết nối, múi giờ, bí mật) | `scripts/validate-workflows.mjs` | ĐÃ KIỂM CHỨNG được | Không |
| Import vào n8n 2.45.0 | `n8n import:workflow` trong Docker | ĐÃ KIỂM CHỨNG được | Không |
| Chuỗi thu thập, chuẩn hóa, loại trùng, lọc watchlist | Chạy với fixture: phục vụ file XML mẫu qua máy chủ tệp cục bộ trong container (n8n gọi `http://localhost:...`), hoặc `pinData` | ĐÃ KIỂM CHỨNG được, **trên dữ liệu mẫu** | Chạy 1 lần với nguồn thật |
| Mẫu RSS thật (giai đoạn 1) | **Không tải được.** Fixture sẽ do Claude dựng theo cấu trúc RSS chuẩn và gắn nhãn "dữ liệu giả" | CHƯA KIỂM CHỨNG TRỰC TIẾP | Rick tải 16 feed bằng lệnh `curl` có sẵn, hoặc mở phiên với mạng mở rộng (xem mục Việc cần Rick) |
| Nguồn chính thức HOSE/HNX/UBCKNN | Không truy cập được trang, `robots.txt`, điều khoản | CHƯA KIỂM CHỨNG TRỰC TIẾP | Như trên |
| Phân loại AI | Gọi được `api.anthropic.com` về mạng, nhưng **chưa có khóa API** | CHƯA KIỂM CHỨNG TRỰC TIẾP cho tới khi có khóa | Tạo khóa và đặt hạn mức chi tiêu |
| Gửi Telegram | Không tới được `api.telegram.org`. Kiểm phần định dạng (escape HTML, tách 4096 ký tự) bằng Code node và máy chủ giả lập cục bộ | Định dạng: ĐÃ KIỂM CHỨNG được; gửi thật: CHƯA KIỂM CHỨNG TRỰC TIẾP | Tạo bot, gửi thử ở chế độ `DRY_RUN` |
| Chạy theo lịch, khởi động lại (giai đoạn 6) | Làm được trong container (để lịch chạy vài chu kỳ, khởi động lại container) | ĐÃ KIỂM CHỨNG được, với dữ liệu mẫu | 3 ngày chạy song song |

## Phát hiện cần ghi lại (đã chuyển vào `docs/DECISIONS.md` và `docs/NODE-NOTES.md`)

1. Trên npm, n8n 2.45.x đang là bản **beta**; bản ổn định (`latest`) là 2.44.5 (tra 2026-10-22).
2. Telegram node 1.1+ tự chèn dòng quảng cáo "sent automatically with n8n" trừ khi đặt `appendAttribution: false`.
3. RSS Read không có tùy chọn timeout.
4. Đổi `N8N_ENCRYPTION_KEY` trên thư mục dữ liệu cũ làm n8n từ chối khởi động (đã gặp thật ở lần thử 2, `n8n-start.log`).
5. Repo `lilrick23/n8n` là **công khai** (public fork). Mọi thứ commit vào đây, gồm tài liệu và bằng chứng, ai cũng đọc được.

## Lệnh đã chạy (tóm tắt, theo thứ tự)

| Thời điểm UTC | Lệnh | Log |
|---|---|---|
| 04:31:40 | `node -v; pnpm -v; uname -a; docker --version; free -h` … | `env-raw.log` |
| 04:31:55 | `curl -sS -o /dev/null -m 20 -L -w ...` cho 28 URL; `curl $HTTPS_PROXY/__agentproxy/status` | `egress-test.log` |
| 04:32:32 | khởi động `dockerd`; `docker pull n8nio/n8n:2.45.0` → 429 | `docker-pull.log` |
| 04:32:48 | `docker pull mirror.gcr.io/n8nio/n8n:2.45.0` → thành công | `docker-pull.log` |
| 04:33:35 | `docker run ...` lần 1 → lỗi địa chỉ IPv6 `::` | `n8n-start.log` |
| 04:35:48 | lần 2 thêm `N8N_LISTEN_ADDRESS=0.0.0.0` → lỗi lệch khóa mã hóa | `n8n-start.log` |
| 04:39:05 | lần 3, xóa thư mục dữ liệu thử (trống), giữ một khóa cố định → `{"status":"ok"}` | `n8n-start.log` |
| 04:39:36 | `n8n import:workflow`, `n8n execute --id=p0smoke000000001` | `n8n-smoke-execute.log` |
| 04:41:06 | thử mạng từ bên trong container | `egress-test.log` (cuối file) |
| 04:41:37 | `n8n export:workflow` để xác nhận `settings` còn nguyên | `n8n-smoke-execute.log` |

Bí mật: khóa mã hóa thử nghiệm được thay bằng `<redacted-test-key>` trong log; `resumeToken` của execution đã thay bằng `<redacted>`. Không có token, khóa API hay chat ID nào trong thư mục này.
