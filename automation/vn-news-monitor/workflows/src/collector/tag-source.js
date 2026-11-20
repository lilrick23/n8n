// Gan ma nguon vao chinh van ban XML, vi node XML khong giu lien ket voi item dau vao.
// Bo BOM o dau feed (hai feed tieng Anh co BOM, giai doan 1).
const src = $('Tach nguon').item.json;
let xml = String($json.data ?? '').replace(/^﻿/, '');
const tag = `<n8n_source_id>${src.id}</n8n_source_id>`;
if (/<channel[^>]*>/.test(xml)) {
  xml = xml.replace(/<channel([^>]*)>/, `<channel$1>${tag}`);
}
return { json: { data: xml, source_id: src.id } };
