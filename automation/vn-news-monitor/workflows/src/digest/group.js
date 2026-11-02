// Chon tin trong ky, gop tin trung su kien, xep theo muc quan trong.
// Gop theo (ma, loai su kien, ngay): cung su kien tu nhieu bao chi hien thi tren mot dong.
const cfg = $('Config').first().json;
const period = $('Tinh ky').first().json;
const since = DateTime.fromISO(period.since).toMillis();
const until = DateTime.fromISO(period.until).toMillis();
const toDt = (v) => {
  if (!v) return null;
  const d = typeof v === 'string' ? DateTime.fromISO(v) : DateTime.fromJSDate(new Date(v));
  return d.isValid ? d.setZone('Asia/Ho_Chi_Minh') : null;
};
const ORIGIN_RANK = { official_disclosure: 0, reported_fact: 1, analyst_opinion: 2, rumor: 3 };
const rows = $input.all().map((i) => i.json).filter((r) => r.item_id);
const inPeriod = rows.filter((r) => {
  const f = toDt(r.fetched_at);
  return f && f.toMillis() > since && f.toMillis() <= until;
});

const classified = inPeriod.filter((r) => Number(r.importance) >= cfg.MIN_IMPORTANCE && r.classified_by !== 'excluded');
const groups = new Map();
for (const r of classified) {
  const shown = toDt(r.published_at) ?? toDt(r.fetched_at);
  const tickers = String(r.tickers || '').split(',').map((t) => t.trim()).filter(Boolean);
  const key = tickers.length
    ? `${tickers[0]}|${r.event_type}|${shown.toFormat('yyyy-MM-dd')}`
    : `item|${r.item_id}`;
  const g = groups.get(key) ?? { key, tickers, topics: r.topics || '', items: [] };
  g.items.push({ ...r, shown_at: shown.toISO() });
  groups.set(key, g);
}

const lines = [...groups.values()].map((g) => {
  g.items.sort((a, b) => (Number(b.importance) - Number(a.importance))
    || ((ORIGIN_RANK[a.fact_or_opinion] ?? 9) - (ORIGIN_RANK[b.fact_or_opinion] ?? 9)));
  const top = g.items[0];
  const origin = g.items.map((i) => i.fact_or_opinion).sort((a, b) => (ORIGIN_RANK[a] ?? 9) - (ORIGIN_RANK[b] ?? 9))[0];
  let section = { official_disclosure: 'official', reported_fact: 'reported', analyst_opinion: 'opinion', rumor: 'rumor' }[origin] ?? 'reported';
  // Tin khong co ma watchlist: vi mo neu la chinh sach/tin dung hoac khop chu de, con lai la doanh nghiep khac.
  if (!g.tickers.length && (section === 'reported' || section === 'official')) {
    const macro = g.topics || ['chinh_sach_vi_mo', 'ngan_hang_tin_dung'].includes(top.event_type);
    section = macro ? 'macro' : 'other';
  }
  const seen = new Set();
  const sources = g.items.filter((i) => !seen.has(i.source_name) && seen.add(i.source_name))
    .map((i) => ({ name: i.source_name, url: i.url }));
  return {
    section,
    tickers: g.tickers.join(', '),
    importance: Number(top.importance),
    event_type: top.event_type,
    summary: top.summary_vi || top.title,
    title: top.title,
    shown_at: top.shown_at,
    sources,
    needs_human_check: g.items.some((i) => i.needs_human_check === true),
  };
}).sort((a, b) => b.importance - a.importance || String(b.shown_at).localeCompare(String(a.shown_at)));

const listed = lines.slice(0, cfg.MAX_LINES);
// Tin khop ma nhung chua qua AI (vuot han muc hoac loi API): liet ke rieng de khong bo sot.
const unclassified = inPeriod
  .filter((r) => r.tickers && (r.classified_by === 'keyword_only' || r.classified_by === 'fallback' || r.classified_by === 'pending_ai'))
  .slice(0, cfg.MAX_UNCLASSIFIED)
  .map((r) => ({ tickers: r.tickers, title: r.title, url: r.url, source_name: r.source_name,
    shown_at: (toDt(r.published_at) ?? toDt(r.fetched_at)).toISO() }));

// Dau vao cho AI viet diem nhan: chi cac dong muc >= 4, chi dung tom tat da co.
const hi = listed.filter((l) => l.importance >= 4).slice(0, 12);
const aiInput = hi.map((l, n) => `${n + 1}. [${l.tickers || 'vi mo'}] (muc ${l.importance}) ${l.summary}`)
  .join('\n').replace(/</g, '‹').replace(/>/g, '›');

return [{ json: {
  period,
  counts: { in_period: inPeriod.length, eligible: lines.length, listed: listed.length,
    unclassified: unclassified.length, needs_check: listed.filter((l) => l.needs_human_check).length },
  lines: listed,
  unclassified,
  has_highlights: hi.length > 0,
  ai_input: aiInput ? `TOM TAT CAC TIN MUC CAO TRONG KY\n${aiInput}` : '',
} }];
