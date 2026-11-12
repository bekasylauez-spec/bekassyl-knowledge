// B109 КМ audit (adapted from 3602 q20_audit.cs). READ-ONLY. Run WITHOUT -Lib. Output: _audit.txt in this folder.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\audit2.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => {  string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В113-КМ.rvt")); r = Audit(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

class Mb { public FamilyInstance f; public XYZ a, b, u; public double len, e0, e1, th; public string mk, blk, fam; public bool col; public ElementId mat; }
class Pc { public Element El; public string Name; public bool Bolt, Plate, Node; public Solid S; public XYZ Mn, Mx; }

static string Audit(Document nd)
{
    const double M = 304.8; var sb = new System.Text.StringBuilder();
    var R = new Dictionary<string, List<string>>(); foreach (var c in new[] { "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14", "C15" }) R[c] = new List<string>();
    var note = new Dictionary<string, string>();
    Func<XYZ, string> P3 = p => Math.Round(p.X * M) + "," + Math.Round(p.Y * M) + "," + Math.Round(p.Z * M);
    var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    var fr = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")
        && (x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || x.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).ToList();
    var A = new List<Mb>();
    foreach (var f in fr)
    {
        var t = nd.GetElement(f.GetTypeId()); var mb = new Mb { f = f, fam = f.Symbol.Family.Name, blk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "" };
        mb.mk = mb.blk.Split(' ')[0];
        double b = t.LookupParameter("b")?.AsDouble() ?? t.LookupParameter("B")?.AsDouble() ?? 0, h = t.LookupParameter("h")?.AsDouble() ?? t.LookupParameter("H")?.AsDouble() ?? 0;
        mb.th = Math.Max(b, h) / 2; if (mb.th < 30 / M) mb.th = 150 / M;
        if (f.Location is LocationCurve lc) { var c = lc.Curve; mb.a = c.GetEndPoint(0); mb.b = c.GetEndPoint(1); mb.e0 = f.get_Parameter(BuiltInParameter.START_EXTENSION)?.AsDouble() ?? 0; mb.e1 = f.get_Parameter(BuiltInParameter.END_EXTENSION)?.AsDouble() ?? 0; }
        else { var bb = f.get_BoundingBox(null); var lp = ((LocationPoint)f.Location).Point; mb.a = new XYZ(lp.X, lp.Y, bb.Min.Z); mb.b = new XYZ(lp.X, lp.Y, bb.Max.Z); mb.col = true; }
        mb.len = mb.a.DistanceTo(mb.b); mb.u = (mb.b - mb.a).Normalize(); mb.mat = f.StructuralMaterialId; A.Add(mb);
    }
    double tol = 3 / M;
    Func<Mb, XYZ, double> dseg = (o, p) => { double s = Math.Max(0, Math.Min(o.len, (p - o.a).DotProduct(o.u))); return (p - o.a - o.u * s).GetLength(); };
    Func<Mb, Mb, bool> par = (x, y) => x.u.CrossProduct(y.u).GetLength() < 1e-3;
    var DSs = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var nodeDS = DSs.Where(x => x.ApplicationDataId != "база").ToList();
    var baseDS = DSs.Where(x => x.ApplicationDataId == "база").ToList();
    // C13 (ереже 41, 09.11): every ФФ1 top chord / БП1 / БП2 end at a column has its node group named with the joint type —
    //   ФФ1 ВП → «шарнир», БП1 / БП2 → «жёсткий». C14: every column stands on its grid intersection (grid A was once dragged with 28 columns).
    {
        var cC13 = A.Where(m => m.col).ToList(); var dsC13 = nodeDS.Select(d => d.Name ?? "").ToList();
        foreach (var m in A.Where(m => !m.col && (m.blk.StartsWith("ФФ1 ВП") || m.mk == "БП1" || m.mk == "БП2")))
            foreach (var p in new[] { m.a, m.b })
            {
                var c = cC13.FirstOrDefault(k => Math.Abs(k.a.X - p.X) < 30 / M && Math.Abs(k.a.Y - p.Y) < 330 / M && (k.mk == "К1" || k.mk == "К2"));
                if (c == null) continue;
                string want = m.blk.StartsWith("ФФ1") ? "шарнир" : "жёсткий";
                string key = "к колонне " + ((long)Math.Round(c.a.X * M)).ToString() + " ";
                if (!dsC13.Any(n => n.Contains(key) && n.Contains(want))) R["C13"].Add(m.f.Id.Value + " " + m.blk + " у колонны " + P3(c.a) + ": нет узла «" + want + "»");
            }
        var gC13 = new FilteredElementCollector(nd).OfClass(typeof(Grid)).Cast<Grid>().Select(g => g.Curve).OfType<Line>().ToList();
        var gxC = gC13.Where(l => Math.Abs(l.Direction.Y) > 0.99).Select(l => l.GetEndPoint(0).X).ToList();
        var gyC = gC13.Where(l => Math.Abs(l.Direction.X) > 0.99).Select(l => l.GetEndPoint(0).Y).ToList();
        foreach (var c in cC13.Where(k => k.mk == "К1" || k.mk == "К2"))
            if (!gxC.Any(x => Math.Abs(x - c.a.X) < 1 / M) || !gyC.Any(y => Math.Abs(y - c.a.Y) < 1 / M)) R["C14"].Add(c.f.Id.Value + " " + c.blk + " не на пересечении осей @" + P3(c.a));
        foreach (var l in gC13) { var d = l.Direction; if (Math.Abs(d.X) > 0.99 && Math.Abs(l.GetEndPoint(0).X * M + 4000) > 1) R["C14"].Add("ось смещена вдоль: " + P3(l.GetEndPoint(0))); }
    }
    string c15info = ""; string rib51 = "";
    // C15 — В113 nodes, one script per node (12.11.2026, keys renumbered): tube ends = analog Алатау typical detail — every Р1 / СВ1 / ГС1 end has a cap −4
    // and an insert −8 (b+20)×220 through the slots (crossing ends 7г: insert b+40, no bolts); СВ1 in every braced panel = ЛИРА Λ / V; every Р1 end has a gusset (узел 3);
    // purlin stand plates (узел 8), ПБ1 hangers / web splices / stops (узел 9); every Б1/Б2 end at a К1 — узел 1 жёсткий; Б1 ridge ribs (узел 2).
    {
        Func<string, List<Solid>> SolidsOf = key => nodeDS.Where(d => d.ApplicationDataId == key && d.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections)
            .SelectMany(d => d.get_Geometry(new Options()).OfType<Solid>().Where(q => q.Volume > 1e-9)).ToList();
        double mm3 = M * M * M;
        var tubeKeys = new[] { "узел 3", "узел 4", "узел 5", "узел 6", "узел 7" };
        var tubeS = tubeKeys.SelectMany(k => SolidsOf(k)).Select(s => s.Volume * mm3).ToList();
        int caps4 = tubeS.Count(v => v > 40000 && v < 70000);                 // −4 × 120 × 120 (− slot) / −4 × 140 × 120
        int ins8 = tubeS.Count(v => v > 150000 && v < 215000);                // −8 × 120 × 220 (− holes, slots)
        int insX = tubeS.Count(v => v > 70000 && v < 150000);                 // crossing inserts −8 × 140 × ≈110
        int tubeEnds = A.Count(m => m.mk == "СВ1" || m.mk == "Р1" || m.mk == "ГС1") * 2;
        if (caps4 < tubeEnds) R["C15"].Add("заглушек −4 " + caps4 + " < торцов труб " + tubeEnds);
        if (ins8 + insX < tubeEnds) R["C15"].Add("вставок −8 " + (ins8 + insX) + " < торцов труб " + tubeEnds);
        foreach (var grp in A.Where(m => m.mk == "СВ1").GroupBy(m => Math.Floor(Math.Min(m.a.X, m.b.X) * M / 6000.0) + " " + Math.Round(m.a.Y * M)))
        {
            int mid = grp.Count(m => new[] { m.a, m.b }.Any(p => Math.Abs((p.X * M) % 6000 - 3000) < 600));
            if ((grp.Count() != 4 && grp.Count() != 2) || mid != grp.Count()) R["C15"].Add("СВ1 панель " + grp.Key + ": " + grp.Count() + " шт, к середине Р1 " + mid + " (Λ / V 4 + 4, портал над воротами — только V 2 + 2)");
        }
        int g3 = SolidsOf("узел 3").Count(s => s.Volume * mm3 > 70000 && s.Volume * mm3 < 140000 || s.Volume * mm3 >= 215000); int r1Ends = A.Count(m => m.mk == "Р1") * 2;
        if (SolidsOf("узел 3").Count < r1Ends * 3) R["C15"].Add("Р1: тел узла 3 " + SolidsOf("узел 3").Count + " < 3 × торцов " + r1Ends + " (фасонка + вставка + заглушка)");
        int st8 = SolidsOf("узел 8").Count; if (st8 < 50) R["C15"].Add("опорных листов прогонов " + st8 + " (нужно 50: 5 рядов × 10 осей)");
        int n9 = SolidsOf("узел 9").Count; if (n9 < 18 + 28 + 4) R["C15"].Add("подвески ПБ1: тел " + n9 + " (18 подвесок — прокладки/пластины, 28 накладок стенки, 4 упора)");
        int n2 = SolidsOf("узел 2").Count; if (n2 < 8 * 4) R["C15"].Add("узел 2 (конёк Б1): тел " + n2 + " (нужно 32: 2 ребра + 2 половины накладки × 8)");
        // ереже 56 (11.11): колонна–балка Б1/Б2 — жёсткий узел по аналогу (оголовок, столик, накладки), не шарнир
        if (!nodeDS.Any(dd => (dd.Name ?? "").StartsWith("Узел 1 (жёсткий)"))) R["C15"].Add("узел 1 колонна–балка не «жёсткий» (аналог Алатау узел 1, ереже 56)");
        int n1 = SolidsOf("узел 1").Count; if (n1 < 20 + 20) R["C15"].Add("узел 1: оголовков + торцевых пластин " + n1 + " (нужно 40)");
        c15info = "заглушек −4 " + caps4 + ", вставок " + ins8 + " + " + insX + " (пересечения), торцов труб " + tubeEnds + ", узел 3 тел " + SolidsOf("узел 3").Count + ", опорных листов прогонов " + st8 + ", узел 9 тел " + n9 + ", узел 2 тел " + n2;
    }
    var nodeBB = nodeDS.Concat(baseDS).Where(x => x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionWelds && x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionBolts)
        .SelectMany(x => x.get_Geometry(new Options()).OfType<Solid>().Where(q => q.Volume > 1e-9)).Select(q => { var bb = q.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            return new[] { Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z), Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z) }; }).ToList();
    Func<XYZ, bool> NearNode = p => { double tl = 25 / M; return nodeBB.Any(q => p.X > q[0] - tl && p.X < q[3] + tl && p.Y > q[1] - tl && p.Y < q[4] + tl && p.Z > q[2] - tl && p.Z < q[5] + tl); };
    var uncapped = new List<string>();
    var levelsZ = new FilteredElementCollector(nd).OfClass(typeof(Level)).Cast<Level>().Select(L => L.Elevation).ToList();

    var freeBy = new Dictionary<string, int>(); int ends = 0, joints = 0, freeEnds = 0, tubeFree = 0, extNonZero = 0; var freeEx = new List<string>(); var jointEx = new List<string>(); var seam = new List<string>(); var splice = new List<string>();
    for (int i = 0; i < A.Count; i++)
    {
        var m = A[i]; if (Math.Abs(m.e0) > 1e-6 || Math.Abs(m.e1) > 1e-6) extNonZero++;
        for (int e = 0; e < 2; e++)
        {
            var P = e == 0 ? m.a : m.b; ends++;
            bool cont = false, touch = false; Mb contM = null;
            for (int j = 0; j < A.Count; j++) { if (j == i) continue; var o = A[j];
                if (par(o, m)) { if ((o.a.DistanceTo(P) < tol || o.b.DistanceTo(P) < tol)) { cont = true; contM = o; } continue; }
                if (dseg(o, P) < o.th + tol) touch = true; }
            string id = m.f.Id.Value + " " + m.blk + (e == 0 ? " нач" : " кон") + " @" + P3(P);
            if (touch || cont) { joints++; if (jointEx.Count < 6) jointEx.Add(id); }
            else { freeEnds++; bool tube = m.fam.Contains("труба"); if (tube && !NearNode(P)) uncapped.Add(m.f.Id.Value + " " + m.blk + " @" + P3(P)); if (tube) { tubeFree++; freeBy[m.mk] = freeBy.ContainsKey(m.mk) ? freeBy[m.mk] + 1 : 1; } if (tube && freeEx.Count < 12) freeEx.Add(id); }
            if (cont && contM.f.Id.Value > m.f.Id.Value && contM.mk == m.mk)
            {
                bool unj = !JoinGeometryUtils.AreElementsJoined(nd, m.f, contM.f); string seamS = (m.f.Id.Value + "|" + contM.f.Id.Value + " " + m.blk + " @" + P3(P));
                bool hi = false; for (int j = 0; j < A.Count && !hi; j++) { var x = A[j]; if (x == m || x == contM || par(x, m)) continue; if (dseg(x, P) < (x.col ? x.th + 500 / M : x.th + Math.Max(m.th, 140 / M) + 30 / M)) hi = true; }  // channel [27П: th from b only (48) -> half-height 135 used  // support radius = half-section of support + half-section of member (purlin on chord, beam on bracket КН)
                bool lvl = Math.Abs(m.u.Z) > 0.99 && levelsZ.Any(z => Math.Abs(P.Z - z) < 600 / M);
                if (!hi && unj) seam.Add(seamS); if (!hi && !lvl) splice.Add(m.f.Id.Value + "|" + contM.f.Id.Value + " " + m.blk + " лишний стык @" + P3(P));
            }
        }
    }
    foreach (var s in seam) R["C7"].Add(s); foreach (var s in splice) R["C10"].Add(s);
    // B109: a cap DS holds every cap of its node (two halves around the insert slot per tube end) → count halves / 2
    int caps = nodeDS.Where(x => (x.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)?.AsString() ?? "") == "ПЛ3" || x.Name.IndexOf("заглушка", StringComparison.OrdinalIgnoreCase) >= 0)
        .Sum(x => x.get_Geometry(new Options()).OfType<Solid>().Count(so => so.Volume > 1e-9) / 2);
    foreach (var s in uncapped.Take(30)) R["C4"].Add("открытый торец без пластины узла: " + s);   // 09.11: per end (a free tube end needs a node plate within 25 mm)
    if (false) R["C4"].Add("открытых торцов труб " + tubeFree + ", заглушек " + caps + " (ожидаемо: узлы не построены); первые: " + string.Join(" ; ", freeEx.Take(6)));
    int weldsNode = nodeDS.Count(x => x.Name.StartsWith("шов") || (x.Category != null && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionWelds));
    if (joints > 0 && weldsNode == 0) R["C5"].Add("примыканий концов " + joints + ", швов узлов 0 (ожидаемо: узлы не построены); напр. " + string.Join(" ; ", jointEx.Take(4)));
    note["C6"] = "торцы не обрезаны (удлинений≠0: " + extNonZero + "), узлов нет";
    note["C2"] = "ранг труб К1>Ст1>… в этой модели не введён"; note["C3"] = "то же"; note["C12"] = "нет поясов Б1/стоек трубной схемы";
    int kr = A.Count(x => x.mk == "Кр1" || x.mk == "Кр2"); note["C8"] = kr == 0 ? "кронштейнов Кр1/Кр2 в модели нет" : "";

    var matColors = new Dictionary<string, string>(); var matDup = new List<string>();
    foreach (var m in A)
    {
        var mat = nd.GetElement(m.mat) as Material;
        if (mat == null || !mat.Name.StartsWith("КМ_" + m.mk + " (")) R["C9"].Add(m.f.Id.Value + " " + m.blk + " материал «" + (mat == null ? "—" : mat.Name) + "» @" + P3(m.a));
        else if (mat.Shininess != 0 || mat.Smoothness != 0) R["C9"].Add(m.f.Id.Value + " " + m.blk + " глянец: " + mat.Name);
        else { string k = mat.Color.Red + "," + mat.Color.Green + "," + mat.Color.Blue; matColors[m.mk] = k; }
    }
    foreach (var g in matColors.GroupBy(x => x.Value).Where(g => g.Count() > 1)) matDup.Add(string.Join("=", g.Select(x => x.Key)) + " цвет " + g.Key);
    int gfail = 0;
    foreach (var m in A)
    {
        bool bad = false;
        foreach (var go in m.f.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
            foreach (var o in objs) { var s = o as Solid; if (s == null || s.Volume <= 1e-9) continue; foreach (Face fc in s.Faces) if (fc.MaterialElementId != m.mat) { bad = true; break; } if (bad) break; } if (bad) break; }
        if (bad) { gfail++; if (gfail <= 8) R["C9"].Add(m.f.Id.Value + " " + m.blk + " грань с другим материалом (не материал марки) @" + P3(m.a)); }
    }
    if (gfail > 8) R["C9"].Add("... всего элементов с чужой гранью: " + gfail);
    if (matDup.Count > 0) R["C9"].Add("одинаковый цвет у разных марок: " + string.Join("; ", matDup));

    var els = fr.Cast<Element>().Concat(DSs.Cast<Element>()).ToList(); var pcs = new List<Pc>();
    foreach (var el in els)
    {
        bool bolt = el.Category != null && el.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts; bool weld = el.Category != null && el.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionWelds;
        bool node = el is DirectShape; string nm = el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? el.Name;
        foreach (var go in el.get_Geometry(opt)) { IEnumerable<GeometryObject> objs = go is GeometryInstance gi ? gi.GetInstanceGeometry().Cast<GeometryObject>() : new[] { go };
            foreach (var s in objs.OfType<Solid>().Where(x => x.Volume > 1e-9)) { var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
                pcs.Add(new Pc { El = el, Name = nm, Bolt = bolt, Plate = node && !bolt && !weld, Node = node, S = s, Mn = new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z)), Mx = new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z)) }); } }
    }
    pcs = pcs.OrderBy(p => p.Mn.X).ToList(); int bolted = 0, pairs = 0;
    for (int i = 0; i < pcs.Count; i++)
        for (int j = i + 1; j < pcs.Count && pcs[j].Mn.X <= pcs[i].Mx.X; j++)
        {
            var a = pcs[i]; var b = pcs[j]; if (a.El.Id == b.El.Id) continue;
            if (a.Mx.Y < b.Mn.Y || b.Mx.Y < a.Mn.Y || a.Mx.Z < b.Mn.Z || b.Mx.Z < a.Mn.Z) continue; pairs++;
            double v = 0; try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(a.S, b.S, BooleanOperationsType.Intersect); if (x != null) v = x.Volume; } catch { }
            double mm3 = v * M * M * M; if (mm3 < 1) continue; if (a.Bolt || b.Bolt) { bolted++; continue; }
            var c = (a.Mn + a.Mx) / 2; string s2 = a.El.Id.Value + "×" + b.El.Id.Value + " " + a.Name + " ∩ " + b.Name + " " + Math.Round(mm3) + " мм³ @" + P3(c);
            if (a.Plate && b.Plate) R["C11"].Add(s2); else R["C1"].Add(s2);
        }

    var X = new List<string>();
    var cols = A.Where(x => x.col).ToList(); int noBase = 0; var nbEx = new List<string>();
    var bpts = baseDS.Where(d => d.Name.StartsWith("База")).Select(d => d.get_BoundingBox(null)).Where(b => b != null).ToList();
    foreach (var c in cols) { bool ok = bpts.Any(b => c.a.X >= b.Min.X - 0.01 && c.a.X <= b.Max.X + 0.01 && c.a.Y >= b.Min.Y - 0.01 && c.a.Y <= b.Max.Y + 0.01 && c.a.Z >= b.Min.Z - 60 / M && c.a.Z <= b.Max.Z + 60 / M);
        if (!ok) { noBase++; if (nbEx.Count < 6) nbEx.Add(c.f.Id.Value + " " + c.blk + " @" + P3(c.a)); } }
    X.Add("X1 базы под колоннами: колонн " + cols.Count + ", DS баз " + baseDS.Count + ", колонн без базы " + noBase + (noBase > 0 ? " напр. " + string.Join("; ", nbEx) : ""));
    X.Add("X2 низ колонн по Z: " + string.Join(", ", cols.GroupBy(c => Math.Round(c.a.Z * M)).Select(g => g.Key + " мм x" + g.Count())));
    X.Add("X3 ж/б в модели: стены " + new FilteredElementCollector(nd).OfClass(typeof(Wall)).GetElementCount() + ", плиты " + new FilteredElementCollector(nd).OfClass(typeof(Floor)).GetElementCount() + ", фундаменты " + new FilteredElementCollector(nd).OfCategory(BuiltInCategory.OST_StructuralFoundation).WhereElementIsNotElementType().GetElementCount());
    foreach (var bc in new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds })
    { try { var ct = nd.Settings.Categories.get_Item(bc); var lc = ct.LineColor; X.Add("X4 стиль " + ct.Name + ": вес " + ct.GetLineWeight(GraphicsStyleType.Projection) + ", цвет " + lc.Red + "," + lc.Green + "," + lc.Blue); } catch { } }
    var v3 = new FilteredElementCollector(nd).OfClass(typeof(View3D)).Cast<View3D>().Where(v => !v.IsTemplate).ToList();
    X.Add("X5 3D-виды: " + string.Join("; ", v3.Select(v => v.Name + " [" + v.DisplayStyle + ", фильтров " + v.GetFilters().Count + "]")));
    var bad2 = new[] { "BI_", "KNP_", "RAS_", "Иванов" }; var traces = new List<string>();
    foreach (var f in new FilteredElementCollector(nd).OfClass(typeof(Family)).Cast<Family>()) foreach (var b in bad2) if (f.Name.Contains(b)) traces.Add("семейство " + f.Name);
    var it = nd.ParameterBindings.ForwardIterator(); while (it.MoveNext()) { string pn = ((Definition)it.Key).Name; foreach (var b in bad2) if (pn.Contains(b)) traces.Add("параметр " + pn); }
    foreach (var v in new FilteredElementCollector(nd).OfClass(typeof(View)).Cast<View>()) foreach (var b in bad2) if (v.Name != null && v.Name.Contains(b)) traces.Add("вид " + v.Name);
    foreach (var v in new FilteredElementCollector(nd).OfClass(typeof(ElementType)).Cast<ElementType>()) foreach (var b in bad2) if (v.Name != null && v.Name.Contains(b)) traces.Add("тип " + v.Name);
    foreach (var mt in new FilteredElementCollector(nd).OfClass(typeof(Material)).Cast<Material>()) foreach (var b in bad2) if (mt.Name.Contains(b)) traces.Add("материал " + mt.Name);
    X.Add("X6 следы чужого шаблона: " + (traces.Count == 0 ? "нет" : traces.Distinct().Count() + " напр. " + string.Join("; ", traces.Distinct().Take(8))));
    X.Add("X7 марки: " + string.Join(", ", A.GroupBy(x => x.blk).OrderBy(g => g.Key).Select(g => g.Key + " " + g.Count())));
    int dup = 0; var dupEx = new List<string>();
    for (int i = 0; i < A.Count; i++) for (int j = i + 1; j < A.Count; j++) { if ((A[i].a.DistanceTo(A[j].a) < tol && A[i].b.DistanceTo(A[j].b) < tol) || (A[i].a.DistanceTo(A[j].b) < tol && A[i].b.DistanceTo(A[j].a) < tol)) { dup++; if (dupEx.Count < 5) dupEx.Add(A[i].f.Id.Value + "=" + A[j].f.Id.Value + " " + A[i].blk); } }
    X.Add("X8 дубликаты осей: " + dup + (dup > 0 ? " напр. " + string.Join("; ", dupEx) : ""));
    X.Add("X9 торцы: всего " + ends + ", примыкают " + joints + ", свободных " + freeEnds + " (труб: " + tubeFree + "; по маркам: " + string.Join(", ", freeBy.Select(kv => kv.Key + " " + kv.Value)) + ")");
    X.Add("X10 узловые DS (не база): " + nodeDS.Count + ", швов узлов " + weldsNode);

    foreach (var cc in new[] { "C7", "C10" }) X.Add(cc + " по маркам: " + string.Join(", ", R[cc].GroupBy(s => s.Split(' ')[1]).Select(g => g.Key + " " + g.Count())));
    X.Add("X12 полусечение th по маркам, мм: " + string.Join(", ", A.GroupBy(x => x.mk).Select(g => g.Key + " " + Math.Round(g.First().th * M))));
    X.Add("X13 C4: открытых торцов труб " + tubeFree + ", из них свободные пояса НП ФФ1 " + (freeBy.ContainsKey("ФФ1") ? freeBy["ФФ1"] : 0) + ", заглушек (полу-тел/2) " + caps + "; узловых DS с «заглушка» в имени: " + nodeDS.Count(x => x.Name.IndexOf("заглушка", StringComparison.OrdinalIgnoreCase) >= 0));
    var voidI = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.Contains("срез")).ToList();
    int cutsTotal = 0, latWithCut = 0, latTot = 0, latNoCut = 0; var lat = new List<string>();
    foreach (var m in A) { int cc = 0; try { cc = InstanceVoidCutUtils.GetCuttingVoidInstances(m.f).Count; } catch { } cutsTotal += cc; if (m.blk == "ФФ1 Р1" || m.blk == "ФФ1 Р2") { latTot++; if (cc >= 2) latWithCut++; else { latNoCut++; if (lat.Count < 5) lat.Add(m.f.Id.Value + " cuts " + cc + " @" + P3(m.a)); } } }
    X.Add("X14 C6 БК_срез: войд-экземпляров " + voidI.Count + ", вырезов у элементов " + cutsTotal + "; решётка ФФ1 " + latTot + ", с 2 вырезами " + latWithCut + ", без " + latNoCut + (lat.Count > 0 ? " напр. " + string.Join("; ", lat) : ""));
    X.Add("X11 БМ1 типы/длины: " + string.Join(", ", A.Where(x => x.mk == "БМ1").Take(3).Select(x => x.fam + " " + Math.Round(x.len * M) + " @" + P3(x.a))));
    var names = new Dictionary<string, string> { { "C1", "тело в теле (каркас/узлы)" }, { "C2", "обрезан под младшим" }, { "C3", "старший не перекрывает младших" }, { "C4", "заглушки ПЛ3" }, { "C5", "швы" }, { "C6", "торец в плоскости грани" },
        { "C7", "линия стыка на прямой колонне" }, { "C8", "кронштейн не на ж/б" }, { "C9", "материал/цвет марки" }, { "C10", "лишние стыки" }, { "C11", "пластины друг на друге" }, { "C12", "торец пояса не перекрывает стойку" }, { "C13", "тип узла у колонны (шарнир/жёсткий)" }, { "C14", "колонна/ось сдвинута" }, { "C15", "узлы не по узелдер.dwg (столик, накладки, X-связь)" } };
    sb.AppendLine("В113 КМ AUDIT " + DateTime.Now.ToString("dd.MM.yyyy HH:mm") + " - members " + A.Count + ", node/base DS " + DSs.Count + ", solids " + pcs.Count + ", pairs " + pairs + ", bolt-through " + bolted);
    foreach (var kv in R) sb.AppendLine(kv.Key + " " + names[kv.Key] + ": " + (kv.Value.Count > 0 ? "FAIL " + kv.Value.Count : (note.ContainsKey(kv.Key) && note[kv.Key] != "" ? "N/A - " + note[kv.Key] : "PASS")));
    foreach (var kv in R.Where(x => x.Value.Count > 0)) { sb.AppendLine("-- " + kv.Key); foreach (var s in kv.Value.Take(12)) sb.AppendLine("   " + s); }
    X.Add("X15 C15: " + c15info + rib51);
    sb.AppendLine("-- extra"); foreach (var s in X) sb.AppendLine("   " + s);
    return sb.ToString();
}
static void _end() {
