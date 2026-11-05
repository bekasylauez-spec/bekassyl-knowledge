---
name: model-delegation-setup
description: Opus негізгі + субагенттер haiku/sonnet (04.11): settings, 5 агент, статус-строка, usage_report графигі
metadata:
  type: project
---
04.11.2026 BEKA-1-де орнатылды:
- `~/.claude/settings.json`: `"model": "opus"`, env `CLAUDE_CODE_SUBAGENT_MODEL=sonnet`, statusLine → `~/.claude/statusline.py` (тек CLI терминалда көрінеді).
- Агенттер `~/.claude/agents/` (көшірмесі `D:\РАБОЧКА\.claude\agents\`): obsidian-reader, file-scout (haiku); script-worker, drawing-checker, spec-calculator (sonnet).
- Делегация ережесі CLAUDE.global.md «Модельдер және субагенттер» бөлімінде.
- График: `python D:\РАБОЧКА\.claude\usage_report.py 30` → usage_report.html (модель/күн бойынша $, негізгі vs субагент).
- Бастапқы өлшем (30 күн дейін): 100% Opus, ~$4700 шамалы API бағасы, субагенттер 1%.

05.11.2026 BEKA-2-де орнатылды: 5 агент + statusline.py → `C:\Users\beka\.claude\`; settings.json-ға model/env/statusLine (hooks сақталды, бэкап `backups\settings.json.bak-2026-11-05`); CLAUDE.md блогы `claude-shared.ps1 -Work R:\` арқылы. Агент жолдары өзгертілмеді — BEKA-2-де `D:\РАБОЧКА` = симлинк `\\192.168.0.107\РАБОЧКА`. Есеп: `D:\Бекасыл КЖ КМ\_Стандарт_КЖ\usage_report_BEKA-2.html` (30 күн: тек Opus ≈$2589, оның субагенттер ≈$672; sonnet/haiku 0 — жаңа чаттан бастап өзгереді).

**Why:** пайдаланушы Opus тек басқаратын, ұсақ жұмыс арзан модельдерде, бірақ сапа сақталсын деді.
**How to apply:** BEKA-2-де агенттерді `D:\РАБОЧКА\.claude\agents\` → `~/.claude/agents\` көшір және settings.json-ға model/env қос (автосинхрон жоқ). Бір аптадан соң usage_report-пен салыстыр. [[feedback-full-autonomy]]
