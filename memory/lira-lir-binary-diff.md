---
name: lira-lir-binary-diff
description: "LIRA-SAPR 2024 .lir binary layout (node/element counts, node and element tables) — compare two .lir versions geometrically without opening LIRA (found 17.11.2026)"
metadata:
  node_type: memory
  type: reference
  originSessionId: 9252f8e4-753b-43e2-aae3-c6e03c79625e
  modified: 2026-11-17T11:29:20.611Z
---

LIRA-SAPR 2024 R2.3 `.lir`: the file starts with the ASCII header `ULIRA-SAPR 2013 software ver.13.0.0.a`, then `FileAnsiCP=1251 / 866`, then `Preview=<16 hex digits>`. The hex value is the offset of the preview picture near the end of the file. It is not a zip archive. Offsets were verified on Kasymova v9/v10 (182 k elements):
- int32 at offset 98 = number of nodes; int32 at offset 106 = number of elements; int32 at 94 = 13001 (constant).
- The node table starts at offset 138. Each record is 28 bytes: x, y, z as 3 little-endian doubles (m) plus int32 (=1).
- The element table follows right after the nodes. Each record is 38 bytes: 8 × int32 node indices (0-based, unused slots 0), then int16 kind (2 = plate type 44, 0 = bar type 10), then int32.
  - Bars use only slots 0–1. Slots 2–3 hold other data.
  - Stiffness number and element type are not in this record.
- Element order equals the text export (doc 1), so a key (kind, sorted rounded node coordinates) matches elements across versions even after renumbering.

Use: a quick check of whether someone changed a model, and where (counts in the header, then a geometric multiset diff). Scripts: `D:\_claude_work\Kasymova\v10\lir_bin_diff.py` (diff) and `lir_bin_conn.py` (which new nodes hang free).

For loads, stiffness, C1 and E-factors you still need LIRA «Файл → Создать текстовый файл» and a doc-by-doc diff (`D:\_claude_work\Kasymova\v10\diff_v10.py`). ЖБ materials are in neither.

Related: [[lira-keep-user-edits]], [[lira-model-by-analog]]
