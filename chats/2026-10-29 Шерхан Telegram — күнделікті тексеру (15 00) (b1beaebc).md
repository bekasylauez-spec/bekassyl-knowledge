# Шерхан Telegram — күнделікті тексеру (15:00)

- Дата: 2026-10-29
- Сессия: `b1beaebc-9753-43f5-8fb8-b2247b02843c`

## Пайдаланушы

<scheduled-task name="sherkhan-telegram-daily" file="C:\Users\Admin\.claude\scheduled-tasks\sherkhan-telegram-daily\SKILL.md">
This is an automated run of a scheduled task. The user is not present to answer questions. For implementation details, execute autonomously without asking clarifying questions — make reasonable choices and note them in your output. "write" actions (e.g. MCP tools that send, post, create, update, or delete), only take them if the task file asks for that specific action. When in doubt, producing a report of what you found is the correct output.

Objective: check the Telegram forum group «Шерхан Құлбай | Инженер расчетчик» (private, peer id -3721206452, links t.me/c/3721206452/<msg_id>) for messages newer than the last processed one. Study each new post (text, video/YouTube, links, files) and save what you learn to the Obsidian vault. Reply to the user in Kazakh. Write the vault notes in Russian, like the existing ones.

## State
- State file: `C:\Users\Admin\Documents\Bekassyl\17_Сейсмика (Шерхан Құлбай)\_sync\telegram_state.json`. It has `last_msg_id` and a topic id→name map: 1 General, 2 Подкасты, 4 Сейсмика, 5 Видеоинструкции, 102 Материалы, 151 Eurocode, 324 Нормы / Видеоуроки.
- Section root: `C:\Users\Admin\Documents\Bekassyl\17_Сейсмика (Шерхан Құлбай)\`.
  - Subfolders: 01_Нормы НТП — 3D уроки, 02_Видеоуроки, 03_Разборы землетрясений, 04_Сервисы и материалы, 05_QS Cal — как пользоваться.
  - Hub note: «00 Обзор группы Шерхан Құлбай.md». Cheat sheet: «Шпаргалка — цифры НТП РК по сейсмике.md».
  - Read 1–2 existing notes in the matching subfolder first and copy their format: frontmatter with title/tags/источник/дата_изучения, a header line with post #, date and video length, tables of НТП clauses, an example, and a footer linking back to the hub and the cheat sheet.

## 1. Fetch new messages (Telegram Web K)
Preferred: the Claude built-in browser (mcp__Claude_Browser__* tools; its profile keeps the Telegram login).
1. Open https://web.telegram.org/k/ with preview_start (url) and wait about 5 s.
2. If the page shows «Log in by QR Code», you are not logged in. Do not try to log in. Tell the user (in Kazakh) to scan the QR code in the Claude browser pane (Ctrl+Shift+B). Then try the fallback below.
3. Run this with javascript_tool. The global `rootScope` exists.
```js
const m=rootScope.managers; const peer=await m.appPeersManager.getInputPeerById(-3721206452);
const r=await m.apiManager.invokeApi('messages.getHistory',{peer,offset_id:0,offset_date:0,add_offset:0,limit:100,max_id:0,min_id:LAST_ID,hash:0});
const users={}; (r.users||[]).forEach(u=>users[u.id]=[u.first_name,u.last_name].filter(Boolean).join(' '));
JSON.stringify(r.messages.map(x=>{const md=x.media;let media=null;if(md){media={t:md._};const d=md.document;if(d){media.mime=d.mime_type;media.size=d.size;(d.attributes||[]).forEach(a=>{if(a.file_name)media.fn=a.file_name;if(a.duration)media.dur=a.duration;});}if(md.webpage){media.url=md.webpage.url;media.wt=md.webpage.title;}}return {id:x.id,date:x.date,from:users[x.from_id?.user_id]||x.from_id?.user_id,text:x.message,urls:(x.entities||[]).filter(e=>e.url).map(e=>e.url),rt:x.reply_to&&{to:x.reply_to.reply_to_msg_id,top:x.reply_to.reply_to_top_id},action:x.action&&{t:x.action._,title:x.action.title},media,gid:x.grouped_id}}))
```
   Replace LAST_ID with `last_msg_id`. If 100 messages come back, page with offset_id.
   - Topic of a message: `rt.top`, else `rt.to` if it is a known topic id, else the topic of the message it replies to, else 1 (General).
   - `messageActionTopicCreate`/`TopicEdit` = a new or renamed topic. Add it to the map.

Fallback: the user's Yandex Browser with Telegram Web open, through Windows-MCP.
- The left monitor has virtual x from −2560 to 0. Switch to the Telegram Web tab.
- Ctrl+Shift+J opens the console. Run the same code and store the result in `window.__x`.
- Then run `copy(window.__x)` as a separate command (copy() does not work inside async code). Read the clipboard with PowerShell Get-Clipboard.
- Close DevTools afterwards. Do this only if the user is not actively using that browser. If unsure, skip it and report.

## 2. Filter
- Ignore service messages (joins, adds).
- Ignore chat replies from members, unless they contain useful technical content.
- If nothing new is left: update only `last_check` (and `last_msg_id` to the max id seen) in the state file, make no notes, and reply with one short line: «Шерхан группасында жаңа пост жоқ».

## 3. Study each new author post
- Read the full text.
- YouTube link (youtu.be/ID): get the Russian subtitles with Python `youtube-transcript-api` (installed): `YouTubeTranscriptApi().fetch(ID, languages=['ru','kk','en'])`. Read the transcript and pull out the theory, numbers, НТП/EC clauses and the calculator workflow.
- Telegram-only video with no caption text: do not download it. List it as «не транскрибировано» with name and duration.
- Links to qs-cal.netlify.app (Sherkhan's calculators): the user is logged in in the Claude built-in browser. If the post announces a new or changed calculator, open it, record its fields/steps/buttons, and add or update the note in 05_QS Cal — как пользоваться.
- Telegram bots (t.me/..._bot): describe them only. Never send messages to bots or anyone. Never post in the group.
- Files (pptx/docx/pdf): record the name and description only. Do not download.

## 4. Save to Obsidian
- One note per new lesson/post in the matching subfolder:
  - #норма 3D rules → 01;
  - long #урок videos → 02;
  - earthquake/failure reviews (#разбор of events, #ошибка) → 03;
  - podcasts, materials, bots → 04.
- Content: the essence in plain words, a table of norm clauses with formulas and values, the example numbers, the source link (t.me/c/3721206452/<id> and YouTube), and a «Связано» line with [[wikilinks]] to existing related notes.
- Add every new note to the right section of «00 Обзор группы Шерхан Құлбай.md». Add any new norm figures to the cheat sheet.
- Append a line to `C:\Users\Admin\Documents\Bekassyl\99_Changelog\<YYYY-MM-DD> — сейсмика группа Шерхана.md`, creating the file if needed.
- Check that every [[wikilink]] in the section resolves to an existing note name. Fix any that don't.
- Update the state file: `last_msg_id` = max id processed, `last_check` = now.

## 5. Report
Reply in Kazakh, 3–6 lines:
- how many new posts;
- their titles;
- which notes were created (as markdown links);
- what could not be done (e.g. Telegram not logged in, videos not transcribed).

Constraints: read only in Telegram (no sending, no reactions, no joining). Do not enter passwords or log in on the user's behalf. Do not delete or overwrite existing notes; append or update them.
</scheduled-task>

## Claude

Telegram логинсіз, Яндекс fallback-ы `no-hide-yandex` ережесі бойынша өткізіледі. Тек `last_check` жаңартамын.

## Claude

Шерхан группасы бұл жолы тексерілмеді, себебі Claude браузеріндегі Telegram Web аккаунтқа кірмеген («Log in by QR Code» беті шықты).
- Жаңа посттар: белгісіз, жазба жасалмады.
- Яндекс арқылы тексерген жоқпын: «Яндексті жаппа» ережесі бойынша оған тиіспедім.
- `telegram_state.json` ішінде тек `last_check` жаңартылды. `last_msg_id` = 450 өзгермеді, сондықтан келесі жолы ешбір пост өткізіліп кетпейді.
- Келесі автоматты тексеру жұмыс істеуі үшін Claude браузер панелінде (Ctrl+Shift+B) телефоннан QR-кодты сканерлеу керек.
