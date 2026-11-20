// Gom tin can AI thanh lo AI_BATCH_SIZE tin, dung van ban dau vao theo DESIGN 5.2.
// Noi dung tin duoc thay < > " de tin khong the dong the gia.
let cfg = {};
try {
  cfg = $('Config').first().json;
} catch (e) {
  // Workflow danh gia khong co node Config: dung mac dinh.
}
const size = Number(cfg.AI_BATCH_SIZE) || 10;
const typeOf = Object.fromEntries((cfg.sources ?? []).map((s) => [s.id, s.type]));
const esc = (s) => String(s ?? '').replace(/</g, '‹').replace(/>/g, '›').replace(/"/g, '”');
const HEADER = 'Mã và chủ đề trong watchlist đã khớp được ghi ở từng tin. Phân loại các tin sau.';

const rows = $input.all().map((i) => i.json);
const out = [];
for (let b = 0; b < rows.length; b += size) {
  const batch = rows.slice(b, b + size);
  // id ngan 6 ky tu; neu trung trong lo thi keo dai.
  let len = 6;
  while (new Set(batch.map((r) => String(r.item_id).slice(0, len))).size < batch.length) len += 2;
  const ids = batch.map((r) => String(r.item_id).slice(0, len));
  const parts = batch.map((r, k) => {
    const khop = [r.tickers && `ticker:${r.tickers}`, r.topics && `chu_de:${r.topics}`]
      .filter(Boolean).join(';') || 'khong';
    const loai = r.source_type ?? typeOf[r.source_id] ?? 'press';
    return `<tin id="${ids[k]}" nguon="${esc(r.source_id)}" loai_nguon="${esc(loai)}" khop="${esc(khop)}">\n`
      + `<tieu_de>${esc(r.title)}</tieu_de>\n<trich_doan>${esc(r.snippet)}</trich_doan>\n</tin>`;
  });
  out.push({ json: { batch_no: out.length + 1, ids, rows: batch, text: `${HEADER}\n\n${parts.join('\n')}` } });
}
return out;
