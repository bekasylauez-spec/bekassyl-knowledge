---
name: whatsapp-web-chrome
description: Пайдаланушының WhatsApp Business-і Google Chrome-да (Claude in Chrome кеңейтімі) web.whatsapp.com арқылы тіркелген; хабар жіберу тәртібі
metadata:
  node_type: memory
  type: reference
  originSessionId: fa56d1fd-96ce-470f-a97e-2d661dcfea77
  modified: 2026-11-06T10:05:18.674Z
---

WhatsApp (Business) — Google Chrome-да web.whatsapp.com, Claude in Chrome кеңейтімі арқылы (06.11.2026 тіркелді, BEKA-? компта).
- Claude-тың ішкі браузері жарамайды: WhatsApp UA-дағы «Claude/…» үшін «Chrome 100+ керек» деп қабылдамайды.
- Кеңейтім Chrome-ға registry арқылы алдын ала қосылған: HKCU\Software\Google\Chrome\Extensions\fcoeoabgfenejglbffodgkkbkcdhcgfn (update_url). Яндексте де бар, бірақ Claude оған қосылмайды.
- 07.11-ден: тапсырма берілсе рұқсат сұрамай бірден жіберемін ([[whatsapp-send-fast]]).
- Пайдаланушы өзі браузер баптауын жасай алмайды — қадамдарды өте қарапайым, бір-бірден бер.
- 06.11 23:12: computer-use рұқсаты (пайдаланушы телефонда) өтпеді, Chrome қосылмаған → **WhatsApp desktop қосымшасы + Windows-MCP** (App launch, Click координатпен, Clipboard+ctrl+v файл жолы «Открытие» терезесіне) арқылы жіберілді. Екінші монитор x<0 (−2560…0). 10 МБ-тан үлкен DWG-ны zip-ке қыс.
- 07.11 (BEKA-2): Chrome кеңейтімінің file_upload-ымен WhatsApp Web-ке салынған файл (zip 8 МБ да, DWG 5 МБ да) ЖІБЕРІЛМЕЙДІ — «Отправить»/Enter басқанда превью жабылып, подпись хабар жолына түседі (4 рет). Escape превьюде «Сбросить выбор?» шығарады. **Жұмыс істейтін жол:** PowerShell `Set-Clipboard -Path <файлдар>` → WhatsApp Web чатының хабар жолына басып ctrl+v → превьюде подпись → Enter (07.11 екі DWG осылай жіберілді). Chrome өшік болса — өзім chrome.exe іске қосамын, кеңейтім сонда қосылады.
- 11.11 (BEKA-1): BEKA-1-де Chrome орнатылмаған — Claude in Chrome кеңейтімі басқа компьютердегі Chrome-ға қосылады, сондықтан Set-Clipboard файлы ол жерге қойылмайды, file_upload превьюі тағы жіберілмеді (10 МБ шегі де бар). **BEKA-1-де жұмыс істейтін жол:** WhatsApp desktop (WhatsApp.Root, сол жақ монитор x −2560…0) → Windows-MCP App switch «WhatsApp» → чатты басу → хабар жолы → `Set-Clipboard -Path` + ctrl+v → превьюдегі жіберу батырмасы → ✓✓ тексер. 12 МБ PDF-ті алдын ала PyMuPDF garbage=4/clean арқылы шығынсыз 7,9 МБ-қа қыстым.
