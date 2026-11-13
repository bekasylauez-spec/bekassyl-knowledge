import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
SP = r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w" + "\\"
s = io.open(A + 'rmc_misc_lib.cs', encoding='utf-8').read()
old = 'if (fl) c.CleanFail++; else if (r != null) s = r;'
assert s.count(old) == 1
s = s.replace(old, 'c.L.AppendLine("    DBGDIFF fl " + fl + " sh " + sh + " r? " + (r != null) + " removal " + (r == null ? "-" : QF(QCu(s.Volume - r.Volume))) + " ov0 " + QF(ov0) + " vs0 " + vs0 + " obstbb " + string.Join(",", o.B.Select(QF)));\n        ' + old)
old2 = 'if (s2 == null || s2.Volume < 1e-12) return false;\n    p.G.Add(s2);'
if old2 not in s: old2 = old2.replace('\n', '\r\n')
assert s.count(old2) == 1
s = s.replace(old2, 'if (s2 != null) c.L.AppendLine("    DBGPUT " + p.Title + " vol " + QF(QCu(s.Volume)) + " -> " + QF(QCu(s2.Volume)) + " rem " + QF(rem));\n    ' + old2)
io.open(SP + 'misc_dbg3.cs', 'w', encoding='utf-8').write(s)
u = io.open(A + 'rmc_u05.cs', encoding='utf-8').read()
u = u.replace('const bool PILOT = false; ', 'const bool PILOT = true; ', 1).replace('{ "6-A", "6-D-1", "6-D-2" }', '{ "1-A" }')
io.open(SP + 'u05_dbg3.cs', 'w', encoding='utf-8').write(u)
print('ok')
