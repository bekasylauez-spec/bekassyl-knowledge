---
name: rvt-2026-files-read-strings
description: "BEKA-1-де 16.11.2026-дан Revit 2026.4 бар (өз данам — журнал папкасы тәсілі, BI_Group\\скрипттер); BI/Ержан локал файлдары тек «Отсоединить от хранилища» арқылы; Revit-сіз мәтін оқу — rvt_strings.py"
metadata:
  node_type: memory
  type: reference
  originSessionId: 8c7f20aa-9b03-43f3-b7c9-8d17af4366be
  modified: 2026-11-16T19:25:13.602Z
---

**Жаңарту 16.11.2026:** BEKA-1-ге Revit 2026.4 орнатылды (21:26), плагиннен тек ModPlus; RBLive/pyRevit 2026-да жоқ. Өз Revit 2026 данаңды ашу тәсілі — жеке журнал папкасы + pid құлпы бар add-in: толық сипаты мен ережесі [[revit-own-instance-journal-folder]]. Көшірмелі жинақ: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\BI_Group\скрипттер\` (`start.ps1 -Year 2026`, `rv.ps1`, `stop.ps1`; жұмыс көшірмесі `D:\_claude_work\BI_Group\tool\`). `D:\_claude_work\BI_Group\` түбіріндегі алғашқы нұсқа (`jrn\start.txt` + `BILive2.addin`, арна `_chan2`, `rv.ps1`, pid — түбірдегі `_pid.txt`) да жұмыс істейді, бірақ жолдары қатты жазылған — жаңа жұмысқа `tool\` / `скрипттер` жинағын ал. Төмендегі «2026 жоқ» дегені ескірген; мәтін оқу тәсілі Revit ашпай қарау үшін ғана қалады.

**Ержан/BI файлдары (Revit Server локал көшірмесі, RSN://10.10.1.88):** хранилище қолжетімсіз, сондықтан кәдімгі ашқанда ешбір өзгеріс (визуальный стиль, секущий диапазон, V/G) өтпейді — «Модель из хранилища отсутствует» шығады. Тек «Отсоединить от хранилища» арқылы аш; Revit пайдаланушы атын Ержандікіне ауыстырма. 3D-де арматура бетон ішінде қалып көрінбейді («Показать без перекрытий» жоқ) — пайдаланушы 17.11 осыны сұрады. (API-мен: `OpenDocumentFile` + `DetachFromCentralOption.DetachAndPreserveWorksets` — диалогсыз ашылады.)

**Жаңа Revit ашпас бұрын бос жадты тексер** (`Get-Counter '\Memory\Available MBytes'`): 16.11 түнде 4 Revit данасы қатар тұрып, 32 ГБ-тан 4 ГБ ғана бос қалды — бесінші дананы ашпадым. 450 МБ модель өз данамда ≈ 5–6 ГБ алады; жұмыс біткенде `stop.ps1`.

BEKA-1-де Revit 2025 (және бос Revit 2024 папкасы) ғана бар, Revit 2026 жоқ. 2026-да сақталған .rvt (мыс. Ержанның Омар S03/S05) 2025-те ашылмайды — алдымен `BasicFileInfo.Extract(path).Format` тексер (e00_info.cs, `D:\_claude_work\Erzhan`).

Revit-сіз оқу: `python -I -X utf8 D:\_claude_work\Erzhan\rvt_strings.py <rvt> <TAG> <outdir>` — өз CFB/OLE оқушысы (olefile жоқ), әр ағынның gzip бөліктерін memoryview-пен ашады, UTF-16 мәтінін `<TAG>_strings.txt`-ке жазады (430 МБ файл ≈ 10 мин). `kw2.py` (примечание, атаулар, арматура), `cmp.py` (маркалар, отметка, Ø саны). Береді: парақ/вид атаулары, примечание мәтіні, семейство/параметр атаулары, ведомость деталей жазулары; бермейді: геометрия, шаг, размер.
Python-да `-I` болса PYTHONIOENCODING істемейді — `-X utf8` қолдан.

Related: [[omar-3917-yerzhan-analysis]], [[revit-build-via-addin]], [[revit-own-instance-journal-folder]], [[bi-group-rules]]
