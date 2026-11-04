k = open('km2.cs', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global k
    assert k.count(a) == cnt, (k.count(a), a[:90])
    k = k.replace(a, b)


# portrait A3 titleblock for the technical specification
rep('''            string tbA2 = MakeTitleblock(app, J["rfttb2"], famDir, "КМ_Штамп А2", 594, 420, "А2", J["stampdir"]);''',
    '''            string tbA2 = MakeTitleblock(app, J["rfttb2"], famDir, "КМ_Штамп А2", 594, 420, "А2", J["stampdir"]);
            string tbA3k = MakeTitleblock(app, J["rfttb3"], famDir, "КМ_Штамп А3 книжный", 297, 420, "А3", J["stampdir"]);''')
rep('FamilySymbol tb3 = null, tb2 = null;', 'FamilySymbol tb3 = null, tb2 = null, tb3k = null;')
rep('tb3 = LoadSym(doc, tbA3); tb2 = LoadSym(doc, tbA2);', 'tb3 = LoadSym(doc, tbA3); tb2 = LoadSym(doc, tbA2); tb3k = LoadSym(doc, tbA3k);')
rep('TextNoteType t30 = null, t25 = null, tTitle = null;', 'TextNoteType t30 = null, t25 = null, tTitle = null, t35 = null;')
rep('''                tTitle = TextType(doc, "КМ_Заголовок 3,0", ISO, 3.0, false);''', '''                tTitle = TextType(doc, "КМ_Заголовок 3,0", ISO, 3.0, false);
                t35 = TextType(doc, "КМ_ISOCPEUR 3,5", ISO, 3.5, false);''')
# dimension style as «СПДС» in the DWG
rep('''                dimT.SetUnitsFormatOptions(fd2);''', '''                dimT.SetUnitsFormatOptions(fd2);
                try { dimT.get_Parameter(BuiltInParameter.WITNS_LINE_EXTENSION).Set(1.25 * MM); } catch (Exception ex) { L("dim ext " + ex.Message); }
                try { dimT.get_Parameter(BuiltInParameter.DIM_LINE_EXTENSION).Set(2.0 * MM); } catch (Exception ex) { L("dim lext " + ex.Message); }
                try { dimT.get_Parameter(BuiltInParameter.TEXT_DIST_TO_LINE).Set(0.8 * MM); } catch (Exception ex) { L("dim off " + ex.Message); }
                foreach (Parameter p in dimT.Parameters)
                    if (p.StorageType == StorageType.Double && p.Definition.Name.StartsWith("Зазор")) { try { p.Set(0.625 * MM); L("  dim " + p.Definition.Name + " = 0,625"); } catch { } }''')
# sheet order parameter
rep('''                    doc.ParameterBindings.Insert(def, app.Create.NewInstanceBinding(cs), GroupTypeId.Data);
                }''', '''                    doc.ParameterBindings.Insert(def, app.Create.NewInstanceBinding(cs), GroupTypeId.Data);
                }
                CategorySet csh = app.Create.NewCategorySet(); csh.Insert(Category.GetCategory(doc, BuiltInCategory.OST_Sheets));
                Definition dsh = grp.Definitions.Create(new ExternalDefinitionCreationOptions("КМ_Порядок_листа", SpecTypeId.Number));
                doc.ParameterBindings.Insert(dsh, app.Create.NewInstanceBinding(csh), GroupTypeId.Data);''')
# plates after the frame
rep('''            L("columns " + nc + " framing " + nb);''', '''            L("columns " + nc + " framing " + nb);
            Tx(doc, "plates", delegate { AddPlates(doc, lvBase, lvTop); });''')
# SPDS-style section mark (thick stroke, arrow, number) = type «Разрез»
rep('''            ViewFamilyType vtSec = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section);''',
    '''            ViewFamilyType vtSec = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section && v.Name == "Разрез") ?? Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Section);''')
for a, b in (('Sec(doc, vtSec.Id, "Разрез 1-1",', 'Sec(doc, vtSec.Id, "1",'), ('Sec(doc, vtSec.Id, "Разрез 2-2",', 'Sec(doc, vtSec.Id, "2",'),
             ('Sec(doc, vtSec.Id, "Разрез 3-3",', 'Sec(doc, vtSec.Id, "3",'), ('Sec(doc, vtSec.Id, "Разрез 4-4",', 'Sec(doc, vtSec.Id, "4",')):
    rep(a, b)
# truss schemes Ф1/Ф2 (single-line, markers hidden on the 1:75 plans)
rep('''                View3D v3 = View3D.CreateIsometric(doc, vt3d.Id);''', '''                foreach (string[] fs in new[] { new[] { "Ф1", "4350", "9600" }, new[] { "Ф2", "16450", "8100" } })
                {
                    ViewSection sv = Sec(doc, vtSec.Id, "Схема " + fs[0], "Геометрическая схема фермы " + fs[0], new XYZ(D(fs[1]) * MM - 150 * MM, 0, 0), XYZ.BasisY, -1400, D(fs[2]), 1500, 5300, 400, 50);
                    sv.DetailLevel = ViewDetailLevel.Coarse;
                    sv.DisplayStyle = DisplayStyle.HLR;
                    StyleView(doc, sv, flt, solid, new[] { "ВП1", "НП1", "Р1" });
                    sv.DetailLevel = ViewDetailLevel.Coarse;
                    try { sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), true); sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Sections), true); sv.SetCategoryHidden(new ElementId(BuiltInCategory.OST_GenericModel), true); } catch { }
                    try { sv.get_Parameter(BuiltInParameter.SECTION_COARSER_SCALE_PULLDOWN_METRIC).Set(20); } catch (Exception ex) { L("hide marker " + ex.Message); }
                    sv.CropBoxVisible = false;
                    V["s" + fs[0]] = sv;
                }
                View3D v3 = View3D.CreateIsometric(doc, vt3d.Id);''')
# node callouts after the views
rep('''            L("views ok");''', '''            L("views ok");
            ViewFamilyType vtDet = Find<ViewFamilyType>(doc, v => v.ViewFamily == ViewFamily.Detail);
            Dictionary<string, View> NV = new Dictionary<string, View>();
            Tx(doc, "nodes", delegate
            {
                NV = NodeViews(doc, V, vtDet.Id, vtPlan.Id, lvBase);
                foreach (KeyValuePair<string, View> kv in NV)
                    StyleView(doc, kv.Value, flt, solid, (kv.Key == "8" || kv.Key == "9") ? new[] { "НП1", "СГ1", "РС1", "СВ3" } : null);
            });
            L("nodes " + NV.Count);''')
# plan dimensions as on the DWG sheets
rep('''                        ReferenceArray ra = new ReferenceArray(); foreach (Grid g in gx) ra.Append(new Reference(g));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1300 * MM, 0), new XYZ(1, -1300 * MM, 0)), ra, dimT);
                        ReferenceArray ro = new ReferenceArray(); ro.Append(new Reference(gx.First())); ro.Append(new Reference(gx.Last()));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1900 * MM, 0), new XYZ(1, -1900 * MM, 0)), ro, dimT);
                        ReferenceArray rl = new ReferenceArray(); foreach (Grid g in gy) rl.Append(new Reference(g));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(-1900 * MM, 0, 0), new XYZ(-1900 * MM, 1, 0)), rl, dimT);
                        ReferenceArray rc = new ReferenceArray();
                        foreach (FamilyInstance c in colsL) rc.Append(c.GetReferences(FamilyInstanceReferenceType.CenterLeftRight).First());''',
'''                        ReferenceArray rc = new ReferenceArray();
                        foreach (FamilyInstance c in colsL) rc.Append(c.GetReferences(FamilyInstanceReferenceType.CenterLeftRight).First());
                        ReferenceArray ra = new ReferenceArray(); foreach (Grid g in gx) ra.Append(new Reference(g));
                        ra.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1300 * MM, 0), new XYZ(1, -1300 * MM, 0)), ra, dimT);
                        ReferenceArray ro = new ReferenceArray(); ro.Append(new Reference(gx.First())); ro.Append(new Reference(gx.Last()));
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(0, -1900 * MM, 0), new XYZ(1, -1900 * MM, 0)), ro, dimT);
                        ReferenceArray rl = new ReferenceArray(); foreach (Grid g in gy) rl.Append(new Reference(g));
                        string rowMk = k == "p5" ? "РС1" : k == "p6" ? "П1" : null;
                        List<FamilyInstance> rowEls = rowMk == null ? new List<FamilyInstance>() : new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
                            .Where(f => f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == rowMk && ((LocationCurve)f.Location).Curve.GetEndPoint(0).X > 21000 * MM).GroupBy(f => Math.Round(((LocationCurve)f.Location).Curve.GetEndPoint(0).Y / MM)).Select(g => g.First()).OrderBy(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y).ToList();
                        FamilyInstance cant = rowEls.FirstOrDefault(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y < -600 * MM);
                        if (cant != null) { Reference cr = cant.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (cr != null) rl.Append(cr); }
                        doc.Create.NewDimension(v, Line.CreateBound(new XYZ(-1900 * MM, 0, 0), new XYZ(-1900 * MM, 1, 0)), rl, dimT);
                        if (rowEls.Count > 1)
                        {
                            ReferenceArray rr = new ReferenceArray();
                            foreach (FamilyInstance f in rowEls) { Reference r0 = f.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (r0 != null) rr.Append(r0); }
                            if (rr.Size > 1) doc.Create.NewDimension(v, Line.CreateBound(new XYZ(24700 * MM, 0, 0), new XYZ(24700 * MM, 1, 0)), rr, dimT);
                        }''')
# section dimensions: panel chain on top, levels on the left; overall along the rows
rep('''                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, 0, 300 * MM), new XYZ(x, 1, 300 * MM)), ra, dimT);''',
'''                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, 0, 300 * MM), new XYZ(x, 1, 300 * MM)), ra, dimT);
                        ReferenceArray rp = new ReferenceArray();
                        foreach (FamilyInstance f in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>()
                            .Where(f => f.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == "П1").Where(f => { Curve cv = ((LocationCurve)f.Location).Curve; double a0 = Math.Min(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X), a1 = Math.Max(cv.GetEndPoint(0).X, cv.GetEndPoint(1).X); return a0 < x + 300 * MM && a1 > x + 300 * MM; })
                            .OrderBy(f => ((LocationCurve)f.Location).Curve.GetEndPoint(0).Y))
                        { Reference r0 = f.GetReferences(FamilyInstanceReferenceType.CenterFrontBack).FirstOrDefault(); if (r0 != null) rp.Append(r0); }
                        if (rp.Size > 1) doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, 0, 5000 * MM), new XYZ(x, 1, 5000 * MM)), rp, dimT);
                        ReferenceArray rlv = new ReferenceArray(); foreach (Level lv in levels) rlv.Append(lv.GetPlaneReference());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(x, -1500 * MM, 0), new XYZ(x, -1500 * MM, 1)), rlv, dimT);''')
rep('''                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, 300 * MM), new XYZ(1, y, 300 * MM)), rc, dimT);''',
'''                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, 300 * MM), new XYZ(1, y, 300 * MM)), rc, dimT);
                        ReferenceArray rco = new ReferenceArray(); rco.Append(rc.get_Item(0)); rco.Append(rc.get_Item(rc.Size - 1));
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(0, y, -900 * MM), new XYZ(1, y, -900 * MM)), rco, dimT);
                        ReferenceArray rlv = new ReferenceArray(); foreach (Level lv in levels) rlv.Append(lv.GetPlaneReference());
                        doc.Create.NewDimension(V[s[0]], Line.CreateBound(new XYZ(-1200 * MM, y, 0), new XYZ(-1200 * MM, y, 1)), rlv, dimT);''')
# node marks
rep('''            L("tags ok");''', '''            Tx(doc, "node marks", delegate { foreach (View nv in NV.Values) NodeMarks(doc, nv, t25); });
            L("tags ok");''')
rep('spec.Name = "Спецификация металлопроката";', 'spec.Name = "Ведомость элементов";')
rep('''            // sheets (numbers as in the DWG album)''', '''            // sheet list for «Общие данные»
            ViewSchedule sheetList = null;
            Tx(doc, "sheet list", delegate
            {
                sheetList = ViewSchedule.CreateSheetList(doc);
                sheetList.Name = "Ведомость рабочих чертежей основного комплекта";
                ScheduleDefinition sd = sheetList.Definition;
                Dictionary<string, SchedulableField> sf = new Dictionary<string, SchedulableField>();
                foreach (SchedulableField f in sd.GetSchedulableFields()) { string n = f.GetName(doc); if (!sf.ContainsKey(n)) sf[n] = f; }
                ScheduleField fn = sd.AddField(new SchedulableField(ScheduleFieldType.Instance, new ElementId(BuiltInParameter.SHEET_NUMBER)));
                ScheduleField fm = sd.AddField(new SchedulableField(ScheduleFieldType.Instance, new ElementId(BuiltInParameter.SHEET_NAME)));
                ScheduleField fo = sd.AddField(sf["КМ_Порядок_листа"]); fo.IsHidden = true;
                fn.ColumnHeading = "Лист"; fm.ColumnHeading = "Наименование";
                fn.GridColumnWidth = 15 * MM; fm.GridColumnWidth = 160 * MM;
                sd.AddSortGroupField(new ScheduleSortGroupField(fo.FieldId));
                try { sheetList.BodyTextTypeId = t25.Id; sheetList.HeaderTextTypeId = t25.Id; sheetList.TitleTextTypeId = t30.Id; } catch { }
            });
            // sheets (numbers as in the DWG album)''')
# sheet set
a = k.index('            object[][] sh = {')
b = k.index('            List<ViewSheet> sheets = new List<ViewSheet>();')
k = k[:a] + '''            string note2 = "1. Общие данные см. на листе 1, спецификацию металлопроката - на листе 2.\\r2. Ведомость элементов см. на листе 10.";
            object[][] sh = {
                new object[]{ "1", "Общие данные", "А2", new string[0], "" },
                new object[]{ "2", "Техническая спецификация металла", "А3К", new string[0], "" },
                new object[]{ "3", "Схема расположения закладных деталей", "А3", new[]{ "p3" }, note2 + "\\r3. Закладные детали Зд-1, Зд-2 - см. раздел КЖ. Стойки К1, К2 привариваются к закладным деталям, см. узлы 1, 2 на листе 11." },
                new object[]{ "4", "Схема расположения стоек и вертикальных связей", "А3", new[]{ "p4" }, note2 + "\\r3. Разрезы 3-3, 4-4 см. на листе 9." },
                new object[]{ "5", "Схема расположения ферм и связей по нижним поясам ферм", "А3", new[]{ "p5" }, note2 + "\\r3. Узлы 8, 9 см. на листе 12." },
                new object[]{ "6", "Схема расположения ферм и прогонов по верхним поясам ферм", "А3", new[]{ "p6" }, note2 + "\\r3. Прогоны П1 крепить к верхним поясам ферм, см. узел 4 на листе 11." },
                new object[]{ "7", "Разрез 1-1", "А3", new[]{ "1-1" }, note2 + "\\r3. Узлы 1-6 см. на листе 11, узлы 7, 14 - на листе 12." },
                new object[]{ "8", "Разрез 2-2", "А3", new[]{ "2-2" }, note2 + "\\r3. Узлы см. на листах 11, 12." },
                new object[]{ "9", "Разрезы 3-3, 4-4", "А2", new[]{ "3-3", "4-4" }, note2 + "\\r3. Узлы 10-13 см. на листе 12. Положение разрезов см. на листе 4." },
                new object[]{ "10", "Геометрическая схема фермы Ф1 (Ф2). Ведомости элементов", "А2", new[]{ "sФ1", "sФ2", "spec" }, "1. Общие данные см. на листе 1.\\r2. Длины элементов приняты по осям расчетной схемы." },
                new object[]{ "11", "Узлы 1...6", "А3", new[]{ "n1", "nа-а", "n2", "nб-б", "n3", "n4", "n5", "n6" }, "" },
                new object[]{ "12", "Узлы 7...14", "А3", new[]{ "n7", "n8", "n9", "n10", "n11", "n12", "n13", "n14" }, "1. Открытые торцы поясов ферм ВП1, НП1 и прогонов П1 закрыть заглушками -t4 (С245) сплошным сварным швом по контуру, см. узлы 7, 14." },
                new object[]{ "13", "Общий вид каркаса", "А3", new[]{ "3d" }, "" } };
''' + k[b:]
# sheet loop: formats, order parameter, special sheets, node packing
rep('''                    bool a2 = (string)s[2] == "А2";
                    double W = a2 ? 594 : 420, H = a2 ? 420 : 297;
                    ViewSheet vs = ViewSheet.Create(doc, a2 ? tb2.Id : tb3.Id);
                    vs.SheetNumber = (string)s[0]; vs.Name = (string)s[1];
                    sheets.Add(vs);''', '''                    string fmt = (string)s[2];
                    bool a2 = fmt == "А2", a3k = fmt == "А3К";
                    double W = a2 ? 594 : a3k ? 297 : 420, H = a2 ? 420 : a3k ? 420 : 297;
                    ViewSheet vs = ViewSheet.Create(doc, a2 ? tb2.Id : a3k ? tb3k.Id : tb3.Id);
                    vs.SheetNumber = (string)s[0]; vs.Name = (string)s[1];
                    SetParam(vs, "КМ_Порядок_листа", D((string)s[0]));
                    sheets.Add(vs);
                    if ((string)s[0] == "1") OdSheet(doc, vs, J["od"], t25, t35, tTitle, sheetList, Path.Combine(J["stampdir"], "sig_gip.png"));''')
rep('''                    if ((string)s[0] == "2") Txt(doc, vs.Id, sx + 175, sy + 20.9, "10", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);''',
    '''                    if ((string)s[0] == "1") Txt(doc, vs.Id, sx + 175, sy + 20.9, "13", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);''')
rep('''                    if (((string)s[4]).Length > 0) Txt(doc, vs.Id, 25, 33, (string)s[4], t30, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, Math.Min(W - 25 - 195, 200));''',
    '''                    if (((string)s[4]).Length > 0) Txt(doc, vs.Id, 25, 45, (string)s[4], t30, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, Math.Min(W - 25 - 195, 200));''')
rep('''                        if (vv[j] == "spec") { ScheduleSheetInstance.Create(doc, vs.Id, spec.Id, new XYZ((x0 + 10) * MM, (y1 - 10) * MM, 0)); continue; }
                        XYZ c = vv.Length == 1 ? new XYZ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0) : new XYZ((x0 + x1) / 2 * MM, (j == 0 ? y1 - (y1 - y0) / 4 : y0 + (y1 - y0) / 4) * MM, 0);
                        Viewport vp = Viewport.Create(doc, vs.Id, V[vv[j]].Id, c);
                        vp.ChangeTypeId(vpNoTitle.Id);
                        Parameter dn = vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER);
                        if (vv[j].Contains("-")) { try { dn.Set(vv[j].Substring(0, 1)); } catch { } }''',
'''                        if (vv[j] == "spec") { ScheduleSheetInstance.Create(doc, vs.Id, spec.Id, new XYZ((W - 10 - 185) * MM, (y1 - 10) * MM, 0)); continue; }
                        View vw = vv[j].StartsWith("n") ? (NV.ContainsKey(vv[j].Substring(1)) ? NV[vv[j].Substring(1)] : null) : V[vv[j]];
                        if (vw == null) continue;
                        XYZ c = vv.Length == 1 ? new XYZ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, 0)
                            : (string)s[0] == "10" ? new XYZ((x0 + 150) * MM, (j == 0 ? y1 - 80 : y1 - 250) * MM, 0)
                            : new XYZ((x0 + x1) / 2 * MM, (j == 0 ? y1 - (y1 - y0) / 4 : y0 + (y1 - y0) / 4) * MM, 0);
                        Viewport vp = Viewport.Create(doc, vs.Id, vw.Id, c);
                        vp.ChangeTypeId(vpNoTitle.Id);
                        Parameter dn = vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER);
                        try { dn.Set(vv[j].StartsWith("n") ? vv[j].Substring(1).Replace("-", "") : vv[j].Contains("-") ? vv[j].Substring(0, 1) : vv[j]); } catch { }''')
rep('''            // titles: underlined text centred above each drawing (as in the DWG)''', '''            Tx(doc, "special sheets", delegate
            {
                TechSpec(doc, sheets.First(s => s.SheetNumber == "2"), t25, t30);
                foreach (ViewSheet vs in sheets.Where(s => s.SheetNumber == "11" || s.SheetNumber == "12"))
                {
                    doc.Regenerate();
                    List<Viewport> vps = vs.GetAllViewports().Select(id => (Viewport)doc.GetElement(id)).ToList();
                    double x = 25, yTopRow = 287, rowH = 0;
                    foreach (Viewport vp in vps)
                    {
                        Outline ol = vp.GetBoxOutline();
                        double w = (ol.MaximumPoint.X - ol.MinimumPoint.X) / MM, h = (ol.MaximumPoint.Y - ol.MinimumPoint.Y) / MM;
                        if (x + w > 410) { x = 25; yTopRow -= rowH + 22; rowH = 0; }
                        vp.SetBoxCenter(new XYZ((x + w / 2) * MM, (yTopRow - 14 - h / 2) * MM, 0));
                        x += w + 14; rowH = Math.Max(rowH, h);
                    }
                }
            });
            // titles: underlined text centred above each drawing (as in the DWG)''')
# node titles: bubble «N / sheet of the parent view» as in the DWG; sections а-а, б-б underlined
rep('''                        string ttl = v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).AsString() ?? v.Name;
                        TextNote tn = Txt(doc, vs.Id, (ol.MinimumPoint.X + ol.MaximumPoint.X) / 2 / MM, ol.MaximumPoint.Y / MM + 4, ttl, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                        FormattedText ft = tn.GetFormattedText(); ft.SetUnderlineStatus(true); tn.SetFormattedText(ft);''',
'''                        string ttl = v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).AsString() ?? v.Name;
                        double cx = (ol.MinimumPoint.X + ol.MaximumPoint.X) / 2 / MM, ty = ol.MaximumPoint.Y / MM;
                        if (v.Name.StartsWith("Узел "))
                        {
                            string nn = v.Name.Substring(5);
                            Dictionary<string, string> par = new Dictionary<string, string> { { "8", "5" }, { "9", "5" }, { "10", "9" }, { "11", "9" }, { "12", "9" }, { "13", "9" } };
                            string ps = par.ContainsKey(nn) ? par[nn] : "7";
                            XYZ cc = new XYZ(cx * MM, (ty + 9) * MM, 0);
                            doc.Create.NewDetailCurve(vs, Arc.Create(cc, 6 * MM, 0, 2 * Math.PI, XYZ.BasisX, XYZ.BasisY));
                            doc.Create.NewDetailCurve(vs, Line.CreateBound(new XYZ((cx - 6) * MM, (ty + 9) * MM, 0), new XYZ((cx + 6) * MM, (ty + 9) * MM, 0)));
                            Txt(doc, vs.Id, cx, ty + 12, nn, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                            Txt(doc, vs.Id, cx, ty + 6, ps, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                            continue;
                        }
                        TextNote tn = Txt(doc, vs.Id, cx, ty + 4, ttl, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
                        FormattedText ft = tn.GetFormattedText(); ft.SetUnderlineStatus(true); tn.SetFormattedText(ft);''')
open('km2.cs', 'w', encoding='utf-8').write(k)
print('patched')
