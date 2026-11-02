// Kiem tra dau ra AI (DESIGN 5.4). Khong tin dau ra AI: kiem lai luoc do va ap quy tac cung.
// Moi item vao la ket qua AI cua mot lo, cung thu tu voi node 'Gom lo'.
const MODEL = 'claude-haiku-5-5';
const EVENT = ['kqkd', 'co_tuc', 'phat_hanh_tang_von', 'ma', 'giao_dich_noi_bo', 'nhan_su',
  'niem_yet_huy_niem_yet', 'xu_phat_phap_ly', 'chinh_sach_vi_mo', 'ngan_hang_tin_dung',
  'trai_phieu', 'phan_tich_nhan_dinh', 'khac'];
const ORIGIN = ['official_disclosure', 'reported_fact', 'analyst_opinion', 'rumor'];
const SENT = ['tich_cuc', 'trung_lap', 'tieu_cuc'];
const NO_TICKER_OK = new Set(['chinh_sach_vi_mo', 'ngan_hang_tin_dung']);
// Mau chen lenh trong tieu de/doan trich: gan needs_human_check bat ke AI tra gi.
const INJECTION = /(bỏ qua|bo qua|ignore|disregard|system\s*:|system prompt|hướng dẫn (trước|cho hệ thống)|importance"?\s*[:=]|official_disclosure|‹\/?(tin|tieu_de|trich_doan)|<\/?(tin|tieu_de|trich_doan)|"results"\s*:)/i;

let cfg = {};
try {
  cfg = $('Config').first().json;
} catch (e) {}
const typeOf = Object.fromEntries((cfg.sources ?? []).map((s) => [s.id, s.type]));
// Mo hinh doi khi viet enum co dau ('trung_lập'): bo dau truoc khi so voi danh sach.
const norm = (s) => String(s ?? '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .replace(/đ/g, 'd').replace(/Đ/g, 'D').trim().toLowerCase();
const words = (s) => String(s ?? '').trim().split(/\s+/).filter(Boolean);
const clip = (s, n) => {
  const w = words(s);
  return w.length <= n ? w.join(' ') : `${w.slice(0, n).join(' ')}…`;
};

const batches = $('Gom lo').all();
const out = [];
$input.all().forEach((item, idx) => {
  const batch = batches[idx]?.json;
  if (!batch) return;
  const apiError = item.json?.error ? String(item.json.error.message ?? item.json.error).slice(0, 200) : '';
  const results = Array.isArray(item.json?.output?.results) ? item.json.output.results : [];
  const byId = new Map();
  const extra = [];
  for (const raw of results) {
    const r = raw && typeof raw === 'object'
      ? { ...raw, event_type: norm(raw.event_type), fact_or_opinion: norm(raw.fact_or_opinion), sentiment: norm(raw.sentiment) }
      : raw;
    if (!batch.ids.includes(r?.id) || byId.has(r.id)) extra.push(r?.id);
    else byId.set(r.id, r);
  }
  batch.rows.forEach((row, k) => {
    const r = byId.get(batch.ids[k]);
    const problems = [];
    if (apiError) problems.push('api_error');
    else if (!r) problems.push('missing_id');
    else {
      if (!EVENT.includes(r.event_type)) problems.push('event_type');
      if (!ORIGIN.includes(r.fact_or_opinion)) problems.push('fact_or_opinion');
      if (!SENT.includes(r.sentiment)) problems.push('sentiment');
      if (!Number.isInteger(r.importance) || r.importance < 1 || r.importance > 5) problems.push('importance');
      if (typeof r.summary_vi !== 'string' || typeof r.why_it_matters !== 'string') problems.push('text');
      if (typeof r.needs_human_check !== 'boolean') problems.push('needs_human_check');
    }
    const injected = INJECTION.test(`${row.title} ${row.snippet}`);
    let res;
    if (problems.length) {
      res = {
        event_type: 'khac', fact_or_opinion: 'reported_fact', importance: 3, sentiment: 'trung_lap',
        summary_vi: '', why_it_matters: '', needs_human_check: true,
        // Loi mang/API: chi con khop tu khoa. Sai dinh dang sau khi node da sua mot lan, hoac sai enum: fallback.
        classified_by: apiError && !/format|pars/i.test(apiError) ? 'keyword_only' : 'fallback',
      };
    } else {
      const loai = row.source_type ?? typeOf[row.source_id] ?? 'press';
      let origin = r.fact_or_opinion;
      if (origin === 'official_disclosure' && loai !== 'official') origin = 'reported_fact';
      let importance = r.importance;
      if ((origin === 'analyst_opinion' || origin === 'rumor') && importance > 4) importance = 4;
      if (!row.tickers && !NO_TICKER_OK.has(r.event_type) && importance > 3) importance = 3;
      res = {
        event_type: r.event_type, fact_or_opinion: origin, importance, sentiment: r.sentiment,
        summary_vi: clip(r.summary_vi, 40), why_it_matters: clip(r.why_it_matters, 25),
        needs_human_check: r.needs_human_check || injected, classified_by: `ai:${MODEL}`,
      };
    }
    const { source_type, ...base } = row;
    const json = { ...base, ...res };
    // Chi workflow danh gia co eval_id: giu thong tin chan doan. news_items khong co cot nay.
    if (row.eval_id) {
      Object.assign(json, { ai_raw: r ?? null, ai_problems: problems.join(','), injection_flag: injected,
        batch_extra_ids: extra.join(','), api_error: apiError });
    }
    out.push({ json });
  });
});
return out;
