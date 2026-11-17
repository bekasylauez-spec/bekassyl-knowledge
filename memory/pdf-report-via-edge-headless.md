---
name: pdf-report-via-edge-headless
description: "Мәтінді есеп/анықтаманы PDF-ке шығару тәсілі (BEKA-1) — HTML + Edge headless, тексеріс PyMuPDF-пен"
metadata:
  node_type: memory
  type: reference
  originSessionId: f4a90df7-db27-465b-ae1c-9c1764df3708
  modified: 2026-11-17T08:30:23.933Z
---

Қазақша мәтінді PDF есеп (кесте, сурет) жасау тәсілі, 17.11.2026-да тексерілген:

- Бұл компта `reportlab`, `pypdf`, `pdfplumber` жоқ; `fitz` (PyMuPDF 1.28) мен `PIL` бар. `pdftoppm` жоқ — Read құралы PDF бетін көрсете алмайды.
- Жасау: HTML жазып, `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --headless=new --no-pdf-header-footer --user-data-dir=<scratchpad\edge-profile> --print-to-pdf=<out.pdf> file:///…html`. Қазақ әріптері Arial-мен дұрыс шығады. Бет нөмірі — CSS `@page { @bottom-center { content: counter(page) " / " counter(pages) } }`. Бір бетті альбом ету — `@page wide { size: A4 landscape }` + элементке `page: wide`.
- Бос бет қалмауы үшін мәжбүрлі бет үзілісін қоймай, суретке `max-height` беріп ағынмен орналастыру керек; әр беттің толуын `fitz`-пен өлшеуге болады (мәтін блоктары мен суреттердің төменгі шеті).
- Тексеріс: `page.get_pixmap(dpi=80..90)` → PNG → Read-пен әр бетті қарау; `get_text()` ішінен жеке деректің жоқтығын тексеру.
- Python консолі cp1251 — қазақша мәтінді print еткенде `python -X utf8` керек.
- Нәтиже [[save-in-project-folder]] бойынша жоба папкасына, таза атпен.
