// READ-ONLY region dump (checker). Run WITHOUT -Lib.
var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\q_reg2.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r;
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); r = Q(nd); }
  catch (Exception ex) { r = "ERR " + ex; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
static string Q(Document nd)
{
    const double M = 304.8; var sb = new System.Text.StringBuilder(); var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
    var all = new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionWelds).ToList();
    Func<Solid, double> thick = so => { double af = 0; foreach (Face f in so.Faces) if (f is PlanarFace) af = Math.Max(af, f.Area); return af > 0 ? so.Volume / af * M : 0; };
    var regs = new[] {
      new { n = "R6 purlin support x6000 y3000", x0 = 5800.0, x1 = 6200, y0 = 2900.0, y1 = 3200, z0 = 14000.0, z1 = 16000 },
      new { n = "R7 KN node x6000 rowA +750", x0 = 5800.0, x1 = 6200, y0 = 280.0, y1 = 1000, z0 = 10000.0, z1 = 11100 },
      new { n = "R8 BP1 axis0 rowA rigid", x0 = -160.0, x1 = 160, y0 = 280.0, y1 = 700, z0 = 14000.0, z1 = 15200 },
    };
    foreach (var rg in regs)
    {
        sb.AppendLine("##### " + rg.n);
        foreach (var d in all)
        {
            var bbd = d.get_BoundingBox(null); if (bbd == null) continue;
            if (bbd.Max.X * M < rg.x0 || bbd.Min.X * M > rg.x1 || bbd.Max.Y * M < rg.y0 || bbd.Min.Y * M > rg.y1 || bbd.Max.Z * M < rg.z0 || bbd.Min.Z * M > rg.z1) continue;
            foreach (var go in d.get_Geometry(opt)) { var so = go as Solid; if (so == null || so.Volume < 1e-12) continue; var bb = so.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
                double X0 = Math.Min(a.X, b.X) * M, X1 = Math.Max(a.X, b.X) * M, Y0 = Math.Min(a.Y, b.Y) * M, Y1 = Math.Max(a.Y, b.Y) * M, Z0 = Math.Min(a.Z, b.Z) * M, Z1 = Math.Max(a.Z, b.Z) * M;
                if (X1 < rg.x0 || X0 > rg.x1 || Y1 < rg.y0 || Y0 > rg.y1 || Z1 < rg.z0 || Z0 > rg.z1) continue;
                sb.AppendLine("  " + d.Id.Value + " [" + (d.Name.Length > 46 ? d.Name.Substring(0, 46) : d.Name) + "] t=" + Math.Round(thick(so), 1).ToString("0.0", System.Globalization.CultureInfo.InvariantCulture) + " x " + Math.Round(X0) + ".." + Math.Round(X1) + " y " + Math.Round(Y0) + ".." + Math.Round(Y1) + " z " + Math.Round(Z0) + ".." + Math.Round(Z1)); }
        }
    }
    return sb.ToString();
}
static void _end() {