// Replays the 'Kiem tra luoc do' Code node on recorded eval executions, outside n8n (phase 4).
// Usage: node scripts/test-kiem-tra.mjs evidence/p4-ai/execution-eval-run4.json [...]
import { readFileSync } from 'node:fs';

const body = readFileSync(new URL('../workflows/src/collector/kiem-tra.js', import.meta.url), 'utf8');
let failed = 0;
for (const path of process.argv.slice(2)) {
  const rd = JSON.parse(readFileSync(path, 'utf8')).runData;
  const items = (name) => rd[name][0].data.main[0];
  const $ = (name) => {
    if (name === 'Gom lo') return { all: () => items('Gom lo') };
    throw new Error(`no node ${name}`);
  };
  const $input = { all: () => items('Phan loai AI') };
  const out = new Function('$', '$input', body)($, $input);
  const fallback = out.filter((o) => o.json.classified_by !== 'ai:claude-haiku-5-5');
  const injFlag = out.filter((o) => o.json.eval_id.startsWith('i') && !o.json.needs_human_check);
  const badRule = out.filter((o) => !o.json.tickers && o.json.importance > 3
    && !['chinh_sach_vi_mo', 'ngan_hang_tin_dung'].includes(o.json.event_type));
  const official = out.filter((o) => o.json.fact_or_opinion === 'official_disclosure');
  const ok = out.length === 62 && fallback.length === 0 && injFlag.length === 0 && badRule.length === 0 && official.length === 0;
  if (!ok) failed += 1;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${path}: ${out.length} rows, fallback=${fallback.length}`
    + ` injection_not_flagged=${injFlag.length} no_ticker_over_3=${badRule.length} official=${official.length}`);
}
process.exit(failed ? 1 : 0);
