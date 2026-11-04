---
name: house-3d-web-format
description: "«Үй жобасын 3Д жаса» = three.js web brochure artifact (renders + live 3D), NOT Revit; pipeline and last project Uy_joba_14x8"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 23042271-b03d-4833-b9de-78a4b9df170c
  modified: 2026-10-30T11:27:10.723Z
---

When the user sends a house plan (PDF/photo) and asks for «3Д алдыңғыдай форматта», they mean the web brochure artifact like «Бір қабатты үй жобасы» (claude.ai/artifact/PDpKpgbqV8itpaLJW1BjXc): hero render, facts strip, exterior + interior render gallery, live three.js viewer with view buttons, rooms table, materials. User 30.10.2026: «3Д ревитте емес өз серверіңде жаса», «revit 3d моделін құру тоқтатылсын».
**Why:** these are client visualisations, not КЖ/КМ documentation.
**How to apply:** build in three.js (cdn.jsdelivr [email жасырылды]), render each view via headless Edge `#r-<view>` hash (msedge --headless=new --enable-gpu --window-size=1920,1080 --virtual-time-budget=25000 --screenshot, separate --user-data-dir per run), convert PNG→JPG, publish with `files`. No Blender on this PC. PDF pages render with WinRT Windows.Data.Pdf from PowerShell (no poppler/python). Expect the user to add living details mid-task (animals in pens, two different cars incl. a jeep, extra room renders).
Last job: D:\Бекасыл КЖ КМ\Uy_joba_14x8 (index.html + renders/), artifact https://claude.ai/artifact/ESgAK5KuBiwQm11u7iL4uy — 2 houses 14×8 (house 2 = transposed plan), 4 sheep pens 6/5/6/5 sheep, coop with hens, feed store with hay, sedan + jeep under carport.
