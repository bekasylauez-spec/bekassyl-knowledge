"""Convert Claude Code .jsonl transcripts to clean markdown (user prompts + assistant text only)."""
import json, re, sys, pathlib

src_dirs = [pathlib.Path(p) for p in sys.argv[1:-1]]
out = pathlib.Path(sys.argv[-1]); out.mkdir(parents=True, exist_ok=True)
TAG = re.compile(r"<(system-reminder|command-[a-z]+|local-command-[a-z]+|pasted_content[^>]*)>.*?</\1?[^>]*>", re.S)
TAG2 = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)

def text_of(content):
    if isinstance(content, str):
        return content
    parts = []
    for b in content or []:
        if isinstance(b, dict) and b.get("type") == "text":
            parts.append(b.get("text", ""))
    return "\n".join(parts)

index = []
for d in src_dirs:
    for f in sorted(d.glob("*.jsonl")):
        turns, title, first_ts = [], None, None
        for line in f.open(encoding="utf-8", errors="replace"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("type") == "summary" and not title:
                title = r.get("summary")
            if r.get("type") == "custom-title":
                title = r.get("customTitle") or title
            if r.get("isSidechain") or r.get("type") not in ("user", "assistant"):
                continue
            if r.get("isMeta") or r.get("isCompactSummary"):
                continue
            msg = r.get("message") or {}
            t = TAG2.sub("", text_of(msg.get("content"))).strip()
            if not t or t.startswith("[Request interrupted"):
                continue
            first_ts = first_ts or r.get("timestamp", "")
            turns.append(("Пайдаланушы" if r["type"] == "user" else "Claude", t))
        if not any(w == "Пайдаланушы" for w, _ in turns):
            continue
        date = (first_ts or "")[:10]
        first_user = next(t for w, t in turns if w == "Пайдаланушы")
        title = title or first_user.splitlines()[0][:70]
        safe = re.sub(r'[\\/:*?"<>|\n\r\t]+', " ", title).strip()[:60] or f.stem
        name = f"{date} {safe} ({f.stem[:8]}).md"
        body = [f"# {title}\n", f"- Дата: {date}", f"- Сессия: `{f.stem}`\n"]
        for w, t in turns:
            body.append(f"## {w}\n\n{t}\n")
        (out / name).write_text("\n".join(body), encoding="utf-8")
        index.append((date, name, title))

index.sort()
lines = ["# Чаттар тізімі\n", "| Күні | Чат |", "|---|---|"]
lines += [f"| {d} | [{t.replace('|', '/')}](<{n}>) |" for d, n, t in index]
(out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(index), "chats")
