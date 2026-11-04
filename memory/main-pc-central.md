---
name: main-pc-central
description: "All work is stored on the main PC BEKA-1 (ex DESKTOP-0BGBHI9, 192.168.0.107) in D:\\РАБОЧКА; the second PC opens \\\\192.168.0.107\\РАБОЧКА, never the old read-only `d` share"
metadata:
  node_type: memory
  type: project
  originSessionId: f81d222c-a60d-46ab-a379-ee032f398e22
  modified: 2026-11-04T17:30:07.773Z
---

2026-10-31 the user said: «Енді барлығын осы жақта жинайсың». The main PC is DESKTOP-0BGBHI9 (192.168.0.107), the one this Claude session runs on. Everything goes there: drawings, PDFs, LIRA models, and the knowledge base.

**Why:** two PCs are linked by LAN cable, and the user wants one shared work folder that works like a server. The user refuses a Windows password, so password-protected sharing is off and `РАБОЧКА` is shared to Все with Change rights.

**How to apply:**
- Save results only to `D:\РАБОЧКА\…` on this PC (see [[save-in-project-folder]]).
- The second PC (Windows 10, runs the Claude app with Remote Control into this session) must open `\\192.168.0.107\РАБОЧКА`. The old share `d` (all of D:\) is read-only. The user hit "can't delete" through it on 2026-10-31.
- Files deleted over the network skip the Recycle Bin.
- I cannot control the second PC from here. To act there, the user runs things there or opens Claude on that PC.
- Knowledge sync goes through GitHub, see [[github-knowledge-repo]].
- 2026-10-31 the user said «рабочкадағы база осы компта болуы керек, сол жақтағы білімді қолдана жұмыс жасауым керек». The Obsidian vault was moved to `D:\РАБОЧКА\Bekassyl` (590 files, verified). `C:\Users\Admin\Documents\Bekassyl` is now a junction to it, so build.py/update.ps1 still work. obsidian.json points to the new path (backup at obsidian.json.bak). The old folder went to the Recycle Bin. Read and write rules only in this vault. The second PC should open `D:\РАБОЧКА\Bekassyl` (its symlink to the share) as its vault, not its own Documents copy.
- 2026-10-31 the user sent a migration checklist for the second PC (compare its Documents\Bekassyl with the share, robocopy /XC /XN /XO, repoint obsidian.json, rename the old copy to «Bekassyl (ескі көшірме 31.10)»). It reached this session on the main PC. Here Documents\Bekassyl is the junction, so the copies were identical (593 = 593). Nothing was renamed, because renaming the junction would break build.py/update.ps1. Before any vault migration step, check `hostname` and the `LinkType` of Documents\Bekassyl.
- 2026-11-04 renamed: this main PC DESKTOP-0BGBHI9 → **BEKA-1** (IP still 192.168.0.107, `\\BEKA-1\РАБОЧКА` works). Second PC (Win10, ex DESKTOP-U0SESAK) renamed **BEKA-2** the same day, 192.168.0.133, verified by ping/DNS. User wanted «БЕКА 1/2»; I advised Latin + hyphen (no space/Cyrillic). Renaming is a system setting: give the user the command, do not run it.
- BEKA-2 also has its own local folder `D:\Бекасыл КЖ КМ` (Revit КЖ/КМ work, `_Стандарт_КЖ`, private repo bekasyl-kzh-km). BEKA-1 cannot see it; notes that cite it are BEKA-2 facts. On BEKA-2 `D:\РАБОЧКА` is a link to the share, so `D:\РАБОЧКА\…` paths work on both PCs.
