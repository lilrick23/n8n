// Tach danh sach nguon thanh mot item cho moi nguon.
const cfg = $input.first().json;
return cfg.sources.map((s) => ({
  json: {
    id: s.id,
    name: s.name,
    tier: s.tier,
    lang: s.lang,
    url: cfg.FEED_BASE_OVERRIDE ? `${cfg.FEED_BASE_OVERRIDE}${s.id}.xml` : s.url,
  },
}));
