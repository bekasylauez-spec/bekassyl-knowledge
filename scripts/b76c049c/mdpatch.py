p = r"D:\_claude_work\otst\s4\s4_qty.py"
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)


rep('''L.append("Единицы: мм → м³/м²; r, z - s4_geo.py. Арматура: стержень ≤11700, нахлест 61d (Ø18 1100, Ø12 730), массы 1 м: Ø8 0,395; Ø12 0,888; Ø16 1,578; Ø18 1,998; Ø22 2,984. Бетон - без вычета арматуры.\\n")
''', '''L.append("Единицы: мм → м³/м²; r, z - s4_geo.py. Арматура: стержень ≤11700, нахлест 71d (Ø18 1280, Ø12 860), массы 1 м: Ø8 0,395; Ø12 0,888; Ø16 1,578; Ø18 1,998; Ø22 2,984. Бетон Фм-1, См-1, Км-1: C30/37 W8 F200 (212-101-1307), подготовка C8/10 W6 F100 (212-101-0309), сваи C16/20 W10 с.ф.ц. (212-101-0705). Бетон - без вычета арматуры. Параметры 13.11 (ШЕШІМДЕР): мастика 4 кг/м², грунтовка 0,3 кг/м², кольца См 41 ряд × 2 грани, сетка 116 стержней/напр., геомембрана +10 %, запас-строки не вводятся.\\n")
def cmp_row(name, old, new, fmt="{:,.2f}"):
    d = new - old
    pc = d / old * 100 if old else 0.0
    return f"| {name} | {fmt.format(old).replace(',', ' ')} | {fmt.format(new).replace(',', ' ')} | {fmt.format(d).replace(',', ' ')} | {pc:+.1f} % |"


L.append("## 0. Сравнение: прежний расчет (61d, C25/30) → новый (71d, C30/37, 13.11)\\n")
L.append("| Показатель | Было | Стало | Δ | Δ % |")
L.append("|---|---:|---:|---:|---:|")
L.append(cmp_row("Бетон Фм-1, м³", OLD["conc_fm"], C_FM, "{:,.3f}"))
L.append(cmp_row("Бетон См-1, м³", OLD["conc_sm"], C_SM, "{:,.3f}"))
L.append(cmp_row("Бетон Км-1, м³", OLD["conc_km"], C_KM, "{:,.3f}"))
L.append(cmp_row("**Бетон Σ конструкции, м³**", OLD["conc_sum"], tot_c1, "{:,.3f}"))
L.append(cmp_row("Бетон сваи, м³", OLD["conc_piles"], conc_piles / M3))
L.append(cmp_row("Бетон подготовка, м³", OLD["prep"], PREP["v1_m3"], "{:,.3f}"))
for e in ("Фм-1", "Вп1", "См-1", "Км-1", "Св1"):
    L.append(cmp_row(f"Сталь {e}, кг", OLD["steel"][e], steel_tot_el[e]))
L.append(cmp_row("**Сталь конструкции, кг**", OLD["steel_struct"], steel_struct))
L.append(cmp_row("**Сталь всего, кг**", OLD["steel_all"], steel_all))
for k, v in kg_m3.items():
    L.append(cmp_row(f"{k}, кг/м³", OLD["kg"][k], v, "{:,.1f}"))
L.append(cmp_row("Обратная засыпка, м³", OLD["backfill"], backfill1 / M3))
L.append(cmp_row("Геомембрана, м²", OLD["membrane"], mem_area / M2))
L.append(cmp_row("Грунтовка, кг", OLD["primer"], wp_tot / M2 * WP_PRIM))
L.append(cmp_row("Мастика, кг", OLD["mastic"], wp_tot / M2 * WP_MAST))
L.append("")
L.append("Причины: нахлест 61d→71d (Ø18 1100→1280, Ø12 730→860) во всех стыках/скобах/анкерах; кольца стены 40→41 ряд; сетка 114→116 стержней/напр.; геомембрана +10 %; мастика 2→4 кг/м². Объем бетона не изменился (геометрия та же), только класс.\\n")
''')
rep("{r['gost']} ({r['agsk']}) |", "{r['gost']} |")
rep('''L.append(f"- Геомембрана HDPE = площадь верха подушки (r ≤ 6400, с коническим профилем приямка) = **{f2(mem_area/M2)} м²**; сегменты: " + "; ".join(mem_det) + "\\n")''',
    '''L.append(f"- Геомембрана HDPE AAG-S t=1,5 = площадь верха подушки (r ≤ 6400, с коническим профилем приямка) {f2(mem_base/M2)} м² × 1,10 (нахлест) = **{f2(mem_area/M2)} м²**; сегменты: " + "; ".join(mem_det) + "\\n")''')
rep('''мастика (2 слоя, норма Цеха 1112,04/556,02 = {cex_ratio_m:.3f} кг/м² всего): **{f2(wp_tot/M2*WP_MAST)} кг**\\n")''',
    '''мастика (2 слоя × 2 кг/м² = 4 кг/м²): **{f2(wp_tot/M2*WP_MAST)} кг**. По элементам: Фм-1 {f2((wp_edge+wp_step)/M2)} м², См-1 {f2(wp_wall/M2)} м².\\n")''')
rep('''L.append(f"- Цех: грунтовка {cex_ratio_g:.3f} кг/м² (=0,3 ✓), мастика {cex_ratio_m:.3f} кг/м²; фиксаторы''',
    '''L.append(f"- Цех: грунтовка {cex_ratio_g:.3f} кг/м² (=0,3 ✓), мастика Цеха {cex_ratio_m:.3f} кг/м² (здесь принято 4,0 по ШЕШІМДЕР); фиксаторы''')
rep('assert N1 == 41 and N2 == 12, (N1, N2)',
    'assert N1 == 41 and N2 == 12, (N1, N2)\nassert top["nchords"] == 116 and bot["nchords"] == 116, (top["nchords"], bot["nchords"])')
open(p, "w", encoding="utf-8").write(s)
print("ok")
