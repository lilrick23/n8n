#!/usr/bin/env python3
"""Build the n8n workflow JSON files from workflows/src/ and config/ (phase 3).

Usage:
  python3 -I scripts/build_workflows.py                 # writes workflows/*.json
  python3 -I scripts/build_workflows.py --test-feeds URL --out DIR
      # test copy: feeds load from URL/<source_id>.xml, plus one missing feed

Code node bodies live in workflows/src/collector/*.js so they can be read and diffed.
The output JSON is what Rick imports into n8n.
"""
import argparse
import json
import pathlib
import uuid

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "workflows" / "src" / "collector"

IDS = {
    "setup": "vnNewsSetup00001",
    "collector": "vnNewsCollector1",
    "error": "vnNewsErrorHdl01",
}
SETTINGS = {
    "executionOrder": "v1",
    "timezone": "Asia/Ho_Chi_Minh",
    "saveManualExecutions": True,
    "callerPolicy": "workflowsFromSameOwner",
}

NEWS_ITEMS_COLUMNS = [
    ("item_id", "string"), ("source_id", "string"), ("source_name", "string"),
    ("source_tier", "number"), ("lang", "string"), ("title", "string"), ("url", "string"),
    ("snippet", "string"), ("published_at", "date"), ("fetched_at", "date"),
    ("tickers", "string"), ("topics", "string"), ("match_reason", "string"),
    ("event_type", "string"), ("fact_or_opinion", "string"), ("importance", "number"),
    ("sentiment", "string"), ("summary_vi", "string"), ("why_it_matters", "string"),
    ("needs_human_check", "boolean"), ("classified_by", "string"), ("alert_sent_at", "date"),
    ("run_id", "string"),
]
RUN_LOG_COLUMNS = [
    ("run_id", "string"), ("workflow", "string"), ("trigger", "string"),
    ("started_at", "date"), ("finished_at", "date"), ("sources_total", "number"),
    ("sources_ok", "number"), ("sources_failed", "number"), ("failed_source_ids", "string"),
    ("items_fetched", "number"), ("items_unique", "number"), ("items_new", "number"),
    ("items_matched", "number"), ("items_saved", "number"), ("items_to_ai", "number"),
    ("ai_calls", "number"), ("ai_failures", "number"), ("alerts_sent", "number"),
    ("dry_run", "boolean"), ("error", "string"),
]
AI_USAGE_COLUMNS = [
    ("date", "string"), ("model", "string"), ("calls", "number"), ("items", "number"),
    ("tokens_in", "number"), ("tokens_out", "number"), ("estimated", "boolean"),
    ("cost_usd_est", "number"), ("cap_reached_at", "date"),
]


def js(name, **subs):
    text = (SRC / name).read_text(encoding="utf-8")
    for key, value in subs.items():
        marker = f"/*__{key}__*/"
        assert marker in text, f"{marker} missing in {name}"
        text = text.replace(marker + ("[]" if key == "SOURCES" else "{}" if key == "WATCHLIST" else "''"), value)
    return text


def node(name, type_, version, x, y, params, **extra):
    n = {"parameters": params, "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"vn-news-monitor/{type_}/{name}")),
         "name": name, "type": type_, "typeVersion": version, "position": [x, y]}
    n.update(extra)
    return n


def code(name, x, y, body, each=False, **extra):
    params = {"jsCode": body}
    if each:
        params["mode"] = "runOnceForEachItem"
    return node(name, "n8n-nodes-base.code", 2, x, y, params, **extra)


def table(name):
    return {"__rl": True, "mode": "name", "value": name}


def connect(pairs):
    conns = {}
    for src, dst, out in pairs:
        outputs = conns.setdefault(src, {"main": []})["main"]
        while len(outputs) <= out:
            outputs.append([])
        outputs[out].append({"node": dst, "type": "main", "index": 0})
    return conns


def sticky(text, x, y, w=520, h=300):
    return node("Ghi chu", "n8n-nodes-base.stickyNote", 1, x, y,
                {"content": text, "width": w, "height": h})


def load_sources():
    data = json.loads((ROOT / "config" / "sources.json").read_text(encoding="utf-8"))
    out = []
    for s in data["sources"]:
        if not s.get("enabled"):
            continue
        out.append({"id": s["id"], "name": s["name"], "tier": s["tier"], "url": s["url"],
                    "lang": "en" if "-en-" in s["id"] else "vi"})
    return out


def load_watchlist():
    wl = json.loads((ROOT / "config" / "watchlist.example.json").read_text(encoding="utf-8"))
    return {k: wl[k] for k in ("tickers", "macro_topics", "exclude_keywords")}


def setup_workflow():
    def create(name, title, columns, x):
        return node(title, "n8n-nodes-base.dataTable", 1.1, x, 300, {
            "resource": "table", "operation": "create", "tableName": name,
            "columns": {"column": [{"name": c, "type": t} for c, t in columns]},
            "options": {"createIfNotExists": True},
        })
    nodes = [
        node("Chay tay", "n8n-nodes-base.manualTrigger", 1, 0, 300, {}),
        create("news_items", "Tao news_items", NEWS_ITEMS_COLUMNS, 240),
        create("run_log", "Tao run_log", RUN_LOG_COLUMNS, 480),
        create("ai_usage", "Tao ai_usage", AI_USAGE_COLUMNS, 720),
        sticky("## Tao bang du lieu\nChay mot lan truoc khi bat news-collector.\nNeu bang da co, node tra lai bang cu (khong tao trung).", 0, 0, 760, 220),
    ]
    return {
        "id": IDS["setup"], "name": "VN news - setup tables", "active": False,
        "nodes": nodes,
        "connections": connect([("Chay tay", "Tao news_items", 0), ("Tao news_items", "Tao run_log", 0),
                                ("Tao run_log", "Tao ai_usage", 0)]),
        "settings": {**SETTINGS}, "pinData": {}, "tags": [],
    }


def collector_workflow(feed_override=""):
    sources = load_sources()
    if feed_override:
        sources.append({"id": "test-missing-feed", "name": "Feed thu loi (404)", "tier": 2,
                        "url": "", "lang": "vi"})
    cfg = js("config.js", SOURCES=json.dumps(sources, ensure_ascii=False, indent=2),
             WATCHLIST=json.dumps(load_watchlist(), ensure_ascii=False, indent=2),
             FEED_BASE_OVERRIDE=json.dumps(feed_override))
    http_headers = {"parameters": [
        {"name": "User-Agent", "value": "Mozilla/5.0 (compatible; vn-news-monitor/1.0)"},
        {"name": "Accept", "value": "application/rss+xml, application/xml, text/xml, */*"},
    ]}
    nodes = [
        node("Lich giao dich", "n8n-nodes-base.scheduleTrigger", 1.4, 0, 200, {
            "rule": {"interval": [{"field": "cronExpression", "expression": "*/30 8-16 * * 1-5"}]},
            "misfirePolicy": "skip"}),
        node("Lich ngoai gio", "n8n-nodes-base.scheduleTrigger", 1.4, 0, 360, {
            "rule": {"interval": [
                {"field": "cronExpression", "expression": "0 18,21 * * 1-5"},
                {"field": "cronExpression", "expression": "0 9,20 * * 0,6"}]},
            "misfirePolicy": "skip"}),
        node("Chay tay", "n8n-nodes-base.manualTrigger", 1, 0, 520, {}),
        code("Config", 240, 360, cfg),
        code("Tach nguon", 480, 200, js("split-sources.js")),
        node("Tai feed", "n8n-nodes-base.httpRequest", 4.2, 720, 200, {
            "url": "={{ $json.url }}",
            "sendHeaders": True,
            "headerParameters": http_headers,
            "options": {"timeout": 15000, "response": {"response": {"responseFormat": "text"}}},
        }, retryOnFail=True, maxTries=3, waitBetweenTries=5000, onError="continueErrorOutput"),
        code("Gan nguon", 960, 120, js("tag-source.js"), each=True),
        code("Loi tai feed", 960, 300, js("fetch-error.js"), each=True),
        node("XML sang JSON", "n8n-nodes-base.xml", 1, 1200, 120,
             {"mode": "xmlToJson", "dataPropertyName": "data", "options": {}},
             onError="continueRegularOutput"),
        code("Chuan hoa", 1440, 120, js("normalize.js")),
        node("Tao id", "n8n-nodes-base.set", 3.4, 1680, 120, {
            "assignments": {"assignments": [{
                "id": "3b6f0f6e-5a2d-4c1e-9d55-7f3c2a1b0c01", "name": "item_id",
                "value": "={{ $json.url_canonical.hash('sha256') }}", "type": "string"}]},
            "includeOtherFields": True, "options": {}}),
        node("Gioi han", "n8n-nodes-base.limit", 1, 2160, 120,
             {"maxItems": "={{ $('Config').first().json.MAX_ITEMS_PER_RUN }}"}),
        node("Da co trong news_items?", "n8n-nodes-base.dataTable", 1.1, 1920, 120, {
            "resource": "row", "operation": "rowNotExists",
            "dataTableId": table("news_items"),
            "matchType": "anyCondition",
            "filters": {"conditions": [{"keyName": "item_id", "keyValue": "={{ $json.item_id }}"}]}}),
        code("Khop watchlist", 2400, 120, js("match-watchlist.js")),
        code("Dinh dang dong", 2640, 120, js("shape-row.js")),
        node("Luu tin", "n8n-nodes-base.dataTable", 1.1, 2880, 120, {
            "resource": "row", "operation": "insert", "dataTableId": table("news_items"),
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [],
                        "schema": [], "attemptToConvertTypes": False, "convertFieldsToString": False},
            "options": {}}),
        code("Tong ket", 480, 640, js("run-summary.js")),
        node("Ghi run_log", "n8n-nodes-base.dataTable", 1.1, 720, 640, {
            "resource": "row", "operation": "insert", "dataTableId": table("run_log"),
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [],
                        "schema": [], "attemptToConvertTypes": False, "convertFieldsToString": False},
            "options": {}}),
        sticky("## news-collector\nThu thap tin RSS, chuan hoa, loai trung (bang news_items), khop watchlist, luu.\n"
               "Sua cau hinh o node **Config**. Nhanh AI va canh bao them o giai doan 4-5.\n"
               "Node **Tong ket** phai nam DUOI nhanh thu thap: n8n chay tung nhanh tu tren xuong.\n"
               "Thiet ke: docs/DESIGN.md", 0, -260, 900, 220),
    ]
    pairs = [
        ("Lich giao dich", "Config", 0), ("Lich ngoai gio", "Config", 0), ("Chay tay", "Config", 0),
        ("Config", "Tach nguon", 0), ("Config", "Tong ket", 0),
        ("Tach nguon", "Tai feed", 0),
        ("Tai feed", "Gan nguon", 0), ("Tai feed", "Loi tai feed", 1),
        ("Gan nguon", "XML sang JSON", 0), ("XML sang JSON", "Chuan hoa", 0),
        # Limit after the dedupe check: a cap before it would hide the same old items on every run.
        ("Chuan hoa", "Tao id", 0), ("Tao id", "Da co trong news_items?", 0),
        ("Da co trong news_items?", "Gioi han", 0), ("Gioi han", "Khop watchlist", 0),
        ("Khop watchlist", "Dinh dang dong", 0),
        ("Dinh dang dong", "Luu tin", 0),
        ("Tong ket", "Ghi run_log", 0),
    ]
    return {
        "id": IDS["collector"], "name": "VN news - collector", "active": False,
        "nodes": nodes, "connections": connect(pairs),
        "settings": {**SETTINGS, "errorWorkflow": IDS["error"], "executionTimeout": 600},
        "pinData": {}, "tags": [],
    }


def error_workflow():
    fmt = (
        "// Ban toi thieu (giai doan 3). Giai doan 6 them Telegram va chong bao loi.\n"
        "const e = $json;\n"
        "const redact = (s) => String(s ?? '')\n"
        "  .replace(/\\d{8,10}:[\\w-]{35}/g, '<telegram-token>')\n"
        "  .replace(/sk-[A-Za-z0-9_-]{10,}/g, '<api-key>')\n"
        "  .replace(/Bearer\\s+\\S+/g, 'Bearer <redacted>');\n"
        "return [{ json: {\n"
        "  workflow: e.workflow?.name ?? '',\n"
        "  node: e.execution?.lastNodeExecuted ?? '',\n"
        "  message: redact(e.execution?.error?.message).slice(0, 500),\n"
        "  at: DateTime.now().setZone('Asia/Ho_Chi_Minh').toISO({ suppressMilliseconds: true }),\n"
        "  url: e.execution?.url ?? '',\n"
        "} }];\n"
    )
    nodes = [
        node("Khi co loi", "n8n-nodes-base.errorTrigger", 1, 0, 200, {}),
        code("Dinh dang loi", 240, 200, fmt),
        sticky("## news-error-handler\nNhan loi tu news-collector va news-digest.\nGiai doan 6: gui Telegram, toi da 1 bao loi giong nhau moi 30 phut.", 0, -120, 600, 180),
    ]
    return {
        "id": IDS["error"], "name": "VN news - error handler", "active": False,
        "nodes": nodes, "connections": connect([("Khi co loi", "Dinh dang loi", 0)]),
        "settings": {**SETTINGS}, "pinData": {}, "tags": [],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-feeds", default="")
    ap.add_argument("--out", default=str(ROOT / "workflows"))
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    docs = {"news-collector.json": collector_workflow(args.test_feeds)}
    if not args.test_feeds:
        docs["news-setup.json"] = setup_workflow()
        docs["news-error-handler.json"] = error_workflow()
    else:
        docs["news-collector.json"]["id"] = "vnNewsCollTest01"
        docs["news-collector.json"]["name"] = "VN news - collector (fixture test)"
    for name, wf in docs.items():
        (out / name).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out / name)


if __name__ == "__main__":
    main()
