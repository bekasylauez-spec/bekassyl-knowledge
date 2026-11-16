---
name: disk-cleanup-rules
description: C дискісін тазалау — D дискіге тиіспе; Downloads керек емес; ескі scratchpad скрипттерін сақта
metadata:
  node_type: memory
  type: feedback
  originSessionId: 7eaff2d3-1bbc-4cc2-b79d-28c2183dad49
  modified: 2026-11-16T18:31:42.572Z
---

C дискісін тазалағанда D дискке мүлде тиіспе. Пайдаланушы файлдарын (Downloads, құжаттар) ешқашан Remove-Item-пен біржола өшірме — тек корзинаға жібер (Shell.Application / Microsoft.VisualBasic.FileIO RecycleOption.SendToRecycleBin). 2026-10-27 Downloads Remove-Item-пен өшірілді, бірнеше минуттан кейін пайдаланушы «не бар қайтар» деді; C — NVMe SSD, TRIM қосулы, қалпына келтіру мүмкін болмады.

**Why:** D — жұмыс дискі (РАБОЧКА, жобалар); C толып қалады (2026-10-27: 9 ГБ бос → 32 ГБ).

**How to apply:** Temp, NVIDIA DXCache, браузер/pip/npm кэштері, Downloads — өшір. Ескі сессиялардың `Temp\claude\D---------\<id>` папкаларынан тек ауыр файлдарды (.output/.dxf/.dwg/.bak/.png/.pdf) өшір, скрипттерді (.cs/.py/.ps1/.scr/.dll) сақта — [[cad-console-net-workflow]], [[baitursynova-4floor-new]] соларға сілтейді. Windows.old құралмен өшпейді — пайдаланушы «Очистка диска» арқылы өшіреді.

ЛИРА қалдықтары (2026-11-04): негізгі салмақ `C:\Users\Public\Documents\LIRA SAPR\LIRA SAPR 2024\work` — `<модель>#NN.<модель>`, `.f74*`, `.crsn1`, `_pv/_01/_01c` (бір модельге 3–6 ГБ). Ашық модельдің (LiraSapr терезе атауы) файлдарына тиіспе; жабық модельдердікін өшір (қайта есептеледі), `.ald/.rez/.docs` қалдыр. `data\<комп>\*.lir` — модельдер, тиіспе. Temp-тегі `Rar$*` — ЛИРА rar ішінен ашылған модель болуы мүмкін, тиіспе.

2026-11-06: 3,6 ГБ бос → 64,8 ГБ. Ең үлкен қоқыс — Temp-тегі AutoCAD `UND*.ac$` undo файлдары (632 дана, 30 ГБ) + ЛИРА Work `#NN` (~24 ГБ). Скрипт: scratchpad `cleanC.ps1`. PowerShell-де функцияны `del` деп атама — ол Remove-Item алиасы, функциядан басым. `.DOCS` папкалары (b3rig.DOCS 8 ГБ) және Downloads-тағы инсталляторлар (Revit.2025 11 ГБ, Advance Steel 5,6 ГБ) пайдаланушы рұқсатынсыз қалдырылды.

2026-11-04: C корзинасының лимиті ~16,6 ГБ (BitBucket MaxCapacity 17008 МБ) — көп нәрсе корзинаға жібермес бұрын оның көлемін тексер; толса Windows ескісін біржола өшіреді → алдымен пайдаланушыға тазалат. Steam (CS2 бірге) пайдаланушы шешімімен `D:\Steam`-ге көшірілді (robocopy /MOVE, exit 1 = сәтті), HKCU SteamPath + libraryfolders.vdf (BOM-сыз!) түзетілді; CS-ті өшірме.

2026-11-16: 18,6 ГБ бос → 31,1 ГБ, тек Claude/ChatGPT бойынша (пайдаланушы: «Claude/ChatGPT файлдарын өшір, керегін D-ге ауыстыр»). Чат тарихы (`.claude\projects`, 9,4 ГБ) мен `Documents\Codex` D-ге junction-мен көшті — [[claude-data-on-d-junctions]]; олар арқылы рекурсивті өшірме. Өшірілгені: тірі процесі жоқ және 48 сағаттан ескі сессиялардың `Temp\claude` ішіндегі .output/.png/.jpg/.dxf/.bak/медиа + NVIDIA инсталляторы (2,6 ГБ; .dwg/.pdf/.rfa мен скрипттер қалды), ротацияланған логтар, pip/pnpm кэші, `.claude-server-commander\puppeteer-cache`, `.cache\codex-runtimes\codex-primary-runtime.previous-*` (1,2 ГБ). Скрипттер: `D:\_claude_work\c_cleanup\`. Сол күні C-дегі ең үлкен қоқыс Claude емес еді (менің бақылауым): корзинадағы Revit 2026 zip (14,5 ГБ), WinRAR қалдығы `Temp\Rar$EX*` (14,8 ГБ — Revit 2026 инсталляторы, WinRAR жабық), ЛИРА work 35 ГБ, Desktop-тағы инсталляторлар 12,8 ГБ, `Temp\UND*.ac$` 4 ГБ, NVIDIA DXCache 2,2 ГБ — пайдаланушы тек Claude/ChatGPT деп сұрағандықтан бұларға рұқсатсыз тимедім, тізімін ұсындым.

2026-11-16 (жалғасы): тізімді көрген соң пайдаланушы «Иә, тазала» деді (тек корзина + WinRAR қалдығы + кэштер; ЛИРА work пен инсталляторлар бөлек шешім күтіп қалды) → 31,1 ГБ → 63,8 ГБ бос. Жасалғаны: `Temp\Rar$EX*` өшірілді (ішін қарап Revit инсталляторы екеніне, WinRAR/Setup процесі жоғына көз жеткізгеннен кейін ғана; бос `Rar$DI*` қалды); ескі (2 күннен) `UND*.ac$` 4,1 ГБ; Temp түбіндегі 152 мың кеңейтімсіз hex-атаулы файл 1,1 ГБ — бұл AutoCAD плот кезінде жасайтын CTB/PC3 уақытша көшірмелері (скриптпен көп плот → тез жиналады, қауіпсіз қоқыс); ескі .tmp/.log/.dmp; ескі DXCache 1,1 ГБ (қолданыстағы 14 файл өзі өткізіліп кетті). `.sv$`/`.bak`/`.dwg` (AutoCAD автосақтау) және қосулы Revit-тің temp папкаларына, сол күнгі Autodesk орнату қалдықтарына (`odis_download_dest`, `AdAppMgrRollBackBackup`, `*.msi` — 4,3 ГБ) тимедім. Корзина: аталған 3 үлкен файлды біржола өшірмей `D:\Users\Admin\Downloads` ішіне көшірдім (SHA256-мен), себебі Revit 2026 архивінің басқа көшірмесі D/H-та табылмады (менің шешімім — «пайдаланушы файлын біржола өшірме» ережесі бойынша; пайдаланушының бұған пікірі әлі белгісіз); қалған 38 ұсақ файл корзинада қалды. Корзинаның тек C бөлігін қарау: Shell.Application Namespace(10) элементтерін `Path -like 'C:\*'` бойынша сүз, өлшемі `ExtendedProperty('System.Size')` (`.Size` 2 ГБ-тан асса теріс шығады). Temp түбін санағанда `Get-ChildItem` емес, `DirectoryInfo.EnumerateFiles()` қолдан — 150 мың файлда Get-ChildItem 5 минуттан асады.
