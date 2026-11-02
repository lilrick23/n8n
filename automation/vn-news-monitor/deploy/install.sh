#!/usr/bin/env bash
# Cai vn-news-monitor tren may chu Ubuntu/Debian moi. Chay bang quyen root:
#   curl -fsSL https://raw.githubusercontent.com/lilrick23/n8n/claude/vn-news-monitor/automation/vn-news-monitor/deploy/install.sh -o install.sh
#   sudo bash install.sh
# Script hoi khoa Anthropic va token Telegram ngay tren may chu (khong hien ra man hinh).
# Khoa khong ghi vao tep nao ngoai co so du lieu da ma hoa cua n8n.
set -euo pipefail

REPO_RAW="${REPO_RAW:-https://raw.githubusercontent.com/lilrick23/n8n/claude/vn-news-monitor/automation/vn-news-monitor}"
DIR="${DIR:-/opt/vn-news-monitor}"
WORKFLOWS="news-setup news-error-handler news-collector news-digest"

say() { printf '\n== %s\n' "$*"; }

if ! command -v docker >/dev/null 2>&1; then
  say "Cai Docker"
  curl -fsSL https://get.docker.com | sh
fi
docker compose version >/dev/null

mkdir -p "$DIR/import"
cd "$DIR"

say "Tai cau hinh va workflow"
if [ -n "${LOCAL_SRC:-}" ]; then
  cp "$LOCAL_SRC/deploy/docker-compose.yml" docker-compose.yml
  for w in $WORKFLOWS; do cp "$LOCAL_SRC/workflows/$w.json" "import/$w.json"; done
else
  curl -fsSL "$REPO_RAW/deploy/docker-compose.yml" -o docker-compose.yml
  for w in $WORKFLOWS; do curl -fsSL "$REPO_RAW/workflows/$w.json" -o "import/$w.json"; done
fi

if [ ! -f .env ]; then
  say "Tao khoa ma hoa N8N_ENCRYPTION_KEY"
  umask 077
  printf 'N8N_ENCRYPTION_KEY=%s\n' "$(openssl rand -hex 32)" > .env
  echo "Da luu trong $DIR/.env. SAO LUU tep nay o noi rieng: mat khoa la mat moi credential."
fi

ANTHROPIC_KEY="${ANTHROPIC_KEY:-}"
TELEGRAM_TOKEN="${TELEGRAM_TOKEN:-}"
CHAT_ID="${CHAT_ID:-}"
if [ -z "$ANTHROPIC_KEY" ] && [ -t 0 ]; then
  read -r -s -p "Dan khoa Anthropic API (bat dau sk-ant-api03-), roi Enter: " ANTHROPIC_KEY; echo
fi
if [ -z "$TELEGRAM_TOKEN" ] && [ -t 0 ]; then
  read -r -s -p "Dan token bot Telegram tu @BotFather (de trong neu chua co), roi Enter: " TELEGRAM_TOKEN; echo
fi
if [ -n "$TELEGRAM_TOKEN" ] && [ -z "$CHAT_ID" ]; then
  [ -t 0 ] && read -r -p "Mo Telegram, gui /start cho bot vua tao, roi nhan Enter... " _
  CHAT_ID="$(curl -fsS "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getUpdates" \
    | python3 -c 'import json,sys; r=json.load(sys.stdin).get("result",[]); ids=[u["message"]["chat"]["id"] for u in r if "message" in u]; print(ids[-1] if ids else "")')"
  if [ -n "$CHAT_ID" ]; then echo "Tim thay chat ID cua anh."; else echo "Chua thay tin nhan /start. Ban tin se chua gui; chay lai script sau."; fi
fi

say "Ghi chat ID vao workflow ban tin (chi tren may chu, khong vao repo)"
CHAT_ID="$CHAT_ID" python3 - "$DIR/import/news-digest.json" <<'PY'
import json, os, sys
p = sys.argv[1]
wf = json.load(open(p, encoding="utf-8"))
chat = os.environ.get("CHAT_ID", "")
for n in wf["nodes"]:
    if n["name"] == "Config":
        n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace("TELEGRAM_CHAT_ID: ''", f"TELEGRAM_CHAT_ID: {json.dumps(chat)}")
json.dump(wf, open(p, "w", encoding="utf-8"), ensure_ascii=False)
PY

say "Tao credential trong n8n (ma hoa bang N8N_ENCRYPTION_KEY)"
umask 077
ANTHROPIC_KEY="$ANTHROPIC_KEY" TELEGRAM_TOKEN="$TELEGRAM_TOKEN" python3 - "$DIR/import/credentials.json" <<'PY'
import json, os, sys
creds = []
if os.environ.get("ANTHROPIC_KEY"):
    creds.append({"id": "vnNewsAnthropic1", "name": "Anthropic (vn-news)", "type": "anthropicApi",
                  "data": {"apiKey": os.environ["ANTHROPIC_KEY"]}})
if os.environ.get("TELEGRAM_TOKEN"):
    creds.append({"id": "vnNewsTelegram01", "name": "Telegram (vn-news)", "type": "telegramApi",
                  "data": {"accessToken": os.environ["TELEGRAM_TOKEN"]}})
json.dump(creds, open(sys.argv[1], "w"))
print(f"{len(creds)} credential")
PY
chmod 644 import/credentials.json
docker compose run --rm --no-deps -T n8n import:credentials --input=/import/credentials.json || true
rm -f import/credentials.json
for w in $WORKFLOWS; do docker compose run --rm --no-deps -T n8n import:workflow --input="/import/$w.json"; done

say "Khoi dong n8n"
docker compose up -d
for _ in $(seq 1 60); do curl -fsS http://127.0.0.1:5678/healthz >/dev/null 2>&1 && break; sleep 2; done
curl -fsS http://127.0.0.1:5678/healthz && echo

cat <<MSG

Xong phan cai dat. Buoc tiep theo (lam tren may tinh cua anh):
1. Mo duong ham:  ssh -L 5678:127.0.0.1:5678 root@<IP may chu>
2. Mo trinh duyet: http://localhost:5678 , tao tai khoan quan tri.
3. Mo workflow "VN news - setup tables", bam Execute workflow (mot lan).
4. Bat (Publish) hai workflow: "VN news - collector" va "VN news - digest".
Chi tiet: docs/RUNBOOK.md
MSG
