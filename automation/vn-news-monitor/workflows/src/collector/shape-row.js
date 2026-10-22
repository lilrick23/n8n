// Dua item ve dung cac cot cua bang news_items (Data Table tu choi cot la).
// Giai doan 3 chua co AI: tin khop watchlist/vi mo hoac nguon tier 1 duoc danh dau cho AI.
const runId = String($execution.id);
return $input.all().map(({ json: j }) => {
  const forAi = !j.excluded && (j.tickers !== '' || j.topics !== '' || j.source_tier === 1);
  return {
    json: {
      item_id: j.item_id,
      source_id: j.source_id,
      source_name: j.source_name,
      source_tier: j.source_tier,
      lang: j.lang,
      title: j.title,
      url: j.url,
      snippet: j.snippet,
      published_at: j.published_at,
      fetched_at: j.fetched_at,
      tickers: j.tickers,
      topics: j.topics,
      match_reason: j.match_reason,
      event_type: '',
      fact_or_opinion: '',
      importance: j.excluded ? 1 : null,
      sentiment: '',
      summary_vi: '',
      why_it_matters: '',
      needs_human_check: false,
      classified_by: j.excluded ? 'excluded' : forAi ? 'pending_ai' : 'not_matched',
      alert_sent_at: null,
      run_id: runId,
    },
  };
});
