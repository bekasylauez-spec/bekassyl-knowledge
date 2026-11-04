---
name: kzh-standard-folder
description: "User asked to keep every approved оформление decision in D:\\Бекасыл КЖ КМ\\_Стандарт_КЖ (ЕРЕЖЕЛЕР.md + family, scripts, add-in, sample sheets)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 1627bee1-9218-4ed4-bb58-ee22da3b578f
  modified: 2026-10-17T07:36:47.782Z
---

**BEKA-2 local folder** (not on BEKA-1). Rules are also kept in the Obsidian vault ([[obsidian-first]]); keep both in step.
User (2026-10-16): «Осыған дейін саған дұрыс жасатқандарымды сақтап отыр. Дискке орын ашып». Approved decisions are collected in `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\`: ЕРЕЖЕЛЕР.md (rules in Kazakh), семейства\ (exported tag family .rfa), скрипттер\ (copies of doc_*.cs etc.), қосымша_Revit\ (KZhTagShelf), үлгі_парақтар\ (approved sheet PNGs).

Spec tables (doc_17_spec_tables.cs): per floor only on 2.1–2.4 (no summary on 2.7). The Обозначение column is filled from the element's formwork sheet («Опалубочный чертеж … <mark>»); these sheets come later with each element's reinforcement — **re-run doc_17 after adding them**.

**Why:** user wants the correct way of doing things preserved and reused, not re-explained.
**How to apply:** whenever the user approves a fix («әдемі», «дұрыс») or gives a new оформление rule, append it to ЕРЕЖЕЛЕР.md and refresh the copied script/family/sample sheet. Build new sheets (3.x, 4.x …) from these rules. Related: [[revit-kzh-oformlenie]], [[revit-tag-shelf-addin]]
