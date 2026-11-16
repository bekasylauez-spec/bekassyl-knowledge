---
name: revit-own-instance-journal-folder
description: "Өз Revit 2025/2026 данамды add-in-мен іске қосу — манифест тек жеке журнал папкасынан (Addins папкасына ЕШҚАШАН: пайдаланушының ашық Revit-і оны сеанс ортасында жүктейді); құрал жинағы _Стандарт_КЖ\\BI_Group\\скрипттер (17.11.2026)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 75177c83-08cb-4a64-ab55-fbb5ebd51a19
  modified: 2026-11-16T19:24:18.264Z
---

**Оқиға (16.11.2026, BEKA-1, BI Group талдауы):** өз Revit 2026 данам үшін манифесті `%APPDATA%\Autodesk\Revit\Addins\2026\`-ға ~1,5 минутқа қойдым. Пайдаланушының сол сәтте ашық тұрған Revit 2026-сы жаңа манифесті өзі байқап, «Безопасность — Надстройка без подписи» диалогын шығарды; пайдаланушы 12 минуттан кейін басып, менің add-in-ім оның Revit-іне жүктелді. Екі дана бір арнаны (`job.txt`) тыңдап қалды. Зиян болған жоқ (жаңа жұмыс жіберілмеді, арна бұғатталды), бірақ бұл — пайдаланушы Revit-іне тию.

**Ереже:** манифесті ортақ Addins папкасына (`%APPDATA%` не `%PROGRAMDATA%\Autodesk\Revit\Addins\<жыл>`) қоймаймын — пайдаланушының Revit-і ашық болса да, жабық болса да.

**Дұрыс тәсіл (сыналған, Revit 2026.4):**
- `Revit.exe "<жұмыс папкасы>\_jrn\start.txt"` — бос журнал (`'Dim Jrn` / `Set Jrn = CrsJournalScript`). Журнал режимінде Revit журнал жатқан папкадағы `.addin`-ді жүктейді, қолтаңба диалогы шықпайды, ойнату біткен соң ашық қалады.
- Add-in (`bilive.cs` → `BILive3.dll`): pid құлпы (`_pid.txt`), жеке арна `_chan\job.txt` → фондық ағын → `ExternalEvent` (құжатсыз күйде де істейді, Idling/WM_MOUSEMOVE керек емес), Roslyn-мен скрипт құрастыру, диалог журналы.
- Модель: көшірмесін `OpenDocumentFile` + `DetachAndPreserveWorksets` арқылы жадта ашу (453 МБ ≈ 15 с); PDF экспорт та солай істейді (`doc.Export(dir, ids, PDFExportOptions)`).
- Жинақ: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\BI_Group\скрипттер\` (`build.ps1`, `start.ps1 -Year 2026`, `rv.ps1`, `dlg.ps1`, `stop.ps1`, `scripts\d01…d08, x01_pdf`, `an\render.py`, README). Жұмыс көшірмесі `D:\_claude_work\BI_Group\tool\`. Жаңа объектіге папканы `D:\_claude_work\<объект>\rv\`-ке көшіремін.

Тұзақтар: кесте графикасының bbox-ы мен парақ бойынша view-коллектор 880 кестені қайта есептетеді (>12 мин); .ps1 тек ASCII; екі үлкен модельді қатар ашпа (жад ≈ 5–6 ГБ әрқайсысы).

BEKA-1-де 16.11.2026-дан бастап Revit 2026.4 орнатылған (2025-пен қатар). Бұл тәсіл ортақ `rvjob\live.txt` арнасының мәселесін де шешеді ([[rvjob-shared-channel]], [[revit-shared-channel-private-ee]]) — менің түсіндірмем: Revit 2025 даналарына да қолдануға болады (`-Year 2025`), бірақ 2025-те сыналмаған.

Related: [[revit-own-instance-mcp-autostart]], [[revit-build-via-addin]], [[revit-no-mouse]], [[rvt-2026-files-read-strings]], [[bi-group-rules]]
