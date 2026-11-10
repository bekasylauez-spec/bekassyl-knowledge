// READ-ONLY node-12 / СВ-end / node-9 geometry (checker). Run with -Lib b109_lib.cs.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_nodes.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = NodeChk(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}

class Sp { public Element El; public string Name; public int Kind; public Solid S; public XYZ Mn, Mx; }
static void BB(Solid s, out XYZ mn, out XYZ mx) { var bb = s.GetBoundingBox(); double x0 = 1e18, y0 = 1e18, z0 = 1e18, x1 = -1e18, y1 = -1e18, z1 = -1e18;
    foreach (var cx in new[] { bb.Min.X, bb.Max.X }) foreach (var cy in new[] { bb.Min.Y, bb.Max.Y }) foreach (var cz in new[] { bb.Min.Z, bb.Max.Z }) { var p = bb.Transform.OfPoint(new XYZ(cx, cy, cz)); x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
    mn = new XYZ(x0, y0, z0); mx = new XYZ(x1, y1, z1); }
static string Pt(XYZ p) { return "(" + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + "," + Math.Round(p.Z / MM) + ")"; }
static List<double[]> ZR(Solid s, double x, double y)
{   var r = new List<double[]>(); try { var ln = Line.CreateBound(new XYZ(x, y, -2000 * MM), new XYZ(x, y, 25000 * MM)); var res = s.IntersectWithCurve(ln, new SolidCurveIntersectionOptions());
    if (res == null) return r; for (int i = 0; i < res.SegmentCount; i++) { var c = res.GetCurveSegment(i); r.Add(new[] { Math.Min(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z) / MM, Math.Max(c.GetEndPoint(0).Z, c.GetEndPoint(1).Z) / MM }); } } catch { } return r; }

static string NodeChk(Document nd)
{
    var sb = new System.Text.StringBuilder(); double CELL = 800 * MM;
    var dss = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел").ToList();
    var frames = new List<Sp>();
    foreach (var el in new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")))
    { string nm = el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? el.Name;
      foreach (var s in Solids(el)) { XYZ mn, mx; BB(s, out mn, out mx); frames.Add(new Sp { El = el, Name = nm, Kind = 2, S = s, Mn = mn, Mx = mx }); } }
    Func<double, double, Func<Sp, bool>, List<Sp>> FrAt = (x, y, flt) => frames.Where(f => flt(f) && f.Mn.X <= x && f.Mx.X >= x && f.Mn.Y <= y && f.Mx.Y >= y).ToList();
    // ---- СВ ends with real extensions
    sb.AppendLine("== 1b. СВ1/СВ2/СВ3 ends: bolt diameters at the end (curve end + extension)");
    var bolts = new List<Tuple<XYZ, XYZ, double>>();   // centre, axis, dia
    foreach (var ds in dss.Where(x => x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts))
        foreach (var s in Solids(ds)) { CylindricalFace cf = null; foreach (Face f in s.Faces) { cf = f as CylindricalFace; if (cf != null) break; } if (cf == null) continue;
            var ax = cf.Axis.Normalize(); double t0 = 1e18, t1 = -1e18; foreach (Edge ed in s.Edges) { var c = ed.AsCurve(); foreach (var q in new[] { c.GetEndPoint(0), c.GetEndPoint(1) }) { double t = (q - cf.Origin).DotProduct(ax); t0 = Math.Min(t0, t); t1 = Math.Max(t1, t); } }
            if ((t1 - t0) / MM < 20) continue; bolts.Add(Tuple.Create(cf.Origin + ax * ((t0 + t1) / 2), ax, cf.get_Radius(0).GetLength() / MM * 2)); }
    var sv = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)") && x.Location is LocationCurve && (x.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("СВ")).ToList();
    int ends = 0, no24 = 0, mixed = 0; var bad = new List<string>(); var dcount = new Dictionary<string, int>();
    foreach (var f in sv)
    { var c = ((LocationCurve)f.Location).Curve; string mk = (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").Split(' ')[0];
      double e0 = f.get_Parameter(BuiltInParameter.START_EXTENSION)?.AsDouble() ?? 0, e1 = f.get_Parameter(BuiltInParameter.END_EXTENSION)?.AsDouble() ?? 0;
      for (int k = 0; k < 2; k++)
      { var u = (c.GetEndPoint(k) - c.GetEndPoint(1 - k)).Normalize(); var pe = c.GetEndPoint(k) + u * (k == 0 ? e0 : e1); ends++;
        var near = bolts.Where(b => { double along = (b.Item1 - pe).DotProduct(u); var perp = (b.Item1 - pe) - u * along; return along > -20 * MM && along < 400 * MM && perp.GetLength() < 120 * MM; }).ToList();
        var ds2 = near.Select(b => Math.Round(b.Item3)).Distinct().OrderBy(x => x).ToList(); int n24 = near.Count(b => Math.Abs(b.Item3 - 24) < 0.6);
        string ks = mk + ":" + string.Join("/", ds2) + " n24=" + n24; dcount[ks] = (dcount.ContainsKey(ks) ? dcount[ks] : 0) + 1;
        if (!ds2.Contains(24)) { no24++; if (bad.Count < 10) bad.Add(mk + " end " + Pt(pe) + " dias " + string.Join("/", ds2)); }
        else if (ds2.Any(x => x != 24)) { mixed++; if (bad.Count < 10) bad.Add("MIXED " + mk + " end " + Pt(pe) + " dias " + string.Join("/", ds2)); } } }
    sb.AppendLine("  ends " + ends + ", without Ø24 " + no24 + ", mixed " + mixed); foreach (var kv in dcount.OrderBy(k => k.Key)) sb.AppendLine("   " + kv.Key + " x" + kv.Value);
    foreach (var x in bad) sb.AppendLine("   " + x);
    // ---- node 12 numeric
    sb.AppendLine("== node 12 numeric");
    var P2 = frames.Where(f => f.Name == "Р2").ToList(); var NP = frames.Where(f => f.Name.StartsWith("ФФ1 НП")).ToList();
    Func<List<Sp>, double, double, double> TopAt = (lst, x, y) => { double best = -1e9; foreach (var f in lst) { if (f.Mn.X > x || f.Mx.X < x || f.Mn.Y > y || f.Mx.Y < y) continue; foreach (var t in ZR(f.S, x, y)) best = Math.Max(best, t[1]); } return best; };
    var tabGap = new List<double>(); var tabPlate = new List<double>(); var tabChord = new List<double>(); var plChord = new List<double>(); var ribGap = new List<double>(); var tabInChord = 0; var capTab = new List<double>(); string exb = "";
    var sel = dss.Where(d => (d.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("Узел Р2:")).ToList();
    foreach (var ds in sel)
    {
        var sol = Solids(ds); var q = sol.Select(s => { XYZ a, b; BB(s, out a, out b); return new[] { a, b }; }).ToList();
        for (int i = 0; i < sol.Count; i++)
        {
            double dx = (q[i][1].X - q[i][0].X) / MM, dy = (q[i][1].Y - q[i][0].Y) / MM, dz = (q[i][1].Z - q[i][0].Z) / MM; double xa = Math.Round(((q[i][0].X + q[i][1].X) / 2 / MM) / 6000) * 6000;
            if (Math.Abs(dx - 75) < 1 && Math.Abs(dz - 8) < 1)          // tab
            {
                double xc = (q[i][0].X + q[i][1].X) / 2, yc = (q[i][0].Y + q[i][1].Y) / 2; double zb = q[i][0].Z / MM, zt = q[i][1].Z / MM;
                // Р2 top under the cap side: sample on the Р2 body 100 beyond the tab end
                double sx = xc / MM > xa ? 1 : -1; double xr = xc + sx * 130 * MM; double p2top = TopAt(P2, xr, yc);
                tabGap.Add(zb - p2top);
                // chord top at the tab's y (centre) and at the 2 edges
                double ct = TopAt(NP, xa * MM, yc); tabChord.Add(zt - ct);
                // plate above: the flat plate solid of this DS with dx>=190, dz 8
                foreach (var jj in Enumerable.Range(0, sol.Count)) { double dxj = (q[jj][1].X - q[jj][0].X) / MM, dzj = (q[jj][1].Z - q[jj][0].Z) / MM; if (dxj > 180 && Math.Abs(dzj - 8) < 1) { tabPlate.Add(q[jj][0].Z / MM - zt);
                    double ctc = TopAt(NP, xa * MM, yc); }  }
                foreach (var f in NP) { if (f.Mn.X > q[i][1].X || f.Mx.X < q[i][0].X || f.Mn.Y > q[i][1].Y || f.Mx.Y < q[i][0].Y || f.Mn.Z > q[i][1].Z || f.Mx.Z < q[i][0].Z) continue; try { var xx = BooleanOperationsUtils.ExecuteBooleanOperation(sol[i], f.S, BooleanOperationsType.Intersect); if (xx != null && xx.Volume / (MM * MM * MM) > 1) tabInChord++; } catch { } }
                double xin = Math.Min(Math.Abs(q[i][0].X / MM - xa), Math.Abs(q[i][1].X / MM - xa)); ribGap.Add(xin - 60);       // tab nearest edge from the chord side face
            }
            if (dx > 180 && Math.Abs(dz - 8) < 1)                          // flat plate over the chord
            {
                double zb = q[i][0].Z / MM; foreach (double yy in new[] { q[i][0].Y / MM + 5, (q[i][0].Y + q[i][1].Y) / 2 / MM, q[i][1].Y / MM - 5 }) { double ct = TopAt(NP, xa * MM, yy * MM); plChord.Add(zb - ct); if (zb - ct > 4.3 || zb - ct < -0.01) exb += " [" + ds.Id.Value + " y" + Math.Round(yy) + " gap " + Math.Round(zb - ct, 2) + "]"; }
            }
        }
    }
    Func<List<double>, string> St = l => l.Count == 0 ? "n=0" : "n=" + l.Count + " min " + Math.Round(l.Min(), 2) + " max " + Math.Round(l.Max(), 2);
    sb.AppendLine("  tab bottom - Р2 top (should be 0): " + St(tabGap));
    sb.AppendLine("  plate bottom - tab top (0): " + St(tabPlate));
    sb.AppendLine("  tab top - chord top at tab y (slope, 0..+4): " + St(tabChord));
    sb.AppendLine("  plate bottom - chord top, y = edges/centre (0..4 slope): " + St(plChord) + " out of range:" + exb);
    sb.AppendLine("  tab nearest edge - chord side face (x mm, fillet clearance): " + St(ribGap) + "; tab ∩ chord count " + tabInChord);
    // ВС1 bottom plates vs Р2 top
    var vg = new List<double>(); string exv = "";
    foreach (var ds in dss.Where(d => (d.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").StartsWith("Узел ВС1:")))
    {
        var sol = Solids(ds); var q = sol.Select(s => { XYZ a, b; BB(s, out a, out b); return new[] { a, b }; }).ToList(); double cz = q.Average(t => (t[0].Z + t[1].Z) / 2) / MM; if (cz > 13000) continue;
        double cx = q.Average(t => (t[0].X + t[1].X) / 2) / MM; if (Math.Abs(cx - Math.Round(cx / 6000) * 6000) < 700) continue;
        double yc = q.Average(t => (t[0].Y + t[1].Y) / 2) / MM; double zmin = q.Min(t => t[0].Z) / MM; double top = TopAt(P2, cx * MM, Math.Round((yc - 50) / 50) * 50 * MM + 0 * MM);
        double yp = new[] { 3050.0, 9050, 15050, 21050, 38950, 44950, 50950, 56950 }.OrderBy(v => Math.Abs(v - yc)).First(); top = TopAt(P2, cx * MM, yp * MM);
        vg.Add(zmin - top); if (Math.Abs(zmin - top) > 1) exv += " [" + ds.Id.Value + " at " + Math.Round(cx) + "," + Math.Round(yc) + " gap " + Math.Round(zmin - top, 2) + "]";
    }
    sb.AppendLine("  ВС1 bottom plates: lowest z - Р2 top (should be ~0): " + St(vg) + " |gap|>1:" + exv);    return sb.ToString();
}