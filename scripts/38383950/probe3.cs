// B109 КМ audit (adapted from 3602 q20_audit.cs). READ-ONLY. Run WITHOUT -Lib. Output: ..\..\..\..\..\..\..\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe3.txt in this folder.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\_probe3.txt";
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
    sb.Clear();
    Func<XYZ,string> q = p => Math.Round(p.X*M)+","+Math.Round(p.Y*M)+","+Math.Round(p.Z*M);
    var tr = A.Where(x => x.blk.StartsWith("ФФ1") && Math.Abs(x.a.X*M-6000)<50 && Math.Abs(x.b.X*M-6000)<50).OrderBy(x=>Math.Min(x.a.Y,x.b.Y)).ToList();
    sb.AppendLine("truss x=6000 members " + tr.Count);
    foreach (var x in tr.Take(40)) sb.AppendLine(x.blk + " " + x.fam.Replace("(КМ)","") + " " + q(x.a) + " -> " + q(x.b));
    foreach (var mk in new[]{"СВ1","СВ2","СВ3","Р1","Р2","Б2","БП2","КН"}) { foreach (var x in A.Where(y=>y.mk==mk).Take(3)) sb.AppendLine(mk+" "+x.f.Id.Value+" "+q(x.a)+" -> "+q(x.b)+" "+x.fam.Replace("(КМ)","")); }
    foreach (var x in A.Where(y=>y.mk=="ГС1").Take(6)) sb.AppendLine("ГС1 "+q(x.a)+" -> "+q(x.b));
    foreach (var x in A.Where(y=>y.mk=="Пр1"&&Math.Abs(y.a.X*M-6000)<2000&&Math.Abs(y.b.X*M-6000)<2000).Take(8)) sb.AppendLine("Пр1 "+q(x.a)+" -> "+q(x.b));
    return sb.ToString();
}
static void _end() {