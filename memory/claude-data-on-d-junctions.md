---
name: claude-data-on-d-junctions
description: "BEKA-1 — Claude чат тарихы (.claude\\projects) мен Documents\\Codex D дискінде, C-де тек junction; BEKA-2 — projects\\D--------------- ғана; тазалағанда junction арқылы өшірме"
metadata:
  node_type: memory
  type: reference
  originSessionId: b57dfe74-828d-46e2-816e-c2721c115a9f
  modified: 2026-11-17T06:39:40.177Z
---

2026-11-16, BEKA-1. Пайдаланушы: «C дискім толып қалды, Claude/ChatGPT-ке байланысты файлдарды өшір, керек дүние болса D-ге ауыстыр». Содан бері:

- `C:\Users\Admin\.claude\projects` — junction → `D:\Users\Admin\.claude\projects` (чат тарихы, айына ~9 ГБ өседі; D жағында ACL тек Admin/SYSTEM/Administrators). Ішіндегі `D---------\memory` бұрынғыдай junction → `D:\РАБОЧКА\.claude\memory` ([[shared-memory-two-pcs]]).
- `C:\Users\Admin\Documents\Codex` — junction → `D:\Users\Admin\Documents\Codex` (Codex чаттарының outputs-тары; Codex sandbox-тың 4 explicit ACE-і түбірге қайталанған).
- BEKA-2 (17.11.2026): `C:\Users\beka\.claude\projects\D---------------` (2,7 ГБ, тірі сессиясы жоқ) junction арқылы `D:\Users\beka\.claude\projects\D---------------`-ге көшті.
  - Тәртібі: robocopy /XJ → treecmp → Directory.Move → mklink /J → қайта treecmp → rd /s /q.
  - C-де қалғаны: `R--` (тірі сессия, ішінде `memory` symlink) және `D---------` (`memory` → `\\BEKA-1\РАБОЧКА\.claude\memory` symlink). Developer Mode өшік, админсіз symlink жасалмайды.
- C-де қалғаны (ChatGPT қосымшасы ашық тұрғанда көшірілмейді): `C:\Users\Admin\.codex` (~2,8 ГБ: sessions + thread_history sqlite), `.cache\codex-runtimes\codex-primary-runtime` (~1,4 ГБ). Пайдаланушы ChatGPT-ті жапса, сол тәсілмен `D:\Users\Admin\...` ішіне көшіруге болады.

**How to apply:**
- C-ні тазалағанда осы жолдарға `Remove-Item -Recurse` жасама: Windows PowerShell 5.1 junction ішіне кіріп, D-дегі нақты деректі өшіреді. Junction-ның өзін алу — `[IO.Directory]::Delete($path, $false)` немесе `cmd /c rmdir` (/s жоқ); ағаш өшіру — `cmd /c rd /s /q` (junction ішіне кірмейді), алдымен ішінде reparse point жоғын тексер. Бұл [[disk-cleanup-rules]] «D-ге тиіспе» ережесінің бөлігі.
- Тірі сессиялар жұмыс істеп тұрғанда папканы D-ге көшіру тәсілі (сессиялар үзілген жоқ): `robocopy /E /XJ` → src==dst екенін snapshot-пен тексеру → `[IO.Directory]::Move(src, old)` және алдын ала жасалған junction-ды бірден орнына Move → сол терезеде өзгерген `.jsonl`-дың құйрығын D-дегі файлға append → тексеріп, old-ты `rd /s /q`. Дайын скрипттер: `D:\_claude_work\c_cleanup\` (`mv1_copy.ps1`, `mv2_swap.ps1`, `clean_temp.ps1`, `clean_misc.ps1`, `sizes.ps1`).
- `robocopy /COPY:DATS` (/SEC) админсіз «ERROR 5» береді де, ішкі папкаларды үнсіз көшірмей кетеді — `/COPY:DAT` қолдан, explicit ACE-лерді `(Get-Item).GetAccessControl('Access')` → `AddAccessRule` → `SetAccessControl` арқылы қайтала.
