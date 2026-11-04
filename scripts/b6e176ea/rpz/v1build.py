# -*- coding: utf-8 -*-
# Variant 1 (СП РК 2.03-30-2017*, без СВ2): РПЗ ЛК-1.1 / ЛК-1.2 from the original 22.10 calc (base/res + Work snapshots scr01-23),
# ЛК-2 from a fresh calc of the pre-СВ2 model (Work AUTORES + snapshots listed in MAP2). No СВ2 text, no НТП post-process.
import io, os, shutil, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tit"))
import retitle
ARGS, sys.argv = sys.argv[1:], sys.argv[:1]  # setup.py builds whatever is in argv on import
import setup

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
W = setup.W
MAP2 = {}  # ЛК-1.1 snapshot number -> snapshot number in «Навес для ЛК 2.DOCS» (filled after retaking the views)


def build(al):
    d = os.path.join(OUT, "v1_lk" + al)
    if os.path.exists(d):
        shutil.rmtree(d)
    shutil.copytree(setup.BASE, d)
    sub = setup.sub
    if al in ("1.1", "1.2"):
        f = os.path.join(d, "build_lk.py")
        s = io.open(f, encoding="utf-8").read()
        s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК %s.docx"' % al.replace(".", ","))
        if al == "1.2":
            s = sub(s, "ЛК-1.1", "ЛК-1.2", 4)
            s = sub(s, "«КМ Чертеж Лестница ЛК-1»", "«КМ Чертеж Лестница ЛК-1.2»")
            s = sub(s, "вдоль оси Ф между осями 7 и 8", "вдоль оси Г между осями 7 и 8")
            p = os.path.join(d, "res", "protocol.txt")
            t = io.open(p, encoding="utf-8").read()
            io.open(p, "w", encoding="utf-8").write(t.replace("Навес для ЛК 1.txt", "Навес для ЛК 1,2.txt"))
        else:
            s = sub(s, "«КМ Чертеж Лестница ЛК-1»", "«КМ Чертеж Лестница ЛК-1.1»")
        io.open(f, "w", encoding="utf-8").write(s)
    else:
        task = "Навес для ЛК 2"
        g = setup.GEO["2"]
        A = W + task + ".DOCS/AUTORES/"
        res = os.path.join(d, "res")
        for x in os.listdir(res):
            os.remove(os.path.join(res, x))
        for src, dst in (("tbl01.101.csv", "tbl01.101.csv"), ("tbl02.102.csv", "tbl02.102.csv"),
                         ("tbl03.5_1.csv", "tbl03.5_1.csv"), ("tbl05.9_1.csv", "tbl05.9_1.csv"),
                         ("tbl12.49_1.csv", "tbl09.49_1.csv"), ("tbl12.49_2.csv", "tbl09.49_2.csv"),
                         ("tbl12.49_3.csv", "tbl09.49_3.csv"), ("tbl09.23_1.csv", "rsn_disp.csv")):
            shutil.copy(A + src, os.path.join(res, dst))
        proto = open(W + "%s_01.%s" % (task, task), "rb").read().decode("utf-8-sig", errors="replace")
        io.open(os.path.join(res, "protocol.txt"), "w", encoding="utf-8").write(proto.strip("\r\n").replace("\r\n", "\n"))
        f = os.path.join(d, "figures_lk.py")
        s = io.open(f, encoding="utf-8").read()
        s = sub(s, 'for row, y in (("А", 0.0), ("Б", 1.4)):', 'for row, y in (("А", 0.0), ("Б", %s)):' % g["yB"])
        s = sub(s, "H_COL = max(c[2] for n, c in co.items() if abs(c[1]) < 1e-6 and abs(c[0]) < 1e-6)",
                "H_COL = max(co[n][2] for e, (st, ns) in els.items() if st == 1 for n in ns)")
        io.open(f, "w", encoding="utf-8").write(s)
        f = os.path.join(d, "build_lk.py")
        s = io.open(f, encoding="utf-8").read()
        s = sub(s, '"Навес над наружной лестницей ЛК-1.1"),', '"Навес над наружной лестницей ЛК-2"),')
        s = sub(s, 'лестницей ЛК-1.1, выполненный', 'лестницей ЛК-2, выполненный')
        s = sub(s, '«КМ Чертеж Лестница ЛК-1»', '«КМ Чертеж Лестница ЛК-2»')
        s = sub(s, '"Навес над наружной лестницей ЛК-1.1 – отдельно', '"Навес над наружной лестницей ЛК-2 – отдельно')
        s = sub(s, '"8,5×1,4 м по осям стоек (габарит покрытия 9,0×2,0 м), расположенное вдоль оси Ф между осями 7 и 8. "\n'
                   '    "Шаг рам – 1,7 м (6 рам), консоли покрытия за ряды стоек – по 0,3 м.",', '"%s",' % g["plan"])
        s = sub(s, "(12 шт., два ряда на расстоянии 1,4 м)", g["cols"])
        s = sub(s, "(1,4 м между стойками и консоли по 0,3 м)", g["truss"])
        s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 2.docx"')
        s = sub(s, 'Work/Навес для ЛК 1.DOCS/"', 'Work/%s.DOCS/"' % task)
        s = sub(s, '_m.read_rsm("Навес для ЛК")', '_m.read_rsm("%s")' % task)
        s = sub(s, "для пролета 1,7 м – \"\n       \"L/250 = 6,8 мм", "для пролета %s м – \"\n       \"L/250 = %s мм" % (g["span"], g["lim"]))
        s = sub(s, "при допустимом 6,8 мм", "при допустимом %s мм" % g["lim"])
        for k in sorted(MAP2, reverse=True):
            s = s.replace('picture("scr%02d.png"' % k, 'picture("@@%02d.png"' % MAP2[k])
        s = s.replace('picture("@@', 'picture("scr')
        io.open(f, "w", encoding="utf-8").write(s)
    os.makedirs(os.path.join(d, "rpz"), exist_ok=True)
    r = subprocess.run([sys.executable, "-X", "utf8", "build_lk.py"], cwd=d, capture_output=True, text=True, encoding="utf-8")
    print(al, r.returncode, r.stdout[-600:], r.stderr[-1500:])
    out = os.path.join(d, "rpz", [x for x in os.listdir(os.path.join(d, "rpz")) if x.endswith(".docx")][0])
    retitle.apply(out, out)
    print("ok", out)


if __name__ == "__main__":
    for al in ARGS:
        build(al)
