var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\capcheck.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var ds = new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел" && x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionWelds && x.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionBolts).ToList();
    var sol = new List<Tuple<string, Solid>>();
    foreach (var x in ds) foreach (var so in x.get_Geometry(new Options()).OfType<Solid>().Where(q => q.Volume > 1e-9)) sol.Add(Tuple.Create(x.Name, so));
    var tubes = new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Symbol.Family.Name.Contains("труба")).ToList();
    int ends = 0, open = 0; var cnt = new Dictionary<string, int>();
    foreach (var f in tubes) {
      var pts = new List<XYZ>(); var lc = f.Location as LocationCurve;
      if (lc != null) { pts.Add(lc.Curve.GetEndPoint(0)); pts.Add(lc.Curve.GetEndPoint(1)); }
      else { var bb = f.get_BoundingBox(null); var lp = ((LocationPoint)f.Location).Point; pts.Add(new XYZ(lp.X, lp.Y, bb.Min.Z)); pts.Add(new XYZ(lp.X, lp.Y, bb.Max.Z)); }
      string mk = (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "").Split(' ')[0];
      foreach (var p in pts) { ends++;
        bool ok = false;
        foreach (var t in sol) { var bb = t.Item2.GetBoundingBox(); var a = bb.Transform.OfPoint(bb.Min); var b = bb.Transform.OfPoint(bb.Max);
          double tol = 25 * MM; if (p.X > Math.Min(a.X, b.X) - tol && p.X < Math.Max(a.X, b.X) + tol && p.Y > Math.Min(a.Y, b.Y) - tol && p.Y < Math.Max(a.Y, b.Y) + tol && p.Z > Math.Min(a.Z, b.Z) - tol && p.Z < Math.Max(a.Z, b.Z) + tol) { ok = true; break; } }
        if (!ok) { open++; cnt[mk] = cnt.ContainsKey(mk) ? cnt[mk] + 1 : 1; if (open <= 15) sb.AppendLine("open " + f.Id + " " + mk + " @" + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + "," + Math.Round(p.Z / MM)); } } }
    sb.AppendLine("tube ends " + ends + ", without any node plate within 25 mm: " + open + "  " + string.Join(", ", cnt.Select(k => k.Key + " " + k.Value)));
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
