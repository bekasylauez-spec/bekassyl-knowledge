---
name: project-node-20k1-25b1
description: "КМ node 25Б1 beam → 20К1 column flange (rigid flanged), file Узлы_КМ\\БК-КМ_Узел_20К1-25Б1.rvt; I-beam + rib families; оформление still to do with the user"
metadata:
  node_type: memory
  type: project
  originSessionId: c4f44258-6943-4b10-8e73-e6f1e42efec6
  modified: 2026-10-31T14:13:18.053Z
---

31.10.2026 the user asked for «20к1 колоннамен 25б1 балканың жалғану узелын сыз». Their answers: a rigid flanged joint, attached to the column flange, in a new file from БК_КМ.rte. The model comes first; оформление is done together with them ([[feedback-oformlenie-together]]).

**Sections (ГОСТ Р 57837-2017):**
- 20К1: 196×199×6.5×10, r13, 41.4 kg/m. This is not the old ГОСТ 26020 195×200.
- 25Б1: 248×124×5×8, r12, 25.7 kg/m.

**Files and scripts:**
- Model file: `D:\Бекасыл КЖ КМ\Узлы_КМ\БК-КМ_Узел_20К1-25Б1.rvt`.
- Scripts in `_Стандарт_КЖ\скрипттер`: `uz_01_model.cs` (re-runnable), `uz_03_edges.cs`, `uz_04_audit.cs` (node audit C1–C5; q20 does not fit a joint).

**Node parts:**
- ПЛ1: end plate −20×180×420.
- ПЛ2: 4 ribs −8×95×176 with a chamfer of 20.
- Bolts: 8 HS М20×65 ГОСТ Р 52644, as DirectShape in category «Болты».
- Welds: DirectShape in category «Сварные швы»; kf 8 on the flanges, kf 5 on the web and the ribs.
- No calculation was made, since the user gave no loads. Bolt holes Ø23 are not modelled yet.

**New families in `_Стандарт_КЖ\семейства`:**
- `(КМ)двутавр_ГОСТ57837_каркас.rfa` / `_колонна.rfa` (`fam_03_ibeam.cs`):
  - parameters h, b, s, t, r;
  - the root fillets are 4 extrusions per radius, switched by type Yes/No params «скругление_rNN», so r is exact for each type.
- `(КМ)ребро_ГОСТ19903.rfa` (`fam_04_rib.cs`): face-based, chamfer c on the web side.

**API lessons:**
- In a framing family the section-side planes must be Is Reference Front/Back. Left/Right belong to the member ends; setting them on the section planes froze the beam at the template's 2500 mm.
- «Материал несущих конструкций» needs a value in the family before solids can be associated (otherwise regeneration fails). In the project it is an instance parameter.
- JoinGeometry does not work in family documents.
- A 3D view of a node must be 1:10, otherwise pen 1 exports as thick strokes.

**Final version (31.10.2026)** — the user changed the request twice: first «15 процент уклонмен … жоғарғы жағына», then «колоннаның жанынан жалғансын».
- Script `uz_07_side_slope.cs`: sloped 25Б1, 15 % falling away, rigid end plate −20×180×430 on the column flange, 8 М20×65.
- The column top is closed by ПЛ3 −10×220×230.
- The beam end is cut vertically by a face-based void «БК_срез_плоскостью»; a work-plane-based void ignores a sloped plane.
- Root-radius welds: lofted along the exact ellipse for the sloped beam, swept arcs for the column.
- Audits: `uz_09_audit.cs` plus the checker's probes `uz_10_gap_probe.cs` / `uz_11_weld_probe.cs`. km-model-checker gave ALL PASS on the 3rd round.
- Not done: оформление sheet; «Длина» counts 23 mm extra (≈0.6 kg).
- Superseded scripts: uz_01 (horizontal), uz_05 (on the column top).

Related: [[km-tube-families]], [[revit2025-plugins-families]].
