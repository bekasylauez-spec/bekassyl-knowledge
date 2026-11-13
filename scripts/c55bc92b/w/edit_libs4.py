import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
def edit(p, reps):
    s = io.open(A + p, encoding='utf-8').read()
    for old, new in reps:
        assert s.count(old) == 1, (p, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(A + p, 'w', encoding='utf-8', newline='').write(s)

# node lib: Clean verifies the Difference actually removed ~ov0; else shifted-target retry
edit('rmc_node_lib.cs', [
 ('bool shd, fld; var r = DiffRetry(s, o.S, out shd, out fld); if (fld) c.CleanFail++; else if (r != null) s = r;',
  '''bool shd, fld; var r = DiffRetry(s, o.S, out shd, out fld);
        if (!fld && r != null && vs0 && ov0 > 1 && Cu(s.Volume - r.Volume) < 0.5 * ov0) { r = DiffShiftOnly(s, o.S, 0.5 * ov0); if (r == null) fld = true; }      // q20: булев ескертусіз өзгермеген солид қайтарды (бір жазықтықтағы беттер) — ығыстырумен қайталау
        if (fld) c.CleanFail++; else if (r != null) s = r;'''),
 ('static Solid DiffRetry(Solid s, Solid o, out bool shifted, out bool fail) {',
  '''static Solid DiffShiftOnly(Solid s, Solid o, double minRem) {
    foreach (double tmm in new[] { 0.05, 0.1, 0.2 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4), new XYZ(-0.3, -0.5, -0.8) }) {
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(ShiftS(s, dv.Normalize() * (tmm * MM)), o, BooleanOperationsType.Difference); if (r != null && r.Volume > 1e-12 && Cu(s.Volume - r.Volume) >= minRem) return r; } catch { } }
    return null; }
static Solid DiffRetry(Solid s, Solid o, out bool shifted, out bool fail) {'''),
])
# misc lib
edit('rmc_misc_lib.cs', [
 ('bool sh, fl; var r = QDiffRetry(s, o.S, out sh, out fl); if (fl) c.CleanFail++; else if (r != null) s = r;',
  '''bool sh, fl; var r = QDiffRetry(s, o.S, out sh, out fl);
        if (!fl && r != null && vs0 && ov0 > 1 && QCu(s.Volume - r.Volume) < 0.5 * ov0) { r = QDiffShiftOnly(s, o.S, 0.5 * ov0); if (r == null) fl = true; }      // q20: булев ескертусіз өзгермеген солид қайтарды (бір жазықтықтағы беттер) — ығыстырумен қайталау
        if (fl) c.CleanFail++; else if (r != null) s = r;'''),
 ('static Solid QDiffRetry(Solid s, Solid o, out bool shifted, out bool fail) {',
  '''static Solid QDiffShiftOnly(Solid s, Solid o, double minRem) {
    foreach (double tmm in new[] { 0.05, 0.1, 0.2 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4), new XYZ(-0.3, -0.5, -0.8) }) {
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(QShiftS(s, dv.Normalize() * (tmm * QMM)), o, BooleanOperationsType.Difference); if (r != null && r.Volume > 1e-12 && QCu(s.Volume - r.Volume) >= minRem) return r; } catch { } }
    return null; }
static Solid QDiffRetry(Solid s, Solid o, out bool shifted, out bool fail) {'''),
])
# brace lib: Diff residual check with verified InterX
edit('rmc_brace_lib.cs', [
 ('if (direct) { bool v0, f0; double o0 = InterX(r0, b, out v0, out f0); if (f0 || o0 <= 1) return r0; }', 'if (direct) { bool v0, f0; double o0 = InterXV(r0, b, out v0, out f0); if (f0 || o0 <= 1) return r0; }'),
 ('bool v1, f1; double ov = InterX(r, b, out v1, out f1); if (f1) ov = 1e8;', 'bool v1, f1; double ov = InterXV(r, b, out v1, out f1); if (f1) ov = 1e8;'),
])
print('ok')
