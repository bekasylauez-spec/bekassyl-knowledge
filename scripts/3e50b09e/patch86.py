import io
p = r"D:/_claude_work/RMC/kzh/kz86_rb.cs"
s = io.open(p, encoding="utf-8-sig").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# 1) кроп тізбектерді қамтиды (тірек сызықтары кроптан тыс болса Revit размерді өшіреді)
rep("Sec(VN[0], new XYZ(mid, ri.c - 20, 0), XYZ.BasisZ, XYZ.BasisY, XYZ.BasisX, -h, h, -1530, -470, 200)",
    "Sec(VN[0], new XYZ(mid, ri.c - 20, 0), XYZ.BasisZ, XYZ.BasisY, XYZ.BasisX, -h, h, -2375, -300, 200)")
rep("Sec(VN[0], new XYZ(ri.c + 20, mid, 0), XYZ.BasisZ, -XYZ.BasisX, XYZ.BasisY, -h, h, -1530, -470, 200)",
    "Sec(VN[0], new XYZ(ri.c + 20, mid, 0), XYZ.BasisZ, -XYZ.BasisX, XYZ.BasisY, -h, h, -2375, -300, 200)")
rep("Sec(VN[1], new XYZ(ri.s1, ri.c, 0), XYZ.BasisZ, -XYZ.BasisX, XYZ.BasisY, -170, 170, -1420, -580, 120)",
    "Sec(VN[1], new XYZ(ri.s1, ri.c, 0), XYZ.BasisZ, -XYZ.BasisX, XYZ.BasisY, -520, 170, -2150, -580, 120)")
rep("Sec(VN[1], new XYZ(ri.c, ri.s1, 0), XYZ.BasisZ, -XYZ.BasisY, -XYZ.BasisX, -170, 170, -1420, -580, 120)",
    "Sec(VN[1], new XYZ(ri.c, ri.s1, 0), XYZ.BasisZ, -XYZ.BasisY, -XYZ.BasisX, -520, 170, -2150, -580, 120)")
rep("double lo0 = iv == 0 ? 4 : 18, ro0 = iv == 0 ? 4 : 28, to0 = iv == 0 ? 12 : 18, bo0 = iv == 0 ? 46 : 40;",
    "double lo0 = iv == 0 ? 4 : 2, ro0 = iv == 0 ? 4 : 28, to0 = iv == 0 ? 6 : 18, bo0 = iv == 0 ? 14 : 12;")
# 2) разрез белгілерінің санатын жасырмаймыз (өз 1-1 белгіміз көрінсін); бөтен/өз көрініс белгілері B-да жеке жасырылады
rep("foreach (var hc in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_Viewers, BuiltInCategory.OST_Sections, BuiltInCategory.OST_Views, BuiltInCategory.OST_SectionBox })",
    "foreach (var hc in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_SectionBox })")
rep("    Func<double, double> Sc = mmPaper => mmPaper * 25;\n    // тізбек: көрінбейтін",
    "    Func<double, double> Sc = mmPaper => mmPaper * 25;\n"
    "    // көріністердің өз белгілері (фасадтағы 1-1 көрінісі, 1-1-дегі фасад) және бөтен белгілер жасырылады; 1-1 сілтеме-разрезбен көрсетіледі (kz30/kz31)\n"
    "    foreach (var vw0 in views) { var hv = new FilteredElementCollector(d, vw0.Id).OfCategory(BuiltInCategory.OST_Viewers).WhereElementIsNotElementType().ToElements().Where(x => x.CanBeHidden(vw0)).Select(x => x.Id).ToList(); foreach (var id in hv) try { vw0.HideElements(new List<ElementId> { id }); } catch { } }\n"
    "    // тізбек: көрінбейтін")
# 3) фасадта көрінетін жақтағы шеткі стерженьнің позициясы; ерте иілген ортаңғы стерженьді геометриядан анықтау
rep("    string zt = \"ш.\" + string.Join(\";\", ri.zones.Select(z => z[2]).Distinct());",
    "    string zt = \"ш.\" + string.Join(\";\", ri.zones.Select(z => z[2]).Distinct());\n"
    "    int vis = ri.hx ? 1 : -1;   // фасадта көрінетін жақ: X — +Y, Y — −X\n"
    "    Func<Autodesk.Revit.DB.Structure.Rebar, double> Cross = r0 => { var l0 = Leg(r0); var pm = l0.GetEndPoint(0) / MM; return ri.hx ? pm.Y : pm.X; };\n"
    "    Func<Autodesk.Revit.DB.Structure.Rebar, string, double> Dm = (r0, nm0) => { var pq = r0.LookupParameter(nm0); return pq != null && pq.HasValue ? pq.AsDouble() / MM : 0; };\n"
    "    foreach (var kind in new[] { \"rb:top\", \"rb:bot\" }) { var bars = K(kind); if (bars.Count < 3) continue; var cen = bars.OrderBy(r0 => Math.Abs(Cross(r0) - ri.c)).First(); var oth = bars.Where(r0 => r0.Id != cen.Id).ToList();\n"
    "      if (Math.Max(Dm(cen, \"BI_A\"), Dm(cen, \"BI_C\")) > oth.Max(r0 => Math.Max(Dm(r0, \"BI_A\"), Dm(r0, \"BI_C\"))) + 100) notesOdd.Add(Pos(cen)); }")
rep('if (topG.Count > 0) { string p = topG[0].Key; double cu = ri.a + L * 0.25, hw = HW(p, null); Lbl(v, p, null, cu, wT, new[] { new[] { cu + hw + 80, zTop } }); }',
    'if (topG.Count > 0) { string p = Pos(K("rb:top").OrderByDescending(r0 => vis * (Cross(r0) - ri.c)).First()); double cu = ri.a + L * 0.25, hw = HW(p, null); Lbl(v, p, null, cu, wT, new[] { new[] { cu + hw + 80, zTop } }); }')
rep('if (botG.Count > 0) { string p = botG[0].Key; double cu = ri.a + L * 0.16, hw = HW(p, null); Lbl(v, p, null, cu, wB, new[] { new[] { cu + hw + 80, zBot } }); }',
    'if (botG.Count > 0) { string p = Pos(K("rb:bot").OrderByDescending(r0 => vis * (Cross(r0) - ri.c)).First()); double cu = ri.a + L * 0.16, hw = HW(p, null); Lbl(v, p, null, cu, wB, new[] { new[] { cu + hw + 80, zBot } }); }')
rep("    // ерте иілген ортаңғы стерженьдер — примечаниеге\n    foreach (var gg in topG.Skip(1).Concat(botG.Skip(1))) notesOdd.Add(gg.Key);\n", "")
# 4) 1-1: әр позицияға бір выноска (КЖ-3.2 стилі) — топтың ең оң жақтағы стерженіне; полкалар веер болып, выноскалар қиылыспайды
i0 = s.index("      int gi = 0;\n      foreach (var gg in topG)")
i1 = s.index("      if (hoops.Count > 0)\n      { var h0")
s = s[:i0] + ("      int gi = 0;\n"
              "      foreach (var rp in topG.Select(gg => gg.OrderByDescending(r0 => UW(r0)[0]).First()).OrderByDescending(r0 => UW(r0)[0])) { string ps0 = Pos(rp); double hw = HW(ps0, null); var q = UW(rp); Lbl(v, ps0, null, uS + hw, -600 + Sc(8) + gi * Sc(5), new[] { new[] { q[0] + 6, q[1] + 9 } }); gi++; }\n"
              "      gi = 0;\n"
              "      foreach (var rp in botG.Select(gg => gg.OrderByDescending(r0 => UW(r0)[0]).First()).OrderByDescending(r0 => UW(r0)[0])) { string ps0 = Pos(rp); double hw = HW(ps0, null); var q = UW(rp); Lbl(v, ps0, null, uS + hw, -1400 - Sc(6) - gi * Sc(5), new[] { new[] { q[0] + 6, q[1] - 9 } }); gi++; }\n") + s[i1:]
# 5) атау: аннотация кропы өшкен соң қорап үлкейеді → атау орны алдын ала есептеліп, кейін қайта қойылады
i0 = s.index("    foreach (var vw in views) { var vp = VP(vw); var ob = vp.GetBoxOutline(); double cx")
i1 = s.index("    log.Add(\"layout commit \" + t.Commit());")
s = s[:i0] + ("    var titleT = new Dictionary<long, XYZ>();\n"
              "    foreach (var vw in views) { var vp = VP(vw); var ob = vp.GetBoxOutline(); titleT[vp.Id.Value] = new XYZ((ob.MinimumPoint.X + ob.MaximumPoint.X) / 2, ob.MaximumPoint.Y + 1 * MM, 0); }\n"
              "    // фасадта БК_обрыв бар → аннотация кропы соңында өшіріледі (kz85: қосулы кезде белгі көрінбейді)\n"
              "    try { views[0].get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(0); } catch { }\n"
              "    d.Regenerate();\n"
              "    foreach (var vw in views) { var vp = VP(vw); var tg = titleT[vp.Id.Value]; var ob = vp.GetBoxOutline();\n"
              "        vp.LabelOffset = new XYZ(tg.X - ob.MinimumPoint.X - 30 * MM, tg.Y - ob.MinimumPoint.Y, 0); d.Regenerate();\n"
              "        var lo = vp.GetLabelOutline(); vp.LabelOffset = vp.LabelOffset + new XYZ(tg.X - (lo.MinimumPoint.X + lo.MaximumPoint.X) / 2, tg.Y - lo.MinimumPoint.Y, 0); d.Regenerate();\n"
              "        var lo2 = vp.GetLabelOutline(); log.Add(vw.Name + \" title \" + Math.Round(lo2.MinimumPoint.X / MM, 1) + \"; \" + Math.Round(lo2.MinimumPoint.Y / MM, 1) + \" .. \" + Math.Round(lo2.MaximumPoint.X / MM, 1) + \"; \" + Math.Round(lo2.MaximumPoint.Y / MM, 1)); }\n") + s[i1:]
# 6) КЖ_* параметрлері «Каркас несущий» санатына да байланады (рандбалка бетоны «Материалы» кестесіне түссін)
rep("double coverTop = 0;\nusing (var t = new Transaction(d, SHEET + \": кесте деректері\"))",
    "double coverTop = 0;\n"
    "using (var t = new Transaction(d, \"КЖ_* → Каркас несущий\"))\n"
    "{ t.Start(); var fr = Category.GetCategory(d, BuiltInCategory.OST_StructuralFraming); var map = d.ParameterBindings; var it = map.ForwardIterator(); var fix = new List<Tuple<Definition, ElementBinding>>();\n"
    "  while (it.MoveNext()) { var df = it.Key; var bnd = it.Current as ElementBinding; if (df == null || bnd == null || !(bnd is InstanceBinding)) continue; if (!df.Name.StartsWith(\"КЖ_\") || df.Name.StartsWith(\"КЖ_сх_\")) continue; if (!bnd.Categories.Contains(fr)) fix.Add(Tuple.Create(df, bnd)); }\n"
    "  foreach (var pr in fix) { var ncs = new CategorySet(); foreach (Category cq in pr.Item2.Categories) ncs.Insert(cq); ncs.Insert(fr); bool ok = map.ReInsert(pr.Item1, new InstanceBinding(ncs)); log.Add(\"bind \" + pr.Item1.Name + \" +Каркас: \" + ok); }\n"
    "  log.Add(\"bind commit \" + t.Commit()); }\n"
    "using (var t = new Transaction(d, SHEET + \": кесте деректері\"))")
io.open(p, "w", encoding="utf-8-sig").write(s)
print("ok")
