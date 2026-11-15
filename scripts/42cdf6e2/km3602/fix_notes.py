import io
# 1) project note: broken path (octal escape)
p3 = r"D:/РАБОЧКА/Bekassyl/15_Проекты/3602 NRG Maftun Makon (Ташкент)/Порталы — Revit файлдары (15.11).md"
s = io.open(p3, encoding="utf-8", newline="").read()
s = s.replace("КМ\u00f02_Порталы_КМ", "КМ\\3602_Порталы_КМ")
io.open(p3, "w", encoding="utf-8", newline="").write(s)
print("note path ok:", "КМ\\3602_Порталы_КМ" in s, "\u00f0" not in s)

# 2) ЕРЕЖЕЛЕР.md: the 29.10 rule kept the main model — mark it superseded, and say so in the new section
p = r"D:/Бекасыл КЖ КМ/_Стандарт_КЖ/ЕРЕЖЕЛЕР.md"
s = io.open(p, encoding="utf-8", newline="").read()
old = "Негізгі файл түзету мен жинау үшін сақталады; ондағы түзетуден кейін бөлу қайта жүргізіледі."
new = old + " **15.11.2026-дан: бөлгеннен кейін жалпы модель сақталмайды (корзинаға), түзету объект файлының өзінде — «Бір модельдегі объектілерді бөлу» бөлімі.**"
if old in s and new not in s:
    s = s.replace(old, new, 1)
old2 = "- Тазалаудан кейін әр файлда q20; бұрыннан бар қате (мыс. C12) бөлек айтылады.\r\n"
new2 = old2 + "- Бұл бөлім 29.10 «Әр каркас — жеке файл» ережесіндегі «негізгі файл сақталады» деген жерін ауыстырады: енді түзету объект файлының өзінде жасалады.\r\n"
if old2 in s and new2 not in s:
    s = s.replace(old2, new2, 1)
io.open(p, "w", encoding="utf-8", newline="").write(s)
print("ЕРЕЖЕЛЕР ok:", new in s, new2 in s)
