---
name: no-hide-yandex
description: "Never close or hide the user's Yandex browser in any task; computer-use screenshots hide non-allowlisted windows, so avoid GUI control when a file-level route exists"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b6e176ea-26b4-4762-a290-80708f71b8b2
  modified: 2026-10-29T14:54:22.640Z
---

The user, 2026-10-21 and again 2026-10-22: «яндексті жаппа», «кез келеген жұмыста яндексті жаппа».

**Why:** computer-use `screenshot`/actions hide every window that is not in the session allowlist, and Яндекс Браузер is one of them. To the user this looks like I closed their browser while they were working in it. LIRA and AutoCAD are often in use by the user at the same time.

**How to apply:**
- Prefer file-level routes: read .lir/.dwg in binary, use accoreconsole, plugins, and DXF.
- Use computer-use only when there is no other way, and keep it short.
- Never close, minimize or kill Яндекс (or any other window of the user's).
- Before clicking, check that the target tab is still active: the user switches LIRA tabs themselves (резервуар).

Related: [[cad-dedicated-instance]], [[lira-model-by-analog]]
- 2026-10-29: the user repeated «яндекситі жаппа» during LIRA GUI work. Fix that worked: add «Яндекс Браузер с Алисой AI» to the computer-use allowlist (request_access) so screenshots no longer hide it; never click or type in it.
- 2026-10-29 (Қарасу ЛК, again): «кезкелген жұмыста яндексті жаппа бұл ереже». Do the allowlist step BEFORE the first screenshot of any computer-use session, not after the user complains.
