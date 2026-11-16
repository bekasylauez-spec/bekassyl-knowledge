import io
p = r"D:/_claude_work/RMC/kzh/kz94_tables.cs"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# «тақырып-кесте»: бүкіл кесте тақырып бөлігінде (Revit дерек алдындағы бос жолды API-сыз өшіру мүмкін емес), денесі бос
helper = (
    "    // Кесте толығымен тақырып бөлігінде: жолдар биіктігі, біріктіру — шаблондағыдай; денесі бос (сүзгі ештеңе бермейді) → тақырып пен дерек арасында бос жол жоқ\n"
    "    Func<string, double[], List<string[]>, List<double>, List<int[]>, ViewSchedule> HT = (name, widths, rows, heights, merges) =>\n"
    "    { foreach (var old in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(x => x.Name == name).ToList()) d.Delete(old.Id);\n"
    "      var vs = ViewSchedule.CreateSchedule(d, new ElementId(BuiltInCategory.OST_GenericModel)); vs.Name = name; var def = vs.Definition;\n"
    "      Func<string, ScheduleField> AF = pn => def.AddField(def.GetSchedulableFields().First(f => f.ParameterId == PID(pn)));\n"
    "      var f0 = AF(\"КЖ_т0\"); f0.IsHidden = true;\n"
    "      for (int c = 0; c < widths.Length; c++) { var f = AF(\"КЖ_т\" + (c + 1)); f.ColumnHeading = \"\"; f.GridColumnWidth = widths[c] * MM; f.HorizontalAlignment = ScheduleHorizontalAlignment.Center; }\n"
    "      def.AddFilter(new ScheduleFilter(f0.FieldId, ScheduleFilterType.Equal, \"__бос__\")); def.IsItemized = true; def.ShowGrandTotal = false; def.ShowHeaders = false; def.ShowTitle = true;\n"
    "      vs.BodyTextTypeId = tt25.Id; vs.HeaderTextTypeId = tt25.Id; vs.TitleTextTypeId = tt25.Id; d.Regenerate();\n"
    "      var hd = vs.GetTableData().GetSectionData(SectionType.Header); while (hd.NumberOfColumns < widths.Length) hd.InsertColumn(hd.NumberOfColumns);\n"
    "      for (int c = 0; c < widths.Length; c++) hd.SetColumnWidth(c, widths[c] * MM);\n"
    "      while (hd.NumberOfRows < rows.Count) hd.InsertRow(hd.NumberOfRows);\n"
    "      foreach (var m in merges) hd.MergeCells(new TableMergedCell(m[0], m[1], m[2], m[3]));\n"
    "      for (int r = 0; r < rows.Count; r++) { hd.SetRowHeight(r, heights[r] * MM); for (int c = 0; c < rows[r].Length && c < widths.Length; c++) if (!string.IsNullOrEmpty(rows[r][c])) hd.SetCellText(r, c, rows[r][c]); }\n"
    "      d.Regenerate(); return vs; };\n")
rep("    // көп деңгейлі тақырып (шаблон ВРС): GroupHeaders", helper + "    // көп деңгейлі тақырып (шаблон ВРС): GroupHeaders")
# спецификация: тақырып жолы 15 мм + дерек жолдары 8 мм
i0 = s.index("        var wS = new[] { 15.0, 60, 65, 10, 15, 20 };")
i1 = s.index("        d.Regenerate();\n        // ---- орналастыру")
s = s[:i0] + (
    "        var wS = new[] { 15.0, 60, 65, 10, 15, 20 };\n"
    "        foreach (var e in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).WhereElementIsNotElementType().ToElements().Where(e => PS(e, \"КЖ_т0\") == S + \"/спец-ш\" || PS(e, \"КЖ_т0\") == S + \"/врс-ш\").ToList()) d.Delete(e.Id);\n"
    "        var rowsS = new List<string[]> { new[] { \"Поз.\", \"Обозначение\", \"Наименование\", \"Кол.\", \"Масса ед.кг\", \"Примечание\" } }; rowsS.AddRange(spec);\n"
    "        var hS = new List<double> { 15 }; for (int k = 0; k < spec.Count; k++) hS.Add(8);\n"
    "        var vsS = HT(S + \" Спецификация элементов\", wS, rowsS, hS, new List<int[]>());\n"
    "        // ВРС: Марка элемента | Изделия арматурные → Арматура класса → А240 / А500С → ГОСТ → Ø… → Итого | Всего\n"
    "        int a0 = 1, a1 = a0 + DA.Length, b0 = a1 + 1, b1 = b0 + DB.Length, nc = b1 + 2;\n"
    "        var wV = new double[nc]; wV[0] = 32; for (int c = 1; c < nc - 1; c++) wV[c] = 15; wV[nc - 1] = 18;\n"
    "        var rowsV = new List<string[]>(); for (int r = 0; r < 5; r++) rowsV.Add(new string[nc]);\n"
    "        rowsV[0][0] = \"Марка элемента\"; rowsV[0][1] = \"Изделия арматурные\"; rowsV[0][nc - 1] = \"Всего\"; rowsV[1][1] = \"Арматура класса\";\n"
    "        rowsV[2][a0] = \"А240\"; rowsV[2][b0] = \"А500С\"; rowsV[3][a0] = \"ГОСТ 34028-2016 (214-210-0101)\"; rowsV[3][b0] = DB.Any(q => double.Parse(q) <= 10) ? \"ГОСТ 34028-2016 (214-210-0501, 214-210-0502)\" : \"ГОСТ 34028-2016 (214-210-0502)\";\n"
    "        for (int k = 0; k < DA.Length; k++) rowsV[4][a0 + k] = \"Ø\" + DA[k]; rowsV[4][a1] = \"Итого\"; for (int k = 0; k < DB.Length; k++) rowsV[4][b0 + k] = \"Ø\" + DB[k]; rowsV[4][b1] = \"Итого\";\n"
    "        rowsV.AddRange(vrs);\n"
    "        var hV = new List<double> { 7, 7, 7, 10, 7 }; for (int k = 0; k < vrs.Count; k++) hV.Add(8);\n"
    "        var mV = new List<int[]> { new[] { 0, 0, 4, 0 }, new[] { 0, nc - 1, 4, nc - 1 }, new[] { 0, 1, 0, nc - 2 }, new[] { 1, 1, 1, nc - 2 }, new[] { 2, a0, 2, a1 }, new[] { 2, b0, 2, b1 }, new[] { 3, a0, 3, a1 }, new[] { 3, b0, 3, b1 } };\n"
    "        var vsV = HT(S + \" Ведомость расхода стали\", wV, rowsV, hV, mV);\n"
) + s[i1:]
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
