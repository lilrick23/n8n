// Mot dong cho digest_log: ky, so muc, so phan, da gui hay chua.
const cfg = $('Config').first().json;
const g = $('Chon va nhom').first().json;
const parts = $('Dinh dang').all();
let sent = 0;
let error = '';
try {
  const res = $('Gui Telegram').all();
  sent = res.filter((r) => r.json && (r.json.ok === true || r.json.message_id || r.json.result)).length;
  const bad = res.find((r) => r.json && r.json.error);
  if (bad) error = String(bad.json.error.message ?? bad.json.error).slice(0, 300);
} catch (e) {
  sent = 0;
}
return [{ json: {
  slot: cfg.slot,
  period_start: g.period.since,
  period_end: g.period.until,
  items_in_period: g.counts.in_period,
  items_listed: g.counts.listed,
  parts: parts.length,
  parts_sent: sent,
  sent: parts.length > 0 && sent === parts.length,
  dry_run: cfg.DRY_RUN,
  error: error || (cfg.TELEGRAM_CHAT_ID ? '' : 'chua_co_chat_id'),
  created_at: DateTime.now().setZone('Asia/Ho_Chi_Minh').toISO({ suppressMilliseconds: true }),
} }];
