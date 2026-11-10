var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_dump2.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Run2(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
const double M = 304.8;
static string V(XYZ p) { return "(" + Math.Round(p.X, 3) + "," + Math.Round(p.Y, 3) + "," + Math.Round(p.Z, 3) + ")"; }
static string Run2(Document nd)
{
    var sb = new System.Text.StringBuilder();
    foreach (long id in new long[] { 3571387, 3571395 })
    {
        var el = nd.GetElement(new ElementId(id)); sb.AppendLine("DS#" + id + " " + el.Name);
        var ge = el.get_Geometry(new Options { DetailLevel = ViewDetailLevel.Fine });
        foreach (var go in ge) { var so = go as Solid; if (so == null || so.Volume < 1e-9) continue;
            var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
            PlanarFace big = null; foreach (Face fc in so.Faces) { var pf = fc as PlanarFace; if (pf != null && (big == null || pf.Area > big.Area)) big = pf; }
            sb.AppendLine("  vol " + Math.Round(so.Volume * M * M * M) + " faces " + so.Faces.Size + " bb " + Math.Round(a.X * M) + "," + Math.Round(a.Y * M) + "," + Math.Round(a.Z * M) + " .. " + Math.Round(b.X * M) + "," + Math.Round(b.Y * M) + "," + Math.Round(b.Z * M) + " bigFace " + Math.Round(big.Area * M * M) + " n " + V(big.FaceNormal) + " cen " + V(so.ComputeCentroid() * M)); }
    }
    return sb.ToString();
}
static void _end() {