p = r'D:\Бекасыл КЖ КМ\Завод_В109_КМ\_авто\revit\b109_q20_audit.cs'
s = open(p, encoding='utf-8').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a)); s = s.replace(a, b)
rep('"C12", "C13", "C14" })', '"C12", "C13", "C14", "C15" })')
rep('{ "C14", "колонна/ось сдвинута" } };', '{ "C14", "колонна/ось сдвинута" }, { "C15", "узлы не по узелдер.dwg (столик, накладки, X-связь)" } };')
i = s.index('        foreach (var l in gC13) { var d = l.Direction;')
j = s.index('\n', i) + 1
s = s[:j] + r'''    }
    // C15 (ереже 43, 09.11 кеш): user's «КМ Чертеж узелдер.dwg» — узел 1: ФФ1 at a column has the support table −20 × 100 × 250 under its end plate;
    //   узлы 4 / 8: БП1 / БП2 rigid node has two cover plates −16 (300 wide at the column face, ≥ 285 long); Разрез 6-6: every СВ1 tier is an X cross
    //   (in each braced bay / row: 2 through diagonals ≥ 6500 and 4 halves).
    {
        Func<DirectShape, List<XYZ[]>> Boxes = ds => { var lst = new List<XYZ[]>(); var ge = ds.get_Geometry(opt); if (ge == null) return lst;
            foreach (var go in ge) { var so = go as Solid; if (so == null || so.Volume < 1e-9) continue; var bb = so.GetBoundingBox(); var tr = bb.Transform;
                var a = tr.OfPoint(bb.Min); var b = tr.OfPoint(bb.Max); lst.Add(new[] { new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), Math.Min(a.Z, b.Z)), new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), Math.Max(a.Z, b.Z)) }); } return lst; };
        int nPin = 0, nRig = 0;
        foreach (var ds in nodeDS.Where(d => (d.Name ?? "").StartsWith("Узел ") && (d.Name.Contains(" шарнир к колонне") || d.Name.Contains(" жёсткий к колонне"))))
        {
            var bx = Boxes(ds);
            if (ds.Name.Contains("шарнир"))
            {
                nPin++;
                bool table = bx.Any(q => { var d3 = new[] { (q[1].X - q[0].X) * M, (q[1].Y - q[0].Y) * M, (q[1].Z - q[0].Z) * M }.OrderBy(v => v).ToArray(); return Math.Abs(d3[0] - 20) < 2 && Math.Abs(d3[1] - 100) < 2 && Math.Abs(d3[2] - 250) < 2; });
                if (!table) R["C15"].Add(ds.Id.Value + " " + ds.Name + ": нет столика −20×100×250 (узел 1)");
            }
            else
            {
                nRig++;
                int covers = bx.Count(q => Math.Abs((q[1].X - q[0].X) * M - 300) < 2 && (q[1].Y - q[0].Y) * M > 280 && (q[1].Z - q[0].Z) * M >= 15.9);
                if (covers < 2) R["C15"].Add(ds.Id.Value + " " + ds.Name + ": накладок −16 " + covers + " (узел 4/8: 2)");
            }
        }
        foreach (var grp in A.Where(m => m.mk == "СВ1").GroupBy(m => Math.Round((m.a.X + m.b.X) / 2 * M / 6000 - 0.5) + " " + Math.Round(m.a.Y * M) + " " + (Math.Min(m.a.Z, m.b.Z) * M > 4000 ? 2 : 1)))
        {
            int thr = grp.Count(m => m.len * M > 6500), half = grp.Count(m => m.len * M <= 6500);
            if (thr != 1 || half != 2) R["C15"].Add("СВ1 ярус " + grp.Key + ": сквозных " + thr + ", половин " + half + " (разрез 6-6: X, 1 + 2)");
        }
        note["C15"] = "шарнир " + nPin + ", жёстких " + nRig + ", ярусов СВ1 " + A.Where(m => m.mk == "СВ1").Count() / 3;
''' + s[j:]
open(p, 'w', encoding='utf-8').write(s); print('ok')
