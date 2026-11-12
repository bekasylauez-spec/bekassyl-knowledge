// READ-ONLY contact audit of every node body: plates (outline, thickness, edge/face contact), bolts (which bodies the shank pierces).
var d = document; double M = 304.8; var ci = System.Globalization.CultureInfo.InvariantCulture;
string dir = @"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\n\";
System.IO.Directory.CreateDirectory(dir);
var sw = System.Diagnostics.Stopwatch.StartNew();
try {
  var opt = new Options { DetailLevel = ViewDetailLevel.Fine };
  Func<Solid, double[]> AABB = s => { var b = s.GetBoundingBox(); var t = b.Transform; var r = new double[] { 1e9, 1e9, 1e9, -1e9, -1e9, -1e9 };
    foreach (var px in new[] { b.Min.X, b.Max.X }) foreach (var py in new[] { b.Min.Y, b.Max.Y }) foreach (var pz in new[] { b.Min.Z, b.Max.Z }) { var p = t.OfPoint(new XYZ(px, py, pz)); r[0] = Math.Min(r[0], p.X); r[1] = Math.Min(r[1], p.Y); r[2] = Math.Min(r[2], p.Z); r[3] = Math.Max(r[3], p.X); r[4] = Math.Max(r[4], p.Y); r[5] = Math.Max(r[5], p.Z); } return r; };
  Func<XYZ, string> P = p => (p.X * M).ToString("0.0", ci) + "," + (p.Y * M).ToString("0.0", ci) + "," + (p.Z * M).ToString("0.0", ci);
  var labs = new List<string>(); var sols = new List<Solid>(); var boxes = new List<double[]>();
  var mem = new StringBuilder(); mem.AppendLine("id\tmark\ttype\ta\tb");
  foreach (var f in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(x => x.Symbol.Family.Name.StartsWith("(КМ)"))) {
    string mk = f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? ""; var bb = f.get_BoundingBox(null); if (bb == null) continue; XYZ a, b;
    if (f.Location is LocationCurve lc) { a = lc.Curve.GetEndPoint(0); b = lc.Curve.GetEndPoint(1); } else { var lp = ((LocationPoint)f.Location).Point; a = new XYZ(lp.X, lp.Y, bb.Min.Z); b = new XYZ(lp.X, lp.Y, bb.Max.Z); }
    mem.AppendLine(f.Id.Value + "\t" + mk + "\t" + f.Symbol.Name + "\t" + P(a) + "\t" + P(b));
    Action<GeometryElement> walk = null; walk = ge => { foreach (var g in ge) { if (g is Solid s && s.Volume > 1e-9) { labs.Add("M|" + mk + "|" + f.Id.Value); sols.Add(s); boxes.Add(AABB(s)); } else if (g is GeometryInstance gi) walk(gi.GetInstanceGeometry()); } };
    walk(f.get_Geometry(opt));
  }
  System.IO.File.WriteAllText(dir + "members.tsv", mem.ToString(), Encoding.UTF8);
  int nMem = sols.Count;
  var pKey = new List<string>(); var bolts = new List<Tuple<string, Solid>>(); int nWeld = 0;
  foreach (var ds in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).Cast<DirectShape>().Where(x => x.ApplicationId == "БК_узел")) {
    long cat = ds.Category.Id.Value; string key = ds.ApplicationDataId;
    foreach (var g in ds.get_Geometry(opt)) { var s = g as Solid; if (s == null || s.Volume < 1e-9) continue;
      if (cat == (long)BuiltInCategory.OST_StructConnectionBolts) bolts.Add(Tuple.Create(key, s));
      else if (cat == (long)BuiltInCategory.OST_StructConnectionWelds) nWeld++;
      else { labs.Add("P|" + (sols.Count - nMem) + "|" + key); sols.Add(s); boxes.Add(AABB(s)); pKey.Add(key); } } }
  int N = sols.Count; double tol = 0.02;
  Func<XYZ, XYZ, int, List<int>> Hit = (a, b, self) => { var res = new List<int>(); double mx = (a.X + b.X) / 2, my = (a.Y + b.Y) / 2, mz = (a.Z + b.Z) / 2; Line ln = null;
    for (int i = 0; i < N; i++) { if (i == self) continue; var bx = boxes[i]; if (mx < bx[0] - tol || mx > bx[3] + tol || my < bx[1] - tol || my > bx[4] + tol || mz < bx[2] - tol || mz > bx[5] + tol) continue;
      try { if (ln == null) ln = Line.CreateBound(a, b); var r = sols[i].IntersectWithCurve(ln, new SolidCurveIntersectionOptions()); if (r.SegmentCount > 0) res.Add(i); } catch { } } return res; };
  var pl = new StringBuilder(); pl.AppendLine("idx\tkey\tt\tarea_cm2\tnormal\tverts\tper\tedge\tfaceA\tfaceB");
  var ed = new StringBuilder(); ed.AppendLine("idx\tx\ty\tz\tw\tlabs");
  for (int i = nMem; i < N; i++) { var s = sols[i]; PlanarFace big = null; foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf != null && (big == null || pf.Area > big.Area)) big = pf; } if (big == null) continue;
    double t = s.Volume / big.Area; XYZ n = big.FaceNormal; var loops = big.GetEdgesAsCurveLoops(); CurveLoop outer = null; double best = -1; foreach (var l in loops) { double len = l.GetExactLength(); if (len > best) { best = len; outer = l; } }
    var verts = new List<string>(); var econt = new Dictionary<string, double>(); double per = 0;
    foreach (Curve c in outer) { verts.Add(P(c.GetEndPoint(0))); double L = c.Length; int k = Math.Max(1, (int)Math.Round(L * M / 20));
      for (int j = 0; j < k; j++) { double u = (j + 0.5) / k; XYZ p = c.Evaluate(u, true); XYZ tau = c.ComputeDerivatives(u, true).BasisX.Normalize(); XYZ o = tau.CrossProduct(n).Normalize(); XYZ pm = p - n * (t / 2); double w = L / k * M; per += w;
        var hs = new HashSet<int>(); foreach (var sg in new[] { 1.0, -1.0 }) { XYZ q = pm + o * (sg * 1.5 / M); foreach (var h in Hit(q - n * (1.0 / M), q + n * (1.0 / M), i)) hs.Add(h); }
        if (hs.Count == 0) { double v; econt.TryGetValue("-", out v); econt["-"] = v + w; }
        else { foreach (var h in hs) { double v; econt.TryGetValue(labs[h], out v); econt[labs[h]] = v + w; } ed.AppendLine((i - nMem) + "\t" + (pm.X * M).ToString("0.0", ci) + "\t" + (pm.Y * M).ToString("0.0", ci) + "\t" + (pm.Z * M).ToString("0.0", ci) + "\t" + w.ToString("0.0", ci) + "\t" + string.Join(";", hs.Select(h => labs[h]))); } } }
    var fa = new Dictionary<string, int>(); var fb = new Dictionary<string, int>(); int tot = 0; var uvb = big.GetBoundingBox();
    for (int a1 = 0; a1 < 7; a1++) for (int b1 = 0; b1 < 7; b1++) { var uv = new UV(uvb.Min.U + (uvb.Max.U - uvb.Min.U) * (a1 + 0.5) / 7, uvb.Min.V + (uvb.Max.V - uvb.Min.V) * (b1 + 0.5) / 7); if (!big.IsInside(uv)) continue; tot++; XYZ p0 = big.Evaluate(uv);
      foreach (var h in Hit(p0 + n * (0.4 / M), p0 + n * (2.4 / M), i)) { int v; fa.TryGetValue(labs[h], out v); fa[labs[h]] = v + 1; }
      foreach (var h in Hit(p0 - n * (t + 0.4 / M), p0 - n * (t + 2.4 / M), i)) { int v; fb.TryGetValue(labs[h], out v); fb[labs[h]] = v + 1; } }
    pl.AppendLine((i - nMem) + "\t" + pKey[i - nMem] + "\t" + (t * M).ToString("0.0", ci) + "\t" + (big.Area * M * M / 100).ToString("0.0", ci) + "\t" + n.X.ToString("0.000", ci) + "," + n.Y.ToString("0.000", ci) + "," + n.Z.ToString("0.000", ci) + "\t" + string.Join(";", verts) + "\t" + per.ToString("0", ci) + "\t" + string.Join(";", econt.Select(kv => kv.Key + "=" + kv.Value.ToString("0", ci))) + "\t" + tot + ":" + string.Join(";", fa.Select(kv => kv.Key + "=" + kv.Value)) + "\t" + tot + ":" + string.Join(";", fb.Select(kv => kv.Key + "=" + kv.Value)));
  }
  System.IO.File.WriteAllText(dir + "plates.tsv", pl.ToString(), Encoding.UTF8); System.IO.File.WriteAllText(dir + "edges.tsv", ed.ToString(), Encoding.UTF8);
  var bo = new StringBuilder(); bo.AppendLine("key\ta\tb\td\tlen\tpierced"); int nShank = 0, nNoCyl = 0;
  foreach (var bt in bolts) { var s = bt.Item2; CylindricalFace cf = null; foreach (Face f in s.Faces) { cf = f as CylindricalFace; if (cf != null) break; } if (cf == null) { nNoCyl++; continue; }
    XYZ ax = cf.Axis.Normalize(); XYZ org = cf.Origin; double rad = cf.get_Radius(0).GetLength(); double mn = 1e9, mxp = -1e9;
    foreach (Edge e in s.Edges) foreach (var pt in e.Tessellate()) { double q = (pt - org).DotProduct(ax); if (q < mn) mn = q; if (q > mxp) mxp = q; }
    double len = mxp - mn; if (len < 3 * rad) continue; nShank++; XYZ a = org + ax * mn, b = org + ax * mxp; var prc = new List<string>(); double mx = (a.X + b.X) / 2, my = (a.Y + b.Y) / 2, mz = (a.Z + b.Z) / 2, hl = len / 2 + tol; Line ln = Line.CreateBound(a, b);
    for (int i = 0; i < N; i++) { var bx = boxes[i]; if (mx < bx[0] - hl || mx > bx[3] + hl || my < bx[1] - hl || my > bx[4] + hl || mz < bx[2] - hl || mz > bx[5] + hl) continue;
      try { var r = sols[i].IntersectWithCurve(ln, new SolidCurveIntersectionOptions()); double L = 0; for (int k = 0; k < r.SegmentCount; k++) L += r.GetCurveSegment(k).Length; if (L * M > 0.5) prc.Add(labs[i] + "=" + (L * M).ToString("0.0", ci)); } catch { } }
    bo.AppendLine(bt.Item1 + "\t" + P(a) + "\t" + P(b) + "\t" + (2 * rad * M).ToString("0.0", ci) + "\t" + (len * M).ToString("0", ci) + "\t" + string.Join(";", prc)); }
  System.IO.File.WriteAllText(dir + "bolts.tsv", bo.ToString(), Encoding.UTF8);
  return "ok members solids " + nMem + ", plates " + (N - nMem) + ", bolt solids " + bolts.Count + " shanks " + nShank + " nocyl " + nNoCyl + ", welds " + nWeld + ", sec " + sw.Elapsed.TotalSeconds.ToString("0") + " modified=" + d.IsModified;
} catch (Exception ex) { return "ERR " + ex; }
