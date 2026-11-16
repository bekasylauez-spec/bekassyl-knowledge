import io
p = r"D:/_claude_work/RMC/kzh/kz94_tables.cs"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# 1) кесте: атау көрсетілмейді (парақта бөлек мәтін — шаблондағыдай кестеден тыс), баған тақырыптары — өрістің өзінде; жол биіктігі 8 мм (шаблон)
i0 = s.index("    Func<string, string, double[], ViewSchedule> Sched = ")
i1 = s.index("    Action<TableSectionData, int, int> NoBorder = ")
s = s[:i0] + (
    "    Func<string, string, double[], string[], ViewSchedule> Sched = (name, tid, widths, heads) =>\n"
    "    { foreach (var old in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(x => x.Name == name).ToList()) d.Delete(old.Id);\n"
    "      var vs = ViewSchedule.CreateSchedule(d, new ElementId(BuiltInCategory.OST_GenericModel)); vs.Name = name; var def = vs.Definition;\n"
    "      Func<string, ScheduleField> AF = pn => def.AddField(def.GetSchedulableFields().First(f => f.ParameterId == PID(pn)));\n"
    "      var f0 = AF(\"КЖ_т0\"); f0.IsHidden = true; var f00 = AF(\"КЖ_т00\"); f00.IsHidden = true;\n"
    "      for (int c = 0; c < widths.Length; c++) { var f = AF(\"КЖ_т\" + (c + 1)); f.ColumnHeading = heads[c]; f.GridColumnWidth = widths[c] * MM; f.HorizontalAlignment = ScheduleHorizontalAlignment.Center; f.HeadingOrientation = ScheduleHeadingOrientation.Horizontal; }\n"
    "      def.AddFilter(new ScheduleFilter(f0.FieldId, ScheduleFilterType.Equal, tid)); def.AddSortGroupField(new ScheduleSortGroupField(f00.FieldId));\n"
    "      def.IsItemized = true; def.ShowGrandTotal = false; def.ShowHeaders = true; def.ShowTitle = false; vs.BodyTextTypeId = tt25.Id; vs.HeaderTextTypeId = tt25.Id; vs.TitleTextTypeId = tt35.Id;\n"
    "      try { vs.RowHeightOverride = RowHeightOverrideOptions.All; vs.RowHeight = 8 * MM; } catch (Exception ex) { log.Add(\"rowheight: \" + ex.Message.Split('\\n')[0]); }\n"
    "      d.Regenerate(); return vs; };\n"
    "    // көп деңгейлі тақырып (шаблон ВРС): GroupHeaders — алдымен берілген жолда, болмаса басқа жолдарда\n"
    "    Func<ViewSchedule, int[], int, int, string, bool> Grp = (vs, rows, l, r, cap) => { foreach (var rr in rows) { try { if (vs.CanGroupHeaders(rr, l, rr, r)) { vs.GroupHeaders(rr, l, rr, r, cap); d.Regenerate(); return true; } } catch { } } log.Add(\"WARN group header «\" + cap + \"» failed\"); return false; };\n"
) + s[i1:]
rep("    Action<ViewSchedule, double> BodyH = (vs, h) => { var bd = vs.GetTableData().GetSectionData(SectionType.Body); int ok = 0; for (int r = 0; r < bd.NumberOfRows; r++) try { bd.SetRowHeight(r, h * MM); ok++; } catch { } if (ok == 0) log.Add(\"body row height not settable\"); };\n", "")
# 2) спецификация мен ВРС жасау бөлігі
i0 = s.index("        var wS = new[] { 15.0, 60, 65, 10, 15, 20 };")
i1 = s.index("        d.Regenerate();\n        // ---- орналастыру")
s = s[:i0] + (
    "        var wS = new[] { 15.0, 60, 65, 10, 15, 20 };\n"
    "        Rows(S + \"/спец-ш\", spec); var vsS = Sched(S + \" Спецификация элементов\", S + \"/спец-ш\", wS, new[] { \"Поз.\", \"Обозначение\", \"Наименование\", \"Кол.\", \"Масса ед.кг\", \"Примечание\" });\n"
    "        { var hd = vsS.GetTableData().GetSectionData(SectionType.Header); try { if (hd.NumberOfRows > 0) hd.SetRowHeight(hd.NumberOfRows - 1, 15 * MM); } catch { } }\n"
    "        var wV = new[] { 32.0, 15, 15, 15, 15, 15, 15, 15, 15, 15, 18 };\n"
    "        var headV = new List<string> { \"Марка элемента\" }; foreach (var dd in DA) headV.Add(\"Ø\" + dd); headV.Add(\"Итого\"); foreach (var dd in DB) headV.Add(\"Ø\" + dd); headV.Add(\"Итого\"); headV.Add(\"Всего\");\n"
    "        Rows(S + \"/врс-ш\", vrs); var vsV = Sched(S + \" Ведомость расхода стали\", S + \"/врс-ш\", wV, headV.ToArray());\n"
    "        { int a0 = 1, a1 = DA.Length + 1, b0 = a1 + 1, b1 = b0 + DB.Length;\n"
    "          Grp(vsV, new[] { 0 }, a0, a1, \"ГОСТ 34028-2016 (214-210-0101)\"); Grp(vsV, new[] { 1, 0 }, b0, b1, \"ГОСТ 34028-2016 (214-210-0501, 214-210-0502)\");\n"
    "          Grp(vsV, new[] { 0 }, a0, a1, \"А240\"); Grp(vsV, new[] { 1, 0 }, b0, b1, \"А500С\");\n"
    "          Grp(vsV, new[] { 0 }, a0, b1, \"Арматура класса\"); Grp(vsV, new[] { 0 }, a0, b1, \"Изделия арматурные\");\n"
    "          var hd = vsV.GetTableData().GetSectionData(SectionType.Header); var txt = new List<string>(); for (int r = 0; r < hd.NumberOfRows; r++) { txt.Add(string.Join(\"|\", Enumerable.Range(0, hd.NumberOfColumns).Select(c => { try { return vsV.GetCellText(SectionType.Header, r, c); } catch { return \"?\"; } }))); }\n"
    "          if (S == SHEETS.First()) log.Add(\"ВРС header: \" + string.Join(\" // \", txt)); }\n"
) + s[i1:]
# 3) атаулар — мәтін (3,5 мм) кесте үстінде ортада; орналастыру: спецификация ескі орнына, ВРС бос жерге (спец астында → ескі ВРС → ескі материалдар → тор бойымен іздеу)
rep("        var sS = Put(vsS, bSpec[0], bSpec[3]); var nbS = SB(sS);",
    "        var sS = Put(vsS, bSpec[0], bSpec[3] - 8); var nbS = SB(sS);\n"
    "        Func<double, double, double, string, TextNote> Title = (x0, x1, yTop, txt0) => TextNote.Create(d, sh.Id, new XYZ((x0 + x1) / 2 * MM, (yTop + 1.5) * MM, 0), txt0, new TextNoteOptions(tt35.Id) { HorizontalAlignment = HorizontalTextAlignment.Center, VerticalAlignment = VerticalTextAlignment.Bottom });\n"
    "        var tS = Title(nbS[0], nbS[2], nbS[3], \"Спецификация элементов\");")
rep("        foreach (var tn in new FilteredElementCollector(d, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().Where(x => x.Id != tnP.Id)) { var bb = tn.get_BoundingBox(sh); obst.Add(new[] { bb.Min.X / MM, bb.Min.Y / MM, bb.Max.X / MM, bb.Max.Y / MM }); }",
    "        foreach (var tn in new FilteredElementCollector(d, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>()) { var bb = tn.get_BoundingBox(sh); obst.Add(new[] { bb.Min.X / MM, bb.Min.Y / MM, bb.Max.X / MM, bb.Max.Y / MM }); }")
rep("        var cands = new List<double[]> { new[] { nbS[0], yP - 6 } }; if (bVrs != null) cands.Add(new[] { bVrs[0], bVrs[3] }); if (bMat != null) cands.Add(new[] { bMat[0], bMat[3] });\n"
    "        double[] pick = null; foreach (var c in cands) { var q = new[] { c[0], c[1] - vsSize[1], c[0] + vsSize[0], c[1] }; if (Free(q)) { pick = c; break; } }",
    "        var cands = new List<double[]> { new[] { nbS[0], yP - 12 } }; if (bVrs != null) cands.Add(new[] { bVrs[0], bVrs[3] - 8 }); if (bMat != null) cands.Add(new[] { bMat[0], bMat[3] - 8 });\n"
    "        { var tb2 = new FilteredElementCollector(d, sh.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).FirstElement().get_BoundingBox(sh); double L2 = tb2.Min.X / MM + 26, T2 = tb2.Max.Y / MM - 5; var grid = new List<double[]>();\n"
    "          for (double yy = T2 - 10; yy - vsSize[1] > B + 2; yy -= 5) for (double xx = L2 + 2; xx + vsSize[0] < R - 1; xx += 5) grid.Add(new[] { xx, yy });\n"
    "          double rx = bVrs != null ? bVrs[0] : nbS[0], ry = bVrs != null ? bVrs[3] : yP; cands.AddRange(grid.OrderBy(g => Math.Abs(g[0] - rx) + Math.Abs(g[1] - ry))); }\n"
    "        double[] pick = null; foreach (var c in cands) { var q = new[] { c[0], c[1] - vsSize[1] - 9, c[0] + vsSize[0], c[1] + 1 }; if (Free(q)) { pick = c; break; } }")
rep("        var sV = Put(vsV, pick[0], pick[1]); var nbV = SB(sV);",
    "        var sV = Put(vsV, pick[0], pick[1] - 8); var nbV = SB(sV); var tV = Title(nbV[0], nbV[2], nbV[3], \"Ведомость расхода стали, кг\");")
rep("(pick == cands[0] ? \" (under spec)\" : \" (old place)\"));",
    "(pick == cands[0] ? \" (under spec)\" : \" (moved)\"));")
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
