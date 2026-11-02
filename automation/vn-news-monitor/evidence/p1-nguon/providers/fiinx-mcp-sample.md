# FiinX MCP — mẫu gọi thử (từ connector của phiên Claude, không phải từ n8n)

Thời điểm: 2026-10-22 ~08:22 UTC (15:22 ICT). Hàm tìm qua `search_tool_candidates` → `get_tool_detail` → `execute_api`.

| Lần | Mã gọi | Kết quả |
|---|---|---|
| 1 | `get_filings(tickers=["FPT","HPG","VCB","VNM"], report_type="disclosure", start_date="2026-10-01", end_date="2026-10-22")` | 0 dòng |
| 1 | `get_stock_business_news(tickers=["FPT","HPG"], from_date="2026-10-20", to_date="2026-10-22")` | 0 dòng |
| 2 | `get_filings(tickers=["FPT"], report_type="all", start_date="2026-07-01")` | 5 dòng; mới nhất 2026-08-22 (BCTC hợp nhất kiểm toán 6T/2026), có `report_url` PDF trên `cmsv6.fiingroup.vn` |
| 2 | `get_stock_business_news(tickers=["FPT"], from_date="2026-09-01")` | 17 dòng; mới nhất 2026-10-19 14:00, nguồn CafeF, có `source_url` và `short_content` do FiinX tóm tắt |

Nhận xét:
- `get_filings` là kho **tài liệu** (BCTC, báo cáo quản trị), không phải luồng tin công bố theo giờ. Hợp với tra cứu, không hợp với cảnh báo tức thời.
- `get_stock_business_news` trả tin báo chí đã gắn mã, kèm tóm tắt. Trong mẫu, mới nhất trễ 3 ngày so với thời điểm gọi (một lần quan sát; có thể do không có tin mới).
- Gọi qua sandbox Python của FiinX; n8n không gọi trực tiếp được kiểu này. Cần kiểm tra FiinX có MCP endpoint dùng được từ node MCP Client của n8n không, hoặc có API REST riêng theo thuê bao FiinXPro.
