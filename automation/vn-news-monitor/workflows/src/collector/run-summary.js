// Tong ket mot lan chay de ghi vao run_log. Node nay nam o nhanh duoi,
// chay sau khi nhanh thu thap xong (executionOrder v1 chay tung nhanh tu tren xuong).
const cfg = $('Config').first().json;
const all = (name) => {
  try {
    return $(name).isExecuted ? $(name).all() : [];
  } catch (e) {
    return [];
  }
};
// 'Luu tin' chay mot lan cho nhanh AI va mot lan cho nhanh khong AI: gom moi lan chay.
const allRuns = (name) => {
  const items = [];
  for (let run = 0; run < 5; run += 1) {
    try {
      const got = $(name).all(0, run);
      if (!got.length && run > 0) break;
      items.push(...got);
    } catch (e) {
      break;
    }
  }
  return items;
};
const xmlItems = all('XML sang JSON');
const fetched = xmlItems.reduce((n, i) => {
  const it = i.json?.rss?.channel?.item;
  return n + (Array.isArray(it) ? it.length : it ? 1 : 0);
}, 0);
const fetchErrors = all('Loi tai feed').map((i) => i.json.source_id);
const xmlErrors = xmlItems.filter((i) => i.json.error).length;
const matched = all('Khop watchlist').filter((i) => i.json.tickers || i.json.topics).length;
const saved = allRuns('Luu tin');
const checked = all('Kiem tra luoc do');
const TZ = 'Asia/Ho_Chi_Minh';

return [{
  json: {
    run_id: String($execution.id),
    workflow: $workflow.name,
    trigger: cfg.trigger,
    started_at: cfg.run_started_at,
    finished_at: DateTime.now().setZone(TZ).toISO({ suppressMilliseconds: true }),
    sources_total: cfg.sources.length,
    sources_ok: all('Gan nguon').length - xmlErrors,
    sources_failed: fetchErrors.length + xmlErrors,
    failed_source_ids: fetchErrors.join(','),
    items_fetched: fetched,
    items_unique: all('Chuan hoa').length,
    items_new: all('Da co trong news_items?').length,
    items_matched: matched,
    items_saved: saved.length,
    items_to_ai: checked.length,
    ai_calls: all('Phan loai AI').filter((i) => !i.json.error).length,
    ai_failures: checked.filter((i) => ['fallback', 'keyword_only'].includes(i.json.classified_by)).length,
    alerts_sent: 0,
    dry_run: cfg.DRY_RUN,
    error: '',
  },
}];
