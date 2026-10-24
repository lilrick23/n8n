# Khảo sát nguồn tin — Giai đoạn 1

Thời điểm tải: 2026-10-22, 07:53–08:03 UTC (14:53–15:03 ICT, ngày thứ Năm, trong phiên chiều).
Số liệu bên dưới là **ảnh chụp một thời điểm**, không phải trung bình dài hạn. Tần suất đăng nên đo lại sau vài ngày chạy thật.

## 1. Kết luận

- **Cả 16 feed báo chí đều tải được (HTTP 200, XML hợp lệ, ngày giờ có múi giờ +0700).** Giữ 14, tạm tắt 1 (tiếng Anh; Rick đã chọn bật lúc 15:20 ICT, xem mục 6), bỏ 1 (feed tiếng Anh về kết quả kinh doanh, chậm gần 4 tuần). `ĐÃ KIỂM CHỨNG`.
- **n8n 2.45.0 đọc được feed thật** bằng node RSS Read: 5 feed đại diện trả đủ 170 mục, ngày giờ quy đổi đúng về ICT, kể cả kiểu năm 2 chữ số của CafeF. `ĐÃ KIỂM CHỨNG` (`n8n-live/n8n-rss-live.log`).
- **Nguồn công bố thông tin chính thức: chưa có cách lấy tự động hợp lệ.** Không tìm thấy RSS hay API công khai của HOSE, HNX, UBCKNN. Không viết trình thu thập dựa vào API nội bộ của các trang này. Phương án: dùng feed "Giao dịch nội bộ", "Niêm yết", "Cổ tức", "Tăng vốn, M&A" của Vietstock làm tín hiệu, Rick đối chiếu trang chính thức trước khi dùng. `CHƯA KIỂM CHỨNG TRỰC TIẾP` cho HNX (không kết nối được).
- **Google News RSS: bỏ.** `robots.txt` chặn đường dẫn `/rss` với mọi bot. `ĐÃ KIỂM CHỨNG`.
- **Chu kỳ quét 30 phút là đủ** trong giờ giao dịch: feed nhanh nhất đăng khoảng 2,8 mục/giờ, mỗi feed giữ 20–50 mục. Rủi ro thật nằm ở **thời gian n8n ngừng chạy**: feed nhanh nhất chỉ phủ khoảng 20 giờ, nên tắt máy qua đêm hoặc cuối tuần sẽ mất tin. `ĐÃ KIỂM CHỨNG` cho số đo; đề xuất xử lý ở giai đoạn 2 là `GIẢ ĐỊNH`.

## 2. Bảng khảo sát 16 feed báo chí

Cột: **n** = số mục trong feed; **Phủ (giờ)** = khoảng cách giữa mục mới nhất và cũ nhất; **/giờ** = số mục đăng trong 09:00–15:00 ICT ngày gần nhất chia 6; **24h** = số mục trong 24 giờ tính từ mục mới nhất.
Mọi feed: mã hóa UTF-8; có đủ `title`, `link`, `guid`, `pubDate`, `description`; `guid` trùng `link`; **không** có tham số theo dõi (`utm_*`...); `description` chứa HTML (ảnh) nên dùng trường `contentSnippet` n8n đã bóc thẻ.

| source_id | HTTP / Content-Type | n | Mới nhất (ICT) | Phủ (giờ) | 24h | /giờ | Link | Đoạn trích (ký tự, trung vị / tối đa) | Kết luận |
|---|---|---|---|---|---|---|---|---|---|
| cafef-chungkhoan | 200 `text/xml` | 50 | 22/10 13:42 | 27,6 | 33 | 1,3 | https | 145 / 322 | **Giữ.** Lẫn tin giá vàng, tin chung |
| cafef-doanhnghiep | 200 `text/xml` | 50 | 22/10 14:47 | 30,7 | 33 | 2,2 | https | 209 / 339 | **Giữ.** Lẫn tin ngoài thị trường |
| cafef-taichinh-nganhang | 200 `text/xml` | 50 | 22/10 14:39 | 50,0 | 21 | 1,3 | https | 237 / 425 | **Giữ.** Trùng nhiều với vietstock-nganhang |
| cafef-vimo | 200 `text/xml` | 50 | 22/10 14:50 | 42,3 | 31 | 2,7 | https | 181 / 424 | **Giữ** |
| vietstock-cophieu | 200 `application/rss+xml` | 20 | 22/10 14:07 | 49,2 | 9 | 0,7 | http | 258 / 443 | **Giữ.** Chung 5 URL với nhandinh |
| vietstock-giaodichnoibo | 200 `application/rss+xml` | 20 | 20/10 07:42 | 303,6 (12,6 ngày) | 3 | 0 | http | 165 | **Giữ** |
| vietstock-niemyet | 200 `application/rss+xml` | 20 | 19/10 16:30 | 2.326,9 (~97 ngày) | 1 | 0 | http | 233 | **Giữ** (tần suất rất thấp) |
| vietstock-hoatdongkinhdoanh | 200 `application/rss+xml` | 20 | 22/10 14:02 | 20,5 | 20 | 2,8 | http | 227 | **Giữ.** Feed nhanh nhất, phủ ngắn nhất |
| vietstock-cotuc | 200 `application/rss+xml` | 20 | 21/10 10:11 | 336,4 | 1 | 0,2 | http | 162 | **Giữ** |
| vietstock-tangvon-ma | 200 `application/rss+xml` | 20 | 22/10 10:30 | 210,8 | 3 | 0,2 | http | 243 | **Giữ** |
| vietstock-chinhsach | 200 `application/rss+xml` | 20 | 21/10 21:32 | 1.034,7 (~43 ngày) | 1 | 0 | http | 280 | **Giữ** (tier 2) |
| vietstock-vimo | 200 `application/rss+xml` | 20 | 21/10 21:00 | 194,9 | 4 | 0 | http | 323 | **Giữ** (tier 2) |
| vietstock-nganhang | 200 `application/rss+xml` | 20 | 22/10 12:27 | 50,9 | 8 | 0,5 | http | 297 | **Giữ** (tier 2) |
| vietstock-nhandinh | 200 `application/rss+xml` | 20 | 22/10 14:07 | 162,6 | 5 | 0,2 | http | 221 | **Giữ** (tier 3, ý kiến) |
| vietstock-en-stocks | 200 `application/rss+xml` | 30 | 22/10 13:45 | 318,2 | 5 | 0,3 | https | 136 | **Chờ Rick.** Tắt mặc định |
| vietstock-en-earnings | 200 `application/rss+xml` | 30 | **25/09** 09:30 | 4.801,3 | — | — | https | 203 | **Bỏ.** Chậm gần 4 tuần |

Nguồn số liệu: `survey.json` (do `scripts/survey_rss.py` tính từ file tải về), log gốc `fetch-<source_id>.log`, mẫu thu gọn `fixtures/rss/<source_id>.xml`.

## 3. Nguồn công bố thông tin chính thức

| Nguồn | Truy cập từ phiên | robots.txt | RSS/API công khai | Kết luận |
|---|---|---|---|---|
| HOSE (`www.hsx.vn`) | 200. `hsx.vn` (không www) bị ngắt kết nối | Cho phép tất cả (`Disallow:` rỗng) | Không tìm thấy. Trang chủ là ứng dụng JavaScript; mã trang chỉ trỏ tới các mục `/tin-tuc/tin-to-chuc-niem-yet`, `/tin-tuc/tin-hose`... được nạp qua API nội bộ. Chỉ tải được 80 KB đầu của gói mã 2,4 MB (kết nối bị cắt), nên kết luận "không có RSS" chưa chắc chắn | **Chờ xác minh.** Không dùng API nội bộ. Cần tra điều khoản sử dụng của HOSE hoặc hỏi dịch vụ dữ liệu chính thức |
| HNX (`www.hnx.vn`) | Không kết nối được: lỗi chứng chỉ khi qua proxy; đi thẳng thì 503 | Chưa đọc được | Chưa biết | **Chờ xác minh**, `CHƯA KIỂM CHỨNG TRỰC TIẾP` |
| UBCKNN (`ssc.gov.vn`) | 200 khi bật cookie (không bật thì lặp chuyển hướng) | Không có (404) | Không thấy RSS trên trang cổng; trang dựng bằng Oracle WebCenter, cần JavaScript | **Chờ xác minh** |
| Google News RSS | 200 | Chặn `/rss` với `User-agent: *`; chặn hẳn `anthropic-ai`, `ClaudeBot`, `GPTBot` | Có RSS nhưng robots không cho phép | **Bỏ** |

Bối cảnh (từ báo chí, chưa đọc văn bản gốc): từ 2024, doanh nghiệp niêm yết công bố thông tin "một đầu mối" qua hệ thống của sở nơi niêm yết (HOSE từ 15/8/2024; HNX từ tháng 3/2024). Nghĩa là trang của HOSE/HNX là nơi chính thức cần đối chiếu. Nguồn: [thitruongtaichinhtiente.vn](https://thitruongtaichinhtiente.vn/ap-dung-cong-bo-thong-tin-mot-dau-moi-doi-voi-cac-to-chuc-niem-yet-va-dang-ky-giao-dich-tren-hose-61853.html), [lsvn.vn](https://lsvn.vn/tu-hom-nay-doanh-nghiep-niem-yet-chi-phai-cong-bo-thong-tin-qua-mot-dau-moi-1723688256-a146215.html). Nhãn: `GIẢ ĐỊNH` cho tới khi đọc quy định gốc.

**Phương án thay thế (mặc định):** dùng 4 feed Vietstock "Giao dịch nội bộ", "Niêm yết", "Cổ tức", "Tăng vốn, M&A" làm tín hiệu cho tin loại công bố; workflow gắn nhãn `reported_fact` (báo chí đưa lại), không gắn `official_disclosure`. Bản tin ghi rõ "đối chiếu trang HOSE/HNX". Nếu sau này có kênh chính thức hợp lệ (ví dụ gói dữ liệu của sở, RSS trang IR doanh nghiệp), thêm vào `sources.json`.

## 4. Phát hiện kỹ thuật ảnh hưởng thiết kế (giai đoạn 2)

1. **User-Agent.** CafeF chuyển hướng sang trang "sorry" (HTML) khi User-Agent là `curl/...`, nhưng trả XML khi User-Agent là `rss-parser` (giá trị node RSS Read gửi, `RssFeedRead/GenericFunctions.ts:11`) hoặc chuỗi kiểu trình duyệt. Nếu giai đoạn 2 chọn HTTP Request thay RSS Read (để có timeout), **phải đặt header User-Agent rõ ràng** và kiểm tra Content-Type trả về là XML. Bằng chứng: `user-agent-test.log`.
2. **Ngày giờ.** Mọi feed dùng RFC 822 có `+0700`. CafeF ghi năm 2 chữ số (`Thu, 22 Oct 26 14:51:50 +0700`); n8n trả `isoDate = 2026-10-22T07:58:00.000Z`, đổi sang ICT đúng 14:58. Không cần xử lý riêng, nhưng bước chuẩn hóa nên dùng `isoDate` thay vì tự phân tích `pubDate`.
3. **Chuẩn hóa URL để băm `id`.** Vietstock dùng `http://`, CafeF dùng `https://`. Chuẩn hóa: ép `https`, bỏ `www.`, bỏ `utm_*` (hiện chưa thấy nhưng giữ quy tắc).
4. **BOM UTF-8** ở hai feed tiếng Anh của Vietstock. n8n vẫn đọc được (`vietstock-en-stocks`: 30 mục, không lỗi). Fixture đã bỏ BOM và ghi chú trong dòng đầu.
5. **Thứ tự mục không đảm bảo theo thời gian** (CafeF có mục mới hơn nằm sau). Không dựa vào "mục đầu là mới nhất".
6. **Trùng giữa các nguồn.** Trên 460 mục: 454 URL khác nhau; 5 URL xuất hiện ở cả `vietstock-cophieu` và `vietstock-nhandinh`. Khác nhà xuất bản: 5 cặp tiêu đề gần như giống hệt (độ giống Jaccard ≥ 0,95) và 7 cặp ≥ 0,6, tập trung ở mảng ngân hàng (CafeF ↔ Vietstock). Ví dụ: "VPBank đồng loạt giảm lãi suất cho vay và huy động" có ở cả hai. Kết luận: loại trùng theo URL là bắt buộc; loại trùng theo tiêu đề tương tự (ngưỡng khoảng 0,6–0,8, đã bỏ dấu) đáng làm ở tầng bản tin để không báo một sự kiện hai lần.
7. **Tỉ lệ khớp watchlist.** Với watchlist ví dụ (VNM, FPT, VCB, HPG và tên gọi khác), 6/460 tiêu đề khớp mã, thêm 4 tiêu đề chỉ khớp chủ đề vĩ mô. Bước lọc trước AI sẽ loại khoảng 98% tin, nên chi phí AI phụ thuộc chủ yếu vào watchlist thật của Rick. `GIẢ ĐỊNH` cho watchlist thật.
8. **Độ dài đoạn trích** tối đa 443 ký tự, vừa giới hạn 500 ký tự trong lược đồ.
9. **Thời gian ngừng tối đa chấp nhận được** ≈ 20 giờ (phủ của `vietstock-hoatdongkinhdoanh`). Đề xuất cho giai đoạn 2 (`GIẢ ĐỊNH`): thêm một lần quét buổi tối (ví dụ 20:00) và một lần mỗi ngày cuối tuần, để n8n chạy trên máy luôn bật (liên quan quyết định #6 trong `DECISIONS.md`).

## 5. Việc cần Rick

- Chọn có bật `vietstock-en-stocks` (tin tiếng Anh) không. Mặc định: tắt.
- Nguồn chính thức: nếu Vietcap có quyền truy cập dịch vụ dữ liệu của HOSE/HNX hoặc nhà cung cấp dữ liệu (FiinX, SSI...), cho biết để xem có kênh tự động hợp lệ. Mặc định: dùng feed Vietstock và đối chiếu tay.

## 6. Bổ sung 2026-10-22 15:20 ICT: kênh dữ liệu Rick đề xuất

Rick trả lời: bật tin tiếng Anh; các kênh có thể dùng là Vietcap AI News, SSI MCP, FiinXPro MCP, Vnstock; thử lại HNX nếu được.

| Kênh | Đã thử gì | Kết quả | Hợp với | Kết luận |
|---|---|---|---|---|
| **SSI MCP** (`marketdata_list_company_news`) | Gọi 2 lần từ connector của phiên Claude | Trả **thông báo công bố chính thức** của HOSE và HNX: mã, tiêu đề, `news_source` = HOSE/HNX, link gốc trên `hsx.vn`/`hnx.vn`, file PDF đính kèm, `public_date`, `update_date`, mã loại tin (`indtr` giao dịch nội bộ, `div` cổ tức, `manac` nhân sự, `bod` nghị quyết HĐQT, `eanno` giải trình KQKD...). Lúc 15:20 ICT ngày 22/10, tin mới nhất có `update_date` 21/10 18:00, tức **trễ ít nhất ~21 giờ** | Bản tin tổng hợp hằng ngày, đối chiếu "công bố chính thức" | **Giữ, ưu tiên cao cho nhóm "Công bố chính thức".** Không dùng cho cảnh báo tức thời cho tới khi đo được độ trễ thật qua nhiều ngày |
| **FiinX MCP** | `get_filings`, `get_stock_business_news` qua sandbox | Filings: kho tài liệu (BCTC, báo cáo quản trị), mới nhất của FPT là 22/08. Business news: tin báo chí đã gắn mã, có tóm tắt; mẫu FPT mới nhất 19/10 | Tra cứu tài liệu; làm giàu tin (gắn mã) | **Chờ xác minh.** Gọi bằng mã Python trong sandbox của FiinX, chưa biết n8n gọi được không |
| **Vietcap AI News** (`trading.vietcap.com.vn/ai-news`) | Tải trang, robots.txt | Trang ứng dụng JavaScript (single-spa), nội dung tải bằng API nội bộ sau khi đăng nhập (chưa xác nhận). robots.txt cho phép, `Crawl-delay: 10` | Nguồn nội bộ của công ty Rick | **Chờ Rick.** Không tự gọi API nội bộ. Cách hợp lệ: hỏi bộ phận IT/sản phẩm Vietcap có API hoặc export chính thức cho nhân viên |
| **Vnstock** (`vnstocks.com`) | Đọc giấy phép gói `vnstock3` trên PyPI; xem `vnstock-news` | Giấy phép `vnstock3` 3.2.1: chỉ dùng cá nhân, **cấm tổ chức dùng cho mục đích thương mại** khi chưa có văn bản đồng ý của tác giả. `vnstock-news` (tin doanh nghiệp) chỉ dành cho nhà tài trợ (gói trả phí). Thư viện Python, n8n không chạy trực tiếp được (cần máy chủ Python riêng) | Nghiên cứu cá nhân | **Không dùng trong hệ thống này** trừ khi Rick có văn bản cho phép dùng trong công việc tại Vietcap. Rủi ro tuân thủ cao hơn lợi ích, vì SSI MCP đã có cùng loại dữ liệu |
| **HNX** (thử lại) | `curl` tới `hnx.vn`, `www.hnx.vn` lúc 15:21 ICT | Vẫn lỗi chứng chỉ qua proxy của phiên | — | `CHƯA KIỂM CHỨNG TRỰC TIẾP`. Không cần gấp: SSI MCP đã trả tin công bố HNX kèm link gốc |

**Cách n8n gọi MCP.** n8n 2.45.0 có node **MCP Client** (`@n8n/n8n-nodes-langchain.mcpClient`, phiên bản 1 và 1.1; `packages/@n8n/nodes-langchain/nodes/mcp/McpClient/McpClient.node.ts`). Node này gọi trực tiếp một công cụ (tool) của máy chủ MCP như một bước bình thường, không cần mô hình AI. Xác thực: Bearer, Header, nhiều Header, hoặc **MCP OAuth2**. Đây là cách phù hợp nhất: n8n gọi `marketdata_list_company_news` của SSI MCP theo lịch. Điều kiện còn thiếu: địa chỉ endpoint của SSI MCP và cách cấp quyền cho một máy (n8n) thay vì cho tài khoản Claude của Rick. `CHƯA KIỂM CHỨNG TRỰC TIẾP`.

**Điều khoản.** SSI MCP và FiinX là dịch vụ có thuê bao. Dùng dữ liệu trong công cụ nội bộ có thể bị giới hạn bởi hợp đồng thuê bao. Rick cần xác nhận quyền sử dụng; Claude không giả định là được phép.

Bằng chứng: `providers-probe.log`, `providers/ssi-mcp-sample.json`, `providers/fiinx-mcp-sample.md`.
