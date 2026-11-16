# -*- coding: utf-8 -*-
"""Print what started / ended each recent turn of the given transcripts (data only, for timing analysis)."""
import json, os, sys
from datetime import datetime

ROOT = r"C:\Users\Admin\.claude\projects\D---------"
TAIL = 40 * 1024 * 1024


def ts_local(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S")
    except Exception:
        return "--:--:--"


def text_of(msg):
    c = (msg or {}).get("content")
    if isinstance(c, str):
        return c, False
    parts, tool = [], False
    for b in c or []:
        if not isinstance(b, dict):
            continue
        if b.get("type") == "text":
            parts.append(b.get("text", ""))
        elif b.get("type") == "tool_result":
            tool = True
    return " ".join(parts), tool


for sid in sys.argv[1:]:
    p = os.path.join(ROOT, sid + ".jsonl")
    with open(p, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        n = min(size, TAIL)
        f.seek(size - n)
        data = f.read(n)
    lines = data.split(b"\n")
    if n < size:
        lines = lines[1:]
    print("=== %s (%.0f MB, tail %.0f MB)" % (sid[:8], size / 1e6, n / 1e6))
    rows = []
    for raw in lines:
        if not raw.strip():
            continue
        # cheap pre-filter: skip giant tool results quickly
        if b'"type":"user"' not in raw and b'"stop_hook_summary"' not in raw and b'"end_turn"' not in raw and b'"queue-operation"' not in raw:
            continue
        try:
            o = json.loads(raw)
        except ValueError:
            continue
        if o.get("isSidechain"):
            continue
        t = o.get("type")
        if t == "user":
            txt, tool = text_of(o.get("message"))
            if tool and not txt.strip():
                continue
            txt = " ".join(txt.split())
            kind = "USER"
            if "task-notification" in txt or "SYSTEM NOTIFICATION" in txt:
                kind = "TASK-NOTIFY"
            elif "side-sessions-event" in txt:
                kind = "SIDE-EVENT"
            elif "Request interrupted" in txt:
                kind = "INTERRUPT"
            elif o.get("isMeta"):
                kind = "META"
            rows.append((o.get("timestamp", ""), kind, txt[:110]))
        elif t == "assistant":
            m = o.get("message") or {}
            if m.get("stop_reason") == "end_turn":
                txt, _ = text_of(m)
                txt = " ".join(txt.split())
                rows.append((o.get("timestamp", ""), "END_TURN", txt[:110] + " ... " + txt[-90:] if len(txt) > 220 else txt))
        elif t == "queue-operation":
            rows.append((o.get("timestamp", ""), "QUEUE:" + str(o.get("operation")), str(o.get("content", ""))[:90].replace("\n", " ")))
    for ts, kind, txt in rows[-14:]:
        print("  %s  %-12s %s" % (ts_local(ts), kind, txt))
