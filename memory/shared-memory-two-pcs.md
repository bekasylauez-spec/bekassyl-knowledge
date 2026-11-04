---
name: shared-memory-two-pcs
description: "Claude memory is one shared folder D:\\РАБОЧКА\\.claude\\memory on BEKA-1; BEKA-1 links via junction, BEKA-2 via symlink set up by link-memory.cmd"
metadata:
  node_type: memory
  type: project
  originSessionId: 146fd8e6-8f0c-4e5e-9625-7c635097f701
  modified: 2026-11-04T17:48:43.719Z
---

2026-11-04 the user wanted both PCs to use each other's data live: a change made on one should show on the other at once.

Setup:
- The real memory folder is `D:\РАБОЧКА\.claude\memory` on BEKA-1 (shared as `\\BEKA-1\РАБОЧКА`).
- BEKA-1: `C:\Users\Admin\.claude\projects\D---------\memory` is a **junction** to it. Backup of the old folder: `memory.bak-2026-11-04` next to it (56 files, hashes matched).
- BEKA-2: the user runs `D:\РАБОЧКА\.claude\link-memory.cmd` (asks for admin) → `link-memory.ps1`. It fixes `D:\РАБОЧКА` symlink if it still points to the old name DESKTOP-0BGBHI9, moves BEKA-2-only notes into the shared folder, merges MEMORY.md lines, keeps differing BEKA-2 copies in `_с_BEKA-2_<stamp>`, renames the old folder to `memory.bak-<stamp>`, then makes a **symlink** to the share. Junctions can't target network paths, so the symlink needs admin.
- **Done 2026-11-04 22:38 (verified from log `D:\РАБОЧКА\.claude\link-memory-BEKA-2.log`):** BEKA-2 user is `beka`, `C:\Users\beka\.claude\projects\D---------\memory` = SymbolicLink → `\\BEKA-1\РАБОЧКА\.claude\memory` (57 files seen). BEKA-2 had no own memory there, so nothing was merged. Its `D:\РАБОЧКА` → `\\192.168.0.107\РАБОЧКА`. BEKA-2 also has a project folder `D---------------` (another work folder, not linked; contents unknown).
- I can't read BEKA-2's disk from here. To check it, the user re-runs `link-memory.cmd`; the script writes its log back to `D:\РАБОЧКА\.claude\link-memory-<PC>.log`.
- Obsidian on BEKA-2: `D:\РАБОЧКА\.claude\link-obsidian.cmd` (no admin) sets `%APPDATA%\obsidian\obsidian.json` (no BOM!) so only `D:\РАБОЧКА\Bekassyl` opens, moves BEKA-2-only notes in, keeps differing newer ones in `99_Changelog\_с_BEKA-2_<stamp>`. `link-git.cmd` runs the same step through setup.ps1.
- **R:\ sessions (04.11.2026 23:40):** BEKA-2 also opens Claude in `R:\` (= `\\192.168.0.107\рабочка`) → project key `R--`, whose memory was empty. `tools/claude-shared.ps1` (called by setup.ps1, so by `link-git.cmd`, and by link-memory.ps1) finds every drive whose root has `.claude\memory\MEMORY.md` (also from `HKCU:\Network` when elevated) and makes `projects\<key>\memory` a **junction** to the local `D---------\memory` (local target → no admin; it then follows the UNC symlink). Tested on BEKA-1 with `subst R:` + fake profile: 80/80. BEKA-2 not verified until the user runs `link-git.cmd` and the log comes back.
- **Global rules:** the same script writes `tools/CLAUDE.global.md` into `%USERPROFILE%\.claude\CLAUDE.md` as a marked block `<!-- bekassyl-global:start … end -->`, keeping the user's own text (BEKA-2 already had one) and a `.bak`. Edit the rules in `tools/CLAUDE.global.md`, never inside the block. Installed on BEKA-1 04.11.
- The Obsidian vault `D:\РАБОЧКА\Bekassyl` was already shared the same way, see [[main-pc-central]].

**Why:** two Claude installs used separate memory, so rules learned on one PC were missing on the other.

**How to apply:**
- Memory written on either PC is the same file, so both PCs see it. A running session loads MEMORY.md only at start, so changes from the other PC show up in the next chat.
- Before writing, re-read the file you're editing: the other PC may have changed it.
- If BEKA-1 is off, BEKA-2 has no memory at all. The backup `memory.bak-*` on BEKA-2 is the fallback.
- GitHub sync ([[github-knowledge-repo]]) still works through the junction. `tools/connect.ps1` default host was changed locally to BEKA-1 (not pushed yet).
