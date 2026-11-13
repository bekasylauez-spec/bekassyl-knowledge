    // ======================= аннотация: размер, выноска, шов, обрыв, отметка, шеңбер =======================
    public void DIM(RnV c, double[] pos, bool alongU, double at, double from)
    {
        var v = c.V; var pl = pos.Distinct().OrderBy(x => x).ToList(); if (pl.Count < 2) return; var ra = new ReferenceArray();
        double sg = Math.Sign(at - from); if (sg == 0) sg = 1;
        foreach (var p in pl) { var a = alongU ? Pw(c, p, from) : Pw(c, from, p); var b = alongU ? Pw(c, p, from + sg * 25) : Pw(c, from + sg * 25, p);
            var dc = d.Create.NewDetailCurve(v, Line.CreateBound(a, b)); dc.LineStyle = invis; ra.Append(dc.GeometryCurve.Reference); }
        var l0 = alongU ? Line.CreateBound(Pw(c, pl.First() - 50, at), Pw(c, pl.Last() + 50, at)) : Line.CreateBound(Pw(c, at, pl.First() - 50), Pw(c, at, pl.Last() + 50));
        try
        {
            var dm = d.Create.NewDimension(v, l0, ra, dimT); nDim++;
            if (dm.Segments.Size >= 2) { d.Regenerate(); int k = 0, n = dm.Segments.Size; var along = alongU ? v.RightDirection : v.UpDirection; var outw = (alongU ? v.UpDirection : v.RightDirection) * sg; bool prevSmall = false; int alt = 0;
                foreach (DimensionSegment sgm in dm.Segments) { double pap = (sgm.Value ?? 0) / RN_M / RN_SC; var tp = sgm.TextPosition;
                    if (pap < 4.5 && (k == 0 || k == n - 1)) sgm.TextPosition = tp + along * ((pap / 2 + 2.6) * RN_SC * RN_M * (k == 0 ? -1 : 1));
                    else if (pap < 4.5) { int sd = prevSmall ? (alt++ % 2 == 0 ? 1 : -1) : 0; sgm.TextPosition = tp + outw * (3.6 * RN_SC * RN_M) + along * (sd * 3.0 * RN_SC * RN_M); prevSmall = true; k++; continue; }
                    prevSmall = false; k++; } }
            else { double pap = (dm.Value ?? 0) / RN_M / RN_SC; if (pap < 4.5) { d.Regenerate(); var along = alongU ? v.RightDirection : v.UpDirection; dm.TextPosition = dm.TextPosition + along * ((pap / 2 + 2.6) * RN_SC * RN_M); } }
        }
        catch (Exception ex) { sb.AppendLine("  dim ERR «" + c.Name + "» " + ex.Message.Split('\n')[0]); nWarn++; return; }
        // кедергілер: тізбек сызығы, куә сызықтары, сандар қорабы
        if (alongU) { c.AddSeg(pl.First() - 50, at, pl.Last() + 50, at); foreach (var p in pl) c.AddSeg(p, from, p, at); } else { c.AddSeg(at, pl.First() - 50, at, pl.Last() + 50); foreach (var p in pl) c.AddSeg(from, p, at, p); }
        for (int i = 0; i + 1 < pl.Count; i++) { double len = pl[i + 1] - pl[i], mid = (pl[i] + pl[i + 1]) / 2; double wm = (Math.Round(len).ToString().Length * 1.7 + 1) * RN_SC, hm = 35;
            bool tiny = len / RN_SC < 4.5; double off = tiny ? sg * 36 : 0;
            if (alongU) c.AddBox(new[] { mid - wm / 2, at + off - hm / 2 - 5, mid + wm / 2, at + off + hm / 2 + 5 }); else c.AddBox(new[] { at + off - hm / 2 - 5, mid - wm / 2, at + off + hm / 2 + 5, mid + wm / 2 }); }
    }
    // ----- авто-размерлер: тізбек = бөлшек қырлары + болт центрлері (≤ 8 нүкте); төменгі (u) және сол жақ (v) қатар; 2-ші жолақ = жалпы габарит
    public void AutoDims(RnV c)
    {
        var shp = c.Own.Where(x => x.P != null).ToList(); if (shp.Count == 0) return;
        for (int axis = 0; axis < 2; axis++)
        {
            var f = new List<double[]>();   // {coord, weight}
            foreach (var s in shp)
            {
                bool bolt = s.P.Bolt && (s.P.Title.Contains("стержень") || s.P.Title.Contains("анкер") || s.P.Title.Contains("болт")); double w = bolt ? 1e7 : s.Area;
                if (bolt) f.Add(new[] { axis == 0 ? s.Cu : s.Cv, w }); else if (!s.P.Bolt) { f.Add(new[] { axis == 0 ? s.U0 : s.V0, w }); f.Add(new[] { axis == 0 ? s.U1 : s.V1, w }); }
            }
            if (f.Count < 2) continue; f = f.OrderBy(x => x[0]).ToList(); var m = new List<double[]>();
            foreach (var x in f) { if (m.Count > 0 && x[0] - m[m.Count - 1][0] < 8) { if (x[1] > m[m.Count - 1][1]) m[m.Count - 1] = x; } else m.Add(x); }
            while (m.Count > 8) { int k = 1; for (int i = 2; i < m.Count - 1; i++) if (m[i][1] < m[k][1]) k = i; m.RemoveAt(k); }
            var pos = m.Select(x => x[0]).ToList(); if (pos.Count < 2) continue;
            if (axis == 0) { DIM(c, pos.ToArray(), true, c.V0 - 100, c.V0); if (pos.Count >= 3) DIM(c, new[] { pos.First(), pos.Last() }, true, c.V0 - 180, c.V0); }
            else { DIM(c, pos.ToArray(), false, c.U0 - 100, c.U0); if (pos.Count >= 3) DIM(c, new[] { pos.First(), pos.Last() }, false, c.U0 - 180, c.U0); }
        }
    }
    // ----- выноска (ЕРЕЖЕ_Выноска_узел): стрелка ұшы (tu, tv), полка орталығы (cu, cv)
    public bool LD(RnV c, double tu, double tv, double cu, double cv, string top, string bot, bool plain)
    {
        var v = c.V; double w = Math.Max(8, Math.Max(top.Length, bot.Length) * 1.6 + 3);
        var cp = Pw(c, cu, cv); var end = Pw(c, tu, tv);
        var fi = d.Create.NewFamilyInstance(cp, plain ? sNoArrow : sArrow, v); fi.LookupParameter("Текст верх")?.Set(top); fi.LookupParameter("Текст низ")?.Set(bot); fi.LookupParameter("Ширина полки")?.Set(w * RN_M);
        var an = fi as AnnotationSymbol; if (an == null) return false; an.addLeader(); d.Regenerate(); var lds = an.GetLeaders(); if (lds.Count == 0) return false;
        var l = lds[0]; l.End = end; XYZ R = v.RightDirection; double wm = w * RN_M * v.Scale;
        XYZ se = cp + R * ((end - cp).DotProduct(R) > 0 ? wm / 2 : -wm / 2); l.Elbow = se + (end - se).Normalize() * (1.0 * RN_M * v.Scale); nLd++;
        var dl = end - se; double dxp = dl.DotProduct(R) * ((end - cp).DotProduct(R) > 0 ? 1 : -1), dyp = Math.Abs(dl.DotProduct(v.UpDirection)); double ang = Math.Atan2(dyp, Math.Abs(dxp)) * 180 / Math.PI, len = dl.GetLength() / RN_M / v.Scale;
        if (dxp < 0 || ang < 25 || ang > 65 || len < 6 || len > 40) { sb.AppendLine("  leader «" + c.Name + "» «" + top + "»: угол " + Math.Round(ang) + "°, " + Math.Round(len) + " мм" + (dxp < 0 ? ", стрелка полка астында" : "")); nWarn++; }
        return true;
    }
    class Grp { public string Key, Top, Bot = ""; public bool Plain, Frame; public List<RnSh> Sh = new List<RnSh>(); }
    public void AutoLeaders(RnV c)
    {
        var gs = new Dictionary<string, Grp>();
        foreach (var s in c.Own) { if (s.P == null) continue; string t, b, k; bool pl; if (!RnLabel(s.P, out t, out b, out k, out pl)) continue; Grp g; if (!gs.TryGetValue(k, out g)) { g = new Grp { Key = k, Top = t, Bot = b, Plain = pl }; gs[k] = g; } g.Sh.Add(s); }
        foreach (var s in c.Fr) { if (s.Mark == "" || s.Hull.Count < 2) continue; string k = "F" + s.Mark; Grp g; if (!gs.TryGetValue(k, out g)) { g = new Grp { Key = k, Top = s.Mark, Frame = true }; string nt; if (c.S.FrameNote.TryGetValue(s.Mark, out nt)) g.Bot = nt; gs[k] = g; } g.Sh.Add(s); }
        double cuC = (c.U0 + c.U1) / 2, cvC = (c.V0 + c.V1) / 2;
        var all = c.Own.Concat(c.Thin).Concat(c.Fr).ToList();
        foreach (var g in gs.Values.OrderBy(x => x.Plain ? 1 : 0).ThenByDescending(x => x.Sh.Max(q => q.Area)))
        {
            var prim = g.Sh.OrderByDescending(q => q.Area).First(); var targets = new List<RnSh> { prim };
            if (!g.Plain && !g.Frame && g.Sh.Count >= 2) { var far = g.Sh.OrderByDescending(q => (q.Cu - prim.Cu) * (q.Cu - prim.Cu) + (q.Cv - prim.Cv) * (q.Cv - prim.Cv)).First(); if (Math.Sqrt((far.Cu - prim.Cu) * (far.Cu - prim.Cu) + (far.Cv - prim.Cv) * (far.Cv - prim.Cv)) > 400) targets.Add(far); }
            foreach (var tg in targets) if (!PlaceLeader(c, g, tg, all, cuC, cvC)) { sb.AppendLine("  WARN leader орны табылмады: «" + c.Name + "» «" + g.Top + "»"); nWarn++; }
        }
    }
    bool PlaceLeader(RnV c, Grp g, RnSh sh, List<RnSh> all, double cuC, double cvC)
    {
        var cand = new List<double[]>();   // tu, tv, nx, ny, score
        if (g.Plain) { double dx = sh.Cu - cuC, dy = sh.Cv - cvC, L = Math.Max(1, Math.Sqrt(dx * dx + dy * dy)); cand.Add(new[] { sh.Cu, sh.Cv, dx / L, dy / L, 0 }); }
        else
        {
            var h = sh.Hull; for (int i = 0; i < h.Count; i++)
            {
                var a = h[i]; var b = h[(i + 1) % h.Count]; double ex = b[0] - a[0], ey = b[1] - a[1], len = Math.Sqrt(ex * ex + ey * ey); if (len < 25) continue; double nx = ey / len, ny = -ex / len;
                foreach (double t in new[] { 0.5, 0.3, 0.7 })
                {
                    double px = a[0] + ex * t, py = a[1] + ey * t;
                    if (sh.Frame && (px < c.U0 + 4 || px > c.U1 - 4 || py < c.V0 + 4 || py > c.V1 - 4)) continue;     // кадр шекарасы — нақты қыр емес
                    double dmin = 80; foreach (var o in all) { if (g.Sh.Contains(o)) continue; if (RnInPoly(px, py, o.Hull)) { dmin = 0; break; } dmin = Math.Min(dmin, RnDistPtPoly(px, py, o.Hull)); }
                    if (dmin < 6) continue;   // басқа бөлшектің сызығымен түйіскен нүктеге қойылмайды (§4)
                    cand.Add(new[] { px, py, nx, ny, dmin + (len >= 60 ? 10 : 0) + (nx * (px - cuC) + ny * (py - cvC) > 0 ? 15 : 0) });
                }
            }
            cand = cand.OrderByDescending(x => x[4]).Take(8).ToList();
            if (cand.Count == 0) cand.Add(new[] { sh.U1, sh.Cv, 1, 0, 0 });
        }
        double w = Math.Max(8, Math.Max(g.Top.Length, g.Bot.Length) * 1.6 + 3) * RN_SC, hm = 70;
        double bestCost = 1e18; double[] best = null; int idx = 0;
        double[] Ls = { 120, 160, 210, 270, 330 }, angs = { 45, 35, 55, 40, 50, 60, 30 };
        foreach (var cd in cand)
        {
            double tu = cd[0], tv = cd[1], nx = cd[2], ny = cd[3];
            var sxs = Math.Abs(nx) > 0.25 ? new[] { Math.Sign(nx), -Math.Sign(nx) } : new[] { (tu - cuC) >= 0 ? 1 : -1, (tu - cuC) >= 0 ? -1 : 1 };
            var sys = Math.Abs(ny) > 0.25 ? new[] { Math.Sign(ny), -Math.Sign(ny) } : new[] { (tv - cvC) >= 0 ? 1 : -1, (tv - cvC) >= 0 ? -1 : 1 };
            foreach (double Lk in Ls) foreach (double ang in angs) foreach (int sx in sxs) foreach (int sy in sys)
            {
                idx++; double rad = ang * Math.PI / 180; double eu = tu + sx * Lk * Math.Cos(rad), ev = tv + sy * Lk * Math.Sin(rad); double cu = eu + sx * w / 2, cv = ev;
                var box = new[] { cu - w / 2, cv - hm / 2, cu + w / 2, cv + hm / 2 };
                bool bad = false; foreach (var b in c.Boxes) if (RnRectRect(b, box, 20)) { bad = true; break; }
                if (bad) continue;
                foreach (var s2 in c.Segs) { if (RnSegRect(s2[0], s2[1], s2[2], s2[3], new[] { box[0] - 10, box[1] - 10, box[2] + 10, box[3] + 10 })) { bad = true; break; } if (RnSegSeg(tu, tv, eu, ev, s2[0], s2[1], s2[2], s2[3])) { bad = true; break; } }
                if (bad) continue;
                double cost = idx; foreach (var o in all) { if (RnPolyRect(o.Hull, box)) cost += g.Sh.Contains(o) ? 1500 : 1000; else if (!g.Sh.Contains(o) && RnDistPtPoly(tu, tv, o.Hull) > 3 && RnSegPoly(tu, tv, eu, ev, o.Hull)) cost += 150; }
                if (cost < bestCost) { bestCost = cost; best = new[] { tu, tv, cu, cv, eu, ev, box[0], box[1], box[2], box[3] }; if (cost < 60) goto done; }
            }
        }
    done:
        if (best == null) return false;
        if (!LD(c, best[0], best[1], best[2], best[3], g.Top, g.Bot, g.Plain)) return false;
        c.AddBox(new[] { best[6], best[7], best[8], best[9] }); c.AddSeg(best[0], best[1], best[4], best[5]);
        if (bestCost >= 1000) { sb.AppendLine("  note leader «" + c.Name + "» «" + g.Top + "»: бос орын жетпеді — полка бөлшек үстінде (§5 рұқсат)"); }
        return true;
    }
    // ----- обрыв: каркас элементі кадр шекарасында үзілген жерде
    public void AutoBreaks(RnV c)
    {
        foreach (var s in c.Fr)
        {
            if (s.Hull.Count < 3) continue;
            for (int side = 0; side < 4; side++)
            {
                double bnd = side == 0 ? c.V0 : side == 1 ? c.V1 : side == 2 ? c.U0 : c.U1; bool horiz = side < 2; var on = new List<double>();
                foreach (var p in s.Hull) { double q = horiz ? p[1] : p[0]; if (Math.Abs(q - bnd) < 1.5) on.Add(horiz ? p[0] : p[1]); }
                if (on.Count < 2) continue; double a = on.Min(), b = on.Max(); if (b - a < 20) continue;
                double mid = (a + b) / 2, lenP = (b - a) / RN_SC + 6; var p0 = horiz ? Pw(c, mid, bnd) : Pw(c, bnd, mid);
                try { var fb = d.Create.NewFamilyInstance(p0, sObr, c.V); fb.LookupParameter("Длина")?.Set(lenP * RN_M); if (!horiz) ElementTransformUtils.RotateElement(d, fb.Id, Line.CreateBound(p0, p0 + c.V.ViewDirection), Math.PI / 2); nB++; }
                catch (Exception ex) { sb.AppendLine("  break ERR «" + c.Name + "» " + ex.Message.Split('\n')[0]); nWarn++; }
            }
        }
    }
    // ----- шов белгілері: заводской ||| / монтажный ××× (В113 NS.WELDS)
    public void Welds(RnV c)
    {
        var v = c.V; double wd = c.S.WDep; var placed = new List<XYZ[]>();
        foreach (var wds in c.Welds)
        {
            bool field = wds.Title.Contains("монтаж");
            foreach (var so in RnSolids(wds.Ds))
            {
                Edge lon = null; double ll = 0; foreach (Edge ed in so.Edges) { var cu = ed.AsCurve(); if (cu.Length > ll) { ll = cu.Length; lon = ed; } } if (lon == null) continue;
                var c0 = lon.AsCurve(); var dw = (c0.GetEndPoint(1) - c0.GetEndPoint(0)).Normalize(); if (Math.Abs(dw.DotProduct(v.ViewDirection)) > 0.35) continue;
                var vp = new List<XYZ>(); foreach (Edge ed in so.Edges) foreach (var p in ed.Tessellate()) vp.Add(Lc(c, p));
                double cu0 = vp.Average(p => p.X), cv0 = vp.Average(p => p.Y), cz = vp.Average(p => p.Z);
                if (cz < -2 || cz > wd || cu0 < c.U0 || cu0 > c.U1 || cv0 < c.V0 || cv0 > c.V1) continue;
                var la = Lc(c, c0.GetEndPoint(0)); var lb = Lc(c, c0.GetEndPoint(1)); var d2 = new XYZ(lb.X - la.X, lb.Y - la.Y, 0); if (d2.GetLength() < 1e-6) continue; d2 = d2.Normalize(); var n2 = new XYZ(-d2.Y, d2.X, 0);
                var cen = new XYZ(cu0, cv0, 0); double t0 = vp.Min(p => (new XYZ(p.X, p.Y, 0) - cen).DotProduct(d2)), t1 = vp.Max(p => (new XYZ(p.X, p.Y, 0) - cen).DotProduct(d2));
                double side = vp.Average(p => (new XYZ(p.X, p.Y, 0) - cen).DotProduct(n2)) >= 0 ? 1 : -1;
                var a = cen + d2 * t0 - n2 * 7.5 * side; var b = cen + d2 * t1 - n2 * 7.5 * side; if ((b - a).GetLength() < 30) continue;
                if (placed.Any(q => { var qd = (q[1] - q[0]).Normalize(); if (Math.Abs(qd.DotProduct(d2)) < 0.98) return false; if (Math.Abs((a - q[0]).DotProduct(new XYZ(-qd.Y, qd.X, 0))) > 12) return false; double s0 = (a - q[0]).DotProduct(qd), s1 = (b - q[0]).DotProduct(qd), L0 = (q[1] - q[0]).GetLength(); return Math.Max(s0, s1) > 5 && Math.Min(s0, s1) < L0 - 5; })) continue;
                placed.Add(new[] { a, b }); var pa = Pw(c, a.X, a.Y);
                try { var fi = d.Create.NewFamilyInstance(pa, field ? sWm : sWf, v); fi.LookupParameter("Длина")?.Set((b - a).GetLength() / RN_SC * RN_M);
                    var ang = Math.Atan2((Pw(c, b.X, b.Y) - pa).DotProduct(v.UpDirection), (Pw(c, b.X, b.Y) - pa).DotProduct(v.RightDirection)); if (Math.Abs(ang) > 1e-6) ElementTransformUtils.RotateElement(d, fi.Id, Line.CreateBound(pa, pa + v.ViewDirection), ang); nW++;
                    c.AddBox(new[] { Math.Min(a.X, b.X) - 15, Math.Min(a.Y, b.Y) - 15, Math.Max(a.X, b.X) + 15, Math.Max(a.Y, b.Y) + 15 }); }
                catch (Exception ex) { sb.AppendLine("  weld ERR «" + c.Name + "» " + ex.Message.Split('\n')[0]); nWarn++; }
            }
        }
    }
    // ----- отметка (спот): бөлшектің жоғарғы беті
    public void Spots(RnV c)
    {
        if (spotT == null || c.S.SpotTop == null) return;
        foreach (var pat in c.S.SpotTop)
        {
            var p = c.Parts.FirstOrDefault(x => x.Title.IndexOf(pat, StringComparison.OrdinalIgnoreCase) >= 0); if (p == null) continue; var sh = c.Own.FirstOrDefault(x => x.P == p); if (sh == null) continue;
            var wp = new XYZ((p.BB[0] + p.BB[3]) / 2, (p.BB[1] + p.BB[4]) / 2, p.BB[5]); var o2 = new Options { ComputeReferences = true, View = c.V }; Reference rf = null; XYZ fp = null; double best = 1e9;
            foreach (var g in p.Ds.get_Geometry(o2)) { var so = g as Solid; if (so == null || so.Faces.Size == 0) continue;
                foreach (Face f in so.Faces) { var pf = f as PlanarFace; if (pf == null || pf.FaceNormal.Z < 0.95 || f.Reference == null) continue; var pr = f.Project(wp * RN_M); if (pr == null) continue; double dd = pr.XYZPoint.DistanceTo(wp * RN_M); if (dd < best) { best = dd; fp = pr.XYZPoint; rf = f.Reference; } } }
            if (rf == null || best > 60 * RN_M) { sb.AppendLine("  spot: беті табылмады «" + c.Name + "» " + pat); continue; }
            var lp = Lc(c, fp); double bu = (c.Env[0]) - 80, bv = lp.Y + 60; var bend = Pw(c, bu, bv);
            try { var sp = d.Create.NewSpotElevation(c.V, rf, fp, bend, bend, fp, true); sp.ChangeTypeId(spotT.Id); nSp++; c.AddBox(new[] { bu - 450, bv - 30, bu + 20, bv + 30 }); }
            catch (Exception ex) { sb.AppendLine("  spot ERR «" + c.Name + "» " + ex.Message.Split('\n')[0]); nWarn++; }
        }
    }
    public void Circle(RnV c, string num)
    {
        double u = (c.U0 + c.U1) / 2, v = c.Env[3] + 110;
        try { var fc = d.Create.NewFamilyInstance(Pw(c, u, v), sKrug, c.V); (fc.LookupParameter("Номер") ?? fc.LookupParameter("Номер узла"))?.Set(num); c.AddBox(new[] { u - 80, v - 80, u + 80, v + 80 }); }
        catch (Exception ex) { sb.AppendLine("  circle ERR «" + c.Name + "» " + ex.Message.Split('\n')[0]); nWarn++; }
    }
    // ======================= 3D =======================
    public View3D V3D(RnT3 t)
    {
        var keys = t.Keys ?? S.Keys; string loc = t.Loc ?? S.Loc; var ps = All.Where(p => !p.RC && keys.Contains(p.Key) && p.Loc == loc).ToList(); if (ps.Count == 0) throw new Exception("3D «" + t.Name + "»: бөлшек жоқ");
        double g = 200; var mn = new XYZ(ps.Min(p => p.BB[0]) - g, ps.Min(p => p.BB[1]) - g, ps.Min(p => p.BB[2]) - g); var mx = new XYZ(ps.Max(p => p.BB[3]) + g, ps.Max(p => p.BB[4]) + g, ps.Max(p => p.BB[5]) + g);
        var fr = RnFrame(loc); var fw0 = new XYZ(t.Fw[0], t.Fw[1] * fr.Sy, t.Fw[2]);
        var w3 = View3D.CreateIsometric(d, vft3.Id); w3.Name = t.Name; w3.DetailLevel = ViewDetailLevel.Fine; w3.DisplayStyle = DisplayStyle.ShadingWithEdges; w3.CropBoxActive = false;
        w3.SetSectionBox(new BoundingBoxXYZ { Min = mn * RN_M, Max = mx * RN_M });
        var f = fw0.Normalize(); var rt = f.CrossProduct(XYZ.BasisZ).Normalize(); var upv = rt.CrossProduct(f).Normalize();
        w3.SetOrientation(new ViewOrientation3D((mn + mx) / 2 * RN_M - f * 50, upv, f));
        foreach (var bic in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_Grids, BuiltInCategory.OST_Sections, BuiltInCategory.OST_SectionBox, BuiltInCategory.OST_Floors, BuiltInCategory.OST_StructuralFoundation, BuiltInCategory.OST_Elev, BuiltInCategory.OST_CLines, BuiltInCategory.OST_Viewers })
        { var c = Category.GetCategory(d, bic); if (c != null && w3.CanCategoryBeHidden(c.Id)) w3.SetCategoryHidden(c.Id, true); }
        var own = new HashSet<long>(ps.Select(p => p.Id)); var hide = new List<ElementId>();
        foreach (var p in All) { if (own.Contains(p.Id)) continue; bool inB = !(p.BB[3] < mn.X || p.BB[0] > mx.X || p.BB[4] < mn.Y || p.BB[1] > mx.Y || p.BB[5] < mn.Z || p.BB[2] > mx.Z); if (inB && p.Ds.CanBeHidden(w3)) hide.Add(p.Ds.Id); }
        foreach (var id in hide) { try { w3.HideElements(new List<ElementId> { id }); } catch { } }
        var black = new Color(0, 0, 0);
        foreach (var bic in new[] { BuiltInCategory.OST_StructuralFraming, BuiltInCategory.OST_StructuralColumns, BuiltInCategory.OST_StructConnections, BuiltInCategory.OST_StructConnectionBolts, BuiltInCategory.OST_StructConnectionWelds })
        { var o = new OverrideGraphicSettings(); o.SetProjectionLineColor(black); o.SetProjectionLineWeight(1); try { w3.SetCategoryOverrides(new ElementId(bic), o); } catch { } }
        w3.Scale = (int)RN_SC; try { w3.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(""); } catch { } V3.Add(w3); return w3;
    }
    // ======================= парақ: орналасу (А3 → А2) =======================
    class It { public RnV C; public double W, H, EL, EB, CW, CH, ET, X, Y; }
    static bool Pack(List<It> items, double ax0, double ay0, double ax1, double ay1)
    {
        double gap = 12, x = ax0, y = ay1, rowH = 0;
        foreach (var it in items) { if (it.W > ax1 - ax0 + 0.01) return false; if (x + it.W > ax1 + 0.01) { y -= rowH + gap; x = ax0; rowH = 0; } if (y - it.H < ay0 - 0.01) return false; it.X = x; it.Y = y - it.H; x += it.W + gap; rowH = Math.Max(rowH, it.H); }
        return true;
    }
    public void BuildSheet()
    {
        int nl = 0; foreach (var line in (S.Notes ?? "").Split('\n')) nl += Math.Max(1, (int)Math.Ceiling(line.Length / 100.0)); double notesH = (S.Notes ?? "") == "" ? 0 : nl * 4.0 + 3;
        var items = new List<It>(); foreach (var c in Vs) { var e = c.Env; bool tit = c.Title != ""; var it = new It { C = c, CW = (c.U1 - c.U0) / RN_SC, CH = (c.V1 - c.V0) / RN_SC, EL = (c.U0 - e[0]) / RN_SC, EB = (c.V0 - e[1]) / RN_SC, ET = (e[3] - c.V1) / RN_SC };
            it.W = (e[2] - e[0]) / RN_SC; it.H = (e[3] - e[1]) / RN_SC + (tit ? 9 : 0); items.Add(it); }
        items = items.Take(1).Concat(items.Skip(1).OrderByDescending(x => x.H)).ToList();
        string tb = null; double SW = 0, SH = 0; double rc = 185 + 6;
        foreach (var cand in new[] { new object[] { "А3", 420.0, 297.0 }, new object[] { "А2", 594.0, 420.0 } })
        { if (S.TBForce != null && S.TBForce != (string)cand[0]) continue; double w = (double)cand[1], h = (double)cand[2]; bool ok = Pack(items, 22, 7, w - 5 - rc, h - 7); if (ok) { tb = (string)cand[0]; SW = w; SH = h; break; } }
        if (tb == null) throw new Exception("«" + S.Name + "»: А2-ге де сыймайды (А1 жоқ) — парақты бөл (бір узелге бір парақ; көріністер мөлшері: " + string.Join(", ", items.Select(i => RnF(i.W) + "x" + RnF(i.H))) + ")");
        var tbs = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().Cast<FamilySymbol>().First(x => x.Name == tb);
        sheet = ViewSheet.Create(d, tbs.Id); sheet.SheetNumber = S.SN; sheet.Name = S.Name; d.Regenerate();
        tbb = new FilteredElementCollector(d, sheet.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).FirstElement().get_BoundingBox(sheet);
        double aw = (tbb.Max.X - tbb.Min.X) / RN_M, ah = (tbb.Max.Y - tbb.Min.Y) / RN_M; sb.AppendLine("sheet " + S.SN + " " + tb + " (" + RnF(aw) + " x " + RnF(ah) + "; күтілген " + SW + " x " + SH + ")" + (Math.Abs(aw - SW) > 2 || Math.Abs(ah - SH) > 2 ? "  WARN: рамка өлшемі күткеннен өзгеше — орналасуды тексер" : ""));
        foreach (var it in items)
        {
            var c = it.C; var v = c.V; if (c.Title != "") v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(c.Title);
            var vp = Viewport.Create(d, sheet.Id, v.Id, (tbb.Min + tbb.Max) / 2); vp.ChangeTypeId(c.Title == "" ? vpNone.Id : vpTitle.Id); vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(c.Num); d.Regenerate();
            var cb2 = v.CropBox; double cw = (cb2.Max.X - cb2.Min.X) / v.Scale, chh = (cb2.Max.Y - cb2.Min.Y) / v.Scale; var T = vp.GetProjectionToSheetTransform();
            var want = tbb.Min + new XYZ(it.X + it.EL + it.CW / 2, it.Y + it.EB + it.CH / 2, 0) * RN_M;
            vp.SetBoxCenter(vp.GetBoxCenter() + (want - (T.Origin + new XYZ(cb2.Min.X / v.Scale + cw / 2, cb2.Min.Y / v.Scale + chh / 2, 0)))); d.Regenerate();
            if (c.Title != "") { T = vp.GetProjectionToSheetTransform(); var ob = vp.GetBoxOutline(); double top = it.ET + 2;
                vp.LabelOffset = new XYZ(T.Origin.X + cb2.Min.X / v.Scale - ob.MinimumPoint.X + cw / 2 - 16 * RN_M, T.Origin.Y + cb2.Min.Y / v.Scale - ob.MinimumPoint.Y + chh + top * RN_M, 0); vp.LabelLineLength = 0; d.Regenerate();
                try { var lo = vp.GetLabelOutline(); double cxv = T.Origin.X + cb2.Min.X / v.Scale + cw / 2; vp.LabelOffset = vp.LabelOffset + new XYZ(cxv - (lo.MinimumPoint.X + lo.MaximumPoint.X) / 2, 0, 0); } catch { } }
        }
        // 3D: оң баған, штамп пен ескертпенің үстінде (кіші масштаб = үлкен сурет, 1:5 … 1:25)
        if (V3.Count > 0)
        {
            double x0 = SW - 5 - 185, x1 = SW - 5, y0 = 62 + notesH + 4, y1 = SH - 7; var boxes = new List<double[]>(); int n3 = V3.Count;
            if (n3 == 1) boxes.Add(new[] { x0, x1, y0, y1 }); else { double ww = (185 - 4.0) / 2; for (int k = 0; k < n3; k++) boxes.Add(new[] { x0 + (k % 2) * (ww + 4), x0 + (k % 2) * (ww + 4) + ww, y0, y1 }); }
            var vps = new List<Viewport>(); for (int k = 0; k < n3; k++) { var vp3 = Viewport.Create(d, sheet.Id, V3[k].Id, (tbb.Min + tbb.Max) / 2); vp3.ChangeTypeId(vpNone.Id); vp3.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set("3D" + (k + 1)); vps.Add(vp3); }
            foreach (var sc in new[] { 5, 6, 7, 8, 9, 10, 12, 15, 20, 25 }) { foreach (var w3 in V3) w3.Scale = sc; d.Regenerate(); bool fit = true;
                for (int k = 0; k < n3; k++) { var ob = vps[k].GetBoxOutline(); var bx = boxes[k]; if ((ob.MaximumPoint.X - ob.MinimumPoint.X) / RN_M > bx[1] - bx[0] || (ob.MaximumPoint.Y - ob.MinimumPoint.Y) / RN_M > bx[3] - bx[2]) fit = false; }
                if (fit) break; }
            for (int k = 0; k < n3; k++) { var ob2 = vps[k].GetBoxOutline(); var bx = boxes[k]; var tgt = tbb.Min + new XYZ((bx[0] + bx[1]) / 2, (bx[2] + bx[3]) / 2, 0) * RN_M; vps[k].SetBoxCenter(vps[k].GetBoxCenter() + (tgt - (ob2.MinimumPoint + ob2.MaximumPoint) / 2));
                sb.AppendLine("3D" + (k + 1) + " 1:" + V3[k].Scale + " " + Math.Round((ob2.MaximumPoint.X - ob2.MinimumPoint.X) / RN_M) + " x " + Math.Round((ob2.MaximumPoint.Y - ob2.MinimumPoint.Y) / RN_M) + " мм"); }
        }
        if (!string.IsNullOrEmpty(S.Notes)) TextNote.Create(d, sheet.Id, tbb.Min + new XYZ((SW - 5 - 185) * RN_M, (62 + notesH) * RN_M, 0), 185 * RN_M, S.Notes, new TextNoteOptions(txtT.Id) { HorizontalAlignment = HorizontalTextAlignment.Left, VerticalAlignment = VerticalTextAlignment.Top });
        foreach (var it in items) { double a = it.X, b = it.Y, a2 = it.X + it.W, b2 = it.Y + it.H; if (a < 20 || b < 5 || a2 > SW - 5 || b2 > SH - 5) { sb.AppendLine("  OUT OF FRAME: " + it.C.Name); nWarn++; } }
    }
    public void Png(string path)
    {
        var o = new ImageExportOptions { FilePath = path, ExportRange = ExportRange.SetOfViews, ZoomType = ZoomFitType.FitToPage, PixelSize = 7000, ImageResolution = ImageResolution.DPI_300, HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, FitDirection = FitDirectionType.Horizontal };
        o.SetViewsAndSheets(new List<ElementId> { sheet.Id }); d.ExportImage(o);
    }
    // ======================= драйвер =======================
    public void Run()
    {
        if (S.Keys == null || S.Loc == null) throw new Exception("RnSheet.Keys/Loc берілмеген");
        int k = 0; foreach (var vs in S.Views) { if (!vs.Main) { k++; vs.Name = vs.Name.Replace("{n}", k.ToString()); vs.Title = vs.Title.Replace("{n}", k.ToString()); vs.Num = vs.Num.Replace("{n}", k.ToString()); } AllNames.Add(vs.Name); }
        foreach (var t3 in S.D3) AllNames.Add(t3.Name);
        Clear();
        for (int i = 0; i < S.Views.Count; i++) { Prepare(S.Views[i], i); }
        foreach (var g in Vs.Select(x => x.S.Group).Distinct().ToList()) { var host = Vs.FirstOrDefault(x => x.S.Group == g && x.S.Main); if (host == null) continue; ExpandHost(host, Vs.Where(x => x.S.Group == g && !x.S.Main).ToList()); }
        foreach (var c in Vs) { var host = Vs.FirstOrDefault(x => x.S.Group == c.S.Group && x.S.Main); bool mir = !c.S.Main && host != null && WantMirror(c, host); Create(c, mir); }
        d.Regenerate();
        foreach (var c in Vs)
        {
            var secs = c.S.Main ? Vs.Where(x => x.S.Group == c.S.Group && !x.S.Main).ToList() : new List<RnV>();
            AddFrame(c); Dress(c, secs.Select(x => x.Name).ToArray());
            if (c.S.Main) foreach (var s in secs) { var m = MarkSeg(s, c); c.AddSeg(m[0], m[1], m[2], m[3]); c.AddBox(new[] { Math.Min(m[0], m[2]) - 160, Math.Min(m[1], m[3]) - 160, Math.Min(m[0], m[2]) + 40, Math.Min(m[1], m[3]) + 40 }); c.AddBox(new[] { Math.Max(m[0], m[2]) - 40, Math.Max(m[1], m[3]) - 40, Math.Max(m[0], m[2]) + 160, Math.Max(m[1], m[3]) + 160 }); }
        }
        d.Regenerate();
        foreach (var c in Vs) { AutoDims(c); Welds(c); AutoBreaks(c); Spots(c); AutoLeaders(c); if (c.S.Main && !string.IsNullOrEmpty(c.S.Circle)) Circle(c, c.S.Circle); }
        foreach (var t3 in S.D3) V3D(t3);
        d.Regenerate(); BuildSheet();
        sb.AppendLine("dims " + nDim + " leaders " + nLd + " welds " + nW + " spots " + nSp + " breaks " + nB + " C26 " + nBad + " warnings " + nWarn);
        if (nBad > 0) throw new Exception("C26 = " + nBad + " ≠ 0 — парақ шығарылмайды (КМ_стандарт 03 §7): көріністе бөтен/тереңдіктен тыс дене бар");
    }
}
static string RnRunSheets(Document d, List<RnSheet> sheets)
{
    var sb = new StringBuilder();
    if (d == null || d.PathName == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT: белсенді құжат РМЦ-КМ.rvt емес: " + (d == null ? "null" : d.PathName);
    foreach (var S in sheets)
    {
        try
        {
            RnB B = null;
            using (var t = new Transaction(d, "РМЦ: " + S.Name))
            {
                t.Start(); var fo = t.GetFailureHandlingOptions(); fo.SetFailuresPreprocessor(new RnSwallow()); t.SetFailureHandlingOptions(fo);
                B = new RnB(d, sb, S); B.Run(); t.Commit();
            }
            if (S.Png != null && B != null) { try { B.Png(S.Png); sb.AppendLine("png " + S.Png); } catch (Exception ex) { sb.AppendLine("png ERR " + ex.Message.Split('\n')[0]); } }
            d.Save(); sb.AppendLine("saved: " + S.Name);
        }
        catch (Exception ex) { sb.AppendLine("ERR «" + S.Name + "»: " + ex.Message + "   (транзакция кері қайтарылды, құжатқа ештеңе жазылмады)"); }
    }
    return sb.ToString();
}
static void _libEnd() {
