import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
SP = r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\w" + "\\"
s = io.open(A + 'rmc_node_lib.cs', encoding='utf-8').read()
old = 'bool vs0, fl0; double ov0 = OvlVolV(s, o.S, out vs0, out fl0); if (!vs0 && !fl0 && ov0 <= 0.3) continue;'
assert s.count(old) == 1
new = 'bool vs0, fl0; double ov0 = OvlVolV(s, o.S, out vs0, out fl0); c.L.AppendLine("    DBGCLEAN obst bb " + string.Join(",", o.B.Select(F)) + " me " + string.Join(",", bx.Select(F)) + " ov0 " + F(ov0) + " viaShift " + vs0 + " fail " + fl0); if (!vs0 && !fl0 && ov0 <= 0.3) continue;'
s = s.replace(old, new)
io.open(SP + 'node_dbg.cs', 'w', encoding='utf-8').write(s)
u = io.open(A + 'rmc_u02.cs', encoding='utf-8').read()
import re
print(re.findall(r'PILOT_LOCS[^\n]*', u)[:2])
u = u.replace('const bool PILOT = false; ', 'const bool PILOT = true; ', 1)
io.open(SP + 'u02_dbg.cs', 'w', encoding='utf-8').write(u)
