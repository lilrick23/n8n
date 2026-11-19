// Mot dong bao WhatsApp qua CallMeBot sau moi ban tin. Chi gui gio, so tin, so phan va trang thai.
// Khong gui tieu de, ma co phieu hay noi dung: CallMeBot la ben trung gian (docs/DECISIONS.md muc 19).
const cfg = $('Config').first().json;
const s = $json;
const LABEL = { sang: 'Bản tin sáng', chieu: 'Bản tin chiều', tay: 'Bản tin chạy tay' };
const at = DateTime.fromISO(s.period_end).setZone('Asia/Ho_Chi_Minh').toFormat('HH:mm dd/MM');
const status = s.sent
  ? `đã gửi Telegram ${s.parts_sent}/${s.parts} phần, ${s.items_listed} tin`
  : `CHƯA gửi được Telegram (${s.parts_sent}/${s.parts} phần). Mở n8n, mục Executions để xem lỗi`;
return [{ json: {
  phone: String(cfg.WHATSAPP_PHONE || ''),
  text: `${cfg.DRY_RUN ? '[THỬ NGHIỆM] ' : ''}${LABEL[s.slot] ?? LABEL.tay} ${at}: ${status}.`,
} }];
