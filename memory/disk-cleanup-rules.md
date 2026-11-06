---
name: disk-cleanup-rules
description: C дискісін тазалау — D дискіге тиіспе; Downloads керек емес; ескі scratchpad скрипттерін сақта
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7eaff2d3-1bbc-4cc2-b79d-28c2183dad49
  modified: 2026-11-06T12:44:19.316Z
---

C дискісін тазалағанда D дискке мүлде тиіспе. Пайдаланушы файлдарын (Downloads, құжаттар) ешқашан Remove-Item-пен біржола өшірме — тек корзинаға жібер (Shell.Application / Microsoft.VisualBasic.FileIO RecycleOption.SendToRecycleBin). 2026-10-27 Downloads Remove-Item-пен өшірілді, бірнеше минуттан кейін пайдаланушы «не бар қайтар» деді; C — NVMe SSD, TRIM қосулы, қалпына келтіру мүмкін болмады.

**Why:** D — жұмыс дискі (РАБОЧКА, жобалар); C толып қалады (2026-10-27: 9 ГБ бос → 32 ГБ).

**How to apply:** Temp, NVIDIA DXCache, браузер/pip/npm кэштері, Downloads — өшір. Ескі сессиялардың `Temp\claude\D---------\<id>` папкаларынан тек ауыр файлдарды (.output/.dxf/.dwg/.bak/.png/.pdf) өшір, скрипттерді (.cs/.py/.ps1/.scr/.dll) сақта — [[cad-console-net-workflow]], [[baitursynova-4floor-new]] соларға сілтейді. Windows.old құралмен өшпейді — пайдаланушы «Очистка диска» арқылы өшіреді.

ЛИРА қалдықтары (2026-11-04): негізгі салмақ `C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\work` — `<модель>#NN.<модель>`, `.f74*`, `.crsn1`, `_pv/_01/_01c` (бір модельге 3–6 ГБ). Ашық модельдің (LiraSapr терезе атауы) файлдарына тиіспе; жабық модельдердікін өшір (қайта есептеледі), `.ald/.rez/.docs` қалдыр. `data\<комп>\*.lir` — модельдер, тиіспе. Temp-тегі `Rar$*` — ЛИРА rar ішінен ашылған модель болуы мүмкін, тиіспе.

2026-11-06: 3,6 ГБ бос → 64,8 ГБ. Ең үлкен қоқыс — Temp-тегі AutoCAD `UND*.ac$` undo файлдары (632 дана, 30 ГБ) + ЛИРА Work `#NN` (~24 ГБ). Скрипт: scratchpad `cleanC.ps1`. PowerShell-де функцияны `del` деп атама — ол Remove-Item алиасы, функциядан басым. `.DOCS` папкалары (b3rig.DOCS 8 ГБ) және Downloads-тағы инсталляторлар (Revit.2025 11 ГБ, Advance Steel 5,6 ГБ) пайдаланушы рұқсатынсыз қалдырылды.

2026-11-04: C корзинасының лимиті ~16,6 ГБ (BitBucket MaxCapacity 17008 МБ) — көп нәрсе корзинаға жібермес бұрын оның көлемін тексер; толса Windows ескісін біржола өшіреді → алдымен пайдаланушыға тазалат. Steam (CS2 бірге) пайдаланушы шешімімен `D:\Steam`-ге көшірілді (robocopy /MOVE, exit 1 = сәтті), HKCU SteamPath + libraryfolders.vdf (BOM-сыз!) түзетілді; CS-ті өшірме.
