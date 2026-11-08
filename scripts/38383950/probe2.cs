// B109 КМ audit (adapted from 3602 q20_audit.cs). READ-ONLY. Run WITHOUT -Lib. Output: ..\..\..\..\..\..\..\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe2.txt in this folder.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe2.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Audit(nd); }
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
    var R = new Dictionary<string, List<string>>(); foreach (var c in new[] { "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12" }) R[c] = new List<string>();
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
    var stat = new Dictionary<string,int>();
    for (int i = 0; i < A.Count; i++) { var m = A[i];
      for (int e = 0; e < 2; e++) { var P = e == 0 ? m.a : m.b;
        Mb contM = null; foreach (var o in A) { if (o == m) continue; if (par(o, m) && (o.a.DistanceTo(P) < tol || o.b.DistanceTo(P) < tol)) contM = o; }
        if (contM == null || contM.f.Id.Value <= m.f.Id.Value || contM.mk != m.mk) continue;
        Mb best = null; double bd = 1e9; foreach (var x in A) { if (x == m || x == contM || par(x, m)) continue; double d2 = dseg(x, P); if (d2 < bd) { bd = d2; best = x; } }
        if (m.mk == "БМ1") { Mb kn = null; double kd = 1e9; foreach (var x in A) if (x.mk == "КН") { double d3 = dseg(x, P); if (d3 < kd) { kd = d3; kn = x; } } stat["БМ1 nearest KH d=" + Math.Round(kd * M / 25) * 25 + " KH dir " + Math.Round(kn.u.X,1)+","+Math.Round(kn.u.Y,1)+","+Math.Round(kn.u.Z,1) + " bm1 th " + Math.Round(m.th*M)] = 1 + (stat.ContainsKey("БМ1 nearest KH d=" + Math.Round(kd * M / 25) * 25 + " KH dir " + Math.Round(kn.u.X,1)+","+Math.Round(kn.u.Y,1)+","+Math.Round(kn.u.Z,1) + " bm1 th " + Math.Round(m.th*M)) ? stat["БМ1 nearest KH d=" + Math.Round(kd * M / 25) * 25 + " KH dir " + Math.Round(kn.u.X,1)+","+Math.Round(kn.u.Y,1)+","+Math.Round(kn.u.Z,1) + " bm1 th " + Math.Round(m.th*M)] : 0); }
        string k = m.mk + " split; nearest nonpar " + (best == null ? "none" : best.mk + " d=" + (Math.Round(bd * M / 50) * 50) + " th=" + Math.Round(best.th * M));
        stat[k] = stat.ContainsKey(k) ? stat[k] + 1 : 1; } }
    sb.Clear(); foreach (var kv in stat.OrderBy(x => x.Key)) sb.AppendLine(kv.Value + "  " + kv.Key);
    return sb.ToString();
}
static void _end() {