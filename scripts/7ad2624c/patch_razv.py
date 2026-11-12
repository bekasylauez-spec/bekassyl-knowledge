import io
p = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/v113_razv.cs"
s = io.open(p, encoding="utf-8-sig").read()
pairs = [
 ('{ "10", new[] { new[] { 1904.0, 3904, 900, 2400 }, new[] { 4205.0, 5205, 0, 2100 }, new[] { 6454.0, 8454, 900, 2400 }, new[] { 9454.0, 11454, 900, 2400 } } },',
  '{ "10", new[] { new[] { 1900.0, 3900, 900, 2400 }, new[] { 4200.0, 5200, 0, 2100 }, new[] { 6450.0, 8450, 900, 2400 }, new[] { 9450.0, 11450, 900, 2400 } } },   // АР фасад А-В: 1900,2000,300,1000,1250,2000,1000,2000,550 (r06)'),
 ('{ "1", new[] { new[] { 9496.0, 10496, 0, 2100 } } } };', '{ "1", new[] { new[] { 9500.0, 10500, 0, 2100 } } } };   // АР фасад В-А: ДНГ-1 1500…2500 от оси В (r06)'),
 ('Tuple.Create("20", "Развертка фасадных элементов по оси А"', 'Tuple.Create("28", "Развертка фасадных элементов по оси А"'),
 ('Tuple.Create("21", "Развертка фасадных элементов по оси В"', 'Tuple.Create("29", "Развертка фасадных элементов по оси В"'),
 ('Tuple.Create("22", "Развертка фасадных элементов по оси 1"', 'Tuple.Create("30", "Развертка фасадных элементов по оси 1"'),
 ('Tuple.Create("23", "Развертка фасадных элементов по оси 10"', 'Tuple.Create("31", "Развертка фасадных элементов по оси 10"'),
 ('foreach (var sn2 in new[] { "20", "21", "22", "23" })', 'foreach (var sn2 in new[] { "28", "29", "30", "31" })   // 12.11: final album numbers (the temporary 20–23 now belong to the node sheets)'),
 # opening height dims in the middle of the opening (тексеріс №38: they stood on the post lines)
 ('var ra = new ReferenceArray(); var rz0 = d.Create.NewDetailCurve(v, Line.CreateBound(Wp(u0 + 150, z0), Wp(u0 + 450, z0))); rz0.LineStyle = invis; var rz1 = d.Create.NewDetailCurve(v, Line.CreateBound(Wp(u0 + 150, z1), Wp(u0 + 450, z1))); rz1.LineStyle = invis;',
  'double um = (u0 + u1) / 2; var ra = new ReferenceArray(); var rz0 = d.Create.NewDetailCurve(v, Line.CreateBound(Wp(um - 150, z0), Wp(um + 150, z0))); rz0.LineStyle = invis; var rz1 = d.Create.NewDetailCurve(v, Line.CreateBound(Wp(um - 150, z1), Wp(um + 150, z1))); rz1.LineStyle = invis;'),
 ('try { d.Create.NewDimension(v, Line.CreateBound(Wp(u0 + 300, z0), Wp(u0 + 300, z1)), ra, dimT); nd++; }', 'try { d.Create.NewDimension(v, Line.CreateBound(Wp(um, z0), Wp(um, z1)), ra, dimT); nd++; }'),
]
for o, n in pairs:
    if o not in s: print("MISSING", o[:70]); continue
    s = s.replace(o, n, 1)
# ригель levels: a vertical chain of the opening sills / heads (= ригель faces) at the outer side of the first axis
a = '        sb.AppendLine("развертка " + fac + ": openings " + OPEN[fac].Length + ", dims " + nd);'
add = '''        {   // 12.11 (тексеріс №38): ригель / opening levels chain from ±0.000, left of the facade
            var zs = new List<double> { 0 }; foreach (var op in OPEN[fac]) { zs.Add(op[2]); zs.Add(op[3]); } zs = zs.Distinct().OrderBy(z => z).ToList();
            double ua = row ? (fac == "А" ? -900 : 54900) : (fac == "1" ? 12900 : -900); var raz = new ReferenceArray();
            foreach (var z in zs) { var dc = d.Create.NewDetailCurve(v, Line.CreateBound(Wp(ua - 150, z), Wp(ua + 150, z))); dc.LineStyle = invis; raz.Append(dc.GeometryCurve.Reference); }
            if (zs.Count >= 2) { try { d.Create.NewDimension(v, Line.CreateBound(Wp(ua, zs.First()), Wp(ua, zs.Last())), raz, dimT); nd++; } catch (Exception ex) { sb.AppendLine("  z chain " + ex.Message); } }
        }
'''
if a in s: s = s.replace(a, add + a, 1)
else: print("MISSING log line")
io.open(p, "w", encoding="utf-8").write(s); print("ok")
