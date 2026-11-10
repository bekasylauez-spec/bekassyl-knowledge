var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\chk_g.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var nd = app.Documents.Cast<Document>().First(d => d.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt")); G(nd, sb); }
  catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString(), System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
}
class R { public double x0, x1, y0, y1, z0, z1; public string nm; public long id; }
static void BB(Solid s, out XYZ mn, out XYZ mx) { var bb = s.GetBoundingBox(); double x0 = 1e18, y0 = 1e18, z0 = 1e18, x1 = -1e18, y1 = -1e18, z1 = -1e18;
    foreach (var cx in new[] { bb.Min.X, bb.Max.X }) foreach (var cy in new[] { bb.Min.Y, bb.Max.Y }) foreach (var cz in new[] { bb.Min.Z, bb.Max.Z }) { var p = bb.Transform.OfPoint(new XYZ(cx, cy, cz)); x0 = Math.Min(x0, p.X); y0 = Math.Min(y0, p.Y); z0 = Math.Min(z0, p.Z); x1 = Math.Max(x1, p.X); y1 = Math.Max(y1, p.Y); z1 = Math.Max(z1, p.Z); }
    mn = new XYZ(x0, y0, z0); mx = new XYZ(x1, y1, z1); }
static void G(Document nd, System.Text.StringBuilder sb)
{
    var rib8 = new List<R>(); var knRib = new List<R>();
    foreach (var ds in new FilteredElementCollector(nd).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value == (long)BuiltInCategory.OST_StructConnections))
    {
        foreach (var s in Solids(ds)) { XYZ a, b; BB(s, out a, out b); double dx = (b.X - a.X) / MM, dy = (b.Y - a.Y) / MM, dz = (b.Z - a.Z) / MM;
            var r = new R { x0 = a.X / MM, x1 = b.X / MM, y0 = a.Y / MM, y1 = b.Y / MM, z0 = a.Z / MM, z1 = b.Z / MM, nm = ds.Name, id = ds.Id.Value };
            if (ds.Name.StartsWith("Узел Р1") && Math.Abs(dz - 8) < 0.2 && dx > 100 && dx < 160 && dy > 200) rib8.Add(r);
            if (ds.Name.StartsWith("Узел 9 КН") && Math.Abs(dz - 12) < 0.3 && dx > 100 && dx < 160 && dy > 200) knRib.Add(r); }
    }
    sb.AppendLine("node-7 ribs −8 (Р1 groups): total " + rib8.Count + "; at +5.020 band: " + rib8.Count(r => r.z0 > 4500 && r.z1 < 5600) + "; at +10.340 band: " + rib8.Count(r => r.z0 > 10000 && r.z1 < 10800) + "; other: " + rib8.Count(r => !(r.z0 > 4500 && r.z1 < 5600) && !(r.z0 > 10000 && r.z1 < 10800)));
    sb.AppendLine("КН column ribs −12: " + knRib.Count);
    double minGap = 1e9, minOver = 1e9; string ex = "", exo = ""; int near = 0;
    foreach (var a in rib8.Where(r => r.z0 > 10000 && r.z1 < 10800))
        foreach (var k in knRib)
        {
            if (a.x1 < k.x0 - 0.01 || a.x0 > k.x1 + 0.01 || a.y1 < k.y0 || a.y0 > k.y1) continue; near++;           // overlap in plan
            double gap = a.z0 >= k.z1 ? a.z0 - k.z1 : k.z0 >= a.z1 ? k.z0 - a.z1 : -1;
            if (gap >= 0 && gap < minGap) { minGap = gap; ex = "rib#" + a.id + " z " + Math.Round(a.z0, 1) + ".." + Math.Round(a.z1, 1) + " vs КН rib z " + Math.Round(k.z0, 1) + ".." + Math.Round(k.z1, 1) + " x " + Math.Round(a.x0) + " y " + Math.Round(a.y0); }
            if (gap < 0) { minOver++; exo = "OVERLAP rib#" + a.id + " vs " + k.id + " z " + Math.Round(a.z0, 1) + ".." + Math.Round(a.z1, 1) + " / " + Math.Round(k.z0, 1) + ".." + Math.Round(k.z1, 1) + " x " + Math.Round(a.x0); }
        }
    sb.AppendLine("  +10.340 ribs vs КН ribs overlapping in plan: " + near + ", min vertical gap " + Math.Round(minGap, 2) + " " + ex + "; overlaps " + (minOver > 1e8 ? 0 : minOver) + " " + exo);
}