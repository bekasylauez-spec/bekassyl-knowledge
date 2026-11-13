import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
def edit(p, reps):
    s = io.open(A + p, encoding='utf-8').read()
    for old, new in reps:
        assert s.count(old) == 1, (p, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(A + p, 'w', encoding='utf-8', newline='').write(s)

TPLRAW = '''
// q20: булев Intersect бір бағытты беттесетін (бір жазықтықтағы) беттерде кейде ЕСКЕРТУСІЗ бос нәтиже (null → 0) береді — нағыз қиылысу 100 мм³ болса да.
// Тікелей нәтиже ≤ {THR} мм³ болып, bbox-тар қиылысса (> 1 мм³) — ығыстыру бағасымен қайта тексереді де үлкенін қайтарады (viaShift = true).
static double {NAME}(Solid a, Solid b, out bool viaShift, out bool fail)
{
    double v = {OVL}(a, b, out viaShift, out fail);
    if (viaShift || fail || v > {THR}) return v;
    var ba = {BBX}(a); var bb = {BBX}(b); double ox = Math.Min(ba[3], bb[3]) - Math.Max(ba[0], bb[0]), oy = Math.Min(ba[4], bb[4]) - Math.Max(ba[1], bb[1]), oz = Math.Min(ba[5], bb[5]) - Math.Max(ba[2], bb[2]);
    if (!(ox > 0.05 && oy > 0.05 && oz > 0.05 && ox * oy * oz > 1)) return v;
    var est = new List<double>();
    foreach (double tmm in new[] { 0.1, 0.25, 0.5 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) })
    {
        XYZ sv = dv.Normalize() * (tmm * {MM});
        try {
            var r1 = BooleanOperationsUtils.ExecuteBooleanOperation({SH}(a, sv), b, BooleanOperationsType.Intersect); double v1 = r1 == null ? 0 : {CU}(r1.Volume);
            var r2 = BooleanOperationsUtils.ExecuteBooleanOperation({SH}(a, sv * 2), b, BooleanOperationsType.Intersect); double v2 = r2 == null ? 0 : {CU}(r2.Volume);
            est.Add(Math.Max(0, 2 * v1 - v2));
        } catch { }
    }
    if (est.Count == 0) return v;
    est.Sort(); double m = est[est.Count / 2]; if (m > v) { viaShift = true; return m; }
    return v;
}
'''

def fmt(t, **kw):
    for k, v in kw.items(): t = t.replace('{' + k + '}', v)
    return t
TPL = TPLRAW
# node lib
edit('rmc_node_lib.cs', [
 ('// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді\nstatic bool VShape(',
  fmt(TPL, THR='0.3', NAME='OvlVolV', OVL='OvlVol', BBX='BBox', MM='MM', SH='ShiftS', CU='Cu') + '// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді\nstatic bool VShape('),
 ('double ov0 = OvlVol(s, o.S, out vs0, out fl0);', 'double ov0 = OvlVolV(s, o.S, out vs0, out fl0);'),
])
# misc lib
edit('rmc_misc_lib.cs', [
 ('// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді\nstatic bool QVShape(',
  fmt(TPL, THR='0.3', NAME='QOvlVolV', OVL='QOvlVol', BBX='QBBox', MM='QMM', SH='QShiftS', CU='QCu') + '// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді\nstatic bool QVShape('),
 ('double ov0 = QOvlVol(s, o.S, out vs0, out fl0);', 'double ov0 = QOvlVolV(s, o.S, out vs0, out fl0);'),
])
# brace lib: InterX verified (public static in class BL)
TPLB = TPL.replace('static double {NAME}', 'public static double {NAME}')
edit('rmc_brace_lib.cs', [
 ('    // q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді)\n    public static bool VShape(',
  fmt(TPLB, THR='1', NAME='InterXV', OVL='InterX', BBX='BBox', MM='MM', SH='ShiftS', CU='VolMm3').replace('{CU}(r1.Volume)', 'VolMm3(r1)').replace('VolMm3(r1.Volume)', 'VolMm3(r1)').replace('VolMm3(r2.Volume)', 'VolMm3(r2)') + '    // q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді)\n    public static bool VShape('),
 ('bool vsh0, fl0; double ov = InterX(s, o.S, out vsh0, out fl0); if (fl0) ov = 2; if (ov <= 1) continue;', 'bool vsh0, fl0; double ov = InterXV(s, o.S, out vsh0, out fl0); if (fl0) ov = 2; if (ov <= 1) continue;'),
])
print('ok')
