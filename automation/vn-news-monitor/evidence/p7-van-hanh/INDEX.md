# Giai đoạn 7 (một phần): cài đặt và vận hành

| Khẳng định | Trạng thái | Bằng chứng | Thời điểm |
|---|---|---|---|
| `deploy/install.sh` cài được trên Linux: credential, workflow, khởi động, bảng và bản tin | ĐÃ KIỂM CHỨNG trong phiên Claude Code; VPS thật CHƯA KIỂM CHỨNG TRỰC TIẾP | `install-test.log` | 2026-11-02 |
| Gói `deploy/pc/` (Docker Desktop, `docker compose up -d`) cài được và chạy lại không ghi đè | ĐÃ KIỂM CHỨNG trên Linux; Windows/macOS thật CHƯA KIỂM CHỨNG TRỰC TIẾP | `pc-install-test.md` | 2026-11-17 04:26 UTC (11:26 ICT) |
| `install.sh` ghi chat ID vào workflow bản tin | Sửa 2026-11-17: bản cũ tìm `''`, workflow dựng ra dùng `""`. Bản mới khớp cả hai | `deploy/install.sh` | 2026-11-17 |
