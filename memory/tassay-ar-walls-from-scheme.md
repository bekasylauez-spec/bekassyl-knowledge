---
name: tassay-ar-walls-from-scheme
description: "Tassay АР: walls replaced from «2.Схема каркаса» (370/250/120), m2 room areas recomputed — floor mapping, what was kept, method"
metadata:
  type: project
---

2026-10-20: user asked to take the wall layout from `C:\Users\Admin\Desktop\2.Схема каркаса.dwg` (mm, walls 370/250/120) into АР `D:\РАБОЧКА\ТUNAY STROY\Проект\Тассай курсы\Tassay B Blok_2021.03.22.dwg` (cm, Turkish layers) and fix the areas. Output: `...\Tassay B Blok_2021.03.22 v2 (стеналар схемадан).dwg`.

- Floor mapping (by wall overlap, user confirmed): ZEMİN↔Zemin, 1.KAT↔«2 этаж», 2.KAT↔«3 этаж», 3.KAT↔«4 этаж»; 4.KAT first copied from 3.KAT (v2, wrong) → v3: 4.KAT = copy of 1.KAT (scheme «5 этаж»). The АР has two plan rows (y≈7860 named, y≈12860 Turkish names); both were changed.
- RC comes from the USER'S scheme: block `КУПУФКП` (layer «Размеры», 26 columns/diaphragms/lift shaft) replaces АР `TAŞIYICI SİSTEM` (user correction v3, 2026-10-20).
- Every wall contour gets its own hatch (370 AR-BRSTD 0.1, 250 AR-HBONE 0.1, 120 BOX 0.4 in cm, 90°). .NET: SetHatchPattern before PatternAngle/Scale.
- User's floor numbering: 1=ZEMİN, 3=2.KAT, 4=3.KAT, 5=4.KAT; scheme «5 этаж» (old «2 этаж», mosque/lokal/buffet, = 1.KAT layout) → 4.KAT. 2 этаж (1.KAT) not in scheme — asked user.
- Area labels `yazı-mekan` / POS KUCUK: attribute ALAN = field `AcObjProp Object(_ObjId).Area ×0.0001` linked to a `m2` polyline. Edit polyline vertices in place, `db.EvaluateFields()`.
- Room method: raster 0.5 cm (old room − new walls + freed old-wall strips by axis fill), door gaps closed inside door-block bbox, merge only if ≥60% of the shared wall is gone. Scripts in session 5eb15a46 scratchpad.
- Another chat the same day made an экспликация on the scheme («2 этаж» renamed «5 этаж» with 1.KAT names) — see Obsidian `12_Чаты/2026-10-20 Схема каркаса — экспликация…`.

Related: [[plan-wall-rethickness]], [[cad-console-net-workflow]], [[obsidian-log-work]]
