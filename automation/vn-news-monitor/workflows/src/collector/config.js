// Cau hinh chung cua news-collector. Rick sua o day.
// SOURCES va WATCHLIST duoc tao tu config/sources.json va config/watchlist.example.json
// boi scripts/build_workflows.py. Khong ghi ma khach hang, so tai khoan hay token vao day.
const SOURCES = /*__SOURCES__*/[];
const WATCHLIST = /*__WATCHLIST__*/{};

const TRIGGERS = ['Lich giao dich', 'Lich ngoai gio', 'Chay tay'];
const trigger = TRIGGERS.find((n) => {
  try {
    return $(n).isExecuted;
  } catch (e) {
    return false;
  }
}) ?? '';

return [{
  json: {
    trigger,
    run_started_at: DateTime.now().setZone('Asia/Ho_Chi_Minh').toISO({ suppressMilliseconds: true }),
    sources: SOURCES,
    watchlist: WATCHLIST,
    MAX_ITEMS_PER_RUN: 300,
    MAX_AI_ITEMS_PER_DAY: 200,
    // Phan han muc AI toi da cho tin chi vi nguon tier 1 (khong khop watchlist/vi mo).
    TIER1_ONLY_AI_SHARE: 0.5,
    ALERT_MIN_IMPORTANCE: 4,
    AI_BATCH_SIZE: 10,
    SNIPPET_MAX_CHARS: 500,
    DRY_RUN: true,
    // Chi dung khi kiem thu: tai feed tu may chu tep cuc bo thay cho URL that.
    FEED_BASE_OVERRIDE: /*__FEED_BASE_OVERRIDE__*/'',
  },
}];
