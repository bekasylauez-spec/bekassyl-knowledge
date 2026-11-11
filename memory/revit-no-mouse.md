---
name: revit-no-mouse
description: Revit/кез келген UI скрипті тінтуірге, курсорға, фокусқа тимейді — PostMessage + UI Automation, revit_nomouse.ps1 (11.11)
metadata:
  type: feedback
---

Revit скрипттері SetCursorPos / mouse_event / SetForegroundWindow қолданбайды. Idling күту — `Wait-RevitFile` (PostMessage WM_MOUSEMOVE Revit терезесіне), диалог — UIA (`Press-DialogText`, `Press-Button`, `Press-At`) — бәрі `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\скрипттер\revit_nomouse.ps1`. run_cs.ps1, run_idle.ps1 (екеуі), 3602 run.ps1/win.ps1, Алатау click.ps1 осыған ауыстырылды.

**Why:** пайдаланушы 11.11.2026: «Ревитте жұмыс жасап жатқанда неге мышка басқаруға қарсы келе береді. мышкаға тимейтіндей жаса» — run_cs курсорды әр 0,5 с жылжытатын.

**How to apply:** жаңа скриптте де тек осы файлды dot-source ет; UIA басылмаса — тінтуірге көшпе, тоқтап пайдаланушыға айт. Ескі ережені ауыстырады: [[revit-mcp-bridge]] «real mouse click», [[revit-build-via-addin]].
