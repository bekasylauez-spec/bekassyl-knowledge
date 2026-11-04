# -*- coding: utf-8 -*-
"""ЛК-1.1 RPZ: replace own matplotlib figures by LIRA window snapshots (Книга отчетов) and fresh CSV results."""
import io

def sub(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, a[:70], s.count(a))
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8").write(s)

# drift without drawing
s = io.open("figures_lk.py", encoding="utf-8").read()
i = s.index("def fig_disp():"); j = s.index('if __name__ == "__main__":')
s = s[:i] + '''def drift_calc():
    sr = modal_srss()
    q = 4.0
    drift = {}
    for L, i, lab in ((5, 0, "X"), (6, 1, "Y")):
        for row, y in (("А", 0.0), ("Б", 1.4)):
            ns = [n for n, c in co.items() if abs(c[1] - y) < 1e-6 and abs(c[2] - H_COL) < 0.005]
            n = max(ns, key=lambda n: sr[L][n][i]); de = sr[L][n][i]
            drift["%s_%s" % (lab, row)] = dict(row=row, node=n, h=H_COL, de=de, dr=q * de, drnu=q * de * 0.5)
    json.dump(drift, open("drift.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return drift


''' + s[j:]
io.open("figures_lk.py", "w", encoding="utf-8").write(s)

S = "C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/Навес для ЛК 1.DOCS/"
sub("build_lk.py", [
    ('OUTF = sys_out = "rpz/РПЗ_Навес ЛК-1.1.docx"',
     'OUTF = sys_out = "rpz/РПЗ_Навес для ЛК 1.docx"\nSNAP = "%s"\ndrift_calc()' % S),
    ("    p.add_run().add_picture(OUT + fn, width=Cm(width))",
     "    p.add_run().add_picture(SNAP + fn, width=Cm(width))"),
    ('picture("f_load1.png",', 'picture("scr01.png",'),
    ('picture("f_load2.png",', 'picture("scr02.png",'),
    ('picture("f_load3.png",', 'picture("scr03.png",'),
    ('picture("f_load4.png",', 'picture("scr04.png",'),
    ('picture("f_3d.png", "Рис. 4.1.1 – 3Д вид расчетной модели")\n'
     'picture("f_3d_2.png", "Рис. 4.1.2 – Общий 3Д вид расчетной модели")\n'
     'picture("f_plan_bot.png", "Рис. 4.1.3 – Схема элементов покрытия по нижним поясам ферм")\n'
     'picture("f_plan_top.png", "Рис. 4.1.4 – Схема элементов покрытия по верхним поясам ферм")\n'
     'picture("f_row_A.png", "Рис. 4.1.5 – Сечение по оси А")\n'
     'picture("f_row_B.png", "Рис. 4.1.6 – Сечение по оси Б")\n'
     'picture("f_row_mid.png", "Рис. 4.1.7 – Сечение по оси навеса (распорки РС1, связь СВ1)")\n'
     'picture("f_frame.png", "Рис. 4.1.8 – Поперечное сечение рамы", width=11.0)',
     'picture("scr07.png", "Рис. 4.1.1 – 3Д вид расчетной модели")\n'
     'picture("scr08.png", "Рис. 4.1.2 – Общий 3Д вид расчетной модели. Мозаика назначенных жесткостей")\n'
     'picture("scr09.png", "Рис. 4.1.3 – Схема элементов покрытия (план). Мозаика назначенных жесткостей")\n'
     'picture("scr11.png", "Рис. 4.1.4 – Сечение по оси А")\n'
     'picture("scr10.png", "Рис. 4.1.5 – Сечение по оси Б")\n'
     'picture("scr12.png", "Рис. 4.1.6 – Сечение по оси навеса (распорки РС1, связь СВ1)")\n'
     'picture("scr13.png", "Рис. 4.1.7 – Поперечное сечение рамы (по оси 1)", width=13.0)\n'
     'picture("scr14.png", "Рис. 4.1.8 – Мозаика назначенных материалов")'),
    ('picture("f_chk_I.png",', 'picture("scr15.png",'),
    ('picture("f_chk_II.png",', 'picture("scr16.png",'),
    ('picture("f_chk_MU.png",', 'picture("scr17.png",'),
    ('picture("f_defl.png", "Рис. 5.4 – Мозаика прогибов элементов покрытия (РСН IV, перемещения по Z)")',
     'picture("scr18.png", "Рис. 5.4 – Мозаика результатов проверки назначенных сечений по допускаемым прогибам")\n'
     'picture("scr21.png", "Рис. 5.5 – Мозаика максимальных прогибов элементов покрытия по SLS (РСН11_IV, перемещения по Z)")\n'
     'picture("scr19.png", "Рис. 5.6 – Мозаика максимальных горизонтальных перемещений элементов конструкций по SLS по оси X (РСН11_IV)")\n'
     'picture("scr20.png", "Рис. 5.7 – Мозаика максимальных горизонтальных перемещений элементов конструкций по SLS по оси Y (РСН11_IV)")'),
    ('picture("f_drift_X.png", "Рис. 6.1.1 – Мозаика горизонтальных перемещений dr по оси X")\n'
     'picture("f_drift_Y.png", "Рис. 6.1.2 – Мозаика горизонтальных перемещений dr по оси Y")',
     'picture("scr22.png", "Рис. 6.1.1 – Мозаика перемещений по оси X от сейсмического воздействия по X (составляющая 1 – основная форма по X)")\n'
     'picture("scr23.png", "Рис. 6.1.2 – Мозаика перемещений по оси Y от сейсмического воздействия по Y (составляющая 2 – основная форма по Y)")'),
])
print("patched")
