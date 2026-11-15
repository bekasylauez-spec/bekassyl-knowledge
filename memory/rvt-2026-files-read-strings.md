---
name: rvt-2026-files-read-strings
description: BEKA-1-де тек Revit 2025 — Revit 2026 .rvt ашылмайды; ішіндегі мәтінді rvt_strings.py OLE+gzip арқылы оқу (15.11.2026)
metadata:
  node_type: memory
  type: reference
  originSessionId: 8c7f20aa-9b03-43f3-b7c9-8d17af4366be
  modified: 2026-11-15T15:35:40.697Z
---

BEKA-1-де Revit 2025 (және бос Revit 2024 папкасы) ғана бар, Revit 2026 жоқ. 2026-да сақталған .rvt (мыс. Ержанның Омар S03/S05) 2025-те ашылмайды — алдымен `BasicFileInfo.Extract(path).Format` тексер (e00_info.cs, `D:\_claude_work\Erzhan`).

Revit-сіз оқу: `python -I -X utf8 D:\_claude_work\Erzhan\rvt_strings.py <rvt> <TAG> <outdir>` — өз CFB/OLE оқушысы (olefile жоқ), әр ағынның gzip бөліктерін memoryview-пен ашады, UTF-16 мәтінін `<TAG>_strings.txt`-ке жазады (430 МБ файл ≈ 10 мин). `kw2.py` (примечание, атаулар, арматура), `cmp.py` (маркалар, отметка, Ø саны). Береді: парақ/вид атаулары, примечание мәтіні, семейство/параметр атаулары, ведомость деталей жазулары; бермейді: геометрия, шаг, размер.
Python-да `-I` болса PYTHONIOENCODING істемейді — `-X utf8` қолдан.

Related: [[omar-3917-yerzhan-analysis]], [[revit-build-via-addin]]
