---
name: github-knowledge-repo
description: Public GitHub repo bekassyl-knowledge (target owner bekasylauez-spec) holds Obsidian vault + memory + chat texts; how to update it
metadata:
  node_type: memory
  type: reference
  originSessionId: f81d222c-a60d-46ab-a379-ee032f398e22
  modified: 2026-11-04T17:48:41.425Z
---

2026-10-31 the user asked to put all chat knowledge on GitHub; chose **public** repo `https://github.com/abylayotep/bekassyl-knowledge`.
Local clone: `C:\Users\Admin\Documents\bekassyl-knowledge` (folders `obsidian/` = copy of Bekassyl vault, `memory/`, `chats/` = .jsonl → md via scratchpad `chats2md.py`, text only, no tool output).

**How to update:** re-copy vault/memory, re-run converter, mask phones/emails (public repo), drop `_sync/telegram_state.json` and `.obsidian/workspace*.json`, secret-scan, commit as `abylayotep <[email жасырылды]>`, push. No `gh` CLI: token from `git credential fill`; send API JSON with Cyrillic via a UTF-8 file (`--data-binary @file`), inline curl JSON breaks.

2026-10-31: user said to keep it on account **bekasylauez-spec** (personal user, no credential stored here). Transfer from abylayotep requested via API; it waits for acceptance by email on bekasylauez-spec. After acceptance: `git remote set-url origin https://github.com/bekasylauez-spec/bekassyl-knowledge.git`; pushing needs that account's login (user signs in via Git Credential Manager), or abylayotep added as collaborator.

**Final (2026-10-31):** transfer needs email acceptance, so the user forked instead: `https://github.com/bekasylauez-spec/bekassyl-knowledge` (public fork of abylayotep/bekassyl-knowledge, verified 742 files). Update flow: push to abylayotep (credential stored), then user clicks **Sync fork → Update branch** on the bekasylauez-spec repo. User is signed in to bekasylauez-spec only in Yandex Browser (don't drive it); give one link + one button, link via `Set-Clipboard`. That account also has private repo `bekasyl-kzh-km`.

**Update 2026-10-31 (current):** this PC now pushes straight to bekasylauez-spec (origin `https://[email жасырылды]/...`, GCM credential works) — no more abylayotep/Sync fork. Repo has `tools/build.py` (vault+all projects' memory with MEMORY.md line-merge+chats, masking), `tools/setup.ps1` (new PC: `irm .../tools/setup.ps1 | iex`), `tools/update.ps1` (pull → restore /XO → build → commit → push). «гидхабты жаңарт» = run update.ps1. User will use the account on several PCs; work folder must be `D:\РАБОЧКА` on each so memory key `D---------` matches. D:\РАБОЧКА itself is 64 GB (DWG) — not for GitHub; OneDrive is running here, sync of files not set up yet.

**Two PCs on LAN (2026-10-31):** this PC DESKTOP-0BGBHI9 (192.168.0.107, Ethernet was Public; old read-only share `D` of D:\ exists; Tailscale only this PC) is the MAIN. Repo scripts: `tools/share-main.ps1` (admin: Ethernet->Private, firewall groups, share РАБОЧКА FullAccess for Admin) and `tools/connect.ps1` (other PC, admin: cmdkey, symlink D:\РАБОЧКА -> \\DESKTOP-0BGBHI9\РАБОЧКА, then setup.ps1). User runs them — I must not change security/network settings myself. One-liners: `iex (irm URL).TrimStart([char]0xFEFF)` (BOM breaks plain irm|iex).

**Result 2026-10-31:** Admin has NO password (user refuses one) → network logon failed. User chose open LAN access: ran `tools/share-open.ps1` (share РАБОЧКА + NTFS: Все=Change/Modify) and turned off «Общий доступ с парольной защитой» (Гость enabled). Second PC opened \\192.168.0.107\РАБОЧКА and ran `D:\РАБОЧКА\0_ЕКІНШІ_КОМПЬЮТЕРДІ_ҚОСУ.cmd` (connect.ps1) — user says done; not verified from here (Get-SmbSession needs admin). Launchers on Desktop: RABOCHKA-share.cmd, RABOCHKA-parolsyz.cmd.

**Bug fixed locally 2026-10-31 (not pushed yet):** connect.ps1 had `"\$h\РАБОЧКА"` (single backslash) in place of `"\\$h\..."`, so it could never find the share or create the D:\РАБОЧКА symlink. Second PC = 192.168.0.133 (seen in SMB connections on port 445). The user got a manual one-liner for the symlink; push the fix with the next update.ps1.

**Auto-sync (2026-11-04, user asked: «все важные инфо после завершения в гите», a new PC must work like BEKA-1/2):**
- `~/.claude/settings.json` hooks (written by `tools/install_autosync.py`, exec form `powershell.exe` + args, async): **Stop** → `tools/autosync.ps1` (at most every 10 min), **SessionEnd** → `autosync.ps1 -Force`. autosync starts `update.ps1 -Quiet` hidden/detached. Log: `%LOCALAPPDATA%\bekassyl-sync\sync.log`; `last-ok.txt`, lock `sync.lock`.
- `update.ps1`: pull → `build.py restore` (files another PC changed are put here only if missing here or unchanged since last sync; same-after-masking files untouched, so real phones stay) → `build.py` → commit/push. Vault = `D:\РАБОЧКА\Bekassyl` if it exists.
- `build.py` now compares content (local wins) and also collects **scripts**: `%TEMP%\claude\*\*\scratchpad\**\*.{cs,py,ps1,lsp,bas,vb}` ≤500 KB → `scripts/<session8>/`, skips files with secret-like text. First run: 471 scripts, 135 chats.
- `setup.ps1` (new PC): Git+Python via winget, clone, restore only missing files (skipped on the LAN PCs where D:\РАБОЧКА / memory are links), `obsidian-vault.ps1`, install hooks, first sync (GitHub sign-in as bekasylauez-spec).
- BEKA-2 launcher: `D:\РАБОЧКА\.claude\link-git.cmd` → log back to `D:\РАБОЧКА\.claude\link-git-<PC>.log`. Copies in repo: `tools/lan-*.ps1`.
- Before pushing new kinds of content, scan for secrets (public repo). The graph.json numbers [тел. жасырылды]/87369301206 are false phone hits.

Related: [[obsidian-log-work]], [[shared-memory-two-pcs]]
