---
name: beka2-off-shutdown-beka1
description: "«Бека 2 өшкенде компты өшір, бәрін сақта» — BEKA-1 бақылаушысы beka2_watch.ps1: BEKA-2 5 мин өшік → AutoCAD/Office/Revit/ЛИРА сақтау → shutdown /t 120 (16.11.2026)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 5265c02a-abbe-4f43-ad9f-e0cc6656ee83
  modified: 2026-11-15T19:41:09.773Z
---

16.11.2026 пайдаланушы: «Бека 2 өшен кезде компты сенде өшір. Барлығын сақта».

Құрал: `D:\РАБОЧКА\.claude\shutdown_watch\beka2_watch.ps1` (UTF-8 BOM; лог `watch.log`, күйі `status.txt`).
- BEKA-2-ні әр 20 с тексереді (ping аты → соңғы IP → TCP 445). Бір рет желіде көрініп, кейін 5 мин үздіксіз жауап бермесе (шлюз 192.168.0.1 де жауап бермесе — 10 мин) → сақтау → `shutdown /s /t 120`.
- Сақтау: AutoCAD — COM, тек `Saved=False` DWG `Save()` (аты жоқ/тек оқу → `D:\_claude_work\shutdown_watch\unsaved`); Word/Excel — COM; Revit — алдымен жеке ExternalEvent арнасы (`D:\_claude_work\**\_private2_ok.txt` = pid → сол папкадағы `_private_job2.txt`, РМЦ runner_rmc; РМЦ Revit-і ортақ live.txt-ті алмады), болмаса RBLive ортақ арнасы + `D:\_claude_work\Kasymova\revit\runner_kas.dll`; `IsModified` құжатқа `Save()`; арна жауап бермесе және диалог жоқ болса — WM_CLOSE + «Да»; диалог тұрса — тимейді. ЛИРА — `WM_COMMAND 0xE103` (ID_FILE_SAVE), сосын WM_CLOSE + «Да». COM-сыз AutoCAD даналары — WM_CLOSE + «Да».
- Тоқтату: `STOP` файлы осы папкада (BEKA-2-ден `R:\.claude\shutdown_watch\STOP`); өшу санағы басталса — `shutdown /a`.
- `-DryRun` — тек тізім, ештеңе сақтамайды. Тұзақ: PowerShell-де `R` — Invoke-History алиасы, функциядан басым (функция атын `Rt` қойдым).
- Claude-дың PowerShell-і job object ішінде — ұзақ бақылаушы Task Scheduler арқылы іске қосылады («BEKA2 shutdown watch», триггерсіз, қолмен Start).

Related: [[main-pc-central]], [[rvjob-shared-channel]], [[close-user-file-myself]], [[cad-dedicated-instance]]
