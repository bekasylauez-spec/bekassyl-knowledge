---
name: feedback-search-all-sources
description: "Before saying \"the DWG has no data\" (anchors, sections, base details), search every source of the project — LIRA .lir, the Tekla album, earlier albums/pdfs in the project folder"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 38383950-ff15-462c-99ed-3b9b23e702df
  modified: 2026-11-08T18:07:02.884Z
---

08.11.2026, Завод В109 Revit КМ: I wrote that anchors of the СФ / СФ1 / К3 bases were not in the DWG and placed assumed ones. User: «олар бар. Сен Лираны жақсылап қара». They were on the Tekla album sheets (pdf «Цех негізінде, сызылған парақтар», «Базы колонн. Узлы 3, 4, 5», «База колонн Б1 / Б2»).

**Why:** the project carries several generations of drawings (Tekla original, re-drawn albums, LIRA); a detail missing from the latest album is usually in an earlier one.

**How to apply:** when data is missing, first grep/scan every pdf/dwg/lir of the project folder and the tekla_data dumps; only then call it an assumption and ask. Related: [[project-b109-revit-km]].
