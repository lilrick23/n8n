// Ghi lai nguon tai loi. Cac nguon khac van chay tiep.
const src = $('Tach nguon').item.json;
const err = $json.error;
const message = typeof err === 'string' ? err : (err?.message ?? JSON.stringify(err ?? $json));
return { json: { source_id: src.id, error: String(message).slice(0, 300) } };
