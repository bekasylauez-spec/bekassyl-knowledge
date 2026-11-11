---
name: b109-km-chain-1011
description: "В109 Цех Блок 1 КМ Revit — chain with the new slot step 13, state on 10.11.2026 evening, open items"
metadata:
  node_type: memory
  type: project
  originSessionId: b9d48af9-f7a2-4623-89d1-541fa9dfc459
  modified: 2026-11-10T11:50:49.224Z
---

В109 КМ model (D:\Бекасыл КЖ КМ\Завод_В109_КМ, scripts _авто\revit): chain is now gen.py → b109_01 → b109_10 → b109_11 → nodes.py (run without -I, it imports gen) → b109_12 → **b109_13_slots.cs** (void «БК_паз_541x12_v3» cuts 16 Р1 slots for the узел 6 through gusset; must run after every 01/11) → b109_90 → q20. Last push a82d0c8 (10.11 ~17:40), clash 0, q20 PASS.

**Why:** user's DWG revision 10.11 10:44 + user decisions: bracing Λ/V by LIRA (rule 52), узел 6 one gusset through Р1, Р1 end 180 off the column axis, узел 7 −t8 ribs, узел 1 разрез 2-2 gusset kept wider (M24 does not fit the 150 band).

**How to apply:** R:\ (\\BEKA-1\рабочка) and D:\РАБОЧКА (shared memory, Obsidian) went offline at ~17:30 — the model copy to R:\…\КМ Чертеж\227-23-П-УВПиОС-ВП-В109-КМ (Цех Блок 1, Revit).rvt and the Obsidian/shared-memory notes for rules 53–55 are still to do when BEKA-1 is back. km-model-checker's bolt sweep counts bolt shanks through plates as "nut in solid" — check the part volume (shank Ø16×L) before trusting it. Next: drawings (sheets) after the user confirms. Related: [[km-user-node-dwg-plot-read]].

**11.11.2026 — ОД/штамп/краны в «КМ Чертеж узелдер.dwg».** ОД л.1–2 и блок «Штамп№1» были от Цех аналога (Алматы, 9 баллов, «4П-18.02.2025-КМ», РП) — переписаны по ИГИ/ТХ/ЛИРА, добавлена таблица «Нагрузки от мостовых кранов» (Q 2 т, Fmax 23,9, Fmin 10,4 кН, Lк 22,5/10,5/22,5, ПБ +10,340, ось 750). Подробно: Obsidian `15_Проекты/Завод УВПиОС В109 (Шерхан)/КМ В109 — ОД, краны, замечания экспертизы (11.11.2026).md`. Новые op в rz.cs: txtdump (+file), attdump, blkrepl, blkmtext, plotpdf "dcs":1 (окно минус view target). Ловушки: job не сохраняет — в конце `{"t":"save"}`; JSON с «\» строить в python (heredoc ломает escape).
11.11 (2): user decisions — rail 750 / ПБ +10,340 stay (КМ correct), developer Кулбай Ш. stays. Sheet 4 spec rebuilt: 39 rows, 750.17 t, formulas (`od\mk_spec.py`); Revit members.tsv: length = col 9, КМ_Масса kg = col 7 (volume wrong for tubes). Table body text must be 2.5 mm or it overflows the A3 frame; tcellset on formula cells wipes the formula — re-run tformula after.
11.11 (3): annex drawn on sheet 11 (od\mk_annex.py), spec 753.91 t. User rule: anything in LIRA/ведомость but not drawn — draw it at once («неге жасамадың»). АГСК-1 = list of norms (not material codes) → АГСК-3 needed for codes. Writing one table cell can wipe other formula cells — rewrite all + verify (od\chk_spec.py).
11.11 (4): АГСК-3 codes added to spec col 13 (od\mk_agsk3.py); 3-group format 214-xxx-xxxx; I-beams via ГОСТ 26020 codes, tubes via ГОСТ 13663 codes (noted). 753.91 t.
11.11 (5): album now «Том 14 Водоподготовка ВП-В109.dwg» (user merged; open in my acad 15844 — run jobs with -Doc). Facade marks only РФ1/РФ2/Ст1; duplicate annex removed (search ALL sheets before drawing a 'missing' element); annex marks unified БП1/Пр1/ГС1; spec styled as Цех 5BB580; new rz.cs ops tgrid/tgridset.
