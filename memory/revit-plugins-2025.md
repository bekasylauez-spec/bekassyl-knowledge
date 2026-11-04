---
name: revit-plugins-2025
description: "Revit 2025 plugins installed 2026-10-31 (pyRevit 7, RevitLookup, ModPlus 2025 fix), guide location, DiRoots pending user form"
metadata:
  node_type: memory
  type: project
  originSessionId: 4b6a6dac-f0d8-43e4-95f8-c36276fa5695
  modified: 2026-10-31T11:01:09.771Z
---

On 2026-10-31 the user asked me to find Revit 2025 plugins online, install them all, and learn how to use each.

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
