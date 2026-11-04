---
name: feedback-kzh-sheet-style
description: "User's 18.10.2026 standing rules for every КЖ/КМ Revit job — ISOCPEUR everywhere, one dimension style, reinforcement sections 1:25, straight leaders, round node callouts, native section marks"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-19T06:22:56.115Z
---

Standing rules the user gave on 18.10.2026 for all current and future work (full text in `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\ЕРЕЖЕЛЕР.md`, sections 2 and 3г):

- **Fonts and dimensions:** every text, dimension and section mark uses ISOCPEUR, and every dimension type shares one style. The `style_01_isocpeur.cs` script sets this for dimension types, text types and annotation families; run it on Idling.
- **Reinforcement sections** are drawn at 1:25.
- **Leaders:** a rebar leader runs straight out of the shelf (horizontal) and crosses every bar of the position, with a tick on each bar.
- **Node marks:** use a Revit reference callout drawn as a circle (callout tag with corner radius = half the box). The node drawing is its own drafting view, numbered with a letter. Include every node the original has.
- **Section marks:** all of them must be Revit's own markers, linked to their views. A marker's number = the viewport detail number. When the marker needs extents other than the crop, use a reference section of type «…_ссылка» with an empty reference label.

- **Hoops and caps (19.10.2026):** hoops get 135° hooks at both ends that wrap the corner bar, with a straight part of at least 100 mm (hook type «КЖ_хомут_135°_100»). Hoops and caps sit tight on the bars. L = outer sides + hook ends.
  - Adding hooks with SetHookTypeId flips the set downward and changes the tag prefix. Always re-check both (scripts rebar_08*).
- **Ведомость деталей (19.10.2026):** every bar sketch is a family («КЖ_эскиз_хомут», «КЖ_эскиз_скоба», nested «КЖ_текст_метка») whose A/B/L the КЖ add-in (v12, KZhSketch.cs) fills from the model. Never use DWG lines for sketches.

- **Positions linked inside an element (19.10.2026):** editing one rebar set (size, hooks, plan move) must change all stacked sets of the same position in that element (column), never other elements. Done by add-in v13 (KZhRebarSync.cs). The project must keep working for others without AI, so behaviour lives in the add-in, not in scripts. Install package: `_Стандарт_КЖ\қосымша_Revit`.

**Why:** the user rejected drawn or invented annotation. Everything must come from Revit and look uniform across the whole set.

**How to apply:** apply these rules by default on every new sheet and project, without being asked again. Related: [[feedback-text-height]], [[kzh-standard-folder]], [[originals-are-dwg]].
- Use the project's own template families first (user 19.10.2026: «Анатация и семействоларды поный оқы осыларды пайдаланып жаса»): text leaders = «(типовая_аннотация)текст_с_выноской» (_засечка/_точка), rebar = «(марка)арматурный_стержень» tags, breaks = «Элементы узлов» break families; don't invent ad-hoc types or draw symbols with lines. List families before building anything new.
- **КМ in colour (29.10.2026, «3д моделде оформлениеде барлығы цветной тұрсын»):** steel members coloured per mark by view filters «КМ_<марка>» in every КМ view + per-block 3D views, colour legend on sheet 1, PDF exported in colour (ЕРЕЖЕЛЕР §7).
