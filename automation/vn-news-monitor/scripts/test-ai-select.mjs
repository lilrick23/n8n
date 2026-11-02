// Checks the 'Chon tin cho AI' Code node outside n8n with synthetic rows (phase 4).
import { readFileSync } from 'node:fs';

const body = readFileSync(new URL('../workflows/src/collector/ai-select.js', import.meta.url), 'utf8');
const DateTime = { now: () => ({ setZone: () => ({ toFormat: () => '2026-11-01' }) }) };
const run = (rows, usedToday) => {
  const $ = (name) => ({
    first: () => ({ json: { MAX_AI_ITEMS_PER_DAY: 10, TIER1_ONLY_AI_SHARE: 0.5 } }),
    all: () => rows.map((json) => ({ json })),
  });
  const $input = { all: () => [{ json: { date: '2026-11-01', items: usedToday } }] };
  return new Function('$', '$input', 'DateTime', body)($, $input, DateTime).map((i) => i.json);
};
const row = (n, matched) => ({ item_id: String(n), tickers: matched ? 'HPG' : '', topics: '', classified_by: 'pending_ai' });
const cases = [
  // 8 tier-1-only rows first, then 4 matched rows; empty day; cap 10, tier-1 share 0.5.
  // Matched rows go first (used = 4); tier-1-only rows go to AI only while used < 5.
  { name: 'matched first, tier-1 only while day total < half cap', rows: [...Array(8)].map((_, i) => row(i, false)).concat([...Array(4)].map((_, i) => row(10 + i, true))), used: 0,
    expect: { ai_matched: 4, ai_tier1: 1, keyword_only: 7 } },
  { name: 'day already at tier-1 share: only matched go to AI', rows: [row(1, false), row(2, true)], used: 5,
    expect: { ai_matched: 1, ai_tier1: 0, keyword_only: 1 } },
  { name: 'cap reached: nothing goes to AI', rows: [row(1, true), row(2, false)], used: 10,
    expect: { ai_matched: 0, ai_tier1: 0, keyword_only: 2 } },
];
let failed = 0;
for (const c of cases) {
  const out = run(c.rows, c.used);
  const got = {
    ai_matched: out.filter((r) => r.classified_by === 'pending_ai' && r.tickers).length,
    ai_tier1: out.filter((r) => r.classified_by === 'pending_ai' && !r.tickers).length,
    keyword_only: out.filter((r) => r.classified_by === 'keyword_only').length,
  };
  const ok = JSON.stringify(got) === JSON.stringify(c.expect) && out.length === c.rows.length
    && out.every((r, i) => r.item_id === c.rows[i].item_id);
  if (!ok) failed += 1;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${c.name}: ${JSON.stringify(got)}`);
}
process.exit(failed ? 1 : 0);
