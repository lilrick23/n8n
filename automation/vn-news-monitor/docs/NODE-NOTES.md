# Ghi chú node n8n 2.45.0 (đọc từ mã nguồn repo)

Ngày đọc: 2026-10-22. Nguồn: các file `.node.ts` trong `packages/` của repo này (n8n 2.45.0).
Mục đích: viết JSON workflow đúng `type`, `typeVersion` và tên tham số, không dựa vào trí nhớ.
Cột "Trạng thái": ĐÃ KIỂM CHỨNG = đã chạy thật trong n8n 2.45.0 ở giai đoạn 0; ĐỌC MÃ = mới đọc mã nguồn, chưa chạy.

| Node | `type` | `typeVersion` mới nhất | File nguồn | Trạng thái |
|---|---|---|---|---|
| Schedule Trigger | `n8n-nodes-base.scheduleTrigger` | 1.4 | `nodes-base/nodes/Schedule/ScheduleTrigger.node.ts` | ĐỌC MÃ |
| RSS Read | `n8n-nodes-base.rssFeedRead` | 1.2 | `nodes-base/nodes/RssFeedRead/RssFeedRead.node.ts` | ĐỌC MÃ |
| Remove Duplicates | `n8n-nodes-base.removeDuplicates` | 2 | `nodes-base/nodes/Transform/RemoveDuplicates/v2/` | ĐỌC MÃ |
| Data table | `n8n-nodes-base.dataTable` | 1.1 | `nodes-base/nodes/DataTable/DataTable.node.ts` | ĐỌC MÃ |
| Error Trigger | `n8n-nodes-base.errorTrigger` | 1 | `nodes-base/nodes/ErrorTrigger/ErrorTrigger.node.ts` | ĐỌC MÃ |
| Telegram | `n8n-nodes-base.telegram` | 1.2 | `nodes-base/nodes/Telegram/Telegram.node.ts` | ĐỌC MÃ |
| Gmail | `n8n-nodes-base.gmail` | 2.2 (mặc định) | `nodes-base/nodes/Google/Gmail/Gmail.node.ts` | ĐỌC MÃ |
| Information Extractor | `@n8n/n8n-nodes-langchain.informationExtractor` | 1.2 | `@n8n/nodes-langchain/nodes/chains/InformationExtractor/` | ĐỌC MÃ |
| Text Classifier | `@n8n/n8n-nodes-langchain.textClassifier` | 1.1 | `@n8n/nodes-langchain/nodes/chains/TextClassifier/` | ĐỌC MÃ |
| Anthropic Chat Model | `@n8n/n8n-nodes-langchain.lmChatAnthropic` | 1.6 | `@n8n/nodes-langchain/nodes/llms/LMChatAnthropic/LmChatAnthropic.node.ts` | ĐỌC MÃ |
| Manual Trigger | `n8n-nodes-base.manualTrigger` | 1 | `nodes-base/nodes/ManualTrigger/` | ĐÃ KIỂM CHỨNG (`evidence/p0-moi-truong/n8n-smoke-execute.log`) |
| Code | `n8n-nodes-base.code` | 2 | `nodes-base/nodes/Code/Code.node.ts` | ĐÃ KIỂM CHỨNG (như trên) |
| HTTP Request | `n8n-nodes-base.httpRequest` | 4.5 mới nhất; đã thử 4.2 | `nodes-base/nodes/HttpRequest/` | ĐÃ KIỂM CHỨNG chạy được, lỗi mạng trả về item `error` khi `onError = continueRegularOutput` |

## Chi tiết cần nhớ khi viết JSON

### Schedule Trigger (1.4)
- Tham số `rule.interval[]`, mỗi phần tử có `field` ∈ `seconds | minutes | hours | days | weeks | months | cronExpression`.
- Cron: `field: "cronExpression"`, `expression: "<cron>"`. Gợi ý trong mã: `([Second]) [Minute] [Hour] [Day of Month] [Month] [Day of Week]`, tức trường giây là tùy chọn.
  Ví dụ dự kiến (GIẢ ĐỊNH, kiểm ở giai đoạn 3): `*/30 8-16 * * 1-5`.
- Múi giờ lấy từ `this.getTimezone()` (tức `settings.timezone` của workflow, nếu không có thì `GENERIC_TIMEZONE`).
- Từ 1.4 có `misfirePolicy` (mặc định `skip` = bỏ lần chạy bị lỡ) và `misfireGraceSeconds` (0 = theo cấu hình máy). Giữ `skip` để không gửi dồn bản tin cũ sau khi máy ngủ dậy.

### RSS Read (1.2)
- Tham số: `url`, `options.customFields` (danh sách cách nhau dấu phẩy), `options.ignoreSSL`.
- **Không có tùy chọn thời gian chờ (timeout)** trong node. Gửi `User-Agent: rss-parser`. Nếu cần timeout riêng: dùng HTTP Request (có `options.timeout`) để tải XML rồi phân tích bằng node XML hoặc Code. Quyết định ở giai đoạn 2.
- Lỗi một nguồn: dùng `onError: "continueRegularOutput"` (hoặc `continueErrorOutput`) để các nguồn khác vẫn chạy; khi đó đầu ra là `{ "error": "<thông điệp>" }`.

### Remove Duplicates (2)
- `operation: "removeItemsSeenInPreviousExecutions"`, `logic: "removeItemsWithAlreadySeenKeyValues"`, `dedupeValue: "={{ $json.id }}"`.
- `options.scope`: `node` (mặc định) hoặc `workflow`; `options.historySize` mặc định 10000.
- Có thao tác `clearDeduplicationHistory` để xóa lịch sử.
- GIẢ ĐỊNH chưa kiểm: lịch sử có bền qua khởi động lại và giống nhau giữa chạy tay và chạy theo lịch. Kiểm ở giai đoạn 3 và 6.

### Data table (1.1)
- `resource`: `row` hoặc `table`. Thao tác với dòng: `insert`, `get`, `update`, `upsert`, `delete`, `rowExists`, `rowNotExists`.
- `rowNotExists` là phương án loại trùng thay thế: chỉ cho qua tin chưa có trong bảng `news_items`. So sánh với Remove Duplicates ở giai đoạn 2.
- Tham chiếu bảng qua trường `dataTableId` (resource locator).

### Telegram (1.2)
- Nếu không đặt `additionalFields.parse_mode` thì mặc định `Markdown` (xác nhận `Telegram/GenericFunctions.ts`). Phải đặt `parse_mode: "HTML"` và escape `& < >`.
- **Từ 1.1, `appendAttribution` mặc định `true`**: n8n tự chèn dòng "This message was sent automatically with n8n" vào cuối tin. Phải đặt `additionalFields.appendAttribution: false`. Dòng thêm này cũng chiếm chỗ trong giới hạn 4096 ký tự.
- Tin không chứa URL sẽ được tự đặt `disable_web_page_preview = true`.

### Information Extractor (1.2) và Text Classifier (1.1)
- Information Extractor: `text`, `schemaType` (`fromAttributes`, `fromJson`, `manual`), `attributes` hoặc `jsonSchemaExample`/`inputSchema`, `options.systemPromptTemplate`, tùy chọn gom lô (batching) từ 1.1.
- Text Classifier: `inputText`, `categories`, `options.multiClass`, `options.fallback`, `options.includeConfidenceScores`, `options.systemPromptTemplate`, `options.enableAutoFixing`.
- Lựa chọn giữa hai node làm ở giai đoạn 4. Hướng mặc định: Information Extractor với `schemaType = manual` (JSON Schema có enum) vì cần nhiều trường cùng lúc.

### Anthropic Chat Model (1.6)
- `model` là resource locator, danh sách lấy từ API (`searchModels`) nên cần credential để chọn trong giao diện; trong JSON có thể ghi giá trị trực tiếp (`mode: "id"`). Tên mô hình cụ thể chọn ở giai đoạn 4 sau khi tra danh sách và bảng giá hiện hành.
- `options.temperature`, `options.maxTokensToSample`; có chế độ `thinking` (không dùng cho phân loại).
- Phiên bản node cũ (dưới 1.3) chỉ có các mô hình Claude 3.x đã cũ. Dùng 1.6.

## Hành vi đã kiểm chứng ở giai đoạn 0 (n8n 2.45.0, Docker)
- `import:workflow` giữ nguyên `settings.timezone = "Asia/Ho_Chi_Minh"` và đặt `active: false`. Bằng chứng: `evidence/p0-moi-truong/n8n-smoke-execute.log` (phần export).
- Với `GENERIC_TIMEZONE=Asia/Ho_Chi_Minh`, `$now` trong Code node trả `+07:00`, `zoneName = Asia/Ho_Chi_Minh`.
- Lệnh `n8n execute` chạy trong container đang có n8n chạy sẽ báo trùng cổng task broker 5679; thêm `-e N8N_RUNNERS_BROKER_PORT=5690` khi gọi.
- Container không có IPv6: phải đặt `N8N_LISTEN_ADDRESS=0.0.0.0`.
- Đổi `N8N_ENCRYPTION_KEY` khi thư mục dữ liệu đã có khóa cũ: n8n **từ chối khởi động** ("Mismatching encryption keys"). Đây là bằng chứng thực tế cho quy tắc giữ nguyên khóa trong RUNBOOK.

## Hành vi đã kiểm chứng ở giai đoạn 3 (n8n 2.45.0, Docker)
Bằng chứng: `evidence/p3-collector/`.
- **Data Table**: tham chiếu bảng theo tên bằng `dataTableId: { "__rl": true, "mode": "name", "value": "news_items" }`; không cần biết ID bảng. Thao tác tạo bảng (`resource: table`, `operation: create`, `options.createIfNotExists: true`) tạo được bảng kèm cột.
- Data Table có sẵn cột hệ thống `id`, `createdAt`, `updatedAt`: không đặt cột riêng tên `id`.
- Cột kiểu `date` lưu thời điểm tuyệt đối và trả về dạng UTC (`…Z`).
- `rowNotExists` mất ~16–25 ms mỗi tin (424 tin ≈ 7 giây, SQLite).
- `n8n execute` (CLI) **không** dùng được Data Table: báo "Attempted to use Data table node but the module is disabled". Chạy qua máy chủ n8n (giao diện, lịch, hoặc REST).
- **Code node** (bộ chạy JavaScript) không có lớp `URL`; lỗi bị nuốt nếu bọc `try`. Có sẵn `DateTime` (Luxon); `DateTime.fromRFC2822` đọc đúng năm 2 chữ số của CafeF.
- **XML** (1): đầu ra không giữ `pairedItem`, nên `$('Node trước').item` không dùng được sau node này.
- **HTTP Request** (4.2) với `onError: continueErrorOutput`: lỗi 404 đi ra đầu ra thứ hai, item có trường `error`; các nguồn khác chạy bình thường.
- Biểu thức `{{ $json.x.hash('sha256') }}` trong node Set cho SHA-256 dạng hex, trùng với `hashlib.sha256` của Python.
- `executionOrder: v1`: nhánh nằm trên (tọa độ y nhỏ hơn) chạy xong mới tới nhánh dưới.
