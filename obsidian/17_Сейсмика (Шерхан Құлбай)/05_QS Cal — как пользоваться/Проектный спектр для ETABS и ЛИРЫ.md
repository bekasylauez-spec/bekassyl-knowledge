---
title: "Проектный спектр Sd / Sdv — для ETABS и ЛИРЫ"
tags: [QS-Cal, инструкция]
url: "https://qs-cal.netlify.app/spectrum/spektr_proektny"
изучено: 2026-10-19
---

# Проектный спектр Sd / Sdv — для ETABS и ЛИРЫ

**Открыть:** https://qs-cal.netlify.app/spectrum/spektr_proektny

Расчётный спектр с q (СП РК EN 1998-1 п. 3.2.2.5, S = 1 по НТП, без ветви TD, нижняя граница β·ag) + вертикальный Sdv (2,25·avg/qv, плато до TC, спад (TC/T)ⁿ).

## Поля
- **Горизонтальный:** agR/g, γI, тип грунта (TB/TC авто: II → 0,20/0,64), q, β (нижняя граница), S (=1,0 для НТП), g (Scale Factor ETABS; ЛИРА 9,81/9,825).
- **Вертикальный:** avg/g (пусто = 0,9·agR, табл. 4.7), qv, γIv, TC(верт), n; шаг T, Tmax.
- Разделитель для .txt: **запятая** (русская Windows) / точка.

## Выход
- **ETABS:** Define → Functions → Response Spectrum → **From File** → SPEC-H.txt / SPEC-V.txt; Period vs Value; damping 0,05; RS-X (U1), RS-Y (U2) — SPEC-H, RS-Z (U3) — SPEC-V; **Scale Factor = g**. Путь без кириллицы! Перечитать функцию — неверный разделитель даёт 0 точек молча.
- **ЛИРА:** модуль **61** (СП РК EN 1998) строит спектр сам — карточки в м/с² для сверки с колонками **Beta Hor / Beta Vert**. «Копировать для ЛИРЫ» — если спектр задаётся вручную (модуль **41**).
- Word-отчёт с формулами (для экспертизы).

---
↩ [[QS Cal — как пользоваться (индекс)]] · [[QS Cal — сайт калькуляторов]]
