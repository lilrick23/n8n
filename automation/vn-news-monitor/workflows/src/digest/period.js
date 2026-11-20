// Tinh ky ban tin: tu lan gui truoc (digest_log) toi bay gio, toi da MAX_LOOKBACK_HOURS.
const cfg = $('Config').first().json;
const now = DateTime.fromISO(cfg.now).setZone('Asia/Ho_Chi_Minh');
const logs = $input.all().map((i) => i.json).filter((r) => r.period_end);
const last = logs
  .map((r) => DateTime.fromISO(typeof r.period_end === 'string' ? r.period_end : new Date(r.period_end).toISOString()))
  .filter((d) => d.isValid)
  .sort((a, b) => b.toMillis() - a.toMillis())[0];
let since = last ? last.setZone('Asia/Ho_Chi_Minh') : now.minus({ hours: cfg.DEFAULT_LOOKBACK_HOURS });
const floor = now.minus({ hours: cfg.MAX_LOOKBACK_HOURS });
if (since < floor) since = floor;
return [{ json: {
  since: since.toISO({ suppressMilliseconds: true }),
  until: now.toISO({ suppressMilliseconds: true }),
  since_utc: since.toUTC().toISO(),
} }];
