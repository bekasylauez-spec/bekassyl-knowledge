def conc_row(m3, note, cls=CONC_CLASS, gost=CONC_GOST, pos=""):
    return dict(pos=pos, gost=gost, name=f"Бетон класса {cls}", qty=round(m3, 2), unit="м³", note=note)


elements = {}
for e in ("Фм-1", "Вп1", "См-1", "Км-1", "Св1", "Св2"):
    if e == "Св2":
        d = {"rows": []}
    else:
        d = {"rows": rows[e]}
    if e in conc:
        d["concrete_m3"] = round(conc[e]["v1"], 3)
        d["concrete_m3_method2"] = round(conc[e]["v2"], 3)
        d["concrete_parts"] = rnd(parts[e])
        d["concrete_class"] = f"{CONC_CLASS}, {CONC_GOST}"
        d["concrete_rows"] = [conc_row(conc[e]["v1"], "без вычета арматуры")]
    elif e == "Вп1":
        d["concrete_m3"] = 0.0
        d["concrete_rows"] = []
    elif e == "Св1":
        d["concrete_m3"] = round(N1 * vp1 / M3, 3)
        d["concrete_class"] = "C16/20 W10 с.ф.ц. (212-101-0705)"
        d["concrete_parts"] = dict(n=N1, L_mm=L1, v_each_m3=round(vp1 / M3, 4), v_total_m3=round(N1 * vp1 / M3, 3))
        d["concrete_rows"] = [conc_row(N1 * vp1 / M3, f"{N1} св. Ø500 L=11000", "С16/20 W10 на сульфатостойком цементе", "ГОСТ 7473-2010 (212-101-0705)")]
    else:
        d["concrete_m3"] = round(N2 * vp2 / M3, 3)
        d["concrete_class"] = "C16/20 W10 с.ф.ц. (212-101-0705)"
        d["concrete_parts"] = dict(n=N2, L_mm=L2, v_each_m3=round(vp2 / M3, 4), v_total_m3=round(N2 * vp2 / M3, 3))
        d["concrete_rows"] = [conc_row(N2 * vp2 / M3, f"{N2} св. Ø500 L=9000, без арматуры", "С16/20 W10 на сульфатостойком цементе", "ГОСТ 7473-2010 (212-101-0705)")]
    d["steel_kg"] = round(steel_tot_el.get(e, 0.0), 2)
    elements[e] = d
elements["Фм-1"]["prep_m3"] = round(PREP["v1_m3"], 3)
elements["Фм-1"]["prep_m3_method2"] = round(PREP["v2_m3"], 3)
elements["Фм-1"]["prep_class"] = "C8/10 W6 F100, t100, r≤5900 (212-101-0309)"
elements["Фм-1"]["prep_row"] = conc_row(PREP["v1_m3"], "подготовка t=100, r≤5900", "С8/10 W6 F100", "ГОСТ 7473-2010 (212-101-0309)")

earth = {
    "ground_z": 0.0, "kotlovan_bottom_z": Z_KB, "R_bottom": R_KB, "R_top": R_KT,
    "kotlovan_main_m3_exact": kot_exact / M3, "kotlovan_main_m3_prismoidal": kot_prism / M3,
    "pit_z_bottom": Z_PIT, "pit_R_bottom": R_PIT_B, "pit_R_top": R_PIT_T,
    "pit_m3_exact": pit_exact / M3, "pit_m3_prismoidal": pit_prism / M3,
    "excavation_total_m3": exc_total / M3,
    "cushion_m3": cush1 / M3, "cushion_m3_method2": cush2 / M3,
    "prep_m3": prep1 / M3,
    "structure_below_zero_m3": env1 / M3, "structure_below_zero_m3_method2": env2 / M3,
    "backfill_m3": backfill1 / M3, "backfill_m3_method2": backfill2 / M3,
    "geomembrane_m2_base": mem_base / M2, "geomembrane_overlap_factor": MEM_OVERLAP,
    "geomembrane_m2": mem_area / M2,
    "rows": [
        dict(pos="1", gost="— (код АГСК не задан)", name="Разработка грунта (котлован + шунқыр приямка)", qty=round(exc_total / M3, 2), unit="м³",
             note="дно -4.100 / -5.393, откос 1:1"),
        dict(pos="2", gost="СТ РК 2790-2015 (217-203-0114)", name="Подушка из уплотненного суглинка t=1000, Купл=0,95",
             qty=round(cush1 / M3, 2), unit="м³", note="r 6400, профиль приямка"),
        dict(pos="3", gost="— (211-103-0101)", name="Обратная засыпка грунтом", qty=round(backfill1 / M3, 2), unit="м³",
             note="плотное тело, без коэффициента (как в Цехе)"),
        dict(pos="4", gost="— (без кода, как в Цехе)", name="Геомембрана HDPE AAG-S t=1,5 мм", qty=round(mem_area / M2, 2), unit="м²",
             note=f"{f2(mem_base/M2)} м² + 10 % на нахлест"),
    ],
}
wp_el = {"Фм-1": (wp_edge + wp_step) / M2, "См-1": wp_wall / M2}
waterproof = {
    "by_element_m2": {**{k: round(v, 2) for k, v in wp_el.items()},
                      "детали": {"Фм-1 край r5800 h500": round(wp_edge / M2, 2), "выступ верх r5300…5800": round(wp_step / M2, 2),
                                 "стена наружн. -2.500…0.000 r5300": round(wp_wall / M2, 2)}},
    "total_m2": round(wp_tot / M2, 2),
    "primer": dict(gost="ТУ 2312-021-10861980-2013 (236-101-0101)", name="Грунтовка", norm_kg_m2=WP_PRIM, kg=round(wp_tot / M2 * WP_PRIM, 1)),
    "mastic": dict(gost="ГОСТ 30693-2000 (235-201-0204)", name="Мастика обмазочная, 2 слоя × 2 кг/м²", norm_kg_m2=WP_MAST, kg=round(wp_tot / M2 * WP_MAST, 1)),
    "primer_kg": round(wp_tot / M2 * WP_PRIM, 1), "mastic_kg": round(wp_tot / M2 * WP_MAST, 1),
}
questions = [
    "Сетка (поз.1/2, оголовок): по правилу ⌈2R/100⌉+1 для R=5750 даёт 116 стержней/напр. Принятая раскладка симметрична (ординаты ±50…±5650 = 114), 2 недостающих (y=±5750, нулевая хорда) взяты по длине ближайшей ненулевой хорды y=±5650 (в задании «±5700» - в нашей сетке такой ординаты нет). Для малых сеток (R=1160, 1370, 1460) то же правило даёт +1 стержень (нечётное число) - добавлен с одной стороны с длиной крайней хорды. Если в этих сетках правило не нужно - сказать.",
    "unit_mass для м.п.-строк: оставлен кг/м (1,998; 0,888) в 3 знаках - при 2 знаках (2,00) total_mass не воспроизводится. Для штучных строк - 2 знака, total_mass - 1 знак (суммы по Ø/элементу считаются от нераспущенных значений).",
    "Разработка грунта: код АГСК и обозначение в ШЕШІМДЕР не заданы (gost = «—»). Обратная засыпка: задан код 211-103-0101, обозначение нет. Геомембрана: без кода (С5). Уточнить, если нужны.",
    "Подготовка C8/10 W6 F100 вынесена отдельной строкой elements['Фм-1'].prep_row (не входит в concrete_m3 Фм-1). Бетон свай: C16/20 W10 с.ф.ц., gost «ГОСТ 7473-2010 (212-101-0705)» - обозначение по аналогии с бетонами конструкций, подтвердить.",
    "Кольца: формула ⌈P/11700⌉ дает стержень >11700; принято n=⌈P/(11700−нахлест)⌉ (в задании 13.11 так и указано); сравнение с альтернативой в checks.",
    "Лоток, углубление 800: учтена только доп. высота стенки лотка (500×150×800) и 8 стержней L=1940 (заменяют 8 из 315 L=1440); боковые радиальные стенки/ребра углубления и доп. кольца стенки в задании не заданы - не включены.",
    "Кольца приямка поз.5: радиусы распределены равномерно между краями (внутр. 1200…1500 ×8, наружн. 1416…1845 ×11) - точные радиусы по разрезу не заданы.",
    "Шп1 Фм (приямок): количество = площадь средней поверхности стенки приямка / 0,16 м² (57 шт); L=640 по ШЕШІМДЕР.",
    "Кр1: 74 каркаса = π·5,8²/1,44 по плановой площади r=5800, ⌈⌉ (по ШЕШІМДЕР).",
    "Сваи: верх Св1 в зоне приямка -5.393 принят как отметка; L свай (11000/9000) задана и от отметки не зависит, количество/бетон не меняются. Св1 у приямка (центр и r=1000) оставлены L=11000 - если их надо удлинить до -5.393 (+1293), сказать.",
    "Карман Ø500×281 (r≤250, -3.793…-3.512) в плите Фм-1 вычтен из Фм-1. Км-1 начинается с -3.512; окна Км-1 и отверстие Ø350 в См-1 не вычтены (по заданию).",
    "Обратная засыпка: геометрический объем плотного тела (без коэффициента, как в Цехе).",
]
steel_out = {}
for e in ("Фм-1", "Вп1", "См-1", "Км-1", "Св1", "Св2"):
    v = steel.get(e, {})
    steel_out[e] = {**{k: round(m, 1) for k, m in sorted(v.items())}, "Итого": round(sum(v.values()), 1)}
steel_out["Итого"] = {**{k: round(m, 1) for k, m in sorted(steel_by_dia.items())}, "Итого": round(steel_all, 1)}
out = dict(
    elements=elements,
    steel=steel_out,
    steel_by_dia={k: round(v, 2) for k, v in steel_by_dia.items()},
    steel_total_kg=round(steel_all, 2),
    steel_structures_kg=round(steel_struct, 2),
    concrete_total_m3=round(tot_c1, 3),
    concrete_piles_m3=round(conc_piles / M3, 3),
    earth=rnd(earth), waterproof=rnd(waterproof),
    piles={"Sv1": sv1, "Sv2": sv2},
    kg_per_m3=rnd(kg_m3, 2),
    checks=rnd(checks, 4),
    old_for_comparison=OLD,
    questions=questions,
)
