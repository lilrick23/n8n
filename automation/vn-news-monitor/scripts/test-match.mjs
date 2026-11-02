#!/usr/bin/env node
// Run workflows/src/collector/match-watchlist.js (the Code node body) on fixtures/match/match-cases.jsonl.
// Usage: node scripts/test-match.mjs   (exit code 1 when a case fails). No external packages.
import { readFileSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const body = readFileSync(join(ROOT, 'workflows/src/collector/match-watchlist.js'), 'utf8');
const wl = JSON.parse(readFileSync(join(ROOT, 'config/watchlist.example.json'), 'utf8'));
const cases = readFileSync(join(ROOT, 'fixtures/match/match-cases.jsonl'), 'utf8').trim().split('\n').map((l) => JSON.parse(l));

const $ = () => ({ first: () => ({ json: { watchlist: wl } }) });
const $input = { all: () => cases.map((c) => ({ json: { title: c.title, snippet: c.snippet } })) };
const out = new Function('$', '$input', body)($, $input);

let failed = 0;
cases.forEach((c, i) => {
  const got = out[i].json;
  const ok = got.tickers === c.tickers && got.topics === c.topics && got.excluded === Boolean(c.excluded);
  if (!ok) failed++;
  console.log(`${ok ? 'PASS' : 'FAIL'} ${c.case}: tickers=[${got.tickers}] topics=[${got.topics}] excluded=${got.excluded}` +
    (ok ? '' : ` | expected tickers=[${c.tickers}] topics=[${c.topics}] excluded=${Boolean(c.excluded)}`));
});
console.log(`\n${cases.length} case(s), ${failed} failed`);
process.exit(failed ? 1 : 0);
