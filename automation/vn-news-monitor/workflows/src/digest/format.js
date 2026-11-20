// Dung ban tin HTML cho Telegram va tach thanh nhieu phan <= PART_LIMIT ky tu.
// Khong bao gio cat giua mot khoi, nen khong cat giua the <a> hay URL (docs/DESIGN.md muc 7.3).
const cfg = $('Config').first().json;
const g = $('Chon va nhom').first().json;
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const escAttr = (s) => esc(s).replace(/"/g, '&quot;');
const fmtTime = (iso) => DateTime.fromISO(iso).setZone('Asia/Ho_Chi_Minh').toFormat('HH:mm dd/MM');
const LABEL = { sang: 'Bản tin trước giờ mở cửa', chieu: 'Bản tin sau giờ đóng cửa', tay: 'Bản tin chạy tay' };
const EVENT = { kqkd: 'KQKD', co_tuc: 'Cổ tức', phat_hanh_tang_von: 'Phát hành/tăng vốn', ma: 'M&A',
  giao_dich_noi_bo: 'Giao dịch nội bộ', nhan_su: 'Nhân sự', niem_yet_huy_niem_yet: 'Niêm yết',
  xu_phat_phap_ly: 'Pháp lý', chinh_sach_vi_mo: 'Chính sách', ngan_hang_tin_dung: 'Tín dụng',
  trai_phieu: 'Trái phiếu', phan_tich_nhan_dinh: 'Nhận định', khac: 'Khác' };
const DISCLAIMER = '<i>Công cụ nghiên cứu nội bộ. Không phải khuyến nghị đầu tư. Kiểm tra nguồn gốc trước khi sử dụng.</i>';

const until = DateTime.fromISO(g.period.until).setZone('Asia/Ho_Chi_Minh');
const blocks = [];
blocks.push(`${cfg.DRY_RUN ? '<i>[THỬ NGHIỆM]</i>\n' : ''}<b>${LABEL[cfg.slot] ?? LABEL.tay} · ${until.toFormat('dd/MM/yyyy HH:mm')}</b>\n`
  + `Kỳ: ${fmtTime(g.period.since)} → ${fmtTime(g.period.until)} · ${g.counts.in_period} tin mới, ${g.counts.eligible} tin mức ≥ ${cfg.MIN_IMPORTANCE}`);

// Diem nhan do AI viet (neu co). AI loi hoac khong co tin muc cao thi bo qua muc nay.
let highlights = [];
try {
  const out = $('Viet diem nhan').first().json.output;
  if (out && Array.isArray(out.diem_nhan)) highlights = out.diem_nhan.map((s) => String(s).trim()).filter(Boolean).slice(0, 3);
} catch (e) {
  highlights = [];
}
if (highlights.length) {
  blocks.push(`<b>Điểm nhấn</b> <i>(AI tóm tắt từ các tin bên dưới)</i>\n${highlights.map((h) => `• ${esc(h.split(/\s+/).slice(0, 35).join(' '))}`).join('\n')}`);
}

const line = (l) => {
  const head = l.tickers ? `<b>${esc(l.tickers)}</b> ` : '';
  const links = l.sources.map((s) => `<a href="${escAttr(s.url)}">${esc(s.name)}</a>`).join(', ');
  const flag = l.needs_human_check ? ' ⚠️' : '';
  return `• ${head}(${l.importance}) ${esc(EVENT[l.event_type] ?? l.event_type)}: ${esc(l.summary)}${flag} — ${links} ${fmtTime(l.shown_at)}`;
};
const SECTIONS = [
  ['official', '<b>1. Công bố chính thức</b>'],
  ['reported', '<b>2. Báo chí xác nhận</b>'],
  ['opinion', '<b>3. Ý kiến/nhận định</b> <i>(không phải sự kiện)</i>'],
  ['rumor', '<b>4. Tin đồn</b> <i>(chưa xác nhận)</i>'],
  ['macro', '<b>Vĩ mô</b>'],
  ['other', '<b>Doanh nghiệp ngoài watchlist</b>'],
];
if (g.counts.eligible === 0) {
  blocks.push(`Không có tin mức ≥ ${cfg.MIN_IMPORTANCE} trong kỳ.`);
} else {
  for (const [key, title] of SECTIONS) {
    const ls = g.lines.filter((l) => l.section === key);
    if (key === 'official' && !cfg.OFFICIAL_SOURCE_CONNECTED && !ls.length) {
      blocks.push(`${title}\n• Chưa kết nối nguồn công bố chính thức. Kiểm tra trang HOSE/HNX.`);
      continue;
    }
    if (!ls.length) {
      if (key === 'rumor') blocks.push(`${title}\n• Không có.`);
      continue;
    }
    blocks.push(title);
    for (const l of ls) blocks.push(line(l));
  }
  if (g.counts.eligible > g.counts.listed) blocks.push(`<i>Còn ${g.counts.eligible - g.counts.listed} tin mức thấp hơn không hiển thị.</i>`);
}
if (g.unclassified.length) {
  blocks.push('<b>Tin khớp mã chưa được AI phân loại</b>');
  for (const u of g.unclassified) {
    blocks.push(`• <b>${esc(u.tickers)}</b> ${esc(u.title)} — <a href="${escAttr(u.url)}">${esc(u.source_name)}</a> ${fmtTime(u.shown_at)}`);
  }
}
const tail = [];
if (g.counts.needs_check) tail.push(`⚠️ ${g.counts.needs_check} tin cần người kiểm tra (needs_human_check).`);
tail.push(DISCLAIMER);
blocks.push(tail.join('\n'));

// Ghep khoi thanh phan; mot khoi qua dai (hiem) thi cat phan chu, giu lien ket cuoi.
const limit = cfg.PART_LIMIT;
const parts = [];
let cur = '';
for (let b of blocks) {
  if (b.length > limit) {
    const m = b.match(/ — <a [\s\S]*$/);
    const keep = m ? m[0] : '';
    b = b.slice(0, limit - keep.length - 1).replace(/<[^>]*$/, '').replace(/&[a-z]*$/, '') + '…' + keep;
  }
  if (cur && cur.length + 1 + b.length > limit) {
    parts.push(cur);
    cur = b;
  } else {
    cur = cur ? `${cur}\n${b}` : b;
  }
}
if (cur) parts.push(cur);
const total = parts.length;
return parts.map((text, n) => ({ json: {
  part_no: n + 1,
  parts_total: total,
  text: n === 0 ? text : `<i>(tiếp ${n + 1}/${total})</i>\n${text}`,
  chat_id: String(cfg.TELEGRAM_CHAT_ID || ''),
} }));
