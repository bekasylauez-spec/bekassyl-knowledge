"""Collect knowledge from this computer into the repo: Obsidian vault, Claude memory, chat texts, Claude's scripts.

Run: python tools/build.py
Merges with what is already in the repo (other computers' chats stay), masks phones/emails.
"""
import json, re, shutil, sys, pathlib

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parent.parent
HOME = pathlib.Path.home()
# Shared vault in the work folder (BEKA-1/BEKA-2), else the old place in Documents
VAULT = next((p for p in (pathlib.Path(r"D:\РАБОЧКА\Bekassyl"), HOME / "Documents" / "Bekassyl") if p.exists()),
             HOME / "Documents" / "Bekassyl")
PROJECTS = HOME / ".claude" / "projects"
SCRATCH = HOME / "AppData" / "Local" / "Temp" / "claude"   # <hash>/<session>/scratchpad: AutoCAD/LIRA scripts Claude wrote
SCRIPT_EXT = {".cs", ".py", ".ps1", ".lsp", ".bas", ".vb"}
SECRET = re.compile(r"(?i)(password\s*[=:]|passwd|api[_-]?key\s*[=:]|token\s*[=:]\s*['\"]\w{12,}|ghp_\w{20,}|sk-ant-|api_hash|session_string|BEGIN [A-Z ]*PRIVATE KEY)")
SKIP_VAULT = {"workspace.json", "workspace-mobile.json", "telegram_state.json"}
TEXT_EXT = {".md", ".json", ".txt", ".csv", ".cs", ".py", ".ps1", ".lsp", ".bas", ".vb", ".canvas"}

PHONE = re.compile(r"(?<![\w/])(\+?7|8)[ \-(]*7\d{2}[ \-)]*\d{3}[ \-]*\d{2}[ \-]*\d{2}(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
REMINDER = re.compile(r"<system-reminder>.*?</system-reminder>", re.S)


def mask(s):
    return EMAIL.sub("[email жасырылды]", PHONE.sub("[тел. жасырылды]", s))


def put(f, t):
    """Write f to t (masked if text) only when the content differs. Returns True if written."""
    if f.suffix.lower() in TEXT_EXT:
        new = mask(f.read_text(encoding="utf-8", errors="replace"))
        if t.exists() and t.read_text(encoding="utf-8", errors="replace") == new:
            return False
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(new, encoding="utf-8")
        return True
    data = f.read_bytes()
    if t.exists() and t.read_bytes() == data:
        return False
    t.parent.mkdir(parents=True, exist_ok=True)
    t.write_bytes(data)
    return True


def copy_tree(src, dst):
    """Copy files whose content changed; this computer's copy wins. Nothing is deleted in the repo."""
    n = 0
    for f in src.rglob("*"):
        if not f.is_file() or f.name in SKIP_VAULT or "_sync" in f.parts or ".trash" in f.parts:
            continue
        n += put(f, dst / f.relative_to(src))
    return n


def copy_scripts(out):
    """Claude's own scripts from temp scratchpads (they vanish when Temp is cleaned)."""
    n, skipped = 0, []
    for f in SCRATCH.glob("*/*/scratchpad/**/*"):
        if not f.is_file() or f.suffix.lower() not in SCRIPT_EXT or f.stat().st_size > 500_000:
            continue
        rel = f.relative_to(SCRATCH)
        session = rel.parts[1][:8]
        text = f.read_text(encoding="utf-8", errors="replace")
        if SECRET.search(text):
            skipped.append(f.name)
            continue
        n += put(f, out / session / pathlib.Path(*rel.parts[3:]))
    if skipped:
        print("scripts skipped (secret-like):", ", ".join(skipped))
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
    # Notes merged/retired on purpose: listed in memory/.deleted (one file name per line), removed from the repo
    tomb = REPO / "memory" / ".deleted"
    deleted = {ln.strip() for ln in tomb.read_text(encoding="utf-8").splitlines() if ln.strip()} if tomb.exists() else set()
    for n in deleted:
        (REPO / "memory" / n).unlink(missing_ok=True)
    key = lambda ln: (m.group(1) if (m := re.search(r"\]\(([^)]+\.md)\)", ln)) else None)
    repo_lines = index.read_text(encoding="utf-8").splitlines() if index.exists() else []
    main_dir = PROJECTS / "D---------" / "memory"          # the shared memory of D:\РАБОЧКА: its index is the master
    dirs = [main_dir] + [d for d in PROJECTS.glob("*/memory") if d != main_dir and d.exists()]
    lines, have = [], set()
    for i, d in enumerate(dirs):
        if not d.exists():
            continue
        mem += copy_tree(d, REPO / "memory")
        for n in deleted:
            (REPO / "memory" / n).unlink(missing_ok=True)
        src = d / "MEMORY.md"
        if src.exists():
            for ln in src.read_text(encoding="utf-8").splitlines():
                k = key(ln)
                if k in deleted or (k and k in have) or (i > 0 and not k):
                    continue  # headings only from the master index
                lines.append(ln)
                if k:
                    have.add(k)
    # notes that only another computer has (in the repo, not here) keep their index line at the end
    extra = [ln for ln in repo_lines if (k := key(ln)) and k not in have and k not in deleted and (REPO / "memory" / k).exists()]
    if extra:
        lines += [""] + extra
    index.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print("memory:", mem, "файл жаңарды")
    out = REPO / "chats"
    out.mkdir(exist_ok=True)
    for f in PROJECTS.glob("*/*.jsonl"):
        convert_chat(f, out)
    print("chats:", chat_index(out), "чат")
    if SCRATCH.exists():
        print("scripts:", copy_scripts(REPO / "scripts"), "файл жаңарды")
    for p in list((REPO / "obsidian").rglob("*")) + list((REPO / "memory").rglob("*")):
        if p.is_file() and p.suffix.lower() in (".md", ".json", ".txt", ".csv"):
            s = p.read_text(encoding="utf-8", errors="replace")
            if mask(s) != s:
                p.write_text(mask(s), encoding="utf-8")


def restore(before, after, last_sync, vault, mem):
    """After git pull: bring files another computer changed into this computer's vault/memory.

    A file is put here only if it is missing here, or it was not changed here since the last sync.
    A local file whose masked text already equals the repo copy is left alone (keeps real phones/emails).
    """
    import subprocess, datetime
    out = subprocess.run(["git", "-C", str(REPO), "-c", "core.quotepath=off", "diff", "--name-only",
                          "--diff-filter=AM", before, after, "--", "obsidian", "memory"],
                         capture_output=True, text=True, encoding="utf-8", check=True).stdout.split("\n")
    since = datetime.datetime.fromisoformat(last_sync).timestamp() if last_sync else None
    put_n, kept = 0, []
    tomb = REPO / "memory" / ".deleted"
    deleted = {ln.strip() for ln in tomb.read_text(encoding="utf-8").splitlines() if ln.strip()} if tomb.exists() else set()
    for rel in filter(None, out):
        if rel in ("memory/MEMORY.md", "memory/.deleted") or rel.split("/", 1)[1] in deleted:
            continue  # index lines are merged below; retired notes never come back
        src = REPO / rel
        top, rest = rel.split("/", 1)
        dst = (vault if top == "obsidian" else mem) / rest
        if dst.exists():
            same = (mask(dst.read_text(encoding="utf-8", errors="replace")) == src.read_text(encoding="utf-8", errors="replace")
                    if src.suffix.lower() in TEXT_EXT else dst.read_bytes() == src.read_bytes())
            if same:
                continue
            if since is None or dst.stat().st_mtime >= since:
                kept.append(rel)
                continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        put_n += 1
    idx, ridx = mem / "MEMORY.md", REPO / "memory" / "MEMORY.md"
    if idx.exists() and ridx.exists():
        local = idx.read_text(encoding="utf-8")
        known = set(re.findall(r"\]\(([^)]+\.md)\)", local))
        add = [ln for ln in ridx.read_text(encoding="utf-8").splitlines()
               if (m := re.search(r"\]\(([^)]+\.md)\)", ln)) and m.group(1) not in known and (mem / m.group(1)).exists()]
        if add:
            idx.write_text(local.rstrip("\n") + "\n" + "\n".join(add) + "\n", encoding="utf-8")
    print(f"restore: {put_n} файл қойылды" + (f"; екі жақта да өзгерген (осындағысы қалды): {', '.join(kept)}" if kept else ""))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        # build.py restore <before> <after> <last_sync|-> <vault> <mem>
        a = sys.argv[2:]
        restore(a[0], a[1], None if a[2] == "-" else a[2], pathlib.Path(a[3]), pathlib.Path(a[4]))
    else:
        main()
