# -*- coding: utf-8 -*-
# РПЗ ЛК-1.1 / ЛК-1.2 / ЛК-2 без СВ2 по НТП РК: LIRA tasks «ЛК1 бСВ2», «ЛК2 бСВ2» (pre-СВ2 models, seismic module 61).
# Results from Work AUTORES, pictures from the task's book (MAP: ЛК-1.1 snapshot number -> number in the task's .DOCS).
import io, json, os, shutil, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tit"))
import retitle
ARGS, sys.argv = sys.argv[1:], sys.argv[:1]  # setup.py builds whatever is in argv on import
import setup
import ntp

HERE = os.path.dirname(os.path.abspath(__file__))
W = setup.W
TASK = {"1.1": "ЛК1 бСВ2", "1.2": "ЛК1 бСВ2", "2": "ЛК2 бСВ2"}
MAPF = os.path.join(HERE, "nmap.json")  # {"1": {k: n}, "2": {k: n}}


def build(al):
    task = TASK[al]
    m = {int(k): v for k, v in json.load(open(MAPF, encoding="utf-8")).get(al[0], {}).items()}
    d = os.path.join(HERE, "n_lk" + al)
    if os.path.exists(d):
        shutil.rmtree(d)
    shutil.copytree(setup.BASE, d)
    sub = setup.sub
    # columns Ст1 enlarged to □70×4 (29.10): LIRA keeps them as a new stiffness type (7/8) -> treat it as type 1
    ff = os.path.join(d, "figures_lk.py")
    t = io.open(ff, encoding="utf-8").read()
    t = sub(t, "els[int(r[2])] = (int(r[5]),", "els[int(r[2])] = (int(r[5]) if 2 <= int(r[5]) <= 6 else 1,")
    t = sub(t, "RO = {1: 0.00671,", "RO = {1: 0.00797,")
    io.open(ff, "w", encoding="utf-8").write(t)
    fb = os.path.join(d, "build_lk.py")
    t = io.open(fb, encoding="utf-8").read()
    t = sub(t, "квадратная труба 60×4 по ГОСТ 30245", "квадратная труба 70×4 по ГОСТ 30245")
    t = sub(t, '(1, "Квадратная труба 60 x 4", "ГОСТ 30245-2012", "Ст1", 0.00671)', '(1, "Квадратная труба 70 x 4", "ГОСТ 30245-2012", "Ст1", 0.00797)')
    io.open(fb, "w", encoding="utf-8").write(t)
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
    src_txt = "Навес для ЛК %s.txt" % al.replace(".", ",")
    proto = proto.replace("%s.txt" % task, src_txt).replace(task, src_txt[:-4])
    io.open(os.path.join(res, "protocol.txt"), "w", encoding="utf-8").write(proto.strip("\r\n").replace("\r\n", "\n"))
    f = os.path.join(d, "build_lk.py")
    s = io.open(f, encoding="utf-8").read()
    s = sub(s, 'Work/Навес для ЛК 1.DOCS/"', 'Work/%s.DOCS/"' % task)
    s = sub(s, '_m.read_rsm("Навес для ЛК")', '_m.read_rsm("%s")' % task)
    if al in ("1.1", "1.2"):
        s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК %s.docx"' % al.replace(".", ","))
        if al == "1.2":
            s = sub(s, "ЛК-1.1", "ЛК-1.2", 4)
            s = sub(s, "«КМ Чертеж Лестница ЛК-1»", "«КМ Чертеж Лестница ЛК-1.2»")
            s = sub(s, "вдоль оси Ф между осями 7 и 8", "вдоль оси Г между осями 7 и 8")
        else:
            s = sub(s, "«КМ Чертеж Лестница ЛК-1»", "«КМ Чертеж Лестница ЛК-1.1»")
    else:
        g = setup.GEO["2"]
        ff = os.path.join(d, "figures_lk.py")
        t = io.open(ff, encoding="utf-8").read()
        t = sub(t, 'for row, y in (("А", 0.0), ("Б", 1.4)):', 'for row, y in (("А", 0.0), ("Б", %s)):' % g["yB"])
        t = sub(t, "H_COL = max(c[2] for n, c in co.items() if abs(c[1]) < 1e-6 and abs(c[0]) < 1e-6)",
                "H_COL = max(co[n][2] for e, (st, ns) in els.items() if st == 1 for n in ns)")
        io.open(ff, "w", encoding="utf-8").write(t)
        s = sub(s, '"Навес над наружной лестницей ЛК-1.1"),', '"Навес над наружной лестницей ЛК-2"),')
        s = sub(s, 'лестницей ЛК-1.1, выполненный', 'лестницей ЛК-2, выполненный')
        s = sub(s, '«КМ Чертеж Лестница ЛК-1»', '«КМ Чертеж Лестница ЛК-2»')
        s = sub(s, '"Навес над наружной лестницей ЛК-1.1 – отдельно', '"Навес над наружной лестницей ЛК-2 – отдельно')
        s = sub(s, '"8,5×1,4 м по осям стоек (габарит покрытия 9,0×2,0 м), расположенное вдоль оси Ф между осями 7 и 8. "\n'
                   '    "Шаг рам – 1,7 м (6 рам), консоли покрытия за ряды стоек – по 0,3 м.",', '"%s",' % g["plan"])
        s = sub(s, "(12 шт., два ряда на расстоянии 1,4 м)", g["cols"])
        s = sub(s, "(1,4 м между стойками и консоли по 0,3 м)", g["truss"])
        s = sub(s, 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"', 'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 2.docx"')
        s = sub(s, "для пролета 1,7 м – \"\n       \"L/250 = 6,8 мм", "для пролета %s м – \"\n       \"L/250 = %s мм" % (g["span"], g["lim"]))
        s = sub(s, "при допустимом 6,8 мм", "при допустимом %s мм" % g["lim"])
    for k in sorted(m, reverse=True):
        s = s.replace('picture("scr%02d.png"' % k, 'picture("@@%02d.png"' % m[k])
    s = s.replace('picture("@@', 'picture("scr')
    io.open(f, "w", encoding="utf-8").write(s)
    os.makedirs(os.path.join(d, "rpz"), exist_ok=True)
    r = subprocess.run([sys.executable, "-X", "utf8", "build_lk.py"], cwd=d, capture_output=True, text=True, encoding="utf-8")
    print(al, r.returncode, r.stdout[-600:], r.stderr[-1500:])
    out = os.path.join(d, "rpz", [x for x in os.listdir(os.path.join(d, "rpz")) if x.endswith(".docx")][0])
    retitle.apply(out, out)
    print("ntp", ntp.apply(out))
    print("drift", json.load(open(os.path.join(d, "drift.json"), encoding="utf-8")))


if __name__ == "__main__":
    for al in ARGS:
        build(al)
