---
name: project-b109-revit-km
description: "Завод В109 Цех Блок 1 — КМ Revit модель (08.11.2026, BEKA-2): DWG альбом «(Цех Блок 1, ЛИРА)» + В_109_v3_КМ.lir → gen.py → Revit, Алатау стилі"
metadata:
  node_type: memory
  type: project
  originSessionId: 38383950-ff15-462c-99ed-3b9b23e702df
  modified: 2026-11-09T04:58:09.868Z
---

**Request 08.11.2026:** «…КМ (Цех Блок 1, ЛИРА).dwg-ның КМ-ін Revit-те тұрғыз, алдыңғы цех (Алатау) стилінде». User confirmed the LIRA: `Том 14…\Расчет\В_109_v3_КМ.lir`.

**Files (BEKA-2):** model `D:\Бекасыл КЖ КМ\Завод_В109_КМ\227-23-П-УВПиОС-ВП-В109-КМ_Цех Блок 1.rvt`; scripts `Завод_В109_КМ\_авто\revit\`:
- `gen.py` → `members.tsv` (all members, mm, origin axis 1 × A, X along 1→28, Y A→M); `gs1.json` = ГС1 diagonals read from sheet 8 DXF.
- `b109_01_frame.cs` (project from БК_КМ.rte, grids 1–28 / A…M Latin, levels, members; type per mark, colour per mark), `b109_10_bases.cs`, `b109_90_clash.cs` (al_90 copy), `b109_91_shot.cs` + `_shots.txt` (PNG to `_тексеру\`). Run with `_Стандарт_КЖ\скрипттер\run_cs.ps1 -File … [-Lib b109_lib.cs] -Log …`.
- Library extended: `fam_03b_ibeam.cs` added 60Ш2 589×300×16×21, 60Ш3 597×300×18×25, 40Ш2, 40Ш1, 20Ш1, 30Б1, 40Б1, 45Ш1; `fam_06b_weldedI_asym.cs` → `(КМ)двутавр_сварной_несимметричный.rfa` (БМ1 250х10/640х6/200х10, top-surface line).

**Geometry decisions:** roof = one line +14.490 at A/M column faces → +15.240 ridge (slope 750/29705.5); ФФ1 Warren from section 1-1 (top nodes 3000k, bottom 1498.5+3000k, bottom chord top 12337.4 + 0.025·d); assumed НП 20Ш1, lattice □120x5 (2 per end) / □100x3 (Tekla ФФ1) — album says only «ВП 30Б1, решётка по расчёту». СВ1 Λ/V tiers 0…+5.020…+10.340, СВ2/СВ3 V above; Р1 centre +10.340 axes 3–26; БМ1 bottom +10.340 on КН 40Ш1 (950 from row); площадка from LIRA (Б7 assumed 30Б1, Б3 = К3 box). Bases: К1/К2 by узел 1 (600×950×40, 4 М42) — sheet 2 draws Б1 600×1500 / Б2 600×1790 (contradiction, ask user); СФ/СФ1/К3 anchors not in DWG (assumed).

**Nodes (08.11 evening):** user: «База 1 связ жоқ жерге, База 2 связ бар жерге»; ФФ1 НП 20Ш1 + тор □120x5/□100x3 and Б7 30Б1 confirmed. Base details from the Tekla album pdf «(Цех негізінде, сызылған парақтар)» pp. 17–19 (Б1 −40 600×1500 8×М48; Б2 −40 600×1790 8×М42; К3 узел 3 −40 970×970 4×М48; СФ узел 4 4×М20; СФ1 узел 5 4×М24) — «анкерлер жоқ» деу қате болды, Tekla альбомынан ізде. Scripts: b109_10_bases, b109_11_tube_nodes (cap halves + insert −8 + shared gusset −10, clip 0.3 mm off every support, inserts clipped at the bisector, node grouping by hit point), nodes.py → beamnodes.tsv → b109_12_beam_nodes (caps −14, fins −10 М16, stiffeners −14, purlin bolts, БМ1 ribs + М20). Clash b109_90 = 0 (10839 elements). Revit opens on monitor 2 — move it to the primary before clicking (user's AutoCAD on primary got two stray clicks once).

**LIRA rebuild (08.11 night).** User: «схеманы қате тұрғыздың, сечениелерді лирадан ал, Автокадта қате жасапты; барлығы листпен жалғанбайды, двгдағы узелдерге мұқият қара». LIRA element stiffness array value v → LIRA type number v+1 (types listed in UTF-16 «N. Двутавр …» records; checked on Р1 □100x5, СВ □160x5/□100x5, БМ1, К3 короб) — the 07.11 album mapped the roof one number off. Correct: ФФ1 ВП 20Ш1, НП □120x5, Р1/Р2 □120x5/□100x3 (Tekla «Ферма ФФ1»), БП2 40Б1, БП1 30Б1, Пр1 [27П, Р1 □100x5, Р2 □100x3, СВ1 □160x5 (both lower tiers), СВ2/СВ3 □100x5, площадка Б1 25Б1, Б2 30Б1, Б4 70Б1, Б7 45Ш1, Б3 50Ш2; ЛИРА 15 «Плита по проф.» = deck (Б5/Б6 removed). Lattice welded straight to the chords: ends cut by «БК_срез» voids on the chord faces (cuts.tsv), K-gap 20, weld beads round footprints. New library: (КМ)швеллер_ГОСТ8240_каркас (fam_07), 50Ш2 in fam_03b. Trap: an existing mark type keeps its old profile — b109_01 now copies the profile's type parameters into the mark type every run. Clash 0 (9139 elements).

**Bases by the user's own nodes (09.11).** User: «База колоннаны дұрыста… менің сызған узелымды қара, жаныңда болуы керек» — the source is **«КМ Чертеж узелдер.dwg» next to the main DWG** (Tekla album bases were wrong). Sheets 13–18: Б1/Б2 К1 −40×700×950, Б3 К2 −40×700×960, Б4 К3 −40×800×800, Б5 СФ 40Ш2 −40×700×750 (М30), Б6 СФ1 □200 −30×550×550 (М24); all 4 anchors 09Г2С (М42 else), open slots, washer −20×120×120, ribs −12 С245 h310 straight slope; plate bottom −0.400, grout 50, foundation −0.450 → columns start −0.360. Text is in SPDS proxies: read via ezdxf ProxyGraphic virtual_entities. Trap: anchor washers built in world X/Y — pass world offsets for a rotated column. Clash 0.

How to apply: always look first for the user's own node DWG beside the given file before Tekla/album. Next — оформление/листы with the user; continue with nodes (truss gussets, brace gussets, caps, welds) in the same scripts; ask the user the open points above. Related: [[project-zavod-b109-km]], [[project-alatau-ceh-km]], [[revit-mcp-bridge]].

09.11 кеш: түйіндер шарнир/қатаң бойынша қайта жасалды ([[km-node-rules-purlin-brace-base]] №5). А осі (grid A) y −744-ке сүйретіліп кеткен (28 К1 бірге кеткен) — орнына y 0 қайтарылды; жұмыс алдында Revit-те осьтердің орнын тексер (diag: grid + колонна vs members.tsv). Рабочкадағы көшірме: R:\От Шерхан\Завод\Том 14 Водоподготовка ВП-В109\КМ Чертеж\…(Цех Блок 1, Revit).rvt — модель өзгерсе қайта көшір.
