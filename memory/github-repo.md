---
name: github-repo
description: Whole «D:\Бекасыл КЖ КМ» folder is pushed to private GitHub repo bekasylauez-spec/bekasyl-kzh-km (LFS); memory copy lives in _Стандарт_КЖ/Claude_жады
metadata:
  node_type: memory
  type: reference
  originSessionId: 72af3b3f-2397-48af-af38-773774531e1c
  modified: 2026-10-31T09:26:45.399Z
---

**Private** repo of BEKA-2's work folder, not the public knowledge repo [[github-knowledge-repo]] that the auto-sync pushes.
Private repo https://github.com/bekasylauez-spec/bekasyl-kzh-km (created 31.10.2026, user chose «бүкіл папка, жабық»). gh CLI logged in as bekasylauez-spec (device flow: run `gh auth login --web` in background, the user enters the code — a Terminal-panel tab got stuck on the Y/n prompt).

- Big files go through Git LFS (`.gitattributes` at the repo root — the user once moved it into «Новая папка»; without it .rvt would go to plain git and GitHub rejects them).
- `.gitignore` drops Revit auto backups `*.0001.rvt` and `Архив/*.rvt` — free LFS quota is 10 GiB, already ≈4.5 GB used; commit models rarely.
- Copy of what I learned: `_Стандарт_КЖ/Claude_жады/` = CLAUDE.md + memory/ + agents/. Refresh it from `C:\Users\beka\.claude\...` before each push, so it matches [[kzh-standard-folder]].
