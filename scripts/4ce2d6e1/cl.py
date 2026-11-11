# -*- coding: utf-8 -*-
RULE = ("- **GITHUB СТАНДАРТТАРЫ (11.11): кез келген чертеж жұмысының (КЖ/КМ, DWG/Revit, узел, спецификация, тексеріс) ең бірінші қадамы** — "
        "`powershell -NoProfile -ExecutionPolicy Bypass -File \"D:\\РАБОЧКА\\.claude\\std-pull.ps1\"` (BEKA-2: `R:\\.claude\\std-pull.ps1`): GitHub `bekasyl-kzh-km`-нен соңғы ережелерді тартады, `INDEX=` жолын шығарады. "
        "Сол `00_ЧЕРТЕЖ_ЖҮЙЕСІ.md`-ны оқы, 1-кестесінен жұмыс түрін тауып, көрсетілген файлдарды ретімен оқы — содан кейін ғана жұмыс. `STATE` OK болмаса кэш/Obsidian (`Bekassyl\\00_ЧЕРТЕЖ ЖҮЙЕСІ — осыдан баста.md`) оқылады, пайдаланушыға айтылады. "
        "Жаңа ереже шықса — `ЕРЕЖЕЛЕР.md` + тиісті стандарт файлы + Obsidian + memory, сосын commit + push (индекстің 3-бөлімі).\n")
ANCH = "- Кез келген жұмыс алдында Obsidian-ды оқы:"
for p in (r"C:\Users\Admin\.claude\CLAUDE.md", r"D:\РАБОЧКА\.claude\CLAUDE.global.md"):
    s = open(p, encoding="utf-8").read()
    assert ANCH in s, p
    if "GITHUB СТАНДАРТТАРЫ" not in s:
        s = s.replace(ANCH, RULE + ANCH, 1)
        open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", p)
m = r"C:\Users\Admin\.claude\projects\D---------\memory"
open(m + r"\github-standards-first.md", "w", encoding="utf-8", newline="\n").write("""---
name: github-standards-first
description: Кез келген чертеж жұмысы алдында std-pull.ps1 → GitHub стандартын тартып, 00_ЧЕРТЕЖ_ЖҮЙЕСІ.md индексін оқы (11.11.2026)
metadata:
  type: feedback
---

Кез келген чертеж жұмысының бірінші қадамы: `powershell -NoProfile -ExecutionPolicy Bypass -File "D:\\РАБОЧКА\\.claude\\std-pull.ps1"` → шыққан `INDEX=` файлын (`_Стандарт_КЖ\\00_ЧЕРТЕЖ_ЖҮЙЕСІ.md`) оқы → 1-кестесінен жұмыс түрін тауып, файлдарды ретімен оқы. Жаңа ереже шықса: ЕРЕЖЕЛЕР.md + стандарт файлы + Obsidian + memory → commit + push.

**Why:** пайдаланушы 11.11.2026: «Клаудта кез келген сессияда чертеж жасайтын болса бірден GitHub-тан оқып, қалай жасалуы керек системасын тауып оқитын ереже жасай аласың ба?» Себебі: В113 узелдерінде ережелер үш жерде шашылып, сессия керегін оқымай жасаған ([[km-node-one-by-one-3d]]).

**How to apply:** скрипт BEKA-2-де `D:\\Бекасыл КЖ КМ` ішінде `git pull` жасайды, басқа компта `%LOCALAPPDATA%\\bekassyl-std` кэшін (тек `_Стандарт_КЖ`, LFS-сіз) жаңартады; ps1 UTF-8 BOM-мен сақталуы керек (PS 5.1). Индекстің көшірмесі Obsidian `Bekassyl\\00_ЧЕРТЕЖ ЖҮЙЕСІ — осыдан баста.md` — екеуін бірге өзгерт. Кэштен push жасауға болады (GCM кіруі bekasylauez-spec). Ереже `~/.claude/CLAUDE.md` мен `D:\\РАБОЧКА\\.claude\\CLAUDE.global.md` «Жұмыс тәртібі» бөлімінде. Байланысты: [[github-repo]], [[obsidian-first]], [[km-standard-folder-prompts]].
""")
p = m + r"\MEMORY.md"
s = open(p, encoding="utf-8").read()
a = "- [МІНДЕТТІ: алдымен Obsidian]"
assert a in s
if "github-standards-first" not in s:
    s = s.replace(a, "- [МІНДЕТТІ: алдымен GitHub стандарты](github-standards-first.md) — чертеж алдында std-pull.ps1 → 00_ЧЕРТЕЖ_ЖҮЙЕСІ.md индексін оқы (11.11)\n" + a, 1)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
print("mem ok")
