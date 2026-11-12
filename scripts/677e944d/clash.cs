// Алатау: clash audit of everything steel — frame members ((КМ) families) and node pieces (DirectShapes «БК_узел»). Run with -Lib alatau_lib.cs.
// Works per solid (node DirectShapes hold many plates each), sweep over x for the candidate pairs; result in _авто\_al90.txt (Idling, so a long run
// does not lose its output). Bolts / anchors through a pack are expected (holes are not modelled) and counted apart; so are pieces of one element.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\clash.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В113-КМ.rvt")); r = Audit(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r); };
uiapp.Idling += hnd;
return "queued";
}

class Pc { public Element El; public string Name; public bool Bolt; public Solid S; public XYZ Mn, Mx; }
static string Audit(Document nd)
{
    var sb = new System.Text.StringBuilder();
    var els = new FilteredElementCollector(nd).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)")).Cast<Element>()
        .Concat(new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" || x.ApplicationId == "БК_ЖБ")).ToList();
    var pcs = new List<Pc>();
    foreach (var el in els)
    {
        string nm = el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? el.Name; bool bolt = el.Category.Id.Value == (long)BuiltInCategory.OST_StructConnectionBolts;
        foreach (var s in Solids(el)) { var bb = s.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            pcs.Add(new Pc { El = el, Name = nm, Bolt = bolt, S = s, Mn = new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z)), Mx = new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z)) }); }
    }
    string rf = @"D:\Бекасыл КЖ КМ\Завод_В113_КМ\_авто\_region.txt";
    if (System.IO.File.Exists(rf)) { var v = System.IO.File.ReadAllText(rf).Split(' ').Select(q => double.Parse(q, System.Globalization.CultureInfo.InvariantCulture) * MM).ToArray();
        pcs = pcs.Where(p => p.Mx.X >= v[0] && p.Mn.X <= v[1]).ToList(); sb.AppendLine("region x " + v[0] / MM + "…" + v[1] / MM); }
    pcs = pcs.OrderBy(p => p.Mn.X).ToList();
    var groups = new Dictionary<string, int>(); var ex = new Dictionary<string, string>(); int expected = 0, hits = 0, pairs = 0;
    for (int i = 0; i < pcs.Count; i++)
    {
        var a = pcs[i];
        for (int j = i + 1; j < pcs.Count && pcs[j].Mn.X <= a.Mx.X; j++)
        {
            var b = pcs[j]; if (a.El.Id == b.El.Id) continue;
            if (a.Mx.Y < b.Mn.Y || b.Mx.Y < a.Mn.Y || a.Mx.Z < b.Mn.Z || b.Mx.Z < a.Mn.Z) continue;
            pairs++; double v = 0;
            try { var x = BooleanOperationsUtils.ExecuteBooleanOperation(a.S, b.S, BooleanOperationsType.Intersect); if (x != null) v = x.Volume; } catch { }
            double mm3 = v / (MM * MM * MM); if (mm3 < 1) continue;
            if (a.Bolt || b.Bolt) { expected++; continue; }
            hits++; string key = string.Compare(a.Name, b.Name) < 0 ? a.Name + "  ∩  " + b.Name : b.Name + "  ∩  " + a.Name;
            groups[key] = (groups.ContainsKey(key) ? groups[key] : 0) + 1;
            if (!ex.ContainsKey(key)) { var c = (a.Mn + a.Mx) / 2; ex[key] = "#" + a.El.Id + "/#" + b.El.Id + " " + Math.Round(mm3) + " мм³ near x " + Math.Round(c.X / MM) + " y " + Math.Round(c.Y / MM) + " z " + Math.Round(c.Z / MM); }
        }
    }
    sb.AppendLine("elements " + els.Count + ", solids " + pcs.Count + ", bbox pairs " + pairs + ", intersecting " + hits + " (+ " + expected + " bolt/anchor through a pack, holes not modelled)");
    foreach (var k in groups.OrderByDescending(x => x.Value)) sb.AppendLine("  " + k.Value + " × " + k.Key + "   e.g. " + ex[k.Key]);
    return sb.ToString();
}
