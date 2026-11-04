---
name: revit-kzh-oformlenie
description: Гостевой дом 12-2025-КЖ/КМ — DWG sheets placed on Revit sheets (done 2026-10-10); result files and template quirks
metadata:
  node_type: memory
  type: project
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-10T15:47:04.789Z
---

Project 12-2025-КЖ/КМ (Гостевой дом, ТОО «Namark Project»), source DWGs on D:\РАБОЧКА\От Мадениет\Ресторан\КЖ\09-11-2025\2.Офис.
Done 2026-10-10: D:\Бекасыл КЖ КМ\Revit_оформление\12-2025-КЖ_КМ_Гостевой дом.rvt (from BI_Шаблон_КЖ_v3.52, detached) with 69 sheets (КЖ 1.1–8.5, КМ-1.1…КМ-3), each = drafting view with geometry-DWG (DWG_листы) + title block "(основная_надпись)" Форма 3; PDFs in \PDF. Scripts in \_авто and \Инструменты_AutoCAD.
Template quirks: title block family was customised by another firm (RAS/VSN) — I replaced org text, deleted foreign images, made nested RAS_Фамилия never show "Ошибка в фамилии". Stamp rows: type params Фамилия 2=ГИП, 3=ГАП, instance Фамилия 4=Разраб., type Фамилия 6=Н.контр.
Then (same day) built the 3D concrete model + rebar in the same .rvt (scripts model_0X / rebar_0X / rebar_colors.cs in \_авто), rebar coloured per diameter by view filters + legend "Легенда арматуры (цвета)".
User correction: Ф1 = spatial «лягушка» chair Ø12 (foot 300 / leg 96 up / top 300 / leg 96 down / foot 300, L=1092, Z-shape in plan), placed in a checkerboard 400×400 — not a flat U. Ф1 has its own yellow filter (Comments contains "Ф1").
User correction: wall verticals go up into the slab to 20 mm below its top face, capped by a U «скоба» from above — in the drawings this is pos.1* (U web 220, legs 2980/1690, staggered laps with the foundation outlets). Read the wall section 2-2 on sheets 5.x before modelling. Bars must never cross openings. Rebar colours = user's AutoCAD layer standard "диамNN" (ACI): Ø8 magenta(6), Ø10 ACI30, Ø12 red(1), Ø14 ACI102, Ø16 cyan(4), Ø18 ACI154, Ø20 green(3), Ø22 yellow(2), Ø25 ACI140; Ø28 unknown (temporarily ACI190). Full saturated colours, not soft. Colour strictly by diameter (Ф1 = Ø12 red).
User correction (columns, sheets 4.1/4.2/3.9): column bars are butt-jointed with welded накладки (L=10d, 2 per joint), joints staggered by 600 (L: -2.5/+0.5/+3.8, H: -1.9/+1.1/+4.4), bars reach +6.480 with Ск Ø16 caps; outlets Вп have 950 feet and must sit exactly under the column bars. Always read the elevation, spec and «Ведомость деталей» before modelling an element.
Beams (plans 2.2–2.4): -0.100 Рм-1 on Б,В + Рм-2 on 2,3; +3.200/+6.500 Рм-1 on А,Б,В,Г + Рм-2 on 2,3 + Рм-3 on 1,4 (model_03_beams.cs). Beam Ø20 butt-jointed with Н5 plates, staggered 500; Рм-1 cover 30/50 vs Рм-2/3 50/30 so crossing bars stack. Check the plan sheets for element layout before modelling.
Full audit 2026-10-10 (reports in \_авто\audit\audit_*.md, one per element group, made by parallel subagents reading cropped sheet PNGs): Фм-1 overhang is 700 (not 400); Пм-2 has a balcony x5800..12200 y-1700..-200; Ст-4а centre y5150, Ст-3 from y5000. Scripts now data-driven from those reports. `_diag_outside.cs` checks every rebar vertex lies inside concrete — run it after every rebuild (user complains about bars sticking out). Long scripts: MCP may answer "代码执行超时" while Revit still finishes; responses then shift by one call — re-query.
2026-10-10: КЖ sheets regenerated from the model (doc_02/03/04/09 + doc_lib.cs, run per part _d3_*/_d4_*), same numbers/names as the КЖ set; old DWG sheets renumbered "И-x.x". Sheets 1.x, 3.8, 7.7, 7.15, 7.23 (specs), 8.x (stairs) still DWG. PDF "12-2025-КЖ Гостевой дом (по модели).pdf". User: "қосымшаларын кейін қосамыз" — specs/ВРС later.
User rule (2026-10-10): EVERY sheet must be Revit-native (no DWG imports). Pipeline: subagents transcribe sheet PNGs (_авто\png\rest) to _авто\transcribe\<N>.json (format in FORMAT.md) → doc_10_native.cs builds a 1:1 drafting view (detail lines/text/filled regions) + sheet. Done natively: 1.1–1.5, 3.8, 8.3, 8.5, КМ-1.1, КМ-1.2. TODO next session: 7.7 (json missing — 3.8 agent wrote only 3.8), 7.15, 7.23, КМ-2 (jsons ready); 8.1/8.2/8.4 → model stairs from transcribe\stairs_model.md + rebar + views; КМ-3 → model steel roof from km_model.md + КМ-3_extra.json; then delete old "И-x" DWG sheets. Project Browser sheet organization switched to "все" (template default "03_Каркас" hid all sheets; user wants sheets visible there).
Not modelled yet: stairs Л-1/Л-2, ВП1/ВП2, splice plates.
**How to apply:** reuse the pipeline (split.lsp → make_geom.lsp → create.cs/reimport.cs) for similar КЖ jobs. See [[revit-mcp-bridge]], [[feedback-full-autonomy]].
