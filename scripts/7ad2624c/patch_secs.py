import io
p = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_secs.cs"
s = io.open(p, encoding="utf-8-sig").read()
def rep(o, n):
    global s
    if o not in s: print("MISSING:", o[:90]); return
    s = s.replace(o, n, 1)
# node circles — current numbering (11.11 renumbering + 12.11 sheets): 1→16, 2→17, 3→18, 4→19, 5→20, 6→21, 7…→22/23, 8→24, 9→25, 10→26, 11/12→27
rep('new[] { 24000.0, 6000, 7600, 2, 16, 0, 16 }, new[] { 24000.0, 3000, 7270, 6, 18, -6, 16 }, new[] { 24000.0, 1500, 6550, 7, 19, 12, -12 }',
    'new[] { 24000.0, 6000, 7600, 2, 17, 0, 16 }, new[] { 24000.0, 3000, 7270, 8, 24, -6, 16 }, new[] { 24000.0, 1500, 6500, 9, 25, 12, -12 }')
rep('new[] { 0.0, 6000, 7300, 8, 19, 9, -12 }', 'new[] { 0.0, 6000, 7300, 10, 26, 9, -12 }')
rep('new[] { 54000.0, 6000, 7300, 8, 19, 9, -10 }', 'new[] { 54000.0, 6000, 7300, 10, 26, 9, -10 }')
rep('new[] { 24000.0, 0, 2700, 3, 17, -8, 9 }, new[] { 3000.0, 0, 2700, 9, 17, 9, 9 }, new[] { 6000.0, 0, 6250, 4, 17, -12, -9 }',
    'new[] { 24000.0, -16, 2700, 3, 18, -8, 9 }, new[] { 3000.0, -16, 2700, 6, 21, 9, 9 }, new[] { 6000.0, -16, 6187, 5, 20, -12, -9 }, new[] { 6000.0, -16, 0, 4, 19, -12, 9 }')
rep('new[] { 24000.0, 12000, 2700, 3, 17, -8, 9 }, new[] { 33000.0, 12000, 2700, 9, 17, 9, 9 }',
    'new[] { 24000.0, 12016, 2700, 3, 18, -8, 9 }, new[] { 33000.0, 12016, 2700, 6, 21, 9, 9 }')
# levels: the runway level was renamed (+6.200)
rep('var lvT = new[] { "-0.400 Низ базы", "+2.700 Распорки", "+6.450 Низ балок у колонн", "+7.110 Низ балок в коньке" };',
    'var lvT = new[] { "-0.400 Низ базы", "+2.700 Распорки", "+6.200 Пути подвесного крана", "+6.450 Низ балок у колонн", "+7.110 Низ балок в коньке" };')
# Ведомость элементов — analog columns: Марка | Сечение | Опорные усилия | Группа | Марка стали | Примечание (тексеріс №2, №91)
rep('var fMk = add("Маркировка типоразмера"); var fSec = add("КМ_Сечение"); var fSt = add("КМ_Сталь"); var fGost = add("КМ_ГОСТ"); var fFam = add("Семейство");',
    '''foreach (var ty in new FilteredElementCollector(d).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().Where(x => x.Family.Name.StartsWith("(КМ)"))) { var pd = ty.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION); if (pd != null && !pd.IsReadOnly && string.IsNullOrEmpty(pd.AsString())) pd.Set("—"); }   // усилия: «—» until the LIRA re-run (№85)
          var fMk = add("Маркировка типоразмера"); var fSec = add("КМ_Сечение"); var fUs = add("Описание"); var fGr = add("КМ_Группа"); var fSt = add("КМ_Сталь"); var fGost = add("КМ_ГОСТ"); var fFam = add("Семейство");
          if (fUs != null) { fUs.ColumnHeading = "Опорные усилия N, кН / M, кН·м / Q, кН"; fUs.GridColumnWidth = 55 * M; } if (fGr != null) { fGr.ColumnHeading = "Группа"; fGr.GridColumnWidth = 15 * M; }''')
rep('fMk.GridColumnWidth = 20 * M; fSec.GridColumnWidth = 55 * M; fSt.GridColumnWidth = 30 * M; fGost.GridColumnWidth = 80 * M;',
    'fMk.GridColumnWidth = 15 * M; fSec.GridColumnWidth = 35 * M; fSt.GridColumnWidth = 20 * M; fGost.GridColumnWidth = 45 * M;')
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
