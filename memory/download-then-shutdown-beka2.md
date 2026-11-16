---
name: download-then-shutdown-beka2
description: "«жүктеу біткесін компты өшір» — BEKA-2 бақылаушысы download_then_shutdown.ps1: Downloads\\*.crdownload біткенде (немесе 20 мин тоқтаса) → shutdown /t 120 (17.11.2026)"
metadata:
  node_type: memory
  type: reference
  originSessionId: dbe29fe7-4d8a-42db-bcae-45f4ee738945
  modified: 2026-11-16T19:22:51.292Z
---

17.11.2026 пайдаланушы: «қазір гуглда ревит тартылып жатыр, біткесін компты өшір» (Google Drive-тан ZIP, Chrome).

Құрал: `C:\Users\beka\.claude\shutdown_watch\download_then_shutdown.ps1` (BEKA-2, UTF-8 BOM; лог `download_watch.log`, күйі `download_status.txt`). Task Scheduler «BEKA2 download shutdown» (триггерсіз, Interactive) арқылы іске қосылады — Claude PowerShell-і job object ішінде. Соңында тапсырма өзін өшіреді, келесі жолы қайта тіркеу керек (Register-ScheduledTask + Start-ScheduledTask).
- Әр 15 с `Downloads\*.crdownload` өлшемін handle арқылы оқиды: каталогтағы өлшем ашық файлда ескіреді (0,2 ГБ көрсетті, шынында 3,3 ГБ).
- Бәрі жоғалып, 90 с жаңасы шықпаса → бітті. 20 мин өспесе (Chrome да диске жазбаса) → тоқтап қалды: ZIP толық болса (EOCD/ZIP64 тексерісі) hardlink `Revit_жүктеу_<күн>.zip` жасайды — Chrome растау күтіп тұрса дерек жоғалмасын.
- Өшірер алдында: Revit/AutoCAD/ЛИРА/Office ашық болса — өшірмейді; соңғы 5 мин ішінде тінтуір/пернетақта болса — 10 мин тыныштықты күтеді. Сосын `shutdown /s /t 120` (/t > 0 → /f өзі қосылады, сондықтан алдын ала сақтау маңызды).
- Тоқтату: сол папкада `STOP_DOWNLOAD` файлы, санақ басталса `shutdown /a`. Тест: `-DryRun -Dir <тест папка> -PollSec 1 -StallMin 0.25`.
- «Не подтвержден NNNNNN.crdownload» атауы — Chrome файлды расталмаған/қауіпті деп белгілеген болуы мүмкін; «Сохранить» растауын пайдаланушы өзі басады.

Related: [[beka2-off-shutdown-beka1]], [[main-pc-central]]
