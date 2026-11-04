---
name: revit2025-plugins-families
description: "Revit 2025 plugin survey (.NET 8, КЖ/КМ add-ins) + Autodesk Help family-creation notes; read before building any new .rfa"
metadata:
  node_type: memory
  type: reference
  originSessionId: c4f44258-6943-4b10-8e73-e6f1e42efec6
  modified: 2026-10-31T12:28:38.640Z
---

On 31.10.2026 the user asked me to look for Revit 2025 plugins and to learn family creation from Autodesk Help. The notes are in `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\Revit2025_плагиндер_және_семейство_жасау.md`.

- **Plugins already installed** (2025): ModPlus (has free rebar utilities), KZhTagShelf, mcp-servers-for-revit.
- **Candidates for КЖ/КМ:** Bim-Starter (2 000 ₽/yr, includes КМ plate mass), BIM2B Template Tools, pyRevit 7.0, RevitLookup, DiRoots (freemium), RapidRebar (free).
- **Revit 2025 runs on .NET 8**, so 2024 DLLs will not load.
- **Family workflow from Autodesk:** plan → template → subcategories → framework (pin origin, set ref planes, add dimensions and lock them, label, flex) → types → geometry one layer at a time, locked to planes → flex → visibility → test in a project → type catalog.

Builds on [[km-tube-families]], which records our own API lessons on families.
