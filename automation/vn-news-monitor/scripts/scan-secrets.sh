#!/usr/bin/env bash
# Scan evidence/ and workflows/ for text that looks like a secret.
# Also checks every value in .env (if the file exists), without printing the values.
# Usage: bash scripts/scan-secrets.sh   (exit code 1 when something is found)
set -u
cd "$(dirname "$0")/.." || exit 2
TARGETS=(evidence workflows)
found=0

check() {
  local label="$1" pattern="$2"
  local hits
  hits=$(grep -rIlE -- "$pattern" "${TARGETS[@]}" 2>/dev/null)
  if [ -n "$hits" ]; then
    echo "FOUND $label in:"; echo "$hits" | sed 's/^/  /'
    found=1
  else
    echo "ok    $label"
  fi
}

check "telegram-token" '[0-9]{8,10}:[A-Za-z0-9_-]{35}'
check "api-key-sk" '(^|[^A-Za-z0-9])sk-[A-Za-z0-9_-]{16,}'
check "bearer-token" 'Bearer[[:space:]]+[A-Za-z0-9._~+/-]{8,}'
check "private-key" '-----BEGIN [A-Z ]*PRIVATE KEY-----'

if [ -f .env ]; then
  n=0
  while IFS='=' read -r key value; do
    case "$key" in ''|\#*) continue ;; esac
    value="${value%\"}"; value="${value#\"}"
    [ ${#value} -lt 6 ] && continue
    n=$((n + 1))
    if grep -rIlF -- "$value" "${TARGETS[@]}" >/dev/null 2>&1; then
      echo "FOUND value of .env key $key"
      found=1
    fi
  done < .env
  echo "ok    checked $n value(s) from .env"
else
  echo "info  no .env file"
fi

[ "$found" -eq 0 ] && echo "RESULT: no secrets found" || echo "RESULT: secrets found"
exit "$found"
