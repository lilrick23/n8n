// Chuan hoa tin: URL, ngay gio ICT, doan trich; loai trung trong cung lan chay theo URL chuan hoa.
const cfg = $('Config').first().json;
const sources = Object.fromEntries(cfg.sources.map((s) => [s.id, s]));
const TZ = 'Asia/Ho_Chi_Minh';
const fetchedAt = DateTime.now().setZone(TZ).toISO({ suppressMilliseconds: true });
const TRACKING = /^(utm_.*|fbclid|gclid|zarsrc|ref|source)$/i;

const asText = (v) => {
  if (v === undefined || v === null) return '';
  if (Array.isArray(v)) return asText(v[0]);
  if (typeof v === 'object') return String(v._ ?? '');
  return String(v);
};
const decodeEntities = (s) =>
  s
    .replace(/&nbsp;/g, ' ')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&#(\d+);/g, (_, d) => String.fromCodePoint(Number(d)))
    .replace(/&#x([0-9a-f]+);/gi, (_, h) => String.fromCodePoint(parseInt(h, 16)))
    .replace(/&amp;/g, '&');
const plain = (s) => decodeEntities(s.replace(/<[^>]*>/g, ' ')).replace(/\s+/g, ' ').trim();

// Khong dung lop URL: moi truong chay Code node khong co san (da thay o lan chay thu dau tien).
function cleanUrl(raw) {
  const m = raw.trim().match(/^https?:\/\/([^/?#\s]+)([^?#\s]*)(\?[^#\s]*)?/i);
  if (!m) return null;
  const keep = (m[3] ?? '')
    .slice(1)
    .split('&')
    .filter((p) => p && !TRACKING.test(p.split('=')[0]));
  return `https://${m[1]}${m[2] || '/'}${keep.length ? `?${keep.join('&')}` : ''}`;
}
function canonicalUrl(clean) {
  return clean
    .replace(/^https:\/\/([^/?#]+)/, (_, host) => `https://${host.toLowerCase().replace(/^www\./, '')}`)
    .replace(/\/$/, '');
}
function toIct(raw) {
  if (!raw) return null;
  let d = DateTime.fromRFC2822(raw.trim());
  if (!d.isValid) {
    const js = new Date(raw);
    if (!Number.isNaN(js.getTime())) d = DateTime.fromJSDate(js);
  }
  return d.isValid ? d.setZone(TZ).toISO({ suppressMilliseconds: true }) : null;
}

const seen = new Map();
for (const item of $input.all()) {
  const channel = item.json?.rss?.channel;
  if (!channel) continue; // loi phan tich XML: dem o buoc Tong ket
  const src = sources[asText(channel.n8n_source_id)];
  if (!src) continue;
  const entries = Array.isArray(channel.item) ? channel.item : channel.item ? [channel.item] : [];
  for (const e of entries) {
    const url = cleanUrl(asText(e.link) || asText(e.guid));
    const title = plain(asText(e.title));
    if (!url || !title) continue;
    const canonical = canonicalUrl(url);
    if (seen.has(canonical)) continue;
    seen.set(canonical, {
      source_id: src.id,
      source_name: src.name,
      source_tier: src.tier,
      lang: src.lang,
      title,
      url,
      url_canonical: canonical,
      snippet: plain(asText(e.description)).slice(0, cfg.SNIPPET_MAX_CHARS),
      published_at: toIct(asText(e.pubDate)),
      fetched_at: fetchedAt,
    });
  }
}

const rows = [...seen.values()].sort((a, b) => (b.published_at ?? '').localeCompare(a.published_at ?? ''));
return rows.map((json) => ({ json }));
