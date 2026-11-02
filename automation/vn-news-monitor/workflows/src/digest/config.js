// Cau hinh news-digest. Rick sua o day.
// TELEGRAM_CHAT_ID: chat nhan ban tin (so, vi du 123456789). De trong thi chi dung ban tin, khong gui.
// Khong commit chat ID that vao repo: dien truc tiep trong n8n.
const TRIGGERS = { 'Ban tin sang': 'sang', 'Ban tin chieu': 'chieu', 'Chay tay': 'tay' };
const trigger = Object.keys(TRIGGERS).find((n) => {
  try {
    return $(n).isExecuted;
  } catch (e) {
    return false;
  }
}) ?? 'Chay tay';

return [{
  json: {
    trigger,
    slot: TRIGGERS[trigger],
    now: DateTime.now().setZone('Asia/Ho_Chi_Minh').toISO({ suppressMilliseconds: true }),
    DRY_RUN: true,
    TELEGRAM_CHAT_ID: /*__CHAT_ID__*/'',
    MIN_IMPORTANCE: 3,
    MAX_LINES: 30,
    MAX_UNCLASSIFIED: 10,
    DEFAULT_LOOKBACK_HOURS: 24,
    MAX_LOOKBACK_HOURS: 72,
    PART_LIMIT: 3900,
    // Neu chua co nguon cong bo chinh thuc (SSI MCP), ban tin ghi ro dieu nay.
    OFFICIAL_SOURCE_CONNECTED: false,
  },
}];
