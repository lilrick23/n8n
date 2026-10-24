// Khop watchlist va chu de vi mo theo docs/DESIGN.md muc 4.
const wl = $('Config').first().json.watchlist;
const strip = (s) =>
  s.normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/đ/g, 'd').replace(/Đ/g, 'D');
const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const B = '(^|[^\\p{L}\\p{N}])';
const E = '($|[^\\p{L}\\p{N}])';
const phrase = (p, flags) => new RegExp(`${B}${escapeRe(p)}${E}`, flags);
const hasDiacritics = (s) => strip(s) !== s;

const tickers = (wl.tickers ?? []).map((t) => ({
  ...t,
  re: new RegExp(`(^|[^A-Za-z0-9])${escapeRe(t.ticker)}($|[^A-Za-z0-9])`, 'u'),
  context: new RegExp(`(\\(${escapeRe(t.ticker)}\\)|(mã|cổ phiếu|CP|ticker)\\s*:?\\s*${escapeRe(t.ticker)}(?![A-Za-z0-9]))`, 'iu'),
  aliases: (t.aliases ?? []).filter((a) => a.length >= 4).map((a) => ({
    alias: a,
    re: phrase(a.normalize('NFC').toLowerCase(), 'u'),
    reStripped: phrase(strip(a).toLowerCase(), 'u'),
  })),
}));
const topics = (wl.macro_topics ?? []).map((t) => ({
  topic: t,
  re: phrase(t.normalize('NFC').toLowerCase(), 'u'),
  reStripped: phrase(strip(t).toLowerCase(), 'u'),
}));
const excludes = (wl.exclude_keywords ?? []).map((k) => phrase(k.normalize('NFC').toLowerCase(), 'u'));

return $input.all().map((item) => {
  const raw = `${item.json.title} ${item.json.snippet}`.normalize('NFC');
  const lower = raw.toLowerCase();
  const lowerStripped = strip(lower);
  const accented = hasDiacritics(raw);
  const foundTickers = [];
  const reasons = [];

  for (const t of tickers) {
    const aliasHit = t.aliases.find((a) => a.re.test(lower) || a.reStripped.test(lowerStripped));
    const codeHit = t.re.test(raw) && (!t.ambiguous || t.context.test(raw) || aliasHit);
    if (codeHit || aliasHit) {
      foundTickers.push(t.ticker);
      reasons.push(codeHit ? `ticker:${t.ticker}` : `alias:${aliasHit.alias}`);
    }
  }
  const foundTopics = [];
  for (const t of topics) {
    // Khop ban co dau truoc; ban khong dau chi dung khi tin viet khong dau.
    if (t.re.test(lower) || (!accented && t.reStripped.test(lowerStripped))) {
      foundTopics.push(t.topic);
      reasons.push(`topic:${t.topic}`);
    }
  }
  const excluded = excludes.some((re) => re.test(lower));
  if (excluded) reasons.push('excluded');

  return {
    json: {
      ...item.json,
      tickers: foundTickers.join(','),
      topics: foundTopics.join(','),
      match_reason: reasons.join(';'),
      excluded,
    },
  };
});
