---
name: sherkhan-seismic-group
description: "Sherkhan Kulbay's Telegram forum (seismic NTP/EC8 lessons) is studied into Obsidian section 17; QS Cal site needs the user's login; how to export Telegram Web via DevTools"
metadata:
  node_type: memory
  type: project
  originSessionId: a402af5c-f5fd-45f3-8ee8-1a0b45371809
  modified: 2026-10-19T16:55:29.219Z
---

On 2026-10-19 the user asked me to learn everything in the Telegram group «Шерхан Құлбай | Инженер расчетчик» (private forum, t.me/c/3721206452, peer -3721206452) and save it to Obsidian. The result is in `Bekassyl/17_Сейсмика (Шерхан Құлбай)/` (33 notes: an overview note, a cheat sheet of НТП figures, lessons, earthquake reviews and the QS Cal site).

The user then said «Сайтын қолдануды үйрен и қолданамыз сосын». They plan to use https://qs-cal.netlify.app/ (Sherkhan's calculators for EC8/EC2/НТП РК with ЛИРА import) in real work. The calculators open only after a free login. On 2026-10-19 the user logged in, in the built-in browser pane, and the session persists there (the header shows a 60-day free period). Usage instructions for 12 calculators, with direct URLs, are in `17_.../05_QS Cal — как пользоваться/`. Spectrum and punching were checked against the lesson examples. The calculator list comes from `landing/catalog.mjs`. Field values are set through JS (assign value, then dispatch input and change).

On 2026-10-19 the user asked me to check the group every day at 15:00 and save anything new. I set up the scheduled task `sherkhan-telegram-daily`. Its state lives in `17_.../_sync/telegram_state.json` (`last_msg_id`). Since 2026-10-19, Telegram Web is logged in inside the built-in browser pane, by QR code, so the API can be called with `javascript_tool` and Yandex is not needed.

**Why:** the group is the user's learning source for seismic design, and the calculators are meant for project work.

**How to apply:**
- To export a Telegram Web K chat, open DevTools in Yandex and use `rootScope.managers.apiManager.invokeApi('messages.getHistory', ...)` in a loop, saving the result into `window.__x`. Then run `copy(JSON.stringify(window.__x))` as a separate command, because `copy` does not exist inside async code. Read the clipboard with PowerShell `Get-Clipboard`.
- In Windows-MCP, Yandex is on the left monitor, which has virtual x from −2560 to 0.
- To get YouTube subtitles, use `youtube-transcript-api`, which is installed.
- Still not covered: the 10 videos of the «Сейсмика» course and 15 podcasts. They exist only in Telegram and have not been transcribed.

Related: [[obsidian-log-work]], [[lira-model-by-analog]]
