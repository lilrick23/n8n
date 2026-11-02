#!/usr/bin/env python3
"""Build the n8n workflow JSON files from workflows/src/ and config/ (phases 3-4).

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
DIGEST_SRC = ROOT / "workflows" / "src" / "digest"

IDS = {
    "eval": "vnNewsAiEval0001",
    "setup": "vnNewsSetup00001",
    "collector": "vnNewsCollector1",
    "error": "vnNewsErrorHdl01",
    "digest": "vnNewsDigest0001",
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
DIGEST_LOG_COLUMNS = [
    ("slot", "string"), ("period_start", "date"), ("period_end", "date"),
    ("items_in_period", "number"), ("items_listed", "number"), ("parts", "number"),
    ("parts_sent", "number"), ("sent", "boolean"), ("dry_run", "boolean"), ("error", "string"),
    ("created_at", "date"),
]
AI_USAGE_COLUMNS = [
    ("date", "string"), ("model", "string"), ("calls", "number"), ("items", "number"),
    ("tokens_in", "number"), ("tokens_out", "number"), ("estimated", "boolean"),
    ("cost_usd_est", "number"), ("cap_reached_at", "date"),
]


def js(name, src=SRC, **subs):
    text = (src / name).read_text(encoding="utf-8")
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
                    "type": s.get("type", "press"), "lang": "en" if "-en-" in s["id"] else "vi"})
    return out


def load_watchlist():
    wl = json.loads((ROOT / "config" / "watchlist.example.json").read_text(encoding="utf-8"))
    return {k: wl[k] for k in ("tickers", "macro_topics", "exclude_keywords")}


# Rick only uses the cheapest model (DECISIONS #11). Change it here, not in the node.
AI_MODEL = "claude-haiku-5-5"
ANTHROPIC_CREDENTIAL = {"id": "vnNewsAnthropic1", "name": "Anthropic (vn-news)"}


def ai_nodes(x, y):
    """Return the AI classifier root node and its chat model sub-node."""
    schema = (SRC / "ai-schema.json").read_text(encoding="utf-8")
    prompt = (SRC / "ai-system-prompt.txt").read_text(encoding="utf-8")
    extractor = node("Phan loai AI", "@n8n/n8n-nodes-langchain.informationExtractor", 1.2, x, y, {
        "text": "={{ $json.text }}",
        "schemaType": "manual",
        "inputSchema": schema,
        "options": {"systemPromptTemplate": prompt, "batching": {"batchSize": 2, "delayBetweenBatches": 0}},
    }, retryOnFail=True, maxTries=2, waitBetweenTries=5000, onError="continueRegularOutput")
    model = node("Mo hinh Haiku", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.6, x, y + 200, {
        "model": {"__rl": True, "mode": "id", "value": AI_MODEL},
        "options": {"maxTokensToSample": 3000, "thinkingMode": "disabled"},
    }, credentials={"anthropicApi": dict(ANTHROPIC_CREDENTIAL)})
    return extractor, model


def ai_model_connection(conns):
    conns["Mo hinh Haiku"] = {"ai_languageModel": [[{"node": "Phan loai AI", "type": "ai_languageModel", "index": 0}]]}
    return conns


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
        create("digest_log", "Tao digest_log", DIGEST_LOG_COLUMNS, 960),
        sticky("## Tao bang du lieu\nChay mot lan truoc khi bat news-collector.\nNeu bang da co, node tra lai bang cu (khong tao trung).", 0, 0, 760, 220),
    ]
    return {
        "id": IDS["setup"], "name": "VN news - setup tables", "active": False,
        "nodes": nodes,
        "connections": connect([("Chay tay", "Tao news_items", 0), ("Tao news_items", "Tao run_log", 0),
                                ("Tao run_log", "Tao ai_usage", 0), ("Tao ai_usage", "Tao digest_log", 0)]),
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
        node("Doc ai_usage", "n8n-nodes-base.dataTable", 1.1, 2880, 120, {
            "resource": "row", "operation": "get", "dataTableId": table("ai_usage"),
            "matchType": "anyCondition",
            "filters": {"conditions": [{"keyName": "date",
                                        "keyValue": "={{ $now.setZone('Asia/Ho_Chi_Minh').toFormat('yyyy-MM-dd') }}"}]},
            "returnAll": True}, executeOnce=True, alwaysOutputData=True),
        code("Chon tin cho AI", 3120, 120, js("ai-select.js")),
        node("Vao AI?", "n8n-nodes-base.if", 2.2, 3360, 120, {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                           "conditions": [{"id": "6f1d2c3b-0a4e-4b5f-8c6d-7e8f9a0b1c2d",
                                           "leftValue": "={{ $json.classified_by }}", "rightValue": "pending_ai",
                                           "operator": {"type": "string", "operation": "equals"}}],
                           "combinator": "and"},
            "options": {}}),
        code("Gom lo", 3600, 0, js("gom-lo.js")),
        *ai_nodes(3840, 0),
        code("Kiem tra luoc do", 4080, 0, js("kiem-tra.js")),
        code("Tinh ai_usage", 4320, -160, js("ai-usage.js")),
        node("Ghi ai_usage", "n8n-nodes-base.dataTable", 1.1, 4560, -160, {
            "resource": "row", "operation": "upsert", "dataTableId": table("ai_usage"),
            "matchType": "allConditions",
            "filters": {"conditions": [{"keyName": "date", "keyValue": "={{ $json.date }}"}]},
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [],
                        "schema": [], "attemptToConvertTypes": False, "convertFieldsToString": False},
            "options": {}}),
        node("Luu tin", "n8n-nodes-base.dataTable", 1.1, 4560, 120, {
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
               "Sua cau hinh o node **Config**. Nhanh AI: chi tin khop watchlist/vi mo/tier 1, toi da MAX_AI_ITEMS_PER_DAY tin/ngay, mo hinh Haiku 5.5.\n"
               "Canh bao Telegram them o giai doan 5.\n"
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
        ("Dinh dang dong", "Doc ai_usage", 0), ("Doc ai_usage", "Chon tin cho AI", 0),
        ("Chon tin cho AI", "Vao AI?", 0),
        ("Vao AI?", "Gom lo", 0), ("Gom lo", "Phan loai AI", 0), ("Phan loai AI", "Kiem tra luoc do", 0),
        ("Kiem tra luoc do", "Luu tin", 0), ("Kiem tra luoc do", "Tinh ai_usage", 0),
        ("Tinh ai_usage", "Ghi ai_usage", 0),
        ("Vao AI?", "Luu tin", 1),
        ("Tong ket", "Ghi run_log", 0),
    ]
    return {
        "id": IDS["collector"], "name": "VN news - collector", "active": False,
        "nodes": nodes, "connections": ai_model_connection(connect(pairs)),
        "settings": {**SETTINGS, "errorWorkflow": IDS["error"], "executionTimeout": 600},
        "pinData": {}, "tags": [],
    }


def eval_workflow():
    """Manual workflow: run fixtures/eval/labeled.jsonl through the same AI nodes as the collector."""
    rows = []
    for line in (ROOT / "fixtures" / "eval" / "labeled.jsonl").read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        rows.append({
            "item_id": uuid.uuid5(uuid.NAMESPACE_URL, r["url"] + r["eval_id"]).hex,
            "eval_id": r["eval_id"], "source_id": r["source_id"], "source_type": r["source_type"],
            "source_tier": r["source_tier"], "title": r["title"], "snippet": r["snippet"], "url": r["url"],
            "tickers": r["tickers"], "topics": r["topics"],
        })
    load = ("// Bo mau danh gia, tao tu fixtures/eval/labeled.jsonl boi scripts/build_workflows.py.\n"
            "// Nhan ky vong khong nam o day: scripts/eval_report.py so sanh sau khi chay.\n"
            f"const ROWS = {json.dumps(rows, ensure_ascii=False, indent=1)};\n"
            "return ROWS.map((json) => ({ json }));\n")
    nodes = [
        node("Chay tay", "n8n-nodes-base.manualTrigger", 1, 0, 200, {}),
        code("Nap bo mau", 240, 200, load),
        code("Gom lo", 480, 200, js("gom-lo.js")),
        *ai_nodes(720, 200),
        code("Kiem tra luoc do", 960, 200, js("kiem-tra.js")),
        sticky("## Danh gia AI (giai doan 4)\nChay tay. Goi API Anthropic that (Haiku 5.5), ~0,01 USD moi lan.\n"
               "Khong ghi vao Data Table. Ket qua doc bang scripts/eval_report.py.", 0, -100, 700, 200),
    ]
    pairs = [("Chay tay", "Nap bo mau", 0), ("Nap bo mau", "Gom lo", 0), ("Gom lo", "Phan loai AI", 0),
             ("Phan loai AI", "Kiem tra luoc do", 0)]
    return {
        "id": IDS["eval"], "name": "VN news - AI eval", "active": False,
        "nodes": nodes, "connections": ai_model_connection(connect(pairs)),
        "settings": {**SETTINGS}, "pinData": {}, "tags": [],
    }


TELEGRAM_CREDENTIAL = {"id": "vnNewsTelegram01", "name": "Telegram (vn-news)"}


def digest_workflow(chat_id=""):
    """Scheduled digest (phase 5): read news_items since the last digest, group, add AI highlights, send."""
    d = lambda name, **subs: js(name, src=DIGEST_SRC, **subs)  # noqa: E731
    extractor = node("Viet diem nhan", "@n8n/n8n-nodes-langchain.informationExtractor", 1.2, 1440, 0, {
        "text": "={{ $json.ai_input }}",
        "schemaType": "manual",
        "inputSchema": (DIGEST_SRC / "highlight-schema.json").read_text(encoding="utf-8"),
        "options": {"systemPromptTemplate": (DIGEST_SRC / "highlight-prompt.txt").read_text(encoding="utf-8")},
    }, retryOnFail=True, maxTries=2, waitBetweenTries=5000, onError="continueRegularOutput")
    model = node("Mo hinh Haiku (ban tin)", "@n8n/n8n-nodes-langchain.lmChatAnthropic", 1.6, 1440, 200, {
        "model": {"__rl": True, "mode": "id", "value": AI_MODEL},
        "options": {"maxTokensToSample": 800, "thinkingMode": "disabled"},
    }, credentials={"anthropicApi": dict(ANTHROPIC_CREDENTIAL)})
    nodes = [
        node("Ban tin sang", "n8n-nodes-base.scheduleTrigger", 1.4, 0, 100, {
            "rule": {"interval": [{"field": "cronExpression", "expression": "15 8 * * 1-5"}]}, "misfirePolicy": "skip"}),
        node("Ban tin chieu", "n8n-nodes-base.scheduleTrigger", 1.4, 0, 260, {
            "rule": {"interval": [{"field": "cronExpression", "expression": "30 15 * * 1-5"}]}, "misfirePolicy": "skip"}),
        node("Chay tay", "n8n-nodes-base.manualTrigger", 1, 0, 420, {}),
        code("Config", 240, 260, d("config.js", CHAT_ID=json.dumps(chat_id))),
        node("Doc digest_log", "n8n-nodes-base.dataTable", 1.1, 480, 260, {
            "resource": "row", "operation": "get", "dataTableId": table("digest_log"),
            "matchType": "anyCondition",
            "filters": {"conditions": [{"keyName": "sent", "condition": "isTrue"}]},
            "returnAll": True}, executeOnce=True, alwaysOutputData=True),
        code("Tinh ky", 720, 260, d("period.js")),
        node("Doc tin", "n8n-nodes-base.dataTable", 1.1, 960, 260, {
            "resource": "row", "operation": "get", "dataTableId": table("news_items"),
            "matchType": "allConditions",
            "filters": {"conditions": [{"keyName": "fetched_at", "condition": "gt", "keyValue": "={{ $json.since_utc }}"}]},
            "returnAll": True}, executeOnce=True, alwaysOutputData=True),
        code("Chon va nhom", 1200, 260, d("group.js")),
        node("Co tin muc cao?", "n8n-nodes-base.if", 2.2, 1200, 60, {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                           "conditions": [{"id": "0c9d6c1e-2f3a-4b5c-8d7e-1f2a3b4c5d6e",
                                           "leftValue": "={{ $json.has_highlights }}", "rightValue": "",
                                           "operator": {"type": "boolean", "operation": "true", "singleValue": True}}],
                           "combinator": "and"},
            "options": {}}),
        extractor, model,
        code("Dinh dang", 1680, 260, d("format.js")),
        node("Co chat ID?", "n8n-nodes-base.if", 2.2, 1920, 160, {
            "conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict", "version": 2},
                           "conditions": [{"id": "5a4b3c2d-1e0f-4a9b-8c7d-6e5f4a3b2c1d",
                                           "leftValue": "={{ $json.chat_id }}", "rightValue": "",
                                           "operator": {"type": "string", "operation": "notEmpty", "singleValue": True}}],
                           "combinator": "and"},
            "options": {}}),
        node("Gui Telegram", "n8n-nodes-base.telegram", 1.2, 2160, 100, {
            "chatId": "={{ $json.chat_id }}",
            "text": "={{ $json.text }}",
            "additionalFields": {"appendAttribution": False, "parse_mode": "HTML", "disable_web_page_preview": True},
        }, credentials={"telegramApi": dict(TELEGRAM_CREDENTIAL)},
            retryOnFail=True, maxTries=3, waitBetweenTries=5000, onError="continueRegularOutput"),
        code("Tong ket ban tin", 2160, 400, d("summary.js")),
        node("Ghi digest_log", "n8n-nodes-base.dataTable", 1.1, 2400, 400, {
            "resource": "row", "operation": "insert", "dataTableId": table("digest_log"),
            "columns": {"mappingMode": "autoMapInputData", "value": {}, "matchingColumns": [],
                        "schema": [], "attemptToConvertTypes": False, "convertFieldsToString": False},
            "options": {}}),
        sticky("## news-digest\nBan tin 08:15 va 15:30 thu 2-6 (gio Viet Nam). Doc news_items tu lan gui truoc.\n"
               "Sua cau hinh o node **Config**: dien TELEGRAM_CHAT_ID, tat DRY_RUN khi nghiem thu xong.\n"
               "AI (Haiku 5.5) chi viet 'Diem nhan' tu tom tat da co; loi AI thi ban tin van gui.\n"
               "Thiet ke: docs/DESIGN.md muc 1.2 va 7", 0, -240, 900, 200),
    ]
    pairs = [
        ("Ban tin sang", "Config", 0), ("Ban tin chieu", "Config", 0), ("Chay tay", "Config", 0),
        ("Config", "Doc digest_log", 0), ("Doc digest_log", "Tinh ky", 0), ("Tinh ky", "Doc tin", 0),
        ("Doc tin", "Chon va nhom", 0), ("Chon va nhom", "Co tin muc cao?", 0),
        ("Co tin muc cao?", "Viet diem nhan", 0), ("Co tin muc cao?", "Dinh dang", 1),
        ("Viet diem nhan", "Dinh dang", 0),
        ("Dinh dang", "Co chat ID?", 0), ("Dinh dang", "Tong ket ban tin", 0),
        ("Co chat ID?", "Gui Telegram", 0),
        ("Tong ket ban tin", "Ghi digest_log", 0),
    ]
    conns = connect(pairs)
    conns["Mo hinh Haiku (ban tin)"] = {"ai_languageModel": [[{"node": "Viet diem nhan", "type": "ai_languageModel", "index": 0}]]}
    return {
        "id": IDS["digest"], "name": "VN news - digest", "active": False,
        "nodes": nodes, "connections": conns,
        "settings": {**SETTINGS, "errorWorkflow": IDS["error"], "executionTimeout": 300},
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
        docs["news-ai-eval.json"] = eval_workflow()
        docs["news-digest.json"] = digest_workflow()
    else:
        docs["news-collector.json"]["id"] = "vnNewsCollTest01"
        docs["news-collector.json"]["name"] = "VN news - collector (fixture test)"
    for name, wf in docs.items():
        (out / name).write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("wrote", out / name)


if __name__ == "__main__":
    main()
