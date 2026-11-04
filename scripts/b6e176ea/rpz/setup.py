# -*- coding: utf-8 -*-
# Build RPZ for ЛК-2 / ЛК-3 from the ЛК-1.1 generator (same template, same snapshot set, own results)
import io, os, shutil, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tit"))
import retitle
import ntp

ALBUM_PDF = "D:/РАБОЧКА/От Рас груп/ЖК Қарасу село Абай/КМ Чертеж Лестница ЛК-1.1.pdf"
W = "C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/"
HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, "base")

# ЛК-1.1 snapshot number -> snapshot of the same view in the new task
MAP = {
    "1.2": None,
    "1.1": {1: 38, 2: 39, 3: 40, 4: 41, 7: 34, 8: 35, 10: 37, 11: 36, 14: 33, 15: 50, 16: 49, 17: 48,
            18: 47, 19: 46, 20: 45, 21: 44, 22: 43, 23: 42},
    "2": {1: 60, 2: 61, 3: 62, 4: 63, 7: 56, 8: 57, 9: 33, 10: 59, 11: 58, 12: 35, 13: 36, 14: 55,
          15: 72, 16: 71, 17: 70, 18: 69, 19: 68, 20: 67, 21: 66, 22: 65, 23: 64},
    "3": {1: 24, 2: 25, 3: 26, 4: 27, 7: 28, 8: 29, 9: 30, 10: 31, 11: 32, 12: 33, 13: 34, 14: 35, 15: 53,
          16: 52, 17: 51, 18: 50, 19: 49, 20: 48, 21: 47, 22: 46, 23: 45},
}
# vertical cross bracing СВ2 between columns of rows А and Б (bay between the given axes)
BRACE = {"2": "3 и 4", "1.1": "3 и 4", "1.2": "3 и 4"}
GEO = {
    "2": dict(
        plan="9,15×1,5 м по осям стоек (габарит покрытия 9,65×2,0 м), расположенное вдоль оси М у осей 1-2. "
             "Шаг рам – 1,83 м (6 рам), консоли покрытия за ряды стоек – по 0,25 м.",
        cols="(12 шт., два ряда на расстоянии 1,5 м)", truss="(1,5 м между стойками и консоли по 0,25 м)",
        span="1,83", lim="7,3", yB=1.5),
    "3": dict(
        plan="6,7×1,4 м по осям стоек (габарит покрытия 7,2×2,0 м), расположенное вдоль оси К у осей 10/1-11. "
             "Шаг рам – 1,675 м (5 рам), консоли покрытия за ряды стоек – по 0,3 м.",
        cols="(10 шт., два ряда на расстоянии 1,4 м)", truss="(1,4 м между стойками и консоли по 0,3 м)",
        span="1,675", lim="6,7", yB=1.4),
}


def sub(s, a, b, n=1):
    assert s.count(a) == n, (a[:60], s.count(a))
    return s.replace(a, b)


def build(al):
    task = "Навес для ЛК %s" % ("1" if al in ("1.1", "1.2") else al)
    g = GEO.get(al)
    d = os.path.join(HERE, "lk" + al)
    if os.path.exists(d):
        shutil.rmtree(d)
    shutil.copytree(BASE, d)
    # results
    A = W + task + ".DOCS/AUTORES/"
    res = os.path.join(d, "res")
    for f in os.listdir(res):
        os.remove(os.path.join(res, f))
    for src, dst in (("tbl01.101.csv", "tbl01.101.csv"), ("tbl02.102.csv", "tbl02.102.csv"),
                     ("tbl03.5_1.csv", "tbl03.5_1.csv"), ("tbl05.9_1.csv", "tbl05.9_1.csv"),
                     ("tbl12.49_1.csv", "tbl09.49_1.csv"), ("tbl12.49_2.csv", "tbl09.49_2.csv"),
                     ("tbl12.49_3.csv", "tbl09.49_3.csv"), ("tbl09.23_1.csv", "rsn_disp.csv")):
        shutil.copy(A + src, os.path.join(res, dst))
    proto = open(W + "%s_01.%s" % (task, task), "rb").read().decode("utf-8-sig", errors="replace")
    io.open(os.path.join(res, "protocol.txt"), "w", encoding="utf-8").write(proto.strip("\r\n").replace("\r\n", "\n"))

    f = os.path.join(d, "figures_lk.py")
    if al in ("1.1", "1.2"):
        # ЛК-1.2 is the same model as ЛК-1.1 (copy of the .lir), only the album name and the building axis differ
        f = os.path.join(d, "build_lk.py")
        s = io.open(f, encoding="utf-8").read()
        s = sub(s, '_m.read_rsm("Навес для ЛК")', '_m.read_rsm("%s")' % task)
        s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК %s.docx"' % al.replace(".", ","))
        if al == "1.2":
            s = sub(s, "ЛК-1.1", "ЛК-1.2", 4)
            s = sub(s, "«КМ Чертеж Лестница ЛК-1»", "«КМ Чертеж Лестница ЛК-1.2»")
            s = sub(s, "вдоль оси Ф между осями 7 и 8", "вдоль оси Г между осями 7 и 8")
            p = os.path.join(res, "protocol.txt")
            t = io.open(p, encoding="utf-8").read()
            io.open(p, "w", encoding="utf-8").write(t.replace("Навес для ЛК 1.txt", "Навес для ЛК 1,2.txt"))
        io.open(f, "w", encoding="utf-8").write(s)
        return patch_tail(al, d)
    s = io.open(f, encoding="utf-8").read()
    s = sub(s, 'for row, y in (("А", 0.0), ("Б", 1.4)):', 'for row, y in (("А", 0.0), ("Б", %s)):' % g["yB"])
    s = sub(s, "H_COL = max(c[2] for n, c in co.items() if abs(c[1]) < 1e-6 and abs(c[0]) < 1e-6)",
            "H_COL = max(co[n][2] for e, (st, ns) in els.items() if st == 1 for n in ns)")
    io.open(f, "w", encoding="utf-8").write(s)

    f = os.path.join(d, "build_lk.py")
    s = io.open(f, encoding="utf-8").read()
    s = sub(s, '"Навес над наружной лестницей ЛК-1.1"),', '"Навес над наружной лестницей ЛК-%s"),' % al)
    s = sub(s, 'лестницей ЛК-1.1, выполненный', 'лестницей ЛК-%s, выполненный' % al)
    s = sub(s, '«КМ Чертеж Лестница ЛК-1»', '«КМ Чертеж Лестница ЛК-%s»' % al)
    s = sub(s, '"Навес над наружной лестницей ЛК-1.1 – отдельно', '"Навес над наружной лестницей ЛК-%s – отдельно' % al)
    s = sub(s, '"8,5×1,4 м по осям стоек (габарит покрытия 9,0×2,0 м), расположенное вдоль оси Ф между осями 7 и 8. "\n'
               '    "Шаг рам – 1,7 м (6 рам), консоли покрытия за ряды стоек – по 0,3 м.",', '"%s",' % g["plan"])
    s = sub(s, "(12 шт., два ряда на расстоянии 1,4 м)", g["cols"])
    s = sub(s, "(1,4 м между стойками и консоли по 0,3 м)", g["truss"])
    s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК %s.docx"' % al)
    s = sub(s, 'Work/Навес для ЛК 1.DOCS/"', 'Work/%s.DOCS/"' % task)
    s = sub(s, '_m.read_rsm("Навес для ЛК")', '_m.read_rsm("%s")' % task)
    s = sub(s, "для пролета 1,7 м – \"\n       \"L/250 = 6,8 мм", "для пролета %s м – \"\n       \"L/250 = %s мм" % (g["span"], g["lim"]))
    s = sub(s, "при допустимом 6,8 мм", "при допустимом %s мм" % g["lim"])
    io.open(f, "w", encoding="utf-8").write(s)
    patch_tail(al, d)


def patch_tail(al, d):
    f = os.path.join(d, "build_lk.py")
    s = io.open(f, encoding="utf-8").read()
    if al in BRACE:
        s = sub(s, "в продольном – защемленными в основании стойками, распорками РС1 по рядам стоек ",
                "в продольном – вертикальными крестовыми связями СВ2 по стойкам рядов А и Б в среднем пролете "
                "(между осями %s), распорками РС1 по рядам стоек " % BRACE[al])
        s = sub(s, '"РС1, СВ1", 0.00282)', '"РС1, СВ1, СВ2", 0.00282)')
        s = sub(s, "СГ1, РС1, СВ1 – ферменный элемент.", "СГ1, РС1, СВ1, СВ2 – ферменный элемент.")
        s = sub(s, '"Рис. 4.1.4 – Сечение по оси А"', '"Рис. 4.1.4 – Сечение по оси А (вертикальная связь СВ2)"')
        s = sub(s, '"Рис. 4.1.5 – Сечение по оси Б"', '"Рис. 4.1.5 – Сечение по оси Б (вертикальная связь СВ2)"')
    m = MAP[al] or MAP["1.1"]
    for k in sorted(m, reverse=True):
        s = s.replace('picture("scr%02d.png"' % k, 'picture("@@%02d.png"' % m[k])
    s = s.replace('picture("@@', 'picture("scr')
    io.open(f, "w", encoding="utf-8").write(s)
    os.makedirs(os.path.join(d, "rpz"), exist_ok=True)
    for x in os.listdir(os.path.join(d, "rpz")):
        os.remove(os.path.join(d, "rpz", x))
    r = subprocess.run([sys.executable, "-X", "utf8", "build_lk.py"], cwd=d, capture_output=True, text=True, encoding="utf-8")
    print(al, r.returncode, r.stdout[-400:], r.stderr[-1500:])
    # title pages: РПЗ's own style, company and object address as in the КМ album
    out = os.path.join(d, "rpz", [x for x in os.listdir(os.path.join(d, "rpz")) if x.endswith(".docx")][0])
    retitle.apply(out, out)
    print('ntp', ntp.apply(out))


for al in sys.argv[1:]:
    build(al)
