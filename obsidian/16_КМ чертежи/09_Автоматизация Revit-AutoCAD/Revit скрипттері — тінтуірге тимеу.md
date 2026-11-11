# Revit скрипттері — тінтуірге тимеу (11.11.2026)

Пайдаланушы: «Ревитте жұмыс жасап жатқанда неге мышка басқаруға қарсы келе береді. Мышкаға тимейтіндей жаса.»

**Себебі:** `run_cs.ps1` / `run_idle.ps1` Idling нәтижесін күтіп тұрғанда курсорды әр 0,5 с сайын жылжытатын (SetCursorPos) және Revit-ті алдыңғы планға шығаратын (SetForegroundWindow); диалог батырмалары нақты тінтуірмен басылатын (`click.ps1`, `win.ps1` Click-Text).

**Ереже:** Revit (және кез келген бағдарлама) скрипттері ешқашан SetCursorPos / mouse_event / SetForegroundWindow қолданбайды.
- Idling-ті күту — `Wait-RevitFile` (Revit терезесіне тек PostMessage WM_MOUSEMOVE, курсор қозғалмайды). Тексеріс: курсор 980,600 және фокус өзгермей, Idling 20 мс-та орындалды.
- Диалог батырмасы — UI Automation: `Press-DialogText` (TaskDialog), `Press-Button` (hwnd), `Press-At` (нүкте). Басылмаса — тоқтап, пайдаланушыға айту.
- Ортақ файл: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\скрипттер\revit_nomouse.ps1` (BEKA-2). BEKA-1-дегі RBLive үшін де осы әдіс (WM_MOUSEMOVE PostMessage).

Байланысты: ЕРЕЖЕЛЕР.md «Revit скрипттері», memory `revit-no-mouse`.
