---
name: galaxy-kzh-scheme
description: "ЖК Галакси Тип А6 С2 КЖ — 2.1 пайдаланушыныкі + ЛИРА негіз (АР А9 қате); 2.2–2.7, марки, Фм-1 3.1–3.8 (53 т) «(восстановлено 17-11).dwg»-да сақталды 04.11; стены/плиты әлі жоқ"
metadata:
  node_type: memory
  type: project
  originSessionId: e166461b-bde0-4f75-9345-660eafbd0735
  modified: 2026-11-04T11:54:32.916Z
---

2026-11-04: `D:\РАБОЧКА\От Алмас аға\ЖК Галакси\Кж чертеж\2.Схема каркас для клауда.dwg`. User drew 2.1 (−4.650) and asked to copy it to the next floors and add sections.

**Decision (user):** «2,1 Қалсын. АР Қате. лирамен менің схемамды негізге ал» — the user's 2.1 + LIRA (Тип А6 С2, 03.11.2026) are the basis; AR «Блок А9» is wrong. 2.1 is 5 m deeper than LIRA (А/1–В 22,75 vs 17,75): map LIRA y≤8.0 unchanged, y≥8.875 +5000.

**Why:** I first told the user the AR was 22,75 m deep — wrong (AR and LIRA are both 17,75); check AR geometry by real coordinates before asking.

**How to apply:** done on 04.11: sheets 2.2 −0.100, 2.3 +3.950, 2.4 +7.100…+16.550, 2.5 +19.700 (+21.450/+22.400), 2.6 Разрез 1-1, 2.7 Разрезы 2-2/3-3; oc.py TOTAL 0. Wall marks См-1…11 done. AutoCAD crashed ~17:2x → work continues in `2.Схема каркас для клауда (восстановлено 17-11).dwg` (saved 18:17, has everything; the original file lacks marks/Фм). Фм-1 sheets 3.1–3.8 by analog «Аналог/3.1 Фундамент» from LIRA As CSV: base Ø16 ш.200, dop Ø10–32, third mesh under columns, lap 71d, 53,0 t; band А–Б conditional (LIRA 5 m shorter). Next: walls 4.x (analog 4.1–4.3, lap 61d), slabs 5.x. Open question: Фм sheets landscape like 2.1 vs rule [[sheet-orientation-by-building]]. Tools and details: Obsidian `15_Проекты/ЖК Галакси/КЖ — ход работ.md` + `Инструменты/`.

**User order (04.11, evening):** «Схемада ригелдер жоқ. Оларды да сыз. колонналарға марка бер. Фундаменттен соң колонна… сосын стена, ригель, плита, парапет». LIRA has beams: 464 horizontal bars of stiffness type 8. Sequence: finish Фм (3.3–3.6 analog objects + 3.7 as analog «Поперечное армирование + Разрез а-а») → beams + column marks on scheme 2.x → columns → walls → beams → slabs → parapets. See [[fm-dop-copy-analog-objects]].

**State 04.11 19:45:** user saved+closed «(восстановлено 17-11).dwg» at 19:24 — its 3.3–3.6 lack position callouts; full version = «(Фм с выносками 19-21).dwg» (copy of .bak). Фм now 3.1–3.9 (3.8 поперечное, 3.9 spec 65.9 t). Lesson: killing a python wrapper does not stop the AutoCAD job already queued; never run two pipelines; check the doc is still open before each job.

**State 04.11 late:** working file = «(Фм с выносками 19-21).dwg» (my instance). Фм 3.1–3.9 done (verify_dwg 0, oc 24 left in dense 3.5). Beams Рм-1…5 + column marks Км-1/Км-2 on 2.1–2.3 done; columns added to 2.3. Next: columns reinforcement (LIRA «Арматура в стержнях»).

**Columns (04.11 decision):** sizes per LIRA — Км-1 500×500, Км-2 600×600 («Лирада дұрыс»). Row centres stay per the scheme 23350/28850 (LIRA 23275/28825); the user said «Жоқ, солай қалсын».

Related: [[kzh-scheme-karkasa]], [[no-repeat-check-pipeline]], [[kzh-dim-text-and-shelves]]

**State 05.11 10:00:** column sheet 4.1 Км-1 done in «(Фм с выносками 19-21).dwg» (my AutoCAD instance, saved), frame at x 706779 (after a gap; 3.9 ends 644829). LIRA bar table exported (tbl02.31_1.csv; results unzipped into LIRA work). Км-1 4Ø32+4Ø20, 449.6 kg. Next: Км-2.1/2.2/2.3 sheets with the same generators, then walls 5.x from analog 4.1–4.3 (wall As from tbl01.32_2.csv). Details: Obsidian «КЖ — ход работ» 05.11.

**State 05.11 11:05:** columns done from the user's template sheet «Колонна Км-1» (1:50): 4.1 Км-1 8Ø22 (x 706779), 4.2 Км-2.1 8Ø25, 4.3 Км-2.2 12Ø25 (+Шп1), 4.4 Км-2.3 20Ø25 (+8 Шп1); generator `gen_km.py`. Next: walls (analog 4.1–4.3 Стены), then beams with the same main-bar Ø idea. Open: column выпуски from Фм-1.

**State 05.11 evening:** walls См-1…См-5 done, sheets 5.1–5.19 (5.19 ends 1726800; next sheet slot 1726800). User checked См-4 and said «қателер өте көп» → full side-by-side compare with analog 4.13/4.14 fixed: shifted frame, slanted bar-to-bar notes, stray break lines/SPDSBREAK on the cloned piece, chain texts off analog places, lost plan titles (also 5.8, 5.12, 5.18), crowded notes in the narrow piece B. Lesson: before showing any sheet, compare it zoomed against the analog sheet element by element (titles, notes shape, chains, breaks, frame position) — not only oc.py. Remaining: См-6…См-11 (analog map in Obsidian), restore FILEDIA/SECURELOAD at the end. My AutoCAD instance pid 24600 (restarted 18:1x after a stuck -PLOT sent via 'cmd' op — never send interactive commands via 'cmd').

05.11 (side session): стены См-7 (5.24–5.29, с разрезами армирования) и См-8 (5.30–5.35) готовы, PDF в «Кж чертеж». Генератор вертикали wall_vert: NOTE_MODE='zone' (выноски у своей зоны, без пересечений), PIECES0 с None, PTOP. См-9…См-11 не начаты; Подробно — Obsidian «КЖ — ход работ» 05.11 (29)–(30).
