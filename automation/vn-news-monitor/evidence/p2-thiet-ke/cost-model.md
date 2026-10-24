# Mô hình chi phí AI (giai đoạn 2)

Lập: 2026-10-22, 15:27 ICT. Kết luận: với cấu hình mặc định (phân loại bằng Claude Haiku 5.5, gom 10 tin một lần gọi; bản tin bằng Claude Sonnet 5.5), chi phí ước tính **khoảng 1,2–1,7 USD/tháng**, cả ở kịch bản cao (200 tin/ngày, bằng trần `MAX_AI_ITEMS_PER_DAY`). Khoản lớn nhất là bản tin Sonnet (~1,07 USD/tháng), không phải phân loại.

Nhãn: đơn giá là **ĐÃ KIỂM CHỨNG** (tra trực tiếp trang giá ngày 2026-10-22). Số token mỗi tin và số tin mỗi ngày là **GIẢ ĐỊNH**, đo lại ở giai đoạn 4.

## 1. Công thức

```
Chi phí phân loại/ngày = Σ lượt gọi × [(token vào × giá vào) + (token ra × giá ra)] / 1.000.000

token vào một lượt  = system prompt + lược đồ/công cụ + (số tin trong lô × token mỗi tin)
token ra một lượt   = phần bọc kết quả + token suy nghĩ (nếu có) + (số tin trong lô × token ra mỗi tin)
số lượt gọi/ngày    = làm tròn lên (số tin vào AI mỗi ngày / cỡ lô)
```

Bảng tính chạy lại được: `scripts/cost_model.py` (đổi hằng số ở đầu file rồi chạy `python3 -I scripts/cost_model.py`). Kết quả đầy đủ: [`cost-model-output.md`](cost-model-output.md).

## 2. Đơn giá (USD cho 1 triệu token)

Nguồn: `https://platform.claude.com/docs/en/about-claude/pricing.md`, tra 2026-10-22 bằng WebFetch. Trích đoạn gốc: [`pricing-2026-10-22.txt`](pricing-2026-10-22.txt).

| Mô hình | ID | Giá vào | Giá ra | Ghi chú |
|---|---|---|---|---|
| Claude Haiku 5.5 | `claude-haiku-5-5` | 0,10 | 0,50 | Áp dụng cho prompt ≤ 100.000 token; trên ngưỡng là 0,50/2,50. Hệ thống này luôn dưới ngưỡng |
| Claude Sonnet 5.5 | `claude-sonnet-5-5` | 2 | 10 | |
| Claude Opus 5.5 | `claude-opus-5-5` | 4 | 20 | Không cần cho dự án này |
| Claude Haiku 4.5 | `claude-haiku-4-5` | 1 | 5 | Đắt gấp 10 lần Haiku 5.5, không dùng |

Batch API giảm 50%, nhưng node Anthropic của n8n gọi đồng bộ, không dùng Batch API. Bộ nhớ đệm prompt (prompt caching) chưa tính vào mô hình: node n8n chưa chắc gửi `cache_control` (GIẢ ĐỊNH, kiểm ở giai đoạn 4). Không tính thì kết quả thận trọng hơn.

## 3. Giả định token và lưu lượng

| Tham số | Giá trị | Căn cứ | Nhãn |
|---|---|---|---|
| Tin mới mỗi ngày (15 feed) | ~180 | Cộng `items_last_24h` trong `evidence/p1-nguon/survey.json` (một ngày đo) | ĐÃ KIỂM CHỨNG cho một ngày |
| Tỉ lệ tin khớp watchlist ví dụ | 6/460 (1,3%) | `source-audit.md` | ĐÃ KIỂM CHỨNG với watchlist 4 mã ví dụ |
| Tin vào AI mỗi ngày | thấp 30 / vừa 80 / cao 200 | Watchlist thật dài hơn (20–30 mã) cộng chủ đề vĩ mô; 200 là trần | GIẢ ĐỊNH |
| System prompt | 1.200 token | Rubric tiếng Việt + quy tắc (tiếng Việt tốn token hơn tiếng Anh) | GIẢ ĐỊNH |
| Lược đồ đầu ra | 406 + 700 token | Information Extractor chèn hướng dẫn định dạng JSON vào prompt (`StructuredOutputParser`, đọc mã `InformationExtractor.node.ts` dòng 278), không dùng công cụ. 406 là prompt công cụ của Haiku 5.5 (trang giá), giữ lại làm biên an toàn; 700 = lược đồ JSON | GIẢ ĐỊNH, thận trọng |
| Một tin vào | 300 token | Tiêu đề + đoạn trích ≤ 500 ký tự + mã nguồn | GIẢ ĐỊNH |
| Một tin ra | 180 token | JSON có `summary_vi` ≤ 40 từ, `why_it_matters` ≤ 25 từ | GIẢ ĐỊNH |
| Bản tin | 2 lần/ngày; 40 mục × 80 token + prompt 1.500; ra 1.500 token | Đọc `summary_vi`, không đọc lại bài | GIẢ ĐỊNH |
| Số ngày tính tháng | 22 ngày giao dịch | Quét tối và cuối tuần (DESIGN mục 1.3) thêm ít tin; sai số nhỏ | GIẢ ĐỊNH |

## 4. Ba kịch bản (cấu hình mặc định)

| Kịch bản | Tin vào AI/ngày | Phân loại USD/ngày | Bản tin USD/ngày | Tổng USD/ngày | Tổng USD/tháng |
|---|---|---|---|---|---|
| Thấp | 30 | 0,0044 | 0,0488 | 0,0532 | 1,17 |
| Vừa | 80 | 0,0118 | 0,0488 | 0,0606 | 1,33 |
| Cao | 200 | 0,0296 | 0,0488 | 0,0784 | 1,73 |

## 5. Các nút giảm chi phí và tác động

| Nút | Tác động (kịch bản cao, chỉ phần phân loại) | Mặc định |
|---|---|---|
| Lọc từ khóa/watchlist **trước** AI | Từ ~180 tin xuống 30–80 tin: giảm 55–85% số tin | Bật |
| Gom 10 tin một lần gọi | 0,0801 → 0,0296 USD/ngày (giảm 63%) | Bật |
| Mô hình nhỏ cho phân loại | Sonnet 5.5: 0,5922 → Haiku 5.5: 0,0296 USD/ngày (giảm 95%) | Haiku 5.5 |
| Mô hình lớn hơn chỉ cho bản tin | Sonnet 5.5 cho bản tin 1,07 USD/tháng; đổi sang Haiku 5.5 còn 0,05 USD/tháng | Sonnet 5.5, Rick đổi được |
| Trần `MAX_AI_ITEMS_PER_DAY = 200` | Chặn trên ~0,03 USD/ngày cho phân loại, kể cả khi lọc hỏng | Bật |
| Tắt suy nghĩ mở rộng (Thinking Mode = Disabled) | Nếu để mặc định, Haiku 5.5 có thể tự suy nghĩ; thêm 1.000 token/lượt làm chi phí ×1,34 | Tắt (xem DESIGN mục 5.4) |

## 6. Rủi ro làm sai mô hình

1. **Suy nghĩ tự động.** Node Anthropic 1.6 chỉ gửi `thinking` khi người dùng đặt Thinking Mode. Để trống thì mô hình dùng mặc định của nó (`LmChatAnthropic.node.ts`, dòng ~603). Phải đặt `Disabled` rõ ràng. Nếu Haiku 5.5 từ chối giá trị này, dùng `Adaptive` + `effort = low`. Kiểm ở giai đoạn 4.
2. **Thử lại khi lỗi lược đồ.** Information Extractor dùng `OutputFixingParser`: khi đầu ra sai định dạng, node tự gọi mô hình thêm một lượt để sửa. Cộng với bước kiểm tra lại của ta (PROMPTS giai đoạn 4), một lô lỗi có thể tốn tới 3 lượt. Ở kịch bản cao, kể cả 10% lô lỗi cũng chỉ thêm ~0,006 USD/ngày.
3. **Phí ngoài token.** Không dùng công cụ phía máy chủ (web search), nên không có phí theo lượt.
4. **Định tuyến chỉ ở Mỹ** (`inference_geo`) nhân 1,1 lần. Không dùng.

Việc còn lại: giai đoạn 4 ghi token thật từ phản hồi API vào `ai_usage`, rồi so với bảng này trong `evidence/p4-ai/cost-actual.md`.
