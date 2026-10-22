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
const xmlItems = all('XML sang JSON');
const fetched = xmlItems.reduce((n, i) => {
  const it = i.json?.rss?.channel?.item;
  return n + (Array.isArray(it) ? it.length : it ? 1 : 0);
}, 0);
const fetchErrors = all('Loi tai feed').map((i) => i.json.source_id);
const xmlErrors = xmlItems.filter((i) => i.json.error).length;
const matched = all('Khop watchlist').filter((i) => i.json.tickers || i.json.topics).length;
const saved = all('Luu tin');
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
    items_to_ai: saved.filter((i) => i.json.classified_by === 'pending_ai').length,
    ai_calls: 0,
    ai_failures: 0,
    alerts_sent: 0,
    dry_run: cfg.DRY_RUN,
    error: '',
  },
}];
