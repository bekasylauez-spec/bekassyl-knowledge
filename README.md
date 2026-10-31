# Bekassyl — инженерлік білім базасы

Claude-пен жұмыс барысында жиналған КЖ / КМ / ЛИРА / AutoCAD (СПДС) / Revit тәжірибесі.

| Папка | Мазмұны |
|---|---|
| [`obsidian/`](obsidian/) | Obsidian «Bekassyl» базасы: жалпы ережелер, фундамент/колонна/ригель/плита/стена, типовые узлы, КМ чертежи, жобалар, сейсмика, чаттар журналы |
| [`memory/`](memory/) | Claude memory: бекітілген ережелер мен жобалар бойынша қысқа жазбалар ([индекс](memory/MEMORY.md)) |
| [`chats/`](chats/) | Барлық Claude чаттарының мәтіні (сұрақ + жауап, құралдар шығысынсыз) — [тізім](chats/README.md) |

Телефон нөмірлері мен email-дар жасырылған.
Жаңарту: 2026-10-31.

## Бірнеше компьютерде жұмыс

**Жаңа компьютерде бір рет** — PowerShell ашып, мынаны қойыңыз:

```powershell
irm https://raw.githubusercontent.com/bekasylauez-spec/bekassyl-knowledge/main/tools/setup.ps1 | iex
```

Git пен Python-ды орнатады, базаны `Documents\bekassyl-knowledge` папкасына алады, Obsidian-ға (`Documents\Bekassyl`) және Claude memory-ге (`D:\РАБОЧКА` жобасы) қояды.
Жұмыс папкасы әр компьютерде **`D:\РАБОЧКА`** болуы керек — Claude memory осы жолға байланған.

**Жұмыс соңында** (немесе Claude-қа «гидхабты жаңарт» деңіз):

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\Documents\bekassyl-knowledge\tools\update.ps1"
```

Басқа компьютерлердегі жаңалықты алады, осы компьютердің жаңа ережелері мен чаттарын GitHub-қа жібереді.
