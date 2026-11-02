#!/usr/bin/env python3
"""Decode an n8n execution (REST /rest/executions/:id) and summarise it (phase 3 testing).

Usage: python3 -I scripts/n8n_exec.py <execution.json> [--out decoded.json] [--node NAME ...]
n8n stores execution data in the "flatted" format; this unflattens it with the standard library.
"""
import json
import sys


def unflatten(arr):
    memo = {}

    def revive(i):
        if i in memo:
            return memo[i]
        v = arr[i]
        if isinstance(v, dict):
            out = {}
            memo[i] = out
            for k, x in v.items():
                out[k] = revive(int(x)) if isinstance(x, str) else x
            return out
        if isinstance(v, list):
            out = []
            memo[i] = out
            out.extend(revive(int(x)) if isinstance(x, str) else x for x in v)
            return out
        return v

    return revive(0)


def main():
    args = sys.argv[1:]
    path = args.pop(0)
    out_path = None
    nodes = []
    while args:
        flag = args.pop(0)
        if flag == "--out":
            out_path = args.pop(0)
        elif flag == "--node":
            nodes.append(args.pop(0))
    raw = json.load(open(path, encoding="utf-8"))["data"]
    data = unflatten(json.loads(raw["data"]))
    data.get("resumeToken") and data.update(resumeToken="<redacted>")
    run = data["resultData"]["runData"]
    print(f"status={raw['status']} mode={raw['mode']} started={raw['startedAt']} stopped={raw['stoppedAt']}")
    err = data["resultData"].get("error")
    if err:
        print("ERROR:", err.get("message"), "| node:", (err.get("node") or {}).get("name"))
    for name, tasks in run.items():
        t = tasks[0]
        outs = (t.get("data") or {}).get("main") or []
        counts = [len(o or []) for o in outs]
        e = t.get("error")
        print(f"  {name:28s} status={t.get('executionStatus')} items_out={counts} ms={t.get('executionTime')}" + (f" ERROR={e.get('message')}" if e else ""))
    for name in nodes:
        outs = run.get(name, [{}])[0].get("data", {}).get("main", [])
        for idx, o in enumerate(outs):
            print(f"--- {name} output {idx}: {len(o or [])} items")
            for it in (o or [])[:3]:
                print(json.dumps(it.get("json"), ensure_ascii=False)[:700])
    if out_path:
        slim = {"id": raw["id"], "status": raw["status"], "mode": raw["mode"], "startedAt": raw["startedAt"],
                "stoppedAt": raw["stoppedAt"], "workflowId": raw.get("workflowId"), "data": data}
        json.dump(slim, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
