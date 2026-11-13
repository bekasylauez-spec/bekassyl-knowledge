import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
SP = r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w" + "\\"
s = io.open(A + 'rmc_misc_lib.cs', encoding='utf-8').read()
old = 'if (s2 != null && rem > 1e-4 && !QVShape(c.D, s2)) {'
assert s.count(old) == 1
new = '''if (s2 != null && rem > 1e-4 && !QVShape(c.D, s2)) { c.L.AppendLine("  DBG invalid cut result: vol " + QF(QCu(s2.Volume)) + " (orig " + QF(QCu(s.Volume)) + ") faces " + s2.Faces.Size + " edges " + s2.Edges.Size);
        foreach (Face fc in s2.Faces) { var pf = fc as PlanarFace; var lp = pf == null ? null : pf.GetEdgesAsCurveLoops(); string vs = ""; if (lp != null) foreach (var l0 in lp) foreach (Curve cu in l0) vs += " (" + QF(cu.GetEndPoint(0).X / QMM) + "," + QF(cu.GetEndPoint(0).Y / QMM) + "," + QF(cu.GetEndPoint(0).Z / QMM) + ")"; c.L.AppendLine("     face " + QF(fc.Area / (QMM * QMM)) + (pf == null ? "" : " n=" + QF(pf.FaceNormal.X) + "," + QF(pf.FaceNormal.Y) + "," + QF(pf.FaceNormal.Z)) + vs); }
        foreach (Edge ed in s.Edges) { } c.L.AppendLine("     orig bb " + string.Join(",", QBBox(s).Select(QF)));
        foreach (var o in c.Obst) if (QOvl(QBBox(s), o.B, 0.5)) c.L.AppendLine("     obst bb " + string.Join(",", o.B.Select(QF)) + " ov " + QF(QCu(0)));'''
s = s.replace(old, new)
io.open(SP + 'misc_dbg2.cs', 'w', encoding='utf-8').write(s)
u = io.open(A + 'rmc_u05.cs', encoding='utf-8').read()
u = u.replace('const bool PILOT = false; ', 'const bool PILOT = true; ', 1).replace('{ "6-A", "6-D-1", "6-D-2" }', '{ "1-G" }')
io.open(SP + 'u05_dbg.cs', 'w', encoding='utf-8').write(u)
print('ok')
