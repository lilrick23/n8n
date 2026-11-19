// Cai dat lan dau cho vn-news-monitor tren may ca nhan. Chay trong image n8n bang docker compose.
// Nhap credential (tu khoa.txt) va workflow, ghi chat ID vao workflow ban tin, luu ban sao khoa ma hoa.
// Chi chay mot lan: lan sau thay tep danh dau thi thoat ngay, de khong ghi de workflow anh da sua.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';

const DATA = '/home/node/.n8n';
const SETUP = '/setup';
const MARK = `${DATA}/.vn-news-installed`;
const WORKFLOWS = ['news-setup', 'news-error-handler', 'news-collector', 'news-digest'];
const say = (m) => console.log(`[cai-dat] ${m}`);
const n8n = (...args) => execFileSync('n8n', args, { stdio: ['ignore', 'pipe', 'pipe'] }).toString().trim().split('\n').pop();

if (fs.existsSync(MARK)) {
  say('Da cai truoc do. Bo qua.');
  process.exit(0);
}

const env = (k) => (process.env[k] ?? '').trim();
const anthropic = env('ANTHROPIC_KEY');
const telegram = env('TELEGRAM_TOKEN');
let chatId = env('CHAT_ID');
const callmebot = env('CALLMEBOT_APIKEY');
const waPhone = env('WHATSAPP_PHONE').replace(/[^\d+]/g, '');

if (telegram && !chatId) {
  try {
    const r = await fetch(`https://api.telegram.org/bot${telegram}/getUpdates`, { signal: AbortSignal.timeout(20000) });
    const j = await r.json();
    if (!j.ok) say('Token Telegram bi tu choi. Kiem tra lai TELEGRAM_TOKEN.');
    const ids = (j.result ?? []).map((u) => u.message?.chat).filter((c) => c && c.type === 'private').map((c) => c.id);
    if (ids.length) chatId = String(ids[ids.length - 1]);
  } catch (e) {
    say(`Khong goi duoc Telegram: ${e.message}`);
  }
  say(chatId ? 'Tim thay chat ID.' : 'Chua thay tin /start. Ban tin chua gui duoc; xem huong dan muc "Chua nhan tin".');
}

// Credential: tep tam trong thu muc du lieu, xoa ngay sau khi nhap.
const creds = [];
if (anthropic) creds.push({ id: 'vnNewsAnthropic1', name: 'Anthropic (vn-news)', type: 'anthropicApi', data: { apiKey: anthropic } });
if (telegram) creds.push({ id: 'vnNewsTelegram01', name: 'Telegram (vn-news)', type: 'telegramApi', data: { accessToken: telegram } });
if (callmebot) creds.push({ id: 'vnNewsCallMeBot1', name: 'CallMeBot WhatsApp (vn-news)', type: 'httpQueryAuth', data: { name: 'apikey', value: callmebot } });
const tmp = `${DATA}/.creds-tmp.json`;
if (creds.length) {
  fs.writeFileSync(tmp, JSON.stringify(creds), { mode: 0o600 });
  try {
    say(n8n('import:credentials', `--input=${tmp}`));
  } finally {
    fs.rmSync(tmp, { force: true });
  }
} else {
  say('Chua co khoa trong khoa.txt. Them credential sau trong giao dien n8n.');
}

for (const w of WORKFLOWS) {
  const wf = JSON.parse(fs.readFileSync(`${SETUP}/workflows/${w}.json`, 'utf8'));
  if (w === 'news-digest') {
    for (const node of wf.nodes) {
      if (node.name !== 'Config') continue;
      if (chatId) node.parameters.jsCode = node.parameters.jsCode.replace(/TELEGRAM_CHAT_ID: (""|'')/, `TELEGRAM_CHAT_ID: ${JSON.stringify(chatId)}`);
      if (callmebot && waPhone) node.parameters.jsCode = node.parameters.jsCode.replace(/WHATSAPP_PHONE: (""|'')/, `WHATSAPP_PHONE: ${JSON.stringify(waPhone)}`);
    }
  }
  const p = `${DATA}/.wf-tmp.json`;
  fs.writeFileSync(p, JSON.stringify(wf));
  try {
    say(`${w}: ${n8n('import:workflow', `--input=${p}`)}`);
  } finally {
    fs.rmSync(p, { force: true });
  }
}

// Ban sao khoa ma hoa cho anh luu vao trinh quan ly mat khau. Mat khoa nay la mat moi credential.
try {
  const key = JSON.parse(fs.readFileSync(`${DATA}/config`, 'utf8')).encryptionKey;
  fs.mkdirSync(`${SETUP}/sao-luu`, { recursive: true });
  fs.writeFileSync(`${SETUP}/sao-luu/khoa-ma-hoa-n8n.txt`, `N8N_ENCRYPTION_KEY=${key}\n`, { mode: 0o600 });
  say('Da luu khoa ma hoa vao sao-luu/khoa-ma-hoa-n8n.txt. Chep vao noi an toan.');
} catch (e) {
  say(`Khong doc duoc khoa ma hoa: ${e.message}`);
}

fs.writeFileSync(MARK, new Date().toISOString());
say('Xong. Mo http://localhost:5678');
