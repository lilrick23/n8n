#!/usr/bin/env python3
"""Compute expected collector results from fixtures and compare with an n8n run (phase 3).

Usage: python3 -I scripts/expected_collector.py <decoded_run.json>
The decoded run comes from scripts/n8n_exec.py --out. This is a separate implementation
(Python, not the workflow's JavaScript), so a shared bug does not hide itself.
"""
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRACKING = re.compile(r"^(utm_.*|fbclid|gclid|zarsrc|ref|source)$", re.I)


def clean_url(raw):
    m = re.match(r"^https?://([^/?#\s]+)([^?#\s]*)(\?[^#\s]*)?", raw.strip(), re.I)
    if not m:
        return None
    keep = [p for p in (m.group(3) or "")[1:].split("&") if p and not TRACKING.match(p.split("=")[0])]
    return f"https://{m.group(1)}{m.group(2) or '/'}" + (f"?{'&'.join(keep)}" if keep else "")


def canonical(url):
    url = re.sub(r"^https://([^/?#]+)", lambda m: "https://" + re.sub(r"^www\.", "", m.group(1).lower()), url)
    return url[:-1] if url.endswith("/") else url


def strip(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").replace("đ", "d").replace("Đ", "D")


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", s or "")).strip()


def phrase_in(p, text):
    return re.search(r"(^|[^\w])" + re.escape(p) + r"($|[^\w])", text) is not None


def match(title, snippet, wl):
    raw = unicodedata.normalize("NFC", f"{title} {snippet}")
    lower = raw.lower()
    lower_s = strip(lower)
    accented = strip(raw) != raw
    tickers = []
    for t in wl["tickers"]:
        code = re.search(r"(^|[^A-Za-z0-9])" + re.escape(t["ticker"]) + r"($|[^A-Za-z0-9])", raw)
        alias = any(phrase_in(unicodedata.normalize("NFC", a).lower(), lower) or phrase_in(strip(a).lower(), lower_s)
                    for a in t.get("aliases", []) if len(a) >= 4)
        if code or alias:
            tickers.append(t["ticker"])
    topics = [t for t in wl["macro_topics"]
              if phrase_in(unicodedata.normalize("NFC", t).lower(), lower) or (not accented and phrase_in(strip(t).lower(), lower_s))]
    return tickers, topics


def main():
    run = json.load(open(sys.argv[1], encoding="utf-8"))["data"]["resultData"]["runData"]
    out = lambda n: [i["json"] for i in run[n][0]["data"]["main"][0]]
    sources = [s for s in json.load(open(ROOT / "config/sources.json", encoding="utf-8"))["sources"] if s["enabled"]]
    wl = json.load(open(ROOT / "config/watchlist.example.json", encoding="utf-8"))

    fetched = 0
    expected = {}
    for s in sources:
        root = ET.fromstring((ROOT / "fixtures/rss" / f"{s['id']}.xml").read_bytes())
        for it in root.find("channel").findall("item"):
            fetched += 1
            link = clean_url((it.findtext("link") or it.findtext("guid") or ""))
            title = plain(it.findtext("title"))
            if not link or not title:
                continue
            c = canonical(link)
            if c in expected:
                continue
            tickers, topics = match(title, plain(it.findtext("description"))[:500], wl)
            pub = it.findtext("pubDate")
            expected[c] = {"source_id": s["id"], "item_id": hashlib.sha256(c.encode()).hexdigest(),
                           "tickers": ",".join(tickers), "topics": ",".join(topics),
                           "pub_utc": parsedate_to_datetime(pub).timestamp() if pub else None}

    actual_norm = {i["url_canonical"]: i for i in out("Chuan hoa")}
    actual_saved = {i["item_id"]: i for i in out("Luu tin")}
    exp_ids = {v["item_id"] for v in expected.values()}
    rows = []

    def row(name, exp, act):
        rows.append((name, exp, act, "OK" if exp == act else "LECH"))

    row("Tin doc tu feed (items_fetched)", fetched,
        sum(len(i["rss"]["channel"]["item"]) for i in out("XML sang JSON") if "rss" in i))
    row("Sau loai trung trong lan chay (URL chuan hoa)", len(expected), len(actual_norm))
    row("Tap URL chuan hoa trung khop", "giong nhau", "giong nhau" if set(expected) == set(actual_norm) else "khac")
    row("Tap item_id (SHA-256) trung khop", "giong nhau", "giong nhau" if exp_ids == set(actual_saved) else "khac")
    exp_match = {k for k, v in expected.items() if v["tickers"] or v["topics"]}
    act_match = {k for k, v in actual_norm.items()
                 if actual_saved[expected[k]["item_id"]]["tickers"] or actual_saved[expected[k]["item_id"]]["topics"]}
    row("Tin khop watchlist/vi mo", len(exp_match), len(act_match))
    row("Tap tin khop trung khop", "giong nhau", "giong nhau" if exp_match == act_match else "khac")
    same_tags = all(actual_saved[v["item_id"]]["tickers"] == v["tickers"] and actual_saved[v["item_id"]]["topics"] == v["topics"]
                    for v in expected.values())
    row("Ma va chu de tung tin trung khop", True, same_tags)
    tz_ok = all((v.get("published_at") or "").endswith("+07:00") for v in actual_norm.values())
    row("published_at cua moi tin co +07:00 (sau Chuan hoa)", True, tz_ok)
    from datetime import datetime
    inst_ok = all(abs(datetime.fromisoformat(actual_norm[k]["published_at"]).timestamp() - v["pub_utc"]) < 1
                  for k, v in expected.items() if v["pub_utc"])
    row("Thoi diem dang giu nguyen khi doi sang ICT", True, inst_ok)
    per_source = {}
    for v in actual_norm.values():
        per_source.setdefault(v["source_id"], v["published_at"])
    row("So nguon co it nhat mot tin da doi sang ICT", len(sources), len(per_source))
    print("| Chi so | Ky vong (Python, doc fixture) | Thuc te (n8n) | Ket qua |")
    print("|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print("\nTin khop:")
    for k in sorted(exp_match):
        v = expected[k]
        print(f"- {v['source_id']}: tickers=[{v['tickers']}] topics=[{v['topics']}] {k}")
    print("\nMot tin moi nguon (published_at sau Chuan hoa):")
    for sid, ts in sorted(per_source.items()):
        print(f"- {sid}: {ts}")
    sys.exit(0 if all(r[3] == "OK" for r in rows) else 1)


if __name__ == "__main__":
    main()
