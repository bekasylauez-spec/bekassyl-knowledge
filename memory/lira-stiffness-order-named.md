---
name: lira-stiffness-order-named
description: "LIRA stiffness list in structural order (foundation h → walls by t → columns → beams → slabs), each type commented with element name and size — user rule 15.11.2026"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9252f8e4-753b-43e2-aae3-c6e03c79625e
  modified: 2026-11-15T19:14:31.121Z
---

The user said on 15.11.2026 (Касымова, LIRA): «Жескостты ретте фундамент тольшина, стена тольшина колонна ригел тольшинасымен реттеп жаз».

**Why:** the user reads the stiffness list to check the scheme. Numbers in random order, without names, are hard to check.

**How to apply:** in every LIRA model I build or regenerate, use this order for the stiffness list:
1. foundation plate (h);
2. walls, from the thickest to the thinnest (t);
3. columns, basement first;
4. beams;
5. slabs.

Give each type a comment with the element name and its size, for example «Фундаментная плита h=800», «Стена t=300», «Колонна 600x600 (подвал)», «Ригель 450x500», «Плита перекрытия h=200». LIRA shows the comment in brackets after the type.
- In generated text, write doc 3 in this order.
- After «Сборка схем», pack with «Неиспользуемые жесткости» so that the numbers stay compact. The base model's types come first, and the attached model's types are appended after them.
- Set the comments with Жесткости → row → «Изменить…» → Комментарий. Scripts: `D:\_claude_work\Kasymova\v7\comment.ps1` for plates and `comment_bar.ps1` for bars.
- Renumbering stiffness breaks scripts that read the old numbers, for example the Revit `extract.py` for Касымова. Say so in the report.

Related: [[lira-model-by-analog]], [[project-kasymova-hotel]]
