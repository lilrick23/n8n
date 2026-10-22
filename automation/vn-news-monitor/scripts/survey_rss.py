#!/usr/bin/env python3
"""Survey downloaded RSS files (phase 1).

Usage: python3 -I scripts/survey_rss.py <raw_dir> <sources.json> <out_json>

Reads <raw_dir>/<source_id>.xml for every source in sources.json and writes a JSON
summary per feed plus a cross-feed duplicate analysis. Standard library only.
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, urlparse
import xml.etree.ElementTree as ET

ICT = timezone(timedelta(hours=7))
TRACKING = re.compile(r"^(utm_|fbclid|gclid|zarsrc|ref$|source$)")


def text(el, tag):
    child = el.find(tag)
    return None if child is None or child.text is None else child.text.strip()


def parse_date(raw):
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        return dt  # naive: no timezone in source
    return dt.astimezone(ICT)


def date_shape(raw):
    if not raw:
        return "missing"
    shape = re.sub(r"\d", "9", raw)
    return shape


def strip_html(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def norm_title(t):
    t = unicodedata.normalize("NFD", t.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace("đ", "d")
    return re.findall(r"[a-z0-9]+", t)


def survey(path):
    raw = open(path, "rb").read()
    decl = re.match(rb"<\?xml[^>]*encoding=[\"']([^\"']+)", raw)
    root = ET.fromstring(raw)
    channel = root.find("channel")
    items = channel.findall("item") if channel is not None else []
    rows = []
    for it in items:
        rows.append({
            "title": text(it, "title"),
            "link": text(it, "link"),
            "guid": text(it, "guid"),
            "pubDate_raw": text(it, "pubDate"),
            "description": text(it, "description"),
        })
    dates = [parse_date(r["pubDate_raw"]) for r in rows]
    aware = [d for d in dates if d is not None and d.tzinfo is not None]
    fields = {f: sum(1 for r in rows if r[f]) for f in ("title", "link", "guid", "pubDate_raw", "description")}
    tracking = [r["link"] for r in rows if r["link"] and any(TRACKING.match(k) for k in parse_qs(urlparse(r["link"]).query))]
    schemes = Counter(urlparse(r["link"]).scheme for r in rows if r["link"])
    guid_eq_link = sum(1 for r in rows if r["guid"] and r["link"] and r["guid"] == r["link"])
    desc_html = sum(1 for r in rows if r["description"] and "<" in r["description"])
    snippet_len = [len(strip_html(r["description"])) for r in rows if r["description"]]
    newest = max(aware) if aware else None
    oldest = min(aware) if aware else None
    span_h = round((newest - oldest).total_seconds() / 3600, 1) if aware else None
    # items per hour during today's trading window 09:00-15:00 ICT (6h)
    day = newest.date() if newest else None
    in_window = [d for d in aware if d.date() == day and 9 <= d.hour < 15] if day else []
    last24 = [d for d in aware if newest and (newest - d) <= timedelta(hours=24)]
    return {
        "xml_encoding": decl.group(1).decode() if decl else "(none, default UTF-8)",
        "item_count": len(rows),
        "fields_present": fields,
        "date_shapes": sorted(Counter(date_shape(r["pubDate_raw"]) for r in rows).items(), key=lambda x: -x[1]),
        "has_timezone": bool(aware) and len(aware) == len(rows),
        "unparsed_dates": sum(1 for d in dates if d is None),
        "newest_ict": newest.isoformat() if newest else None,
        "oldest_ict": oldest.isoformat() if oldest else None,
        "span_hours": span_h,
        "items_last_24h": len(last24),
        "items_0900_1500_newest_day": len(in_window),
        "per_hour_0900_1500": round(len(in_window) / 6, 2),
        "links_with_tracking_params": len(tracking),
        "link_schemes": dict(schemes),
        "guid_equals_link": guid_eq_link,
        "description_contains_html": desc_html,
        "snippet_text_len_max": max(snippet_len) if snippet_len else 0,
        "snippet_text_len_median": sorted(snippet_len)[len(snippet_len) // 2] if snippet_len else 0,
        "sample_titles": [r["title"] for r in rows[:5]],
        "_rows": rows,
    }


def canonical(link):
    p = urlparse(link or "")
    return (p.netloc.replace("www.", "") + p.path).lower()


def main():
    raw_dir, sources_path, out_path = sys.argv[1:4]
    sources = json.load(open(sources_path, encoding="utf-8"))["sources"]
    result = {}
    for s in sources:
        try:
            result[s["id"]] = survey(f"{raw_dir}/{s['id']}.xml")
        except Exception as e:  # keep going: one bad feed must not stop the survey
            result[s["id"]] = {"error": repr(e)}

    # cross-feed duplicates
    url_sources = defaultdict(set)
    titles = []
    for sid, r in result.items():
        for row in r.get("_rows", []):
            url_sources[canonical(row["link"])].add(sid)
            titles.append((sid, row["title"] or "", set(norm_title(row["title"] or ""))))
    same_url = {u: sorted(v) for u, v in url_sources.items() if len(v) > 1}
    pair_counts = Counter()
    for srcs in same_url.values():
        for i, a in enumerate(srcs):
            for b in srcs[i + 1:]:
                pair_counts[f"{a} + {b}"] += 1
    similar = []
    for i in range(len(titles)):
        for j in range(i + 1, len(titles)):
            a, b = titles[i], titles[j]
            if a[0].split("-")[0] == b[0].split("-")[0]:
                continue  # same publisher: handled by URL dedupe
            if not a[2] or not b[2]:
                continue
            jac = len(a[2] & b[2]) / len(a[2] | b[2])
            if jac >= 0.5:
                similar.append({"jaccard": round(jac, 2), "a": [a[0], a[1]], "b": [b[0], b[1]]})
    similar.sort(key=lambda x: -x["jaccard"])
    total_items = sum(r.get("item_count", 0) for r in result.values())
    for r in result.values():
        r.pop("_rows", None)
    out = {
        "feeds": result,
        "cross_feed": {
            "total_items": total_items,
            "unique_urls": len(url_sources),
            "urls_in_multiple_feeds": len(same_url),
            "feed_pairs_sharing_urls": dict(pair_counts.most_common()),
            "cross_publisher_similar_titles_jaccard_ge_0_5": similar[:40],
        },
    }
    json.dump(out, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk not in ("sample_titles", "date_shapes")} for k, v in result.items()}, ensure_ascii=False, indent=1))
    print(json.dumps({k: v for k, v in out["cross_feed"].items() if k != "cross_publisher_similar_titles_jaccard_ge_0_5"}, ensure_ascii=False, indent=1))
    print("similar titles:", len(similar))


if __name__ == "__main__":
    main()
