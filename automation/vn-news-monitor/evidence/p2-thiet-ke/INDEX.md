# Bằng chứng giai đoạn 2 — Thiết kế

Phiên: 2026-10-22, 08:22–08:45 UTC (15:22–15:45 ICT).
Kết quả: **ĐẠT.** `docs/DESIGN.md` có đủ 9 mục theo PROMPTS giai đoạn 2. Mọi con số có nguồn hoặc nhãn `GIẢ ĐỊNH`. Giai đoạn này là tài liệu thiết kế: chưa dựng hay chạy workflow nào.

## Khẳng định và bằng chứng

| # | Khẳng định | Nhãn | Bằng chứng | Lệnh / cách làm | Thời điểm (UTC / ICT) |
|---|---|---|---|---|---|
| 1 | Đơn giá Anthropic: Haiku 5.5 0,10/0,50 USD mỗi triệu token (prompt ≤ 100.000 token), Sonnet 5.5 2/10, Opus 5.5 4/20, Haiku 4.5 1/5; Batch API giảm 50% | ĐÃ KIỂM CHỨNG | `pricing-2026-10-22.txt` | WebFetch `https://platform.claude.com/docs/en/about-claude/pricing.md` | 08:24 / 15:24 |
| 2 | Chi phí cấu hình mặc định ~1,17–1,73 USD/tháng cho 30–200 tin vào AI mỗi ngày | Phép tính ĐÃ KIỂM CHỨNG; số token và lưu lượng GIẢ ĐỊNH | `cost-model.md`, `cost-model-output.md`, `cost-model-run.log` | `python3 -I scripts/cost_model.py` | 08:27 / 15:27 |
| 3 | RSS Read không đặt thời gian chờ cho yêu cầu HTTP | ĐỌC MÃ | `packages/nodes-base/nodes/RssFeedRead/GenericFunctions.ts` (khối `requestOptions` không có `timeout`) | đọc mã | 08:23 / 15:23 |
| 4 | Tùy chọn batching của Information Extractor vẫn gọi mô hình một lần cho mỗi tin; node dùng `StructuredOutputParser` + `OutputFixingParser` (tự gọi thêm một lượt khi đầu ra sai định dạng) | ĐỌC MÃ | `packages/@n8n/nodes-langchain/nodes/chains/InformationExtractor/InformationExtractor.node.ts` dòng 258–300 | đọc mã | 08:31 / 15:31 |
| 5 | Node Anthropic 1.6 bỏ `temperature` với mô hình Claude mới; chỉ gửi `thinking` khi người dùng đặt Thinking Mode, để trống thì mô hình dùng mặc định của nó | ĐỌC MÃ | `packages/@n8n/nodes-langchain/nodes/llms/LMChatAnthropic/LmChatAnthropic.node.ts` dòng 95–110 và 590–640 | đọc mã | 08:25 / 15:25 |
| 6 | Data Table giới hạn mặc định 200 MB cho cả máy, cảnh báo ở 80% | ĐỌC MÃ | `packages/@n8n/config/src/configs/data-table.config.ts` | đọc mã | 08:40 / 15:40 |
| 7 | Node MCP Client gọi được một công cụ MCP cụ thể với tham số nhập tay hoặc JSON | ĐỌC MÃ; gọi SSI từ n8n: CHƯA KIỂM CHỨNG TRỰC TIẾP | `packages/@n8n/nodes-langchain/nodes/mcp/McpClient/McpClient.node.ts` | đọc mã | 08:31 / 15:31 |
| 8 | Giờ giao dịch HOSE/HNX dùng để đặt lịch | GIẢ ĐỊNH (nguồn thứ cấp) | `docs/DESIGN.md` mục 1.3 | tìm kiếm web | trong phiên |
| 9 | Phải quét cuối tuần: khoảng nghỉ thứ Sáu → thứ Hai ~63 giờ, feed nhanh nhất giữ ~20,5 giờ | ĐÃ KIỂM CHỨNG cho số đo một ngày | `evidence/p1-nguon/survey.json` (`window_hours`) | — | — |

## Các điểm cần kiểm ở giai đoạn sau

| Điểm | Giai đoạn |
|---|---|
| XML node đọc được cả 16 fixture (BOM, CDATA, năm 2 chữ số); nếu không, quay lại RSS Read | 3 |
| Cú pháp cron của các lịch trong DESIGN mục 1.3 | 3 |
| `rowNotExists` chạy lại cùng fixture cho 0 tin mới | 3, 6 |
| Haiku 5.5 có nhận `Thinking Mode = Disabled` không; token thật mỗi lô | 4 |
| Độ trễ thật của SSI MCP qua 5 ngày; cách n8n xác thực với SSI MCP | 5, 6 |
| Đếm 4096 ký tự trên bản tin dài gấp 3 lần | 5 |
