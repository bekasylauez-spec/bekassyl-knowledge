D = 'D:\\Бекасыл КЖ КМ\\Завод_В109_КМ\\_авто\\revit\\'
p = D + 'b109_q20_audit.cs'; s = open(p, encoding='utf-8').read()
a = 'if (nodeDS.Any(d => (d.Name ?? "").StartsWith("Узел Р2 ") || (d.Name ?? "").StartsWith("шов Узел Р2 ")))'
assert a in s
s = s.replace(a, 'if (nodeDS.Any(d => (d.Name ?? "").StartsWith("Узел Р2 ") && !(d.Name ?? "").Contains("фасонка")))')
s = s.replace('if (nRib < 150) R["C15"]', 'if (nRib < 162) R["C15"]')
open(p, 'w', encoding='utf-8').write(s)
p = D + 'nodes.py'; s = open(p, encoding='utf-8').read()
a = "box(g + ' рёбра',"
assert a in s
s = s.replace(a, "box(g + ' ' + str(int(off)) + ' рёбра',")
open(p, 'w', encoding='utf-8').write(s); print('ok')
