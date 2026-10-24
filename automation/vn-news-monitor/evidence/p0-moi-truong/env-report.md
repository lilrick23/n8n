# Báo cáo môi trường — Giai đoạn 0

Thời điểm thu thập: 2026-10-22 04:31–04:41 UTC (11:31–11:41 ICT). Log gốc: `env-raw.log`.

## Phiên bản

| Thành phần | Giá trị | Nguồn |
|---|---|---|
| Hệ điều hành | Ubuntu 24.04.5 LTS, kernel 6.18.44, x86_64 | `env-raw.log` |
| Node.js trên máy phiên | v22.22.0 (**thấp hơn** yêu cầu ≥ 24 của n8n 2.45) | `env-raw.log`, `npm view n8n@2.45 engines` |
| pnpm | 12.4.2 | `env-raw.log` |
| n8n trong repo | 2.45.0 (`packages/cli/package.json`) | `env-raw.log` |
| n8n dùng để thử | **2.45.0**, image `mirror.gcr.io/n8nio/n8n:2.45.0`, digest `sha256:2797383b01f7…` | `docker-pull.log`, `n8n-start.log` |
| Node.js trong image n8n | v26.10.0 | `n8n-start.log` |
| Docker | 29.9.1 (daemon phải tự khởi động `dockerd`, ban đầu chưa chạy) | `docker-pull.log` |
| Bộ nhớ / đĩa | 15 GiB RAM; còn khoảng 28 GB đĩa | `env-raw.log` |
| npm dist-tags n8n (tra 2026-10-22) | `latest`/`stable` = 2.44.5; `beta`/`next` = 2.45.1 | `npm view n8n dist-tags` |

Ghi chú quan trọng: trên npm, **2.45.x hiện là bản beta**, bản ổn định là 2.44.5. Repo đang ở 2.45.0 nên phần thử dùng 2.45.0 cho khớp tham số node. Khi chạy thật, Rick nên cân nhắc bản `stable` (ghi vào `docs/DECISIONS.md`).

## Truy cập mạng ra ngoài (`egress-test.log`)

| Đích | Kết quả từ máy phiên | Ý nghĩa |
|---|---|---|
| 16 feed RSS CafeF, Vietstock (VN và EN), trang `rss.chn`, `vietstock.vn/rss` | **403** từ proxy (CONNECT bị từ chối) | Không tải được tin thật |
| `api.telegram.org` | **403** | Không gửi thử Telegram được |
| `www.hsx.vn`, `www.hnx.vn`, `ssc.gov.vn`, `news.google.com` | **403** | Không khảo sát được nguồn chính thức |
| `api.anthropic.com` | 404 (kết nối được; 404 là bình thường với đường dẫn gốc) | Gọi API AI được nếu có khóa |
| `registry.npmjs.org`, `nodejs.org`, `hub.docker.com`, `mirror.gcr.io` | 200/401 (kết nối được) | Tải phần mềm được |
| `registry-1.docker.io` (Docker Hub) | Kết nối được nhưng kéo image bị **429 Too Many Requests** | Dùng bản sao Google `mirror.gcr.io` thay thế |

Từ **bên trong container n8n** (không đi qua proxy): RSS và Telegram lỗi `ENOTFOUND` (không phân giải được tên miền); `api.anthropic.com` lỗi chứng chỉ tự ký do proxy chặn giữa. Nếu ở giai đoạn 4 có khóa API, cần chạy container với `NODE_EXTRA_CA_CERTS` trỏ tới bộ CA của proxy (chỉ trong môi trường thử này, không áp dụng cho máy Rick).

## Kết luận

- (i) **Chạy được n8n 2.45.0** bằng Docker (bản sao `mirror.gcr.io`), import và thực thi workflow bằng dòng lệnh: ĐÃ KIỂM CHỨNG (`n8n-start.log`, `n8n-smoke-execute.log`).
- (ii) **Không ra được mạng tới nguồn tin, Telegram, HOSE/HNX/UBCKNN**: ĐÃ KIỂM CHỨNG (`egress-test.log`). Mọi kiểm thử với nguồn thật và Telegram ở trạng thái CHƯA KIỂM CHỨNG TRỰC TIẾP.
- (iii) Kế hoạch kiểm thử: xem `INDEX.md` mục "Kế hoạch kiểm thử".
