import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
def edit(p, reps):
    s = io.open(A + p, encoding='utf-8').read()
    for old, new in reps:
        assert s.count(old) == 1, (p, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(A + p, 'w', encoding='utf-8', newline='').write(s)

HEAL = '''
// q20: булев нәтижесі DS-ке жарамсыз болса «емдеу»: жазық түзу қырлы солидтің төбелерін 0,25 мм ішінде біріктіріп, бүкіл беттерді үшбұрышқа бөліп TessellatedShapeBuilder-мен қайта салу; көлем ≤ 2 % ауытқуы және DS жарамдылығы тексеріледі
static Solid {H}(Document d, Solid s) {
    try {
        var polys = new List<List<XYZ>>();
        foreach (Face f in s.Faces) { var pf = f as PlanarFace; if (pf == null) return null; var lps = pf.GetEdgesAsCurveLoops(); if (lps.Count != 1) return null; var pts = new List<XYZ>(); foreach (Curve c in lps[0]) { if (!(c is Line)) return null; pts.Add(c.GetEndPoint(0)); } polys.Add(pts); }
        var reps = new List<XYZ>(); Func<XYZ, XYZ> snap = p => { foreach (var r in reps) if (r.DistanceTo(p) < 0.25 / 304.8) return r; reps.Add(p); return p; };
        var tris = new List<List<XYZ>>();
        foreach (var pts in polys) {
            var q = new List<XYZ>(); foreach (var p in pts) { var sp = snap(p); if (q.Count == 0 || !ReferenceEquals(q[q.Count - 1], sp)) q.Add(sp); }
            while (q.Count > 1 && ReferenceEquals(q[0], q[q.Count - 1])) q.RemoveAt(q.Count - 1);
            if (q.Count < 3) continue;
            for (int i = 1; i + 1 < q.Count; i++) { var t = new List<XYZ> { q[0], q[i], q[i + 1] }; if (ReferenceEquals(t[0], t[1]) || ReferenceEquals(t[1], t[2]) || ReferenceEquals(t[0], t[2])) continue; if ((t[1] - t[0]).CrossProduct(t[2] - t[0]).GetLength() < 1e-9) continue; tris.Add(t); }
        }
        foreach (bool rev in new[] { false, true }) {
            var tsb = new TessellatedShapeBuilder(); tsb.OpenConnectedFaceSet(true);
            foreach (var t in tris) { var q = new List<XYZ>(t); if (rev) q.Reverse(); tsb.AddFace(new TessellatedFace(q, s.Faces.get_Item(0).MaterialElementId)); }
            tsb.CloseConnectedFaceSet(); tsb.Target = TessellatedShapeBuilderTarget.Solid; tsb.Fallback = TessellatedShapeBuilderFallback.Abort;
            try { tsb.Build(); } catch { continue; }
            var res = tsb.GetBuildResult(); if (res.Outcome != TessellatedShapeBuilderOutcome.Solid) continue;
            foreach (var go in res.GetGeometricalObjects()) { var ns = go as Solid; if (ns != null && ns.Volume > 0 && Math.Abs(ns.Volume - s.Volume) < 0.02 * s.Volume && {V}(d, ns)) return ns; }
        }
    } catch { }
    return null; }
'''

# node lib
edit('rmc_node_lib.cs', [
 ('// кедергілерді кішкентай ығыстырумен кесу; жарамды нәтиже болмаса null', HEAL.replace('{H}', 'HealSolid').replace('{V}', 'VShape') + '// кедергілерді кішкентай ығыстырумен кесу; жарамды нәтиже болмаса null'),
 ('else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }',
  'else { var h = HealSolid(c.D, s2); if (h != null) { s2 = h; c.L.AppendLine("  HEAL «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — төбелер біріктіріліп қайта салынды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } } }'),
])
# misc lib
edit('rmc_misc_lib.cs', [
 ('static Solid QCleanShifted(QCtx c, Solid s) {', HEAL.replace('{H}', 'QHealSolid').replace('{V}', 'QVShape') + 'static Solid QCleanShifted(QCtx c, Solid s) {'),
 ('else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }',
  'else { var h = QHealSolid(c.D, s2); if (h != null) { s2 = h; c.L.AppendLine("  HEAL «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — төбелер біріктіріліп қайта салынды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } } }'),
])
# brace lib (inside static class BL: make method public static)
H2 = HEAL.replace('{H}', 'HealSolid').replace('{V}', 'VShape').replace('static Solid HealSolid', 'public static Solid HealSolid')
edit('rmc_brace_lib.cs', [
 ('    public static Solid CleanShifted(BCtx c, Solid s)', H2 + '    public static Solid CleanShifted(BCtx c, Solid s)'),
 ('else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }',
  'else { var h = HealSolid(c.D, s2); if (h != null) { s2 = h; c.L.AppendLine("  HEAL «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — төбелер біріктіріліп қайта салынды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } } }'),
])
print('ok')
