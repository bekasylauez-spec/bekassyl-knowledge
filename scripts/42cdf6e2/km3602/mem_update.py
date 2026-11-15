import io
M = r"C:/Users/beka/.claude/projects/R--/memory/"

def append(fn, text, marker):
    p = M + fn
    s = io.open(p, encoding="utf-8", newline="").read()
    if marker in s:
        print(fn, "already"); return
    if not s.endswith("\n"):
        s += "\n"
    io.open(p, "w", encoding="utf-8", newline="").write(s + text)
    print(fn, "appended")

append("project-3602-km-portals.md",
"\n- 15.11.2026 (Revit, BEKA-2, пайдаланушы «обектерді жеке жеке айыр, артықтардың барлығын өшір»): `Каркастар\\` 4 файлы қалды, бөтен блок элементі 0. Блок 1 өзгертілмеді (q20 ALL PASS). Блок 2/3/Карниз: BI КЖ шаблон қоқысы өшірілді (58 вид шаблоны, 147 фильтр, семейство 212 → 11, purge ≈ 9 600). Блок 2-дегі 30.10 «ус тест» кері қайтарылды (2730172/2730173 ext мен join архив мәніне, тест көрінісі өшірілді). q20: Карниз ALL PASS, Блок 2 C12 FAIL 2, Блок 3 C12 FAIL 4 — бұрыннан бар, m14_beltends тек Блок 1-ге қолданылған; түзету = Блок 1-дегідей blk_clean (пайдаланушы шешімі). Корзинаға: 13 резерв, Архив, PDF, _backup (8,6 ГБ). Жалпы модель `3602-КМ_Порталы.rvt` пайдаланушы Revit-інде ашық болды, өшіру сол жабылғанға дейін тұр. Бұдан былай s01_split / m02 тізбегінің көзі жоқ: түзету объект файлдарының өзінде. Obsidian: «15_Проекты/3602 …/Порталы — Revit файлдары (15.11).md». Ереже: [[revit-split-objects-delete-extras]].\n",
"обектерді жеке жеке айыр")

append("revit-mcp-bridge.md",
"- 15.11.2026 (3602, фондағы OpenDocumentFile): фон құжатында `ExportImage` жасасаң, кейін `Close(false)` «The active document may not be closed from the API» қатесін береді. Revit-ті жапқанда ол құжаттар сақтау сұрамай жабылды. `Save`/`SaveAs` (MaximumBackups=1) резервті айналдырады: алдыңғы `name.00NN.rvt` корзинасыз біржола өшеді, жаңа нөмір жазылады. Керек резервті сақтаудан бұрын көшір. Фондағы құжатта `Compact` (Save/SaveAs) Блок 2/3 көлемін кішірейтпеді (≈100 МБ қалды), ал белсенді Карниз 104 → 3,4 МБ болды.\n",
"фон құжатында `ExportImage`")

p = M + "MEMORY.md"
s = io.open(p, encoding="utf-8", newline="").read()
anchor = "- [Жоба папкасын таза ұста](feedback-keep-project-clean.md) — скрин/утилита/бэкап scratchpad-та; артығы корзинаға\n"
line = "- [Объектілерді жеке файлға, артығын өшір](revit-split-objects-delete-extras.md) — Revit: әр объект жеке .rvt, резерв/архив/жалпы модель корзинаға (15.11)\n"
if line not in s:
    assert anchor in s
    s = s.replace(anchor, anchor + line, 1)
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("MEMORY.md line added")
