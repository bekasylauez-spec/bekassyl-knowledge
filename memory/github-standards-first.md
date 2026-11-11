---
name: github-standards-first
description: Кез келген чертеж жұмысы алдында std-pull.ps1 → GitHub стандартын тартып, 00_ЧЕРТЕЖ_ЖҮЙЕСІ.md индексін оқы (11.11.2026)
metadata:
  type: feedback
---

Кез келген чертеж жұмысының бірінші қадамы: `powershell -NoProfile -ExecutionPolicy Bypass -File "D:\РАБОЧКА\.claude\std-pull.ps1"` → шыққан `INDEX=` файлын (`_Стандарт_КЖ\00_ЧЕРТЕЖ_ЖҮЙЕСІ.md`) оқы → 1-кестесінен жұмыс түрін тауып, файлдарды ретімен оқы. Жаңа ереже шықса: ЕРЕЖЕЛЕР.md + стандарт файлы + Obsidian + memory → commit + push.

**Why:** пайдаланушы 11.11.2026: «Клаудта кез келген сессияда чертеж жасайтын болса бірден GitHub-тан оқып, қалай жасалуы керек системасын тауып оқитын ереже жасай аласың ба?» Себебі: В113 узелдерінде ережелер үш жерде шашылып, сессия керегін оқымай жасаған ([[km-node-one-by-one-3d]]).

**How to apply:** скрипт BEKA-2-де `D:\Бекасыл КЖ КМ` ішінде `git pull` жасайды, басқа компта `%LOCALAPPDATA%\bekassyl-std` кэшін (тек `_Стандарт_КЖ`, LFS-сіз) жаңартады; ps1 UTF-8 BOM-мен сақталуы керек (PS 5.1). Индекстің көшірмесі Obsidian `Bekassyl\00_ЧЕРТЕЖ ЖҮЙЕСІ — осыдан баста.md` — екеуін бірге өзгерт. Кэштен push жасауға болады (GCM кіруі bekasylauez-spec). Ереже `~/.claude/CLAUDE.md` мен `D:\РАБОЧКА\.claude\CLAUDE.global.md` «Жұмыс тәртібі» бөлімінде. Байланысты: [[github-repo]], [[obsidian-first]], [[km-standard-folder-prompts]].
