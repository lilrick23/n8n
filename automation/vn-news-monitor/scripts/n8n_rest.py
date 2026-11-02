#!/usr/bin/env python3
"""Small REST client for a local test n8n (phase 4). Never prints credentials.

Usage:
  python3 -I scripts/n8n_rest.py setup                 # create owner with a random password, save cookie
  python3 -I scripts/n8n_rest.py run WORKFLOW_ID TRIGGER OUT.json [--timeout 600]
Env: N8N_BASE (default http://127.0.0.1:5688), cookie in /tmp/claude-0/p4/cookie.txt
"""
import http.cookiejar
import json
import os
import secrets
import sys
import time
import urllib.request

BASE = os.environ.get("N8N_BASE", "http://127.0.0.1:5688")
JAR_PATH = "/tmp/claude-0/p4/cookie.txt"
jar = http.cookiejar.MozillaCookieJar(JAR_PATH)
if os.path.exists(JAR_PATH):
    jar.load(ignore_discard=True)
    for c in jar:
        c.secure = False  # local test instance runs on plain http
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(jar))


def call(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json", "browser-id": "p4-test"})
    with opener.open(req, timeout=60) as r:
        jar.save(ignore_discard=True)
        return json.loads(r.read() or b"{}")


def setup():
    pw = "Aa1" + secrets.token_urlsafe(16)
    user = {"email": "owner@example.com", "firstName": "Test", "lastName": "Owner", "password": pw}
    call("POST", "/rest/owner/setup", user)
    call("POST", "/rest/login", {"emailOrLdapLoginId": user["email"], "password": pw})
    print("owner created and logged in (password not stored)")


def run(wf_id, trigger, out, timeout=600):
    wf = call("GET", f"/rest/workflows/{wf_id}")["data"]
    started = time.time()
    res = call("POST", f"/rest/workflows/{wf_id}/run",
               {"workflowData": wf, "triggerToStartFrom": {"name": trigger}})
    ex_id = res["data"]["executionId"]
    while time.time() - started < timeout:
        time.sleep(3)
        ex = call("GET", f"/rest/executions/{ex_id}")["data"]
        if ex.get("finished") or ex.get("status") in ("success", "error", "crashed", "canceled"):
            break
    ex["_wall_seconds"] = round(time.time() - started, 1)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(ex, f, ensure_ascii=False)
    print(f"execution {ex_id} status={ex.get('status')} wall={ex['_wall_seconds']}s -> {out}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "setup":
        setup()
    elif cmd == "run":
        run(sys.argv[2], sys.argv[3], sys.argv[4])
