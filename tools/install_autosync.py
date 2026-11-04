"""Add Claude Code hooks that sync the knowledge base to GitHub after Claude works.

Run: python tools/install_autosync.py
Merges into ~/.claude/settings.json (keeps everything else, replaces only our own hook entries).
Stop      -> autosync.ps1 (at most every 10 minutes)
SessionEnd -> autosync.ps1 -Force
"""
import json, pathlib, shutil, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SCRIPT = pathlib.Path(__file__).resolve().parent / "autosync.ps1"
SETTINGS = pathlib.Path.home() / ".claude" / "settings.json"


def hook(force):
    args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-WindowStyle", "Hidden", "-File", str(SCRIPT)]
    if force:
        args.append("-Force")
    return {"type": "command", "command": "powershell.exe", "args": args, "async": True, "timeout": 30}


def ours(entry):
    return any("autosync.ps1" in " ".join(h.get("args", [])) + h.get("command", "") for h in entry.get("hooks", []))


def main():
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    if SETTINGS.exists():
        data = json.loads(SETTINGS.read_text(encoding="utf-8"))
        shutil.copy2(SETTINGS, SETTINGS.with_name("settings.json.bak-autosync"))
    hooks = data.setdefault("hooks", {})
    for event, force in (("Stop", False), ("SessionEnd", True)):
        kept = [e for e in hooks.get(event, []) if not ours(e)]
        hooks[event] = kept + [{"hooks": [hook(force)]}]
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("autosync hooks ->", SETTINGS)


if __name__ == "__main__":
    main()
