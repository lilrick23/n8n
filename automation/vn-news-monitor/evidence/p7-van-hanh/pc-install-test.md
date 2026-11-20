# Thử gói cài trên máy cá nhân (`deploy/pc/`): 2026-11-17

Môi trường: phiên Claude Code, Linux, Docker Compose, image n8n 2.45.0 (mirror.gcr.io, cùng digest với docker.n8n.io).
Thời điểm: 04:26–04:29 UTC (11:26–11:29 ICT).
Tệp ghi đè chỉ dùng trong phiên thử: `network_mode: host` và proxy của môi trường. Trên máy Rick không cần.

Các bước và kết quả:

1. Chép `deploy/pc/{docker-compose.yml,init.mjs,khoa-mau.txt}` và 4 workflow vào một thư mục mới; tạo `khoa.txt` từ biến môi trường (không in khóa).
2. `docker compose up -d`. Log dịch vụ `cai-dat`:
   ```
   [cai-dat] Tim thay chat ID.
   [cai-dat] Successfully imported 2 credentials.
   [cai-dat] news-setup: Successfully imported 1 workflow.
   [cai-dat] news-error-handler: Successfully imported 1 workflow.
   [cai-dat] news-collector: Successfully imported 1 workflow.
   [cai-dat] news-digest: Successfully imported 1 workflow.
   [cai-dat] Da luu khoa ma hoa vao sao-luu/khoa-ma-hoa-n8n.txt. Chep vao noi an toan.
   [cai-dat] Xong. Mo http://localhost:5678
   ```
3. `GET /healthz` trả `{"status":"ok"}`.
4. Qua REST (`scripts/n8n_rest.py`): setup tables execution 1 success; collector execution 2 success (49 s); digest execution 3 success: `items_listed=28, parts=3, parts_sent=3, sent=true, dry_run=true`.
5. Chạy lại `docker compose up -d`: log `[cai-dat] Da cai truoc do. Bo qua.` Workflow không bị ghi đè.
6. Dọn: `docker compose down -v`, xóa `khoa.txt` và `sao-luu/`.

Chưa kiểm chứng: Windows và macOS thật, tự khởi động lại sau khi máy khởi động lại.
