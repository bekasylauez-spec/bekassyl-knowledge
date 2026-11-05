---
name: fbs-pb-layout
description: ФБС 2 ряда + ПБ плиты раскладка: заводской стандарт из прайса, доборы монолит, перевязка ≥300, листы копией СПДС рамки в своём acad.exe
metadata:
  type: feedback
---

05.11.2026 Ақтау қыз (TUNAY STROY): user asked for ФБС раскладка (2 ряда) + ПБ плиты, «размерлер завод стандартына сай». Answers: доборы — **монолит вставка**; ФБС — **КИС-Актау толық тізімі**; плита — ПБ над 1-м этажом; нестандартная 800 стена — «солай қалсын».

**Why:** user wants buildable layouts with only products from the local price list.

**How to apply:** follow Obsidian `02_Фундамент/Раскладка ФБС и плит ПБ.md`. Sheets 3.7–3.10 added to «Ақтау қыз Кж фундамент лист.dwg» (backup .bak). Tech: SPDS frame/stamp copy needs full acad.exe (accoreconsole COPY of proxy does nothing); launch `acad.exe /nologo /b scr` with `_.OPEN` inside the script (dwg as argument → script never runs); ssget "_W" in full AutoCAD missed off-screen objects → build selection from handles computed from DXF. COM GetActiveObject hits the user's AutoCAD — don't use it when they have AutoCAD open.

Related: [[cad-dedicated-instance]], [[close-user-file-myself]]
