import os, shutil
D = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто'
bak = os.path.join(D, '_bak_0511'); os.makedirs(bak, exist_ok=True)
cache = {}
def T(name):
    if name not in cache:
        p = os.path.join(D, name)
        if not os.path.exists(os.path.join(bak, name)): shutil.copy2(p, os.path.join(bak, name))
        cache[name] = open(p, encoding='utf-8-sig').read()
    return cache[name]
def rep(name, a, b, count=1):
    t = T(name)
    assert t.count(a) >= 1, (name, a)
    cache[name] = t.replace(a, b, count if count else -1) if count else t.replace(a, b)
def save():
    for name, t in cache.items():
        open(os.path.join(D, name), 'w', encoding='utf-8-sig').write(t)

# ---- ведомость form: units in кН (remark 329 п.9) ----
rep('ved_elem.ps1', "'М, тс·м'", "'М, кН·м'"); rep('ved_elem.ps1', "'N, тс'", "'N, кН'"); rep('ved_elem.ps1', "'Q, тс'", "'Q, кН'")
# ved_rows.ps1 written by the Write tool: give it the BOM PowerShell 5.1 needs
T('ved_rows.ps1')

# ---- К = I60Ш2 by ЛИРА (was 60Ш3): the К1 section ----
rep('zavod_grid.ps1', "'К'   = @{ D = 597; B = 300; tf = 24.5; tw = 18; rot = $false }", "'К'   = @{ D = 589; B = 300; tf = 20.5; tw = 16; rot = $false }      # I60Ш2 (ЛИРА В_109_v3_КМ)")

# ---- sheet 3 ----
s = 'sheet03.ps1'
rep(s, "if ($r -eq 'A') { Op \"TXT", "Op \"TXT")
rep(s, "Isocpeur\" }\n  }\n}", "Isocpeur\"\n  }\n}")
rep(s, "foreach ($q in $kn)", "$kn += ,@(12, '17', (AX 10), (RY 'A'), 1800, -1200)\nforeach ($q in $kn)")
rep(s, 'Notes "1. Общие данные см. лист 1.1.\\n2. Колонны установлены по центру осей.\\n3. Разрезы 1-1, 2-2, 3-3 см. листы 9, 10, 11.\\n4. Узлы 1, 2 (базы колонн Б1, Б2) см. листы 13, 14, узлы 3-5 (базы колонн К3, СФ, СФ1) - лист 15.\\n5. Марки вертикальных связей по рядам E, H, M будут указаны после получения данных."',
    'Notes "1. Общие данные см. лист 1.1.\\n2. Колонны установлены по центру осей.\\n3. Разрезы 1-1, 2-2, 3-3 см. листы 9, 10, 11.\\n4. Узлы 1, 2 (базы колонн Б1, Б2) см. листы 13, 14, узлы 3-5 (базы колонн К3, СФ, СФ1) - лист 15, узел 12 - лист 17.\\n5. Вертикальные связи ВС (до отм. +10.340) и ВС1 (выше) - по рядам A, E, H, M в панелях 2-3, 9-10, 19-20, 26-27."\n. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'К\', \'К1\', \'К2\', \'К3\', \'СФ\', \'СФ1\', \'ВС\', \'ВС1\')')

# ---- sheet 4: struts and braces in all four rows (ЛИРА: rows A, E, H, M), рс on axes 1, 28 at +6.200 ----
s = 'sheet04.ps1'
rep(s, "$y = RY 'A'\nfor ($b = 1; $b -le 27; $b++) {", "foreach ($r in 'A', 'E', 'H', 'M') {\n$y = RY $r\nfor ($b = 1; $b -le 27; $b++) {")
t = T(s); i = t.index("# ---- rows E, H, M: the brace bays of sheet 3"); j = t.index("Chains", i)
cache[s] = t[:i] + """}
# ---- рс on the end walls: axes 1 and 28 at +6.200 between the fachwerk posts (ЛИРА) ----
$rl = @($rows.Keys)
foreach ($i in 1, 28) {
  for ($q = 0; $q -lt $rl.Count - 1; $q++) {
    $x = AX $i; $y1 = (RY $rl[$q]) + 300; $y2 = (RY $rl[$q + 1]) - 300
    Op "LINE`t$(F $x) $(F $y1) $(F $x) $(F $y2) 50`t`tВЛ"
  }
  $xt = if ($i -eq 1) { (AX 1) - 0.8*$k } else { (AX 28) + 0.8*$k }
  Op "TXT`t$(F $xt) $(F ((RY 'C') + 3000))`tрс`t$(F (2.5*$k)) 0 $(if ($i -eq 1) { 6 } else { 4 })`tTEXT 2.5`tIsocpeur"
}

""" + t[j:]
rep(s, '\\n3. Распорки рс по ряду A установлены на отм. +5.020 и +10.340, в связевых панелях - вместе со связями ВС (до отм. +10.340) и ВС1 (выше).\\n4. Распорки и марки связей по рядам E, H, M будут указаны после получения данных."',
    '\\n3. Распорки рс по рядам A, E, H, M установлены на отм. +5.020 и +10.340, в связевых панелях - вместе со связями ВС (до отм. +10.340) и ВС1 (выше).\\n4. Распорки рс по осям 1 и 28 (торцевой фахверк) - на отм. +6.200.\\n5. Ведомость связей ВС, ВС1 см. лист 3, узел 12 - лист 17."\n. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'рс\')')

# ---- sheet 5 ----
s = 'sheet05.ps1'
rep(s, 'консоли КН - I 40Ш1, сталь С255.\\n4. Кран мостовой Q=2 т в каждом пролете, рельс Р24, верх подкрановой балки на отм. +11.000."',
    'консоли КН - I 40Ш1, сталь С255.\\n4. Кран мостовой Q=2 т в каждом пролете, рельс Р24, верх подкрановой балки на отм. +11.000.\\n5. Опирание ПБ на консоли КН - узел 11, лист 17."\n. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'ПБ\', \'КН\')\nOp "KNOT`t11`t17`t$(F (AX 3)) $(F ((RY \'A\') + 300)) $(F (4*$k)) $(F ((AX 3) + 1800)) $(F ((RY \'A\') - 1500))"')

# ---- sheet 6: Р/Р1/Р2 were also the truss diagonals of ФФ1 -> Бм1/Бм2/Бм3; а1 = I25Б1 (ЛИРА) ----
s = 'sheet06.ps1'
rep(s, "{ 'Р2' }", "{ 'Бм3' }")
rep(s, "Plan '+4.000' 19 360 @('Р', 'Т', 'Т', 'Р1', 'Т', 'Т', 'Р') @(14, 17)", "Plan '+4.000' 19 360 @('Бм1', 'Т', 'Т', 'Бм2', 'Т', 'Т', 'Бм1') @(14, 17)")
rep(s, "Plan '+7.600' 16 170 @('Р', 'Т', 'Т', 'Р') @(14)", "Plan '+7.600' 16 170 @('Бм1', 'Т', 'Т', 'Бм1') @(14)")
t = T(s); i = t.index("# ---- ведомость элементов (Tekla sheet 7)"); j = t.index("Notes ", i)
cache[s] = t[:i] + '. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'Бм1\', \'Бм2\', \'Бм3\', \'Т\', \'а\', \'а1\') 404\n\n' + t[j:]
rep(s, 'Балки опираются на колонны по ряду M и колонны К3 (линия К3 - 10000 от оси M)."', 'Балки опираются на колонны по ряду M и колонны К3 (линия К3 - 10000 от оси M).\\n4. Балка Бм3 (обрамление проема) в расчетной схеме не учтена - конструктивно."')
rep(s, "PY 205))", "PY 175))")

# ---- sheet 7 ----
s = 'sheet07.ps1'
t = T(s); i = t.index("# ---- ведомость элементов (Tekla sheet 4)"); j = t.index("Title $name", i)
cache[s] = t[:i] + '. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'рф\', \'св\')\n\n' + t[j:]
rep(s, '\\n4. Связи св - V-образные, из Гн □100x3 (сечение по Tekla, лист 4)."', '\\n4. Связи св - вертикальные V-образные между фермами в панелях 2-3, 9-10, 19-20, 26-27 (от нижнего пояса к верхнему)."')

# ---- sheet 8: Б1 -> БП1, ББ -> БП2 (Б1/Б2 are the bases); п = [27П (ЛИРА) ----
s = 'sheet08.ps1'
rep(s, "    Op \"MARK`t$($p[0])`t", "    $mn = switch ($p[0]) { 'Б1' { 'БП1' } 'ББ' { 'БП2' } default { $p[0] } }\n    Op \"MARK`t$mn`t")
t = T(s); i = t.index("# ---- ведомость элементов (Tekla sheet 5)"); j = t.index("Title $name", i)
cache[s] = t[:i] + '. "$PSScriptRoot\\ved_elem.ps1"; . "$PSScriptRoot\\ved_rows.ps1"\n$null = VedSheet @(\'ФФ1\', \'БП1\', \'БП2\', \'п\', \'с\')\nOp "KNOT`t9`t17`t$(F (AX 4)) $(F (RY \'A\')) $(F (4*$k)) $(F ((AX 4) + 1800)) $(F ((RY \'A\') - 1500))"\nOp "KNOT`t10`t17`t$(F (AX 4)) $(F (RY \'E\')) $(F (4*$k)) $(F ((AX 4) + 1800)) $(F ((RY \'E\') + 1500))"\n\n' + t[j:]
rep(s, 'балки Б1, прогоны п, связи с."', 'балки БП1, прогоны п, связи с.\\n4. Опирание ферм ФФ1 и балок БП2 на колонны - узлы 9, 10, лист 17."')

# ---- sheet 12: groups, kN, the notes ----
s = 'sheetD12.ps1'
for a in ("'I 20Ш1', '', '', '', ''", "'Гн □120x5', '', '', '', ''", "'Гн □100x3', '', '', '', ''"):
    rep(s, a, a[:-2] + "'2'", 0)
rep(s, '\\n4. Опорные усилия и группа конструкций в исходных данных (Tekla) не даны."', '\\n4. Опирание ферм на колонны - узлы 9, 10, лист 17.\\n5. Сечения элементов - по расчету (ЛИРА-САПР, схема В_109_v3_КМ)."')

# ---- sheet 16 and the sections: the Tekla mark Б1 of the roof beam is БП1, ББ is БП2, р (strut) is рф ----
for s in ('sheetD16.ps1', 'sheetD09.ps1', 'sheetD10.ps1', 'sheetD11.ps1'):
    t = T(s); i = t.index('[IO.File]::WriteAllLines')
    cache[s] = t[:i] + "for ($q = 0; $q -lt $o.Count; $q++) { $o[$q] = $o[$q] -replace \"^MARK`tБ1`t\", \"MARK`tБП1`t\" -replace \"^MARK`tББ`t\", \"MARK`tБП2`t\" -replace \"^MARK`tр`t\", \"MARK`tрф`t\" }\n" + t[i:]

# ---- sheet 1.4: note about the masses ----
rep('sheet14.ps1', 'Tx 22 ($yb - 6) "1. Общие данные см. лист 1.1." 2.5 0 7',
    'Tx 22 ($yb - 6) "1. Общие данные см. лист 1.1.\\n2. Масса профилей определена по длинам элементов расчетной схемы (ЛИРА-САПР, В_109_v3_КМ), без учета наплавленного металла." 2.5 270 7')

# ---- sheet 2.1: К2 on base Б1 ----
s = 'sheet21.ps1'
rep(s, "    if ($nm -eq 'К2') { continue }\n    if ($nm -eq 'К') {", "    if ($nm -eq 'К' -or $nm -eq 'К2') {")
rep(s, '\\n4. База колонн К2 (ряд M, оси 13...16) будет показана после получения данных."', '\\n4. Под колонны К2 (ряд M, оси 13...16, I60Ш3) принята база Б1 (зеркально), см. узел 1, лист 13."')

# ---- album: sheet 17 = new nodes sheet ----
rep('ceh_build.ps1', "Gen = 'sheetD17.ps1'", "Gen = 'sheetD17n.ps1'")
rep('album_b109.txt', "17\tВедомость элементов каркаса", "17\tУзлы 9, 10, 11, 12")
rep('album_frames.txt', "17\t440000 -900000\t297 420\t100\t1", "17\t440000 -900000\t594 420\t10\t1")
save()
print('saved', sorted(cache))
