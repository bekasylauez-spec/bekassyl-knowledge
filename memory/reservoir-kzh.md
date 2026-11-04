---
name: reservoir-kzh
description: "Резервуар КЖ (31.10.2026) — АР↔ЛИРА шешімдері, файл, менің JSON-ops плагинім, СПДС отметкалардың база деңгейі әдісі"
metadata:
  node_type: memory
  type: project
  originSessionId: 22eb71ac-88c3-4c99-9c61-2c7547468f19
  modified: 2026-10-31T13:24:25.908Z
---

Резервуар (подземный, 15000×18000, стены 250, днище 400, покрытие 300): `D:\РАБОЧКА\Резервуар\КЖ Резервуар.dwg` (шаблон көшірмесі), тапсырма `Резервуар\Задание\` (АР R6 GHV + `резервуар.zip` ЛИРА + мозаика PNG). Obsidian: `15_Проекты/Резервуар/КЖ — ход работ.md`, чек-лист сонда.

User decisions 31.10: днище консоль 500 (ЛИРА, 16000×19000; first answer «АР без консоли» changed later the same day), горловина қабырғасы 150 (ЛИРА), колонна/балкалар ЛИРА бойынша, АР-дағы 1000×1000 квадрат = приямок. Done: лист 2 (−3.700, A3 1:100, frame 0,340000), лист 3 (−0.900, A3, frame 42000,340000), лист 4 (разрезы, A2 1:50, frame 84000,340000), spec+notes on 2–3; A3 frame src 1A0B3, stamp base shifted +17400. Last edits applied in the user's open AutoCAD (uboot.ps1 + RZLISTEN, RZSTOP after), NOT saved — user saves. Армирование Фм-1 redone by vault + analog (sheets 3.1–3.6, w\gen6.py, zones2.json, Ø14 base, one pos «1»; conventions in vault 02_Фундамент/Оформление листов Фм по аналогу). Old drafts 5.1–5.4 (A3, frames x=113700/155700/197700/239700) by w\gen5.py + common.py; zones from LIRA mosaics via w\mos.py + w\zones.py (cell colour → legend bin, mapped to KZh axes); positions in ops
5_pos.json. Punching at columns → шпильки (user). Next: 5.5 шпильки, 5.6 разрез/спецификация, общие данные.

**Why:** келесі сессия АР/ЛИРА-ны қайта салыстырмай жалғастыру үшін.

**How to apply:**
- Tools: session 22eb71ac scratchpad `net\rz.cs` (rr.cs негізі + axis, levbase, moveto, layouts, save, cmd), `net\boot.ps1` (own acad + RZLISTEN), `net\job.ps1`, `w\gen1.py` (`all` = eraseregion + rebuild + save), `w\mkplot.py` + `w\snap.ps1` (wblock → accoreconsole PDF). .ps1 with Cyrillic must have UTF-8 BOM.
- Template sources: frame A2 1:100 `33C2`, A2 1:50 `244FB`, stamp `19522` + name `19523` + number `19525` (from frame 13C7D origin), axis `3201`, dim `3203`, level `3227` ("-2,000"), plane level `239E1` ("-0,080"), ground `3262`, section `238E8` (Word/Dir), title MText `3230`.
- СПДС level mark value = (Y − stored zero Y)/1000; zero is a double (295016.137) inside the object, not the SPDSRELATIONMARK. Order: clone → levbase(new zero) → levelval → mcscale → moveto [0] + sp_set [2],[1] (mcscale does not scale the points).

Related: [[kzh-template-saveas]], [[cad-dedicated-instance]], [[kzh-scheme-karkasa]]
