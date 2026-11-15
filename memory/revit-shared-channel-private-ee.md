---
name: revit-shared-channel-private-ee
description: "Екі сессияның Revit-і RBLive live.txt арнасын бөліседі — бітеліп қалады; шешім: өз Revit-ке ExternalEvent жеке арнасы (runner_rmc + rv.ps1)"
metadata:
  node_type: memory
  type: reference
  originSessionId: c55bc92b-0511-4932-9c00-c1294111057c
  modified: 2026-11-15T18:16:38.831Z
---

BEKA-1-де бір мезетте бірнеше сессия өз Revit-ін RBLive shim арқылы басқарады — бәрі `%LOCALAPPDATA%
vjob\live.txt` + `livedone.txt` бөліседі. 15.11.2026 (РМЦ): басқа сессияның Revit-і диалогта тұрып қалғанда оның жұмысы live.txt-те сағаттап тұрды, менің жұмыстарым өтпеді; бұрын бір-бірінің нәтижесін (livedone) алып кеткен.

Шешім (жұмыс істейді): `D:\_claude_work\RMC\kzh
unner_rmc.cs/.dll` + `kzh
v.ps1`:
- live.txt тек бос болса жазылады (CreateNew), басқаның жұмысын баспайды; бос сәт 5 мс-пен аңдылады; нәтиже өз файлыма (`_res_<job>.txt`), ортақ livedone-ға тек SKIP.
- Бірінші сәтті жұмыста runner Revit-ке ExternalEvent жеке арнасын орнатады (фондық ағын `_private_job2.txt` пайда болса Raise; `_private2_ok.txt` = pid). Жұмыс ішінен тіркелген Idling өңдегіші Revit-те ІСКЕ ҚОСЫЛМАЙДЫ — ExternalEvent керек.
- `rv.ps1 -B2` BEKA-2 қолтаңбасы (Run(Document, object[])) үшін; КМ `go.ps1` пен `rmc_rebuild_sheets.ps1` соған көшірілген.

**Бір Revit-те екі сессия (15.11 22:35, КМ + КЖ пилот бір pid 29428):** пилоттың шаблон-көшіру сынағы «Общий параметр BI_… несовместимы» қате терезесімен Revit-ті тоқтатты, менің жұмысым кезекте қалды. Түзетулер: `PostPrivate` кезектегі бөтен жұмысты үстінен ЖАЗБАЙДЫ (файл бос болғанша күтеді, File.Move атомарлы); `rv.ps1 -Doc "РМЦ-КМ.rvt"` (go.ps1/rmc_rebuild_sheets береді) -B2 жұмысын белсенді құжатқа емес, атымен табылған жобаға бағыттайды. Бөтен диалогты өзім баспаймын — сессияға хабар беремін (`SendMessage`), диалог мәтінін `kzh\dlg.ps1` (UI Automation) оқиды.
**.ps1 файлында UTF-8 BOM міндетті:** Windows PowerShell 5.1 BOM-сыз .ps1-ді ANSI деп оқиды → ішіндегі «РМЦ-КМ.rvt» сияқты кирилл литерал бұзылады (rv.ps1 non-B2 префиксі белсенді «Проект4»-ке түсті, «no sheet»). Жаңа .ps1 жазсам — BOM-мен сақтаймын.

Revit қайта ашылса — бірінші жұмыс қайтадан ортақ арна арқылы өтіп, жеке арнаны орнатады. Басқа сессияның процесіне (WM_MOUSEMOVE қоса) тимеймін. Байланысты: [[beka1-run-beka2-revit-scripts]], [[project-rmc-make]].
