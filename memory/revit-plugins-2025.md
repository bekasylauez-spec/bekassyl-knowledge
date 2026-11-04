---
name: revit-plugins-2025
description: "Revit 2025 plugins on both PCs (BEKA-1: pyRevit 7, RevitLookup, ModPlus fix; BEKA-2: ModPlus, KZhTagShelf, mcp-servers) + Autodesk family-creation workflow"
metadata:
  node_type: memory
  type: project
  originSessionId: 4b6a6dac-f0d8-43e4-95f8-c36276fa5695
  modified: 2026-10-31T11:01:09.771Z
---

**BEKA-1** — on 2026-10-31 the user asked me to find Revit 2025 plugins online, install them all, and learn how to use each.

Installed, each signature checked (Valid):
- pyRevit 7.0.0.26278 (per-user). Code in `%APPDATA%\pyRevit-Master`.
- RevitLookup 2025.2.4 SingleUser.
- ModPlus offline 26.10.30, from modplus.org/offlineinstaller.

The installers and the guide `Нұсқаулық.md`, plus full command lists, are in `D:\РАБОЧКА\Плагины Revit 2025`. A copy of the guide is in Obsidian `16_КМ чертежи/09_Автоматизация Revit-AutoCAD`.

ModPlus was broken for Revit 2025 before this:
- only the core was installed; the 89 `mpr*` functions were 2024-only (.NET 4.8);
- the auto-updater crashed on an mp.Core 1.0/1.2 mismatch.

The offline msi fixed both. To check this again, look for `mpr*_2025.dll` under `%APPDATA%\ModPlus\Functions\Revit` and the registry key `HKCU\Software\ModPlus\Plugins\<fn>`, which lists the supported years.

Still open:
- DiRootsOne and ProSheets need the diroots.com form (name, email). The user fills it and drops the exe into `Установщики\`. Silent install: `/i // /qn accept_eula=1`.
- The user refused computer-use access to Revit, so nobody has seen the tabs load yet. Check via the Revit journal after they open it.

**Why:** the user also said «неге бұлтта жасап отырсың». Tell them plainly that the work runs locally on D:\РАБОЧКА.

**How to apply:** the ModPlus reinforcement plugins (walls, slabs, columns, beams) and Вес пластин are the most relevant for КЖ/КМ. RevitLookup helps when writing the RBLive add-ins ([[revit-build-via-addin]]).

**BEKA-2 (same day, separate survey):**
On 31.10.2026 the user asked me to look for Revit 2025 plugins and to learn family creation from Autodesk Help. The notes are in `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\Revit2025_плагиндер_және_семейство_жасау.md`.

- **Plugins already installed** (2025): ModPlus (has free rebar utilities), KZhTagShelf, mcp-servers-for-revit.
- **Candidates for КЖ/КМ:** Bim-Starter (2 000 ₽/yr, includes КМ plate mass), BIM2B Template Tools, pyRevit 7.0, RevitLookup, DiRoots (freemium), RapidRebar (free).
- **Revit 2025 runs on .NET 8**, so 2024 DLLs will not load.
- **Family workflow from Autodesk:** plan → template → subcategories → framework (pin origin, set ref planes, add dimensions and lock them, label, flex) → types → geometry one layer at a time, locked to planes → flex → visibility → test in a project → type catalog.

Builds on [[km-tube-families]], which records our own API lessons on families.
