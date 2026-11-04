import pathlib, re, shutil, sys
sys.stdout.reconfigure(encoding="utf-8")
M = pathlib.Path(r"D:\РАБОЧКА\.claude\memory")
BAK = pathlib.Path(r"D:\РАБОЧКА\.claude\memory-bak-2026-11-04-consolidate")
if not BAK.exists():
    shutil.copytree(M, BAK)

def rd(n): return (M / n).read_text(encoding="utf-8")
def wr(n, s): (M / n).write_text(s, encoding="utf-8")
def body(n):
    s = rd(n)
    return s.split("---", 2)[2].strip() if s.startswith("---") else s.strip()
def set_desc(s, d):
    return re.sub(r'(?m)^description:.*$', 'description: "' + d.replace('"', "'") + '"', s, count=1)

# 1. В109: uvpios-b109-km (BEKA-1, 03–04.11) -> project-zavod-b109-km (BEKA-2, 04.11)
z = rd("project-zavod-b109-km.md")
head, rest = z.split("---", 2)[1], z.split("---", 2)[2]
early = body("uvpios-b109-km.md")
z = "---" + head + "---\n\n**Ерте кезең (03–04.11.2026, BEKA-1: КМ бір DWG-ға, ТХ, крандар, замечания).**\n\n" + early + \
    "\n\n**Кейінгі кезең (04.11.2026, BEKA-2: Цех альбомы негізінде қайта сызу).**\n" + rest
z = set_desc(z, "Завод УВПиОС В109 (Шерхан) КМ: 03.11 Tekla бір DWG + ТХ крандар (BEKA-1), 04.11 Цех Алатау альбомы рамкасында жаңадан сызу (BEKA-2) — ережелер, pipeline, күйі")
wr("project-zavod-b109-km.md", z)

# 2. Obsidian: reference-obsidian-bekassyl -> obsidian-first
o = rd("obsidian-first.md")
ref = body("reference-obsidian-bekassyl.md")
key = ref.split("Key notes:", 1)[1].split("Related:", 1)[0].strip() if "Key notes:" in ref else ref
o = o.replace("Related: [[obsidian-log-work]]",
    "**Path on both PCs:** `D:\\РАБОЧКА\\Bekassyl` (on BEKA-2 `D:\\РАБОЧКА` is a link to `\\\\BEKA-1\\РАБОЧКА`), see [[shared-memory-two-pcs]]. "
    "BEKA-2 also repeated this rule on 04.11.2026 («обсидианнан қара»).\n\n**Key notes:**\n" + key + "\n\nRelated: [[obsidian-log-work]]", 1)
wr("obsidian-first.md", o)

# 3. Open DWG: feedback-acad-swap-myself -> close-user-file-myself
c = rd("close-user-file-myself.md")
sw = body("feedback-acad-swap-myself.md").split("Related:", 1)[0].strip()
c = c.replace("Related: [[cad-dedicated-instance]], [[galaxy-kzh-scheme]]",
    "**Same rule on BEKA-2 (04.11.2026, В109: «жауып ашар затты өзің жаса»)** — when a rebuilt DWG replaces the open one:\n" + sw +
    "\n\nRelated: [[cad-dedicated-instance]], [[galaxy-kzh-scheme]], [[project-zavod-b109-km]], [[feedback-full-autonomy]]", 1)
c = set_desc(c, "Керекті DWG пайдаланушының AutoCAD-ында ашық тұрса — сұрамай өзім сақтап жабамын/ауыстырамын да қайта ашамын (COM, acad_swap.ps1); өз данамда жұмыс")
wr("close-user-file-myself.md", c)

# 4. Revit plugins: revit2025-plugins-families (BEKA-2) -> revit-plugins-2025 (BEKA-1)
r = rd("revit-plugins-2025.md")
fam = body("revit2025-plugins-families.md")
r = r.replace("On 2026-10-31 the user asked me to find Revit 2025 plugins online",
    "**BEKA-1** — on 2026-10-31 the user asked me to find Revit 2025 plugins online", 1)
r = r.rstrip() + "\n\n**BEKA-2 (same day, separate survey):**\n" + fam + "\n"
r = set_desc(r, "Revit 2025 plugins on both PCs (BEKA-1: pyRevit 7, RevitLookup, ModPlus fix; BEKA-2: ModPlus, KZhTagShelf, mcp-servers) + Autodesk family-creation workflow")
wr("revit-plugins-2025.md", r)

for n in ("uvpios-b109-km.md", "reference-obsidian-bekassyl.md", "feedback-acad-swap-myself.md", "revit2025-plugins-families.md"):
    (M / n).unlink()

# 5. Links + stale paths in every note
links = {"[[uvpios-b109-km]]": "[[project-zavod-b109-km]]", "[[reference-obsidian-bekassyl]]": "[[obsidian-first]]",
         "[[feedback-acad-swap-myself]]": "[[close-user-file-myself]]", "[[revit2025-plugins-families]]": "[[revit-plugins-2025]]"}
paths = [(re.compile(r"\\\\?\\?192\.168\.0\.107\\рабочка", re.I), r"D:\\РАБОЧКА"),
         (re.compile(r"\\\\?\\?Desktop-0bgbhi9\\d\\РАБОЧКА", re.I), r"D:\\РАБОЧКА")]
for f in M.glob("*.md"):
    if f.name == "MEMORY.md":
        continue
    s0 = s = f.read_text(encoding="utf-8")
    for a, b in links.items():
        s = s.replace(a, b)
    for p, b in paths:
        s = p.sub(b, s)
    if s != s0:
        f.write_text(s, encoding="utf-8")
        print("fixed:", f.name)

# 6. BEKA-2-only places
def add_line(n, after_frontmatter):
    s = rd(n); parts = s.split("---", 2)
    wr(n, "---" + parts[1] + "---\n\n" + after_frontmatter + "\n" + parts[2].lstrip("\n"))
add_line("user-env-cad.md", "**BEKA-2** (user `beka`). Python 3.13 is installed there since 04.11.2026 (`%LOCALAPPDATA%\\Programs\\Python\\Python313`); the «no system Python» line below is from 10.10.")
add_line("revit-mcp-bridge.md", "**BEKA-2** method (`D:\\Бекасыл КЖ КМ` is BEKA-2's local disk). BEKA-1 builds Revit models with a csc add-in instead: [[revit-build-via-addin]].")
add_line("kzh-standard-folder.md", "**BEKA-2 local folder** (not on BEKA-1). Rules are also kept in the Obsidian vault ([[obsidian-first]]); keep both in step.")
add_line("github-repo.md", "**Private** repo of BEKA-2's work folder, not the public knowledge repo [[github-knowledge-repo]] that the auto-sync pushes.")
s = rd("revit-build-via-addin.md").replace("Related: [[karasu-lk1-canopy]]", "Related: [[karasu-lk1-canopy]], [[revit-mcp-bridge]] (BEKA-2's way)")
wr("revit-build-via-addin.md", s)
s = rd("maftun-portals-lira.md").replace("Related: [[lira-model-by-analog]]", "Related: [[project-3602-km-portals]] (Revit КМ of the same object), [[lira-model-by-analog]]")
wr("maftun-portals-lira.md", s)
s = rd("project-3602-km-portals.md")
if "[[maftun-portals-lira]]" not in s:
    s = s.rstrip() + "\n\nLIRA models of the same object: [[maftun-portals-lira]].\n"
    wr("project-3602-km-portals.md", s)
s = rd("main-pc-central.md")
if "Бекасыл КЖ КМ" not in s:
    s = s.rstrip() + "\n- BEKA-2 also has its own local folder `D:\\Бекасыл КЖ КМ` (Revit КЖ/КМ work, `_Стандарт_КЖ`, private repo bekasyl-kzh-km). BEKA-1 cannot see it; notes that cite it are BEKA-2 facts.\n"
    wr("main-pc-central.md", s)
print("done")
