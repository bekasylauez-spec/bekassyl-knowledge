---
name: github-knowledge-repo
description: Public GitHub repo bekassyl-knowledge (target owner bekasylauez-spec) holds Obsidian vault + memory + chat texts; how to update it
metadata:
  node_type: memory
  type: reference
  originSessionId: f81d222c-a60d-46ab-a379-ee032f398e22
  modified: 2026-10-31T09:06:30.262Z
---

2026-10-31 the user asked to put all chat knowledge on GitHub; chose **public** repo `https://github.com/abylayotep/bekassyl-knowledge`.
Local clone: `C:\Users\Admin\Documents\bekassyl-knowledge` (folders `obsidian/` = copy of Bekassyl vault, `memory/`, `chats/` = .jsonl → md via scratchpad `chats2md.py`, text only, no tool output).

**How to update:** re-copy vault/memory, re-run converter, mask phones/emails (public repo), drop `_sync/telegram_state.json` and `.obsidian/workspace*.json`, secret-scan, commit as `abylayotep <[email жасырылды]>`, push. No `gh` CLI: token from `git credential fill`; send API JSON with Cyrillic via a UTF-8 file (`--data-binary @file`), inline curl JSON breaks.

2026-10-31: user said to keep it on account **bekasylauez-spec** (personal user, no credential stored here). Transfer from abylayotep requested via API; it waits for acceptance by email on bekasylauez-spec. After acceptance: `git remote set-url origin https://github.com/bekasylauez-spec/bekassyl-knowledge.git`; pushing needs that account's login (user signs in via Git Credential Manager), or abylayotep added as collaborator.

**Final (2026-10-31):** transfer needs email acceptance, so the user forked instead: `https://github.com/bekasylauez-spec/bekassyl-knowledge` (public fork of abylayotep/bekassyl-knowledge, verified 742 files). Update flow: push to abylayotep (credential stored), then user clicks **Sync fork → Update branch** on the bekasylauez-spec repo. User is signed in to bekasylauez-spec only in Yandex Browser (don't drive it); give one link + one button, link via `Set-Clipboard`. That account also has private repo `bekasyl-kzh-km`.

Related: [[obsidian-log-work]]
