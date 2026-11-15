---
name: revit-shared-channel-private-ee
description: Екі сессияның Revit-і RBLive live.txt арнасын бөліседі — бітеліп қалады; шешім: өз Revit-ке ExternalEvent жеке арнасы (runner_rmc + rv.ps1)
metadata:
  type: reference
---

BEKA-1-де бір мезетте бірнеше сессия өз Revit-ін RBLive shim арқылы басқарады — бәрі `%LOCALAPPDATA%
vjob\live.txt` + `livedone.txt` бөліседі. 15.11.2026 (РМЦ): басқа сессияның Revit-і диалогта тұрып қалғанда оның жұмысы live.txt-те сағаттап тұрды, менің жұмыстарым өтпеді; бұрын бір-бірінің нәтижесін (livedone) алып кеткен.

Шешім (жұмыс істейді): `D:\_claude_work\RMC\kzh
unner_rmc.cs/.dll` + `kzh
v.ps1`:
- live.txt тек бос болса жазылады (CreateNew), басқаның жұмысын баспайды; бос сәт 5 мс-пен аңдылады; нәтиже өз файлыма (`_res_<job>.txt`), ортақ livedone-ға тек SKIP.
- Бірінші сәтті жұмыста runner Revit-ке ExternalEvent жеке арнасын орнатады (фондық ағын `_private_job2.txt` пайда болса Raise; `_private2_ok.txt` = pid). Жұмыс ішінен тіркелген Idling өңдегіші Revit-те ІСКЕ ҚОСЫЛМАЙДЫ — ExternalEvent керек.
- `rv.ps1 -B2` BEKA-2 қолтаңбасы (Run(Document, object[])) үшін; КМ `go.ps1` пен `rmc_rebuild_sheets.ps1` соған көшірілген.

Revit қайта ашылса — бірінші жұмыс қайтадан ортақ арна арқылы өтіп, жеке арнаны орнатады. Басқа сессияның процесіне (WM_MOUSEMOVE қоса) тимеймін. Байланысты: [[beka1-run-beka2-revit-scripts]], [[project-rmc-make]].
