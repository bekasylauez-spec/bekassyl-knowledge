---
name: rebars-never-overlap
description: ЕРЕЖЕ — арматуралар бірінің үстіне бірі келмейді (бір орында екі стержень/аймақ жоқ, сызбада да, есепте де); барлық КЖ/КМ жұмыстарына
metadata:
  type: feedback
---

04.11.2026 (БДМ Блок 4, Пм1) after my dop zones overlapped near the atrium corner, the user said «Арматуралар бірінің үстіне бірі келмеуі туралы ережені енгіз» — make it a standing rule.

**Rule:** no bar may lie on top of another bar.
- Two dop zones of one face never share a bar position over an overlapping length; the stronger zone (larger Ø) keeps the place, the weaker one is cut around it (gap ≥ 50 mm).
- Dop bars sit between the base bars (offset 100 at @200), never on a base bar.
- Edge bars (Ск, АВ, обрамление) do not coincide with base or dop bars at the same level.
- Allowed only as a designed lap (нахлёст) with its length shown.
- Applies to the drawing AND to the spec (no double-counted steel in one place).

**How to apply:** after generating zones, run an automatic check (per face: bar position → intervals, any overlap = error, must be 0) before drawing or showing anything. Report the check result.

Related: [[dop-zones-only-on-slab]], [[no-repeat-check-pipeline]], [[bdm-block4-slabs]]
