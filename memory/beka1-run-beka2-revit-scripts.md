---
name: beka1-run-beka2-revit-scripts
description: BEKA-1-де BEKA-2 Revit скрипттерін (send_code_to_revit форматы) іске қосу — өз Revit данам + RBLive + v113r\run.ps1; разрез нөмірі айнасы тексерілді (11.11)
metadata:
  type: reference
---

BEKA-1-де mcp-servers-for-revit жоқ (порт 8080 тыңдамайды), тек RBLive shim. BEKA-2 скрипттері (`Run(Document document, object[] parameters)` денесі, ішінде `uiapp.Idling += hnd`) былай жүреді (11.11.2026, В113 узел 1):
- Репо: `D:\Бекасыл КЖ КМ` = sparse clone (`_Стандарт_КЖ`, `Завод_В113_КМ`, `Алатау_ЦЕХ_КМ`, `Revit_оформление/_авто`), `GIT_LFS_SKIP_SMUDGE=1` + керегін `git lfs pull --include=…`. Скрипттердегі D:\Бекасыл… жолдары өзгертусіз жұмыс істейді.
- Өз Revit данам: `Start-Process Revit.exe "<rvt>"` → pid `D:\_claude_work\v113r\_pid.txt`; диалогтар `v113r\dlg.ps1`: BKLeaderShelf/RBLive «Загрузить один раз», pyRevit «Не загружать». Пайдаланушының Revit-іне тимеймін.
- `D:\_claude_work\v113r\run.ps1 -File x.cs [-Lib lib.cs] [-Log log.txt]`: runner.cs `wrap=b2` (BEKA-2 қолтаңбасы), `pid=` (екі Revit live.txt-ті бөлісетіндіктен басқа дана жұмысты қайтарады), `uiapp.Idling += hnd;` → `hnd(uiapp, null);` (RBLive онсыз да Idling ішінде; ішінен қайта жазылу «Can not subscribe…» қатесі).
- №61 разрез нөмірі: «Марка разреза» типінің көшірмесі `БК_разрез_номер_вида_зерк` (Заголовок ↔ Задняя часть ауыстырылған) + вид типі `БК_разрез_зерк` — нөмір стрелка жағына шықты. Қай разрезге керегін суреттен анықта: В113 узел 1-де тек 1-1 (5-5 қарапайым типпен дұрыс).
Related: [[revit-build-via-addin]], [[project-v113-km]]
