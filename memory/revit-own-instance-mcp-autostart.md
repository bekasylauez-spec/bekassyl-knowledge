---
name: revit-own-instance-mcp-autostart
description: BEKA-2-де өз Revit данамды тінтуірсіз іске қосып MCP көпірін (порт 8080) автоматты қосу — start.ps1 + OtstBoot add-in + rv.ps1 (13.11.2026)
metadata:
  node_type: memory
  type: reference
  originSessionId: 242ab18d-6cb6-4ce2-8994-57b53670cd6c
  modified: 2026-11-12T20:25:36.109Z
---

Revit лентасының қойындылары UI Automation-ға берілмейді, PostMessage-пен де басылмайды, сондықтан «Revit MCP Switch» батырмасын тінтуірсіз басу мүмкін емес. Шешім (13.11.2026, Отстойник):

- `D:\_claude_work\otst\boot\OtstBoot3.dll` — шағын add-in: `%LOCALAPPDATA%\rvjob\otstboot.on` бар болса, бірінші Idling-те `RevitCommandId.LookupCommandId("CustomCtrl_%CustomCtrl_%Add-Ins%Revit MCP Plugin%ID_EXCMD_TOGGLE_REVIT_MCP")` → `PostCommand`. Framework64 csc-пен `-nostdlib` + `C:\Program Files\dotnet\shared\Microsoft.NETCore.App\8.0.0` және `Microsoft.WindowsDesktop.App\8.0.0` сілтемелерімен құрастырылады (жолда бос орын бар — тек .rsp файл арқылы).
- `D:\Бекасыл КЖ КМ\Завод_Отстойник_КЖ\_авто\start.ps1 -Rvt <файл>`: өз данамды жабады, манифесті уақытша қояды, Revit-ті файлмен ашады, «Надстройка без подписи» диалогында `CommandButton_1002` (Загрузить один раз) BM_CLICK, «Open Server» хабарламасын жабады, манифесті өшіреді. pid `D:\_claude_work\otst\_pid.txt`.
- `_авто\rv.ps1`: `RvCode`/`RvFile` (сұраныс кезінде фонда WM_MOUSEMOVE жіберіп тұрады, әйтпесе «代码执行超时»), `RvIdle File Log` + `RvWait` (Idling жұмысының журналын күтеді, Revit диалогтарын жабады).
- Revit қате диалогтары: шешу батырмасының AutomationId = `4` («Удаление элементов», «Удаление опорных объектов»), OK = `1`, Отмена = `3`; OK өшірулі болса тек 4 не 3 жұмыс істейді.
- Workshared 1 ГБ файлды фонда тазалау: Idling ішінде `OpenDocumentFile(DetachAndDiscardWorksets)` → өшіру → `SaveAs` → `Close`; содан кейін Revit-ті жаңа файлмен қайта ашу (Idling ішінде OpenAndActivate жоқ).

Related: [[revit-mcp-bridge]], [[revit-no-mouse]], [[revit-build-via-addin]]
