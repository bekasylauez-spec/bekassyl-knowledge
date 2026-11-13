// probe: why Mono failed for mixed-material welds: face types, loops, TSB outcome
var d = document; var sb = new StringBuilder(); var matName = new Dictionary<long, string>();
Func<ElementId, string> mn = id => { long k = id.Value; string n; if (!matName.TryGetValue(k, out n)) { var m = d.GetElement(id) as Material; n = m == null ? "-" : m.Name; matName[k] = n; } return n; };
var tr = new Transaction(d, "p"); tr.Start(); var seen = new Dictionary<string, int>(); var tmp = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel));
foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>())
{
    if (ds.ApplicationId != "БК_узел" || ds.Category == null || ds.Category.Id.Value != (long)BuiltInCategory.OST_StructConnectionWelds) continue;
    string adi = ds.ApplicationDataId ?? ""; string key = adi.Split('|')[0].Trim(); if (key != "узел 1" && key != "узел 14" && key != "узел 15") continue;
    foreach (var s in QSolidsOf(ds))
    {
        var set = new HashSet<string>(); foreach (Face f in s.Faces) set.Add(mn(f.MaterialElementId)); if (set.Count < 2) continue;
        int c; seen.TryGetValue(key, out c); if (c >= 3) continue; seen[key] = c + 1;
        int planar = 0, nonp = 0, multiLoop = 0, nonLine = 0; var kinds = new List<string>();
        foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) { nonp++; kinds.Add(f.GetType().Name); continue; } planar++; var lps = pf.GetEdgesAsCurveLoops(); if (lps.Count != 1) multiLoop++; foreach (var lp in lps) foreach (Curve cu in lp) if (!(cu is Line)) nonLine++; }
        sb.AppendLine(key + " " + ds.Name + " vol " + QF(QCu(s.Volume)) + " faces " + s.Faces.Size + " planar " + planar + " nonplanar " + nonp + " (" + string.Join(",", kinds) + ") multiLoop " + multiLoop + " nonLine " + nonLine + " mats " + string.Join("+", set));
        try { var r = QMonoSolid(s, ElementId.InvalidElementId); sb.AppendLine("   Mono returned " + (ReferenceEquals(r, s) ? "ORIGINAL" : "NEW")); if (!ReferenceEquals(r, s)) sb.AppendLine("   valid " + tmp.IsValidShape(new List<GeometryObject> { r })); } catch (Exception ex) { sb.AppendLine("   Mono ex " + ex.Message); }
        // TSB direct to see outcome
        try { var faces = new List<List<XYZ>>(); bool ok = true; foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) { ok = false; break; } var lps = pf.GetEdgesAsCurveLoops(); if (lps.Count != 1) { ok = false; break; } var pts = new List<XYZ>(); foreach (Curve cu in lps[0]) pts.Add(cu.GetEndPoint(0)); faces.Add(pts); }
            if (ok) foreach (bool rev in new[] { false, true }) { var tsb = new TessellatedShapeBuilder(); tsb.OpenConnectedFaceSet(true); foreach (var pts in faces) { var q = new List<XYZ>(pts); if (rev) q.Reverse(); tsb.AddFace(new TessellatedFace(q, ElementId.InvalidElementId)); } tsb.CloseConnectedFaceSet(); tsb.Target = TessellatedShapeBuilderTarget.Solid; tsb.Fallback = TessellatedShapeBuilderFallback.Abort; try { tsb.Build(); var res = tsb.GetBuildResult(); string o = "   TSB rev=" + rev + " outcome " + res.Outcome; foreach (var go in res.GetGeometricalObjects()) { var ns = go as Solid; if (ns != null) o += " vol " + QF(QCu(ns.Volume)) + " (orig " + QF(QCu(s.Volume)) + ")"; } sb.AppendLine(o); } catch (Exception ex) { sb.AppendLine("   TSB rev=" + rev + " ex " + ex.Message.Split(new[] { (char)10 })[0]); } } } catch (Exception ex) { sb.AppendLine("   probe ex " + ex.Message); }
    }
}
tr.RollBack(); return sb.ToString();
}
