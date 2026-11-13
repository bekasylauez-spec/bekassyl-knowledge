def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for o, n in pairs:
        assert o in s, o
        s = s.replace(o, n, 1)
    open(p, 'w', encoding='utf-8').write(s)
a = 'D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/'
sub(a + 'v113_secs.cs', [
 ('Origin = new XYZ(24600, 0, 0), Right = XYZ.BasisY, Dir = XYZ.BasisX, U0 = -3400,', 'Origin = new XYZ(24600, 0, 0), Right = XYZ.BasisY, Dir = XYZ.BasisX, U0 = -4200 /* 13.11 (checker): the end stroke crossed the 54000 chain (y -2800) on sheets 3, 6 */,'),
 ('Origin = new XYZ(600, 0, 0), Right = XYZ.BasisY, Dir = XYZ.BasisX, U0 = -3400,', 'Origin = new XYZ(600, 0, 0), Right = XYZ.BasisY, Dir = XYZ.BasisX, U0 = -4200 /* 13.11: as 1-1 */,'),
 ('Right = -XYZ.BasisY, Dir = -XYZ.BasisX, U0 = -14000, U1 = 3400,', 'Right = -XYZ.BasisY, Dir = -XYZ.BasisX, U0 = -14000, U1 = 4200 /* 13.11: as 1-1 */, PadL = 800,'),
 ('Cx = 158 /* 13.11: 150 -> 158, +7,110 head on the frame */', 'Cx = 162 /* 13.11: 150 -> 158 (+7,110 head on the frame), +4 for the 800 longer crop on the right */'),
 ('Levels = lvG, Cx = 166, Cy = 165', 'Levels = lvG, Cx = 170 /* 13.11: +4, 800 longer crop on the right */, Cy = 165'),
 ('Cx = 159 /* 13.11: 151 -> 159, +7,307 head on the frame */', 'Cx = 155 /* 13.11: 151 -> 159 (+7,307 head on the frame), -4 for the 800 longer crop on the left (PadL) */')])
sub(a + 'v113_sec_lib.cs', [
 ('public double Cx, Cy, Lw;', 'public double Cx, Cy, Lw, PadL;'),
 ('double cu0 = cb.Min.X / M, cu1 = cb.Max.X / M, cv0 = cb.Min.Y / M, cv1 = cb.Max.Y / M;', 'double cu0 = cb.Min.X / M + df.PadL, cu1 = cb.Max.X / M, cv0 = cb.Min.Y / M, cv1 = cb.Max.Y / M;   // 13.11: PadL — empty crop on the left (only for the cut line length on the plans)')])
sub(a + 'v113_plans.cs', [
 ('dim(new List<Reference> { new Reference(gy.First()), new Reference(gy.Last()) }, false, -2300, 0, 12000);',
  '{ var dT = dim(new List<Reference> { new Reference(gy.First()), new Reference(gy.Last()) }, false, -2300, 0, 12000); if (dT != null) { try { d.Regenerate(); var tp = dT.TextPosition; dT.TextPosition = new XYZ(tp.X, tp.Y + 2500 * M, tp.Z); } catch (Exception ex) { sb.AppendLine("  12000 text " + ex.Message); } } }   // 13.11 (checker): «12000» sat on axis Б — moved along its line')])
print('ok')
