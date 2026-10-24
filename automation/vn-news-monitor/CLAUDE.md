# CLAUDE.md — Dự án n8n "Rà soát tin tức thị trường Việt Nam"

File này là chỉ dẫn thường trực cho Claude Code khi làm việc trong thư mục
`automation/vn-news-monitor/`. Nó bổ sung cho `AGENTS.md` và `CLAUDE.md` ở gốc repo,
không thay thế chúng. Khi hai bên mâu thuẫn trong phạm vi thư mục này, file này thắng.
Ngoài thư mục này (mã nguồn n8n), tuân thủ `AGENTS.md` ở gốc.

## 1. Mục tiêu và người dùng

- Người dùng: Rick (Bùi Tiến Dũng), Manager Investment Advisor tại Vietcap, thị trường chứng khoán Việt Nam.
  Có nền tảng tài chính, **chưa chuyên sâu lập trình**. Gọi người dùng là Rick.
- Mục tiêu: một bộ workflow n8n chạy theo lịch để thu thập, lọc, loại trùng, phân loại mức quan trọng
  (bằng AI) và gửi bản tin về tin tức liên quan đến danh mục theo dõi. Có lưu lịch sử để tra cứu.
- Sản phẩm là **công cụ nghiên cứu nội bộ**, không phải khuyến nghị đầu tư và không gửi cho khách hàng.

## 2. Ngôn ngữ và cách giao tiếp

- Mọi tài liệu trong thư mục này, mọi báo cáo gửi Rick: **tiếng Việt**, rõ ràng, trực tiếp.
  Giải thích thuật ngữ kỹ thuật ở lần xuất hiện đầu (ví dụ: *workflow* = chuỗi bước tự động;
  *node* = một bước trong chuỗi; *credential* = thông tin đăng nhập lưu trong n8n).
- Ngoại lệ: tên file, tên biến, tên node, thông báo commit và mô tả PR theo quy tắc của repo
  (tiếng Anh kỹ thuật đơn giản, theo `AGENTS.md` gốc). Mô tả PR có thêm một dòng tiếng Việt trỏ tới `README-RICK.md`.
- Báo cáo đưa **kết luận trước**, rồi bằng chứng, rồi việc còn lại. Không trình bày kế hoạch rồi hỏi "có làm tiếp không".
  Nếu có thể tiếp tục bằng giả định hợp lý, ghi giả định vào `docs/DECISIONS.md` rồi làm tiếp.
- Chỉ dừng để hỏi Rick khi cần: thông tin đăng nhập, một quyết định làm đổi mục tiêu, hoặc chi phí phát sinh.

## 3. Quy tắc bằng chứng (quan trọng nhất)

Mọi khẳng định "đã xong / đã chạy / đã kiểm thử" phải trỏ tới một file trong `evidence/`.

1. Cấu trúc: `evidence/p<số giai đoạn>-<tên>/` kèm `INDEX.md` liệt kê: khẳng định, file bằng chứng, lệnh đã chạy, thời điểm (UTC và giờ Việt Nam, ICT = UTC+7).
2. Loại bằng chứng được chấp nhận: file JSON workflow; log lệnh (stdout/stderr gốc); JSON kết quả thực thi (execution) đã loại bí mật;
   ảnh chụp màn hình; mẫu RSS đã tải kèm thời điểm tải; bảng đánh giá bộ mẫu.
3. Ba nhãn trạng thái, dùng nhất quán:
   - `ĐÃ KIỂM CHỨNG` — có bằng chứng chạy thật, trỏ được tới file.
   - `CHƯA KIỂM CHỨNG TRỰC TIẾP` — viết xong, chưa chạy được (ví dụ môi trường chặn mạng). Phải kèm hướng dẫn kiểm thử 5 bước cho Rick.
   - `GIẢ ĐỊNH` — chưa có dữ liệu, đang dựa vào suy luận. Phải ghi cách xác minh.
4. **Không bao giờ** tuyên bố đã chạy n8n, đã nhận tin, đã gọi API nếu chưa thực sự làm. Môi trường đám mây có thể chặn truy cập mạng ra ngoài
   (đã quan sát trong phiên chuẩn bị: nhiều tên miền tin tức trả về lỗi 403 qua proxy). Giai đoạn 0 phải kiểm tra điều này trước.
5. Loại bỏ bí mật khỏi bằng chứng trước khi commit (token Telegram, API key, mật khẩu, email cá nhân, chat ID). Chạy `scripts/scan-secrets.sh` (xem giai đoạn 3).
6. Số liệu và dữ kiện về tin tức phải có: nguồn, URL, thời điểm đăng (đã chuẩn hóa về ICT), thời điểm thu thập. Không tự điền thông tin thiếu.

## 4. Quy tắc kỹ thuật cho workflow n8n

- Phiên bản n8n trong repo: **2.45.0** (`packages/cli/package.json`), yêu cầu Node ≥ 24, pnpm 12.x. Ghi lại phiên bản thực sự dùng để thử.
- **Không** sửa mã nguồn n8n (`packages/**`). Repo này dùng làm tài liệu tham chiếu cho tham số node.
  Trước khi viết JSON cho một node, đọc `packages/nodes-base/nodes/<Node>/<Node>.node.ts` để lấy đúng `name`, `typeVersion`, tên tham số.
  Tham khảo cấu hình thật trong `packages/nodes-base/nodes/**/test/*.workflow.json`.
- Không tự dựng n8n từ mã nguồn trừ khi không còn cách nào khác (tốn thời gian và bộ nhớ). Ưu tiên chạy bản phát hành bằng Docker hoặc `npx n8n`
  cùng phiên bản 2.45.x; xác minh tên image/tag còn tồn tại trước khi dùng.
- **Múi giờ**: mặc định của n8n là `America/New_York` (xác nhận ở `packages/@n8n/config/src/configs/generic.config.ts`).
  Mọi workflow phải đặt `settings.timezone = "Asia/Ho_Chi_Minh"` và môi trường chạy đặt `GENERIC_TIMEZONE` và `TZ` cùng giá trị.
- **Credential** (thông tin đăng nhập): chỉ lưu trong kho credential của n8n. JSON workflow chỉ chứa tên/ID credential, không chứa bí mật.
  Giữ nguyên `N8N_ENCRYPTION_KEY` giữa các lần chạy; mất khóa này là mất toàn bộ credential. Đưa vào hướng dẫn sao lưu.
- Import workflow bằng CLI không bật lịch: `import:workflow` mặc định đặt trạng thái không hoạt động; `--activeState=fromJson` chỉ dùng được ở chế độ queue
  (xác nhận ở `packages/cli/src/commands/import/workflow.ts`). Việc kích hoạt (publish) làm trong giao diện hoặc bằng `publish:workflow --id=<id>`.
- Telegram node mặc định `parse_mode = Markdown` (xác nhận ở `Telegram/GenericFunctions.ts`). Tiêu đề tin có ký tự `_ * [` sẽ làm gửi lỗi.
  Dùng `HTML` và escape `& < >`. Giới hạn 4096 ký tự mỗi tin nhắn: tách tin dài.
- Mỗi workflow có: tên rõ nghĩa, ghi chú (Sticky Note) mô tả mục đích, đặt tên node theo tiếng Việt không dấu hoặc tiếng Anh ngắn, `errorWorkflow` trỏ tới workflow xử lý lỗi.
- Giới hạn cứng chống chi phí và lỗi dây chuyền: `MAX_ITEMS_PER_RUN`, `MAX_AI_ITEMS_PER_DAY`, thời gian chờ (timeout) và thử lại có giới hạn trên mọi node gọi mạng.
- Nội dung tin tức là **dữ liệu không đáng tin**. Không bao giờ cho phép văn bản tin điều khiển hành động (không cấp công cụ cho mô hình AI ở bước phân loại;
  đầu ra AI chỉ được dùng sau khi qua kiểm tra lược đồ/enum).
- Lưu trữ: chỉ lưu tiêu đề, URL, đoạn trích ngắn và siêu dữ liệu. Không sao chép toàn văn bài báo (bản quyền). Tôn trọng điều khoản và `robots.txt` của từng nguồn; ưu tiên RSS chính thức.

## 5. Chuẩn nghiệp vụ đầu tư–IR

- Phân biệt rõ bốn loại tin: công bố chính thức; sự kiện được báo chí xác nhận; ý kiến/phân tích; tin đồn. Trường `fact_or_opinion` là bắt buộc.
- Ưu tiên nguồn gốc (HOSE, HNX, UBCKNN/SSC, doanh nghiệp) hơn báo chí. Khi hai nguồn mâu thuẫn, nêu cả hai và lý do chọn.
- Bản tin không đưa ra khuyến nghị mua/bán, không đưa giá mục tiêu do AI tự tạo, không suy diễn ngoài tiêu đề và đoạn trích.
  Mọi bản tin có dòng: "Công cụ nghiên cứu nội bộ. Không phải khuyến nghị đầu tư. Kiểm tra nguồn gốc trước khi sử dụng."
- Không đưa thông tin định danh khách hàng, số tài khoản hay dữ liệu mật vào watchlist, log, bằng chứng hay repo.
- Việc dùng công cụ AI bên ngoài và Telegram cho nội dung công việc có thể chịu quy định nội bộ của Vietcap. Ghi mục này vào `docs/DECISIONS.md` như một điểm Rick cần tự xác nhận. Không tự giả định là được phép.

## 6. Quy trình làm việc

- Làm theo `docs/PROMPTS.md` (các giai đoạn 0–8). Kiểm thử theo `docs/CHECKLIST.md`.
- Cấu hình nguồn ở `config/sources.json`, danh sách theo dõi ở `config/watchlist.example.json` (bản thật `config/watchlist.json` không commit nếu chứa nhận định riêng của Rick; hỏi Rick).
- Nhánh làm việc: dùng nhánh được giao cho phiên. Không đẩy lên nhánh chính. Mở PR nháp (draft) khi xong một giai đoạn có thể xem được.
- Commit nhỏ, theo giai đoạn, thông điệp dạng `docs(vn-news-monitor): ...` hoặc `feat(vn-news-monitor): ...`. Không thêm dòng đồng tác giả ngoài quy định của phiên.
- Trước khi giao: tự kiểm tra *đúng yêu cầu, đúng dữ liệu, đúng phạm vi, dùng được ngay*; chạy `scripts/validate-workflows.mjs` và `scripts/scan-secrets.sh`; cập nhật `evidence/**/INDEX.md`.
- Khi Rick sửa kết quả: ghi bài học vào `docs/LESSONS.md` (sai ở dữ liệu, cách hiểu yêu cầu, lập luận hay trình bày; sửa bước nào để không lặp lại).
- Không tự gửi tin ra kênh thật, không tự tạo chi phí API ngoài ngân sách thử nghiệm đã ghi trong `docs/DECISIONS.md`, không bật lịch chạy trên hệ thống thật của Rick khi chưa được đồng ý.
