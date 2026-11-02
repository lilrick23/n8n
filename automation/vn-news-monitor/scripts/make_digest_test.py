#!/usr/bin/env python3
"""Build a test copy of news-digest.json that reads fixture rows instead of Data Tables (phase 5).

Usage: python3 -I scripts/make_digest_test.py OUT.json
The fixture has 90 synthetic rows: enough text for about 3 Telegram messages,
special characters in titles and URLs, every origin type, and unclassified rows.
Rows are invented test data (example.invalid URLs), not real news.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TICKERS = ["HPG", "FPT", "VCB", "MWG", "VNM", "SSI", "TCB", "GAS", "VHM", "MSN"]
EVENTS = ["kqkd", "co_tuc", "phat_hanh_tang_von", "ma", "giao_dich_noi_bo", "nhan_su", "trai_phieu"]
ORIGINS = ["reported_fact", "reported_fact", "reported_fact", "analyst_opinion", "rumor", "official_disclosure"]


def rows():
    out = []
    for n in range(90):
        t = TICKERS[n % len(TICKERS)]
        ev = EVENTS[n % len(EVENTS)]
        origin = ORIGINS[n % len(ORIGINS)]
        imp = 5 if n % 17 == 0 and origin != "analyst_opinion" and origin != "rumor" else 4 if n % 3 == 0 else 3
        macro = n % 11 == 0
        special = n % 5 == 0
        title = f"[THU] {t} công bố sự kiện số {n} & kế hoạch <2027> \"đặc biệt\" 'thử'" if special else f"[THU] {t} sự kiện thử nghiệm số {n}"
        out.append({
            "item_id": f"test{n:03d}", "source_id": "test", "source_name": "Nguồn thử A&B" if special else "Nguồn thử",
            "source_tier": 2, "lang": "vi", "title": title,
            "url": f"https://example.invalid/tin?id={n}&ma={t}&q=a<b>\"c\"",
            "snippet": "", "published_at": f"2026-11-02T0{n % 9}:0{n % 6}:00+07:00",
            "fetched_at": "__RECENT__",
            "tickers": "" if macro else t, "topics": "lai_suat" if macro else "",
            "event_type": "chinh_sach_vi_mo" if macro else ev, "fact_or_opinion": origin, "importance": imp,
            "summary_vi": (f"Tóm tắt thử số {n} cho {t}: doanh nghiệp công bố nội dung dài để kiểm tra việc tách tin nhắn "
                           f"theo giới hạn ký tự của Telegram, có ký tự đặc biệt & < > \" ' và số liệu 1.234,5 tỷ đồng."),
            "why_it_matters": "", "needs_human_check": n % 13 == 0, "classified_by": "ai",
        })
    for n in range(4):
        out.append({"item_id": f"kw{n}", "source_name": "Nguồn thử", "title": f"[THU] Tin khớp mã chưa phân loại {n} <b>",
                    "url": f"https://example.invalid/kw?id={n}&x=1", "published_at": "", "fetched_at": "__RECENT__",
                    "tickers": "HPG", "topics": "", "importance": None, "classified_by": "keyword_only"})
    return out


def main():
    out = pathlib.Path(sys.argv[1])
    wf = json.loads((ROOT / "workflows" / "news-digest.json").read_text(encoding="utf-8"))
    data = json.dumps(rows(), ensure_ascii=False, indent=1)
    (ROOT / "fixtures" / "digest" / "rows.json").write_text(data + "\n", encoding="utf-8")
    fixture = ("// Du lieu gia cho kiem thu ban tin (scripts/make_digest_test.py).\n"
               f"const ROWS = {data};\n"
               "const recent = DateTime.now().minus({ minutes: 30 }).toUTC().toISO();\n"
               "return ROWS.map((r) => ({ json: { ...r, fetched_at: r.fetched_at === '__RECENT__' ? recent : r.fetched_at } }));\n")
    for n in wf["nodes"]:
        if n["name"] == "Doc tin":
            n.update({"type": "n8n-nodes-base.code", "typeVersion": 2, "parameters": {"jsCode": fixture}})
            n.pop("executeOnce", None)
        if n["name"] == "Doc digest_log":
            n.update({"type": "n8n-nodes-base.code", "typeVersion": 2, "parameters": {"jsCode": "return [{ json: {} }];"}})
        if n["name"] == "Config":
            # More lines than the default 30 so the text is over 3 times the Telegram limit.
            n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace("MAX_LINES: 30", "MAX_LINES: 45")
        if n["name"] == "Ghi digest_log":
            n.update({"type": "n8n-nodes-base.noOp", "typeVersion": 1, "parameters": {}})
    wf["id"], wf["name"] = "vnNewsDigestTst1", "VN news - digest (fixture test)"
    wf["settings"].pop("errorWorkflow", None)
    out.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
