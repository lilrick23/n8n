// Cong don so lan goi AI, so tin va token trong ngay (ICT) vao bang ai_usage.
// Token la uoc tinh (estimated = true), hieu chinh theo token that do o giai doan 4:
// tieng Viet ~1,3 ky tu/token vao, ~1,9 ky tu/token ra. Xem evidence/p4-ai/cost-actual.md.
const PRICE_IN = 0.10 / 1e6; // USD/token vao, Haiku 5.5, tra ngay 2026-10-22
const PRICE_OUT = 0.50 / 1e6; // USD/token ra
const SYSTEM_TOKENS = 2300; // system prompt + huong dan dinh dang moi lan goi, do o giai doan 4
const CHARS_PER_TOKEN_IN = 1.3;
const CHARS_PER_TOKEN_OUT = 1.9;
const MODEL = 'claude-haiku-5-5';
const cfg = $('Config').first().json;
const TZ = 'Asia/Ho_Chi_Minh';
const today = DateTime.now().setZone(TZ).toFormat('yyyy-MM-dd');
const prev = $('Doc ai_usage').all().map((i) => i.json).find((u) => u.date === today) ?? {};
const batches = $('Gom lo').all();
const ai = $('Phan loai AI').all();
const calls = ai.filter((i) => !i.json.error).length;
const items = $input.all().length;
const tokensIn = Math.round(batches.reduce((n, b) => n + b.json.text.length, 0) / CHARS_PER_TOKEN_IN) + calls * SYSTEM_TOKENS;
const tokensOut = Math.round(ai.reduce((n, i) => n + JSON.stringify(i.json.output ?? '').length, 0) / CHARS_PER_TOKEN_OUT);
const total = {
  calls: (Number(prev.calls) || 0) + calls,
  items: (Number(prev.items) || 0) + items,
  tokens_in: (Number(prev.tokens_in) || 0) + tokensIn,
  tokens_out: (Number(prev.tokens_out) || 0) + tokensOut,
};
const capped = total.items >= Number(cfg.MAX_AI_ITEMS_PER_DAY);
return [{
  json: {
    date: today,
    model: MODEL,
    ...total,
    estimated: true,
    cost_usd_est: Math.round((total.tokens_in * PRICE_IN + total.tokens_out * PRICE_OUT) * 1e6) / 1e6,
    cap_reached_at: prev.cap_reached_at ?? (capped ? DateTime.now().setZone(TZ).toISO({ suppressMilliseconds: true }) : null),
  },
}];
