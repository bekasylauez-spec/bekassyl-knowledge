---
name: disk-cleanup-rules
description: C дискісін тазалау — D дискіге тиіспе; Downloads керек емес; ескі scratchpad скрипттерін сақта
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7eaff2d3-1bbc-4cc2-b79d-28c2183dad49
  modified: 2026-10-27T08:25:21.848Z
---

C дискісін тазалағанда D дискке мүлде тиіспе. Пайдаланушы файлдарын (Downloads, құжаттар) ешқашан Remove-Item-пен біржола өшірме — тек корзинаға жібер (Shell.Application / Microsoft.VisualBasic.FileIO RecycleOption.SendToRecycleBin). 2026-10-27 Downloads Remove-Item-пен өшірілді, бірнеше минуттан кейін пайдаланушы «не бар қайтар» деді; C — NVMe SSD, TRIM қосулы, қалпына келтіру мүмкін болмады.

**Why:** D — жұмыс дискі (РАБОЧКА, жобалар); C толып қалады (2026-10-27: 9 ГБ бос → 32 ГБ).

**How to apply:** Temp, NVIDIA DXCache, браузер/pip/npm кэштері, Downloads — өшір. Ескі сессиялардың `Temp\claude\D---------\<id>` папкаларынан тек ауыр файлдарды (.output/.dxf/.dwg/.bak/.png/.pdf) өшір, скрипттерді (.cs/.py/.ps1/.scr/.dll) сақта — [[cad-console-net-workflow]], [[baitursynova-4floor-new]] соларға сілтейді. Windows.old құралмен өшпейді — пайдаланушы «Очистка диска» арқылы өшіреді.
