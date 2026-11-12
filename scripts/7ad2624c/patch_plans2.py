import io
p = r"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\v113_plans.cs"
s = io.open(p, encoding="utf-8-sig").read()
def rep(o, n):
    global s
    if o not in s: print("MISSING:", o[:90]); return
    s = s.replace(o, n, 1)
# 1. hide every viewer / callout mark on the schemes except the section marks kept on 3 and 6
rep('        if (snum == "3" || snum == "6") { var keepS',
    '''        if (snum != "3" && snum != "6") { var hv = new FilteredElementCollector(d, v.Id).OfCategory(BuiltInCategory.OST_Viewers).WhereElementIsNotElementType().ToElementIds().ToList();
          hv.AddRange(new FilteredElementCollector(d, v.Id).OfCategory(BuiltInCategory.OST_Callouts).WhereElementIsNotElementType().ToElementIds()); if (hv.Count > 0) { try { v.HideElements(hv); } catch { } } }   // 12.11: node-sheet callouts / section marks stayed on the schemes (пилот л.7)
        if (snum == "3" || snum == "6") { var keepS''')
# 2. ridge purlin tags on the side away from the ridge
rep('            var tagP = c + nrm * off; IndependentTag tg = null;',
    '            if (Cm(m) == "Пр1" && Math.Abs(c.Y - 6000) < 1000) nrm = new XYZ(0, Math.Sign(c.Y - 6000), 0) * (nrm.Y >= 0 ? 1 : -1) * (nrm.Y >= 0 ? 1 : -1);   // ridge pair: marks outside the pair\n            var tagP = c + (Cm(m) == "Пр1" && Math.Abs(c.Y - 6000) < 1000 ? new XYZ(0, Math.Sign(c.Y - 6000) * off, 0) : nrm * off); IndependentTag tg = null;')
# 3. 8а inside the bay, not over the dim row
rep('nodeMark(30000, -16, 31400, -1300, "8а", "24");', 'nodeMark(30000, -16, 31400, 1500, "8а", "24");')
# 4. notes under the plan (per sheet)
a = '        made.Add(sheet.Id);'
notes = '''        {   // 12.11 (№39, аналог: примечание под схемой): notes at the lower left, over nothing
            var nt = new Dictionary<string, string> {
              { "7", "1. Общие данные см. на листах 1.1, 1.2.\\n2. Прогоны Пр1 - Гн[250х80х5 по ГОСТ 8278, разрезные, шаг 3000 мм; в коньке - по два прогона в 350 мм от конька (узел 2, лист 17).\\n3. Опирание прогонов на балки Б1, Б2 - узел 8, на оголовки колонн - узел 8а (лист 24). Выступ прогонов за оси 1 и 10 - 250 мм.\\n4. Горизонтальные связи ГС1 показаны тонкой штриховой линией, см. лист 6." },
              { "5", "1. Общие данные см. на листах 1.1, 1.2.\\n2. Пути подвесного крана ПБ1 - двутавр 30М по ГОСТ 19425, Q = 3,2 т, пролет 9,0 м; низ пути на отм. +6,200. Путь - по осям 1-9, в пролете 9-10 кран не предусмотрен.\\n3. Монтажные стыки путей - в 600 мм от осей 2-8, стыковой шов с полным проваром; подвески и упоры - узел 9 (лист 25)." } };
            if (nt.ContainsKey(snum)) { var op = new TextNoteOptions(txtT.Id) { HorizontalAlignment = HorizontalTextAlignment.Left, VerticalAlignment = VerticalTextAlignment.Top };
              TextNote.Create(d, sheet.Id, new XYZ(tbb.Min.X + 60 * M, tbb.Min.Y + 120 * M, 0), 300 * M, nt[snum], op); }
        }
        made.Add(sheet.Id);'''
rep(a, notes)
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
