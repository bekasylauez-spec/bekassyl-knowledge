"""Collect knowledge from this computer into the repo: Obsidian vault, Claude memory, chat texts.

Run: python tools/build.py
Merges with what is already in the repo (other computers' chats stay), masks phones/emails.
"""
import json, re, shutil, sys, pathlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
VAULT = HOME / "Documents" / "Bekassyl"
PROJECTS = HOME / ".claude" / "projects"
SKIP_VAULT = {"workspace.json", "workspace-mobile.json", "telegram_state.json"}

PHONE = re.compile(r"(?<![\w/])(\+?7|8)[ \-(]*7\d{2}[ \-)]*\d{3}[ \-]*\d{2}[ \-]*\d{2}(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def mask(s):
    return EMAIL.sub("[email жасырылды]", PHONE.sub("[тел. жасырылды]", s))


def copy_tree(src, dst):
    """Copy newer files only; nothing is deleted in the repo."""
    n = 0
    for f in src.rglob("*"):
        if not f.is_file() or f.name in SKIP_VAULT or "_sync" in f.parts or ".trash" in f.parts:
            continue
        t = dst / f.relative_to(src)
        if t.exists() and t.stat().st_mtime >= f.stat().st_mtime:
            continue
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, t)
        n += 1
    return n


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def convert_chat(f, out):
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
        t = REMINDER.sub("", text_of((r.get("message") or {}).get("content"))).strip()
        if not t or t.startswith("[Request interrupted"):
            continue
        first_ts = first_ts or r.get("timestamp", "")
        turns.append(("Пайдаланушы" if r["type"] == "user" else "Claude", t))
    users = [t for w, t in turns if w == "Пайдаланушы"]
    if not users:
        return False
    date = (first_ts or "")[:10]
    title = title or users[0].splitlines()[0][:70]
    safe = re.sub(r'[\\/:*?"<>|\n\r\t]+', " ", title).strip()[:60] or f.stem
    for old in out.glob(f"* ({f.stem[:8]}).md"):
        old.unlink()  # the title may have changed since the last build
    body = [f"# {title}\n", f"- Дата: {date}", f"- Сессия: `{f.stem}`\n"]
    body += [f"## {w}\n\n{t}\n" for w, t in turns]
    (out / f"{date} {safe} ({f.stem[:8]}).md").write_text(mask("\n".join(body)), encoding="utf-8")
    return True


def chat_index(out):
    rows = []
    for p in out.glob("*.md"):
        if p.name == "README.md":
            continue
        title = p.read_text(encoding="utf-8").split("\n", 1)[0].lstrip("# ").strip()
        rows.append((p.name[:10], p.name, title))
    rows.sort()
    lines = ["# Чаттар тізімі\n", "| Күні | Чат |", "|---|---|"]
    lines += [f"| {d} | [{t.replace('|', '/')}](<{n}>) |" for d, n, t in rows]
    (out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rows)


def main():
    if VAULT.exists():
        print("obsidian:", copy_tree(VAULT, REPO / "obsidian"), "файл жаңарды")
    mem, index = 0, REPO / "memory" / "MEMORY.md"
    lines = index.read_text(encoding="utf-8").splitlines() if index.exists() else []
    for d in PROJECTS.glob("*/memory"):
        mem += copy_tree(d, REPO / "memory")
        src = d / "MEMORY.md"
        if src.exists():  # each project has its own index: merge lines, one per memory file
            lines += src.read_text(encoding="utf-8").splitlines()
    merged, seen = {}, []
    for ln in lines:
        m = re.search(r"\]\(([^)]+\.md)\)", ln)
        k = m.group(1) if m else ln
        if k not in merged:
            seen.append(k)
        if ln.strip():
            merged[k] = ln  # the later (project) line wins over the repo copy
    index.write_text("\n".join(merged[k] for k in seen if k in merged) + "\n", encoding="utf-8")
    print("memory:", mem, "файл жаңарды")
    out = REPO / "chats"
    out.mkdir(exist_ok=True)
    for f in PROJECTS.glob("*/*.jsonl"):
        convert_chat(f, out)
    print("chats:", chat_index(out), "чат")
    for p in list((REPO / "obsidian").rglob("*")) + list((REPO / "memory").rglob("*")):
        if p.is_file() and p.suffix.lower() in (".md", ".json", ".txt", ".csv"):
            s = p.read_text(encoding="utf-8", errors="replace")
            if mask(s) != s:
                p.write_text(mask(s), encoding="utf-8")


if __name__ == "__main__":
    main()
