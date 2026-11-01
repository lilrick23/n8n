// Chon tin vao AI trong han muc ngay (MAX_AI_ITEMS_PER_DAY, dem theo ngay ICT trong ai_usage).
// Tin khop watchlist/vi mo duoc uu tien. Tin chi vi nguon tier 1 chi vao AI khi tong da dung
// trong ngay < TIER1_ONLY_AI_SHARE * han muc, nen tin khop luon con it nhat phan con lai.
// Tin vuot han muc chuyen sang keyword_only: van luu, khong goi AI.
const cfg = $('Config').first().json;
const today = DateTime.now().setZone('Asia/Ho_Chi_Minh').toFormat('yyyy-MM-dd');
const usage = $input.all().map((i) => i.json).find((u) => u.date === today) ?? {};
const cap = Number(cfg.MAX_AI_ITEMS_PER_DAY) || 0;
const tier1Cap = Math.floor(cap * (Number(cfg.TIER1_ONLY_AI_SHARE) || 0));
let used = Number(usage.items) || 0;

const rows = $('Dinh dang dong').all().map(({ json }) => ({ ...json }));
const isMatched = (r) => r.tickers !== '' || r.topics !== '';
const pending = rows.filter((r) => r.classified_by === 'pending_ai');
for (const r of [...pending.filter(isMatched), ...pending.filter((x) => !isMatched(x))]) {
  const limit = isMatched(r) ? cap : tier1Cap;
  if (used < limit) {
    used += 1;
  } else {
    r.classified_by = 'keyword_only';
    r.needs_human_check = true;
  }
}
return rows.map((json) => ({ json }));
