# Hướng dẫn cho Rick: dùng bộ prompt n8n rà soát tin tức

Ngày soạn: 2026-10-22. Đây là trang đọc đầu tiên. Không cần biết lập trình để dùng.

## 1. Bộ này gồm gì

| File | Dùng để làm gì |
|---|---|
| `CLAUDE.md` | Quy tắc thường trực cho phiên Claude Code (ngôn ngữ, quy tắc bằng chứng, an toàn, chuẩn đầu tư–IR). Claude Code tự đọc khi làm trong thư mục này. |
| `docs/PROMPTS.md` | **Prompt khởi động** (mục A, dán vào Claude Code) và kế hoạch 9 giai đoạn (0–8), mỗi giai đoạn có đầu vào, bước làm, tiêu chí hoàn thành, bằng chứng. |
| `docs/DECISIONS.md` | Các điểm bạn cần chọn, đã có mặc định, và danh sách giả định chưa xác minh. |
| `docs/CHECKLIST.md` | Checklist nghiệm thu để bạn kiểm tra kết quả; kèm kịch bản thử 3 ngày. |
| `config/sources.json` | 16 feed tin (CafeF, Vietstock) và 4 nguồn chính thức/quốc tế còn chờ xác minh. |
| `config/watchlist.example.json` | Mẫu danh sách mã và chủ đề theo dõi (mã chỉ là ví dụ). |

## 2. Cách dùng (4 bước)

1. Mở Claude Code trên repo `lilrick23/n8n`, nhánh chứa các file này.
2. Dán nguyên **Prompt khởi động** trong `docs/PROMPTS.md` mục A.
3. Claude Code làm lần lượt giai đoạn 0 đến 8 và báo cáo cuối mỗi giai đoạn theo mẫu mục D. Bạn chỉ cần trả lời khi nó hỏi về đăng nhập, quyết định hoặc chi phí.
4. Cuối cùng đối chiếu `docs/CHECKLIST.md` và đọc `docs/FINAL-REPORT.md`; mỗi khẳng định trong đó phải trỏ được tới một file bằng chứng.

## 3. Thuật ngữ

- **n8n**: phần mềm tự động hóa; bạn ghép các bước (node) thành chuỗi (workflow).
- **Schedule Trigger**: node bắt đầu chuỗi theo lịch (ví dụ mỗi 30 phút).
- **RSS**: định dạng nguồn tin mà báo cung cấp để máy đọc tự động.
- **Credential**: thông tin đăng nhập (khóa API, token bot) lưu trong n8n.
- **Data Table**: bảng dữ liệu có sẵn trong n8n, dùng để nhớ tin đã xử lý.
- **Dry-run / `DRY_RUN`**: chạy thử, chỉ gửi vào kênh thử của bạn.
- **Fixture**: dữ liệu mẫu để kiểm thử khi không có mạng.

## 4. Việc chỉ bạn làm được (đã có mặc định để Claude Code vẫn tiến hành)

1. Cung cấp danh sách mã theo dõi thật (mã, tên gọi khác, ưu tiên A/B). File mẫu chỉ là ví dụ.
2. Chọn nơi chạy n8n lâu dài (n8n Cloud, máy chủ riêng, hoặc máy cá nhân; máy tắt là lỡ lịch).
3. Tạo khóa API của nhà cung cấp AI. Gói chat đăng ký thường không gồm API, tính phí riêng.
4. Tạo bot Telegram qua BotFather và cho Claude Code biết cách nhận token an toàn (đặt trong credential của n8n, không dán vào chat hay repo).
5. Xác nhận quy định nội bộ của Vietcap về việc dùng Telegram, dịch vụ AI và máy chủ ngoài cho nội dung công việc.
6. Duyệt ít nhất 20 dòng của bộ mẫu đánh giá AI.

## 5. Điều cần biết trước khi kỳ vọng

- Các URL RSS đã được tải thử ngày 2026-10-22 (giai đoạn 1): 16/16 feed trả XML hợp lệ; 14 giữ, 1 tắt, 1 bỏ. Xem `evidence/p1-nguon/source-audit.md`.
- **Chưa xác minh** có cách lấy công bố thông tin tự động hợp lệ từ HOSE, HNX, UBCKNN hay không. Nếu không, bản đầu dựa vào báo chí và bạn tự đối chiếu trang chính thức. Hệ thống không viết trình thu thập lách điều khoản.
- Nếu phiên Claude Code cũng bị chặn mạng, các bước kiểm thử với nguồn thật và API AI sẽ mang nhãn `CHƯA KIỂM CHỨNG TRỰC TIẾP` và đi kèm hướng dẫn 5 bước để bạn tự thử. Nhãn này là trung thực, không phải lỗi.
- Bản tin là công cụ nghiên cứu nội bộ. Nó không đảm bảo bắt hết tin và không đưa khuyến nghị đầu tư.
- Thư mục này nằm trong bản sao (fork) mã nguồn n8n để có chỗ tham chiếu tham số node; không sửa mã n8n. Không cần dựng n8n từ mã nguồn: bản phát hành chạy bằng Docker hoặc `npx n8n` là đủ.
