---
name: template-catalog
description: "BI КЖ Revit template studied 19.10.2026 — catalog of 92 legend nodes, 519 schedules, view templates, groups; use template's own schedules (СА/ВМ/ВРС/ВД) for specs"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-19T17:36:08.880Z
---

Catalog: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\шаблон_каталог\ШАБЛОН_КАТАЛОГ.md` (index) + `легенды_01-30.md`, `легенды_31-60.md`, `легенды_61-92.md` (each node: what / how built / reuse), `кестелер_шаблондар.md` (schedule system, view templates, naming, groups), `легенды\*.png`. Read it before drawing any node, schedule or view in a new project — the template usually already has it (e.g. «(Фундамент)Сетка С1» legend, parametric nodes «(элементы_узлов)узел_нахлеста», «узел_свай»).

Specs (user 19.10.2026 «Ведомость спецификацияны осыныкын пайдаланацық. Ревитті автоматты түрде есептейтін»): use the template's per-mark schedules `(<Группа>)_<Марка>_2СА / 3ВМ(сборка) / 5ВРС / 4ВД`, not the KZhSpec add-in tables. They count ALL rebar of the mark → only one representative element keeps BI_марка_конструкции = mark (others «<mark> (копия)»); the element itself is an assembly with key «Марка по стандарту» = «Колонна Км-1»/«Фундамент Фм-1» (concrete in 3ВМ); product assemblies keep Комментарии empty. Scripts doc_39_tpl_specs_a/b/c.cs. Assembly type names can be set only after the creating transaction commits.

Related: [[revit-kzh-oformlenie]], [[feedback-kzh-sheet-style]], [[kzh-standard-folder]]
