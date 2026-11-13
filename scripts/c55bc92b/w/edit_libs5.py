import io, re
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
def sub_func(p, name, new):
    s = io.open(A + p, encoding='utf-8').read()
    i = s.index('static Solid ' + name + '(')
    # function ends at first "\n    fail = true; return null; }" after i
    j = s.index('fail = true; return null; }', i) + len('fail = true; return null; }')
    s = s[:i] + new + s[j:]
    io.open(A + p, 'w', encoding='utf-8', newline='').write(s)

TPL = '''static Solid {N}(Solid s, Solid o, out bool shifted, out bool fail) {
    shifted = false; fail = false;
    try { return BooleanOperationsUtils.ExecuteBooleanOperation(s, o, BooleanOperationsType.Difference); } catch { }
    shifted = true; Solid best = null; double bestRes = 1e18;
    // q20: нысана (шов) ығыстырылады — нәтиже кескішпен қалдық қиылысуы ең аз вариант таңдалады (ығысу тірекке енсе қалдық үлкен болады)
    foreach (double tmm in new[] { 0.05, 0.1, 0.2 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4), new XYZ(-0.3, -0.5, -0.8), new XYZ(-1, -0.618, -0.382), new XYZ(0.7, -0.3, -0.9), new XYZ(-0.2, 0.9, -0.4), new XYZ(0.3, 0.5, 0.8) }) {
        try {
            var r = BooleanOperationsUtils.ExecuteBooleanOperation({SH}(s, dv.Normalize() * (tmm * {MM})), o, BooleanOperationsType.Difference); if (r == null || r.Volume < 1e-12) continue;
            double res; try { var ix = BooleanOperationsUtils.ExecuteBooleanOperation(r, o, BooleanOperationsType.Intersect); res = ix == null ? 0 : {CU}(ix.Volume); } catch { res = 1e6; }
            if (res < bestRes) { best = r; bestRes = res; if (res <= 0.5) return r; }
        } catch { } }
    if (best == null) fail = true; return best; }'''
def fmt(t, **kw):
    for k, v in kw.items(): t = t.replace('{' + k + '}', v)
    return t
sub_func('rmc_node_lib.cs', 'DiffRetry', fmt(TPL, N='DiffRetry', SH='ShiftS', MM='MM', CU='Cu'))
sub_func('rmc_misc_lib.cs', 'QDiffRetry', fmt(TPL, N='QDiffRetry', SH='QShiftS', MM='QMM', CU='QCu'))

# brace lib: gap override for tilted cap welds
p = 'rmc_brace_lib.cs'
s = io.open(A + p, encoding='utf-8').read()
s = s.replace('public const double WELD_END = 0.3, WELD_GAP = 0.0;', 'public const double WELD_END = 0.3, WELD_GAP = 0.0; public static double GapExtra = 0;      // GapExtra: көлбеу торецті құбырдағы заглушка швтарына 0,2 мм (тубың бұрышындағы 0,01…0,03 мм енуін болдырмау)', 1)
assert 'GapExtra' in s
s = s.replace('XYZ c0 = corner + dir * WELD_END; XYZ cA = c0 + (a + b) * WELD_GAP;\n        var pts = new List<XYZ> { cA * MM, (c0 + a * kf + b * WELD_GAP) * MM, (c0 + a * WELD_GAP + b * kf) * MM };',
              'double gp = WELD_GAP + GapExtra; XYZ c0 = corner + dir * WELD_END; XYZ cA = c0 + (a + b) * gp;\n        var pts = new List<XYZ> { cA * MM, (c0 + a * kf + b * gp) * MM, (c0 + a * gp + b * kf) * MM };')
assert 'double gp = WELD_GAP + GapExtra' in s
old1 = '{ var w = Tri(X(sEnd(ws * hb + dn), -hb, ws * hb + dn), tilt ? u : up,'
assert old1 in s
s = s.replace(old1, '{ GapExtra = tilt ? 0.2 : 0; var w = Tri(X(sEnd(ws * hb + dn), -hb, ws * hb + dn), tilt ? u : up,')
old2 = '{ double wLo = sd < 0 ? -hb + dn : hs2, wHi = sd < 0 ? -hs2 : hb + dn; var w = Tri('
assert old2 in s
s = s.replace(old2, '{ GapExtra = tilt ? 0.2 : 0; double wLo = sd < 0 ? -hb + dn : hs2, wHi = sd < 0 ? -hs2 : hb + dn; var w = Tri(')
# reset after cap welds: before wm0 line
old3 = '        // ---- монтаждық вставка–гусет: ұшы Wi'
assert old3 in s
s = s.replace(old3, '        GapExtra = 0;\n' + old3)
io.open(A + p, 'w', encoding='utf-8', newline='').write(s)
print('ok')
