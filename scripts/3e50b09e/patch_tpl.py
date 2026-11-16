import io

BS = chr(92)
NL = BS + "n"   # C# жолындағы \n


def load(p):
    return io.open(p, encoding="utf-8").read()


def save(p, s):
    io.open(p, "w", encoding="utf-8").write(s)


def rep(s, a, b, cnt=1):
    assert s.count(a) == cnt, (a[:100], s.count(a))
    return s.replace(a, b)


# ======================= kz94 (3.x / 4.x) =======================
p = r"D:/_claude_work/RMC/kzh/kz94_tables.cs"
s = load(p)
# 1) сандар — шаблондағыдай нүктемен (M_10: 86429.42)
s = rep(s, 'Func<double, string> F2 = x => x.ToString("0.00", IC);',
        'var INV = System.Globalization.CultureInfo.InvariantCulture; Func<double, string> F2 = x => x.ToString("0.00", INV);   // шаблон M_10/M_20: ондық бөлгіш — нүкте')
# 2) бетон жолы: Поз. бос (шаблон M_10/M_17/M_20), көлем — нүктемен
s = rep(s, '        var elems = rbs.GroupBy(r => PS(r, "КЖ_элемент")).OrderBy(g => g.Key).ToList();',
        '        var elems = rbs.GroupBy(r => PS(r, "КЖ_элемент")).OrderBy(g => g.Key).ToList();\n'
        '        var concUsed = new HashSet<long>();\n'
        '        Func<Element, string[]> ConcRow = e => { string cls = PS(e, "КЖ_наим").Replace("Бетон кл.", "").Trim(); string code = ConcCode(cls); double v; double.TryParse(PS(e, "КЖ_длина").Replace(" ", "").Replace(",", "."), System.Globalization.NumberStyles.Any, INV, out v);\n'
        '            return new[] { "", "ГОСТ 7473-2010" + (code != "" ? " (" + code + ")" : ""), "Класс бетона " + cls + ", м³", "", "", F2(v) }; };')
# әр элементтің өз «Материалы:» бөлімі (шаблон M_20) — позициялардан кейін
s = rep(s, '            // ВРС жолы\n            var row = new List<string> { elName };',
        '            { var ce = conc.Where(e => !concUsed.Contains(e.Id.Value) && PS(e, "КЖ_поз") != "" && elName.Contains(PS(e, "КЖ_поз"))).ToList();\n'
        '              if (ce.Count > 0) { spec.Add(new[] { "", "", "Материалы:", "", "", "" }); foreach (var e in ce) { spec.Add(ConcRow(e)); concUsed.Add(e.Id.Value); } } }\n'
        '            // ВРС жолы\n            var row = new List<string> { elName };')
s = rep(s, '        spec.Add(new[] { "", "", "Материалы:", "", "", "" });\n'
           '        foreach (var e in conc) { string cls = PS(e, "КЖ_наим").Replace("Бетон кл.", "").Trim(); string code = ConcCode(cls);\n'
           '            spec.Add(new[] { PS(e, "КЖ_поз"), "ГОСТ 7473-2010" + (code != "" ? " (" + code + ")" : ""), "Класс бетона " + cls + ", м³", "", "", PS(e, "КЖ_длина") }); }',
        '        { var rest = conc.Where(e => !concUsed.Contains(e.Id.Value)).ToList(); if (rest.Count > 0) { spec.Add(new[] { "", "", "Материалы:", "", "", "" }); foreach (var e in rest) spec.Add(ConcRow(e)); } }')
# 3) ВРС баған ені: «Изделия арматурные» ≥ 48 мм, А500С екі коды — 52 мм, бір коды — 30 мм; «Марка элемента» мәтінге қарай
s = rep(s, '        var wV = new double[nc]; wV[0] = 32; for (int c = 1; c < nc - 1; c++) wV[c] = 15; wV[nc - 1] = 18;',
        '        var wV = new double[nc]; wV[0] = Math.Max(32, Math.Ceiling(vrs.Max(r => r[0].Length) * 1.55 + 5)); wV[nc - 1] = 18;\n'
        '        { bool two = DB.Any(q => double.Parse(q) <= 10) && DB.Any(q => double.Parse(q) > 10); int na = DA.Length + 1, nb = DB.Length + 1;\n'
        '          double wa = Math.Max(15, 30.0 / na), wb = Math.Max(15, (two ? 52.0 : 30.0) / nb), span = na * wa + nb * wb; if (span < 48) { wa *= 48 / span; wb *= 48 / span; }\n'
        '          wa = Math.Ceiling(wa * 2) / 2; wb = Math.Ceiling(wb * 2) / 2; for (int c = a0; c <= a1; c++) wV[c] = wa; for (int c = b0; c <= b1; c++) wV[c] = wb; }')
save(p, s)
print("kz94 ok")

# ======================= kz97 (5.1, 6.2, 7.1, 1.1) =======================
p = r"D:/_claude_work/RMC/kzh/kz97_static_tables.cs"
s = load(p)
s = rep(s, 'Func<double, string> F2 = x => x.ToString("0.00", IC);',
        'var INV = System.Globalization.CultureInfo.InvariantCulture; Func<double, string> F2 = x => x.ToString("0.00", INV);   // шаблон M_10/M_20: ондық бөлгіш — нүкте\n'
        'Func<string, string> Dt = s0 => { if (string.IsNullOrEmpty(s0)) return s0 ?? ""; var m0 = System.Text.RegularExpressions.Regex.Match(s0.Trim(), @"^(-?[0-9\\u00a0 ]+)(,([0-9]+))?(\\s*м³)?$"); if (!m0.Success) return s0;\n'
        '    return m0.Groups[1].Value.Replace("\\u00a0", "").Replace(" ", "") + (m0.Groups[3].Success ? "." + m0.Groups[3].Value : "") + m0.Groups[4].Value; };\n'
        'Func<double, string> FV = x => x < 0.1 ? x.ToString("0.000", INV) : x.ToString("0.00", INV);   // бетон көлемі\n'
        '// ұзын атауды бағанға сыйғызу: «, » не бос орыннан екі жолға (ISOCPEUR 2,5 мм ≈ 1,55 мм/таңба)\n'
        'Func<string, double, string> Wrap = (s0, wmm) => { if (s0 == null || s0.Length * 1.55 + 4 <= wmm) return s0; int lim = Math.Min(s0.Length - 1, (int)((wmm - 4) / 1.55));\n'
        '    int cut = s0.LastIndexOf(", ", lim); if (cut > 5) return s0.Substring(0, cut + 1) + "' + NL + '" + s0.Substring(cut + 2);\n'
        '    cut = s0.LastIndexOf(\' \', lim); return cut > 5 ? s0.Substring(0, cut) + "' + NL + '" + s0.Substring(cut + 1) : s0; };\n'
        'Func<List<string[]>, List<double>> RH = rws => rws.Select((r, i) => i == 0 ? 15.0 : (r.Any(c => c != null && c.Contains("' + NL + '")) ? 11.0 : 8.0)).ToList();')
# ВРС: баған ені мен «Марка элемента»
s = rep(s, '      var w = new double[nc]; w[0] = 32; for (int c = 1; c < nc - 1; c++) w[c] = 15; w[nc - 1] = 18;',
        '      var w = new double[nc]; w[0] = Math.Max(32, Math.Ceiling(data.Max(r => (r[0] ?? "").Length) * 1.55 + 5)); w[nc - 1] = 18;\n'
        '      { bool two = DB.Any(q => double.Parse(q) <= 10) && DB.Any(q => double.Parse(q) > 10); double wa = na > 0 ? Math.Max(15, 30.0 / na) : 0, wb = nb > 0 ? Math.Max(15, (two ? 52.0 : 30.0) / nb) : 0, span = na * wa + nb * wb;\n'
        '        if (span < 48) { wa *= 48 / span; wb *= 48 / span; } wa = Math.Ceiling(wa * 2) / 2; wb = Math.Ceiling(wb * 2) / 2; for (int c = 0; c < na; c++) w[a0 + c] = wa; for (int c = 0; c < nb; c++) w[b0 + c] = wb; }')
# ---- 5.1: бетон жолында Поз. бос, сандар нүктемен, ұзын атау екі жолда ----
s = rep(s, '      var rows = new List<string[]> { H6, new[] { "", "", "Плита пола Пп-1", "", "", F2(mass) }, new[] { p1[1], p1[2], p1[3], p1[4], p1[5], F2(mass) }, new[] { "", "", "Материалы:", "", "", "" } };\n'
           '      foreach (var m in mt) { string cls = m[3].Replace("Бетон кл.", "").Trim(); bool conc = m[3].StartsWith("Бетон"); rows.Add(new[] { m[1], conc ? "ГОСТ 7473-2010 (212-101-1101)" : "", conc ? "Класс бетона " + cls + ", м³" : m[3] + ", м³", "", "", m[5] }); }\n'
           '      var hh = new List<double> { 15 }; for (int k = 1; k < rows.Count; k++) hh.Add(8);',
        '      var rows = new List<string[]> { H6, new[] { "", "", "Плита пола Пп-1", "", "", F2(mass) }, new[] { p1[1], p1[2], p1[3], p1[4], Dt(p1[5]), F2(mass) }, new[] { "", "", "Материалы:", "", "", "" } };\n'
        '      foreach (var m in mt) { string cls = m[3].Replace("Бетон кл.", "").Trim(); bool conc = m[3].StartsWith("Бетон"); rows.Add(new[] { "", conc ? "ГОСТ 7473-2010 (212-101-1101)" : "", Wrap(conc ? "Класс бетона " + cls + ", м³" : m[3] + ", м³", 65), "", "", FV(Num(m[5])) }); }\n'
        '      var hh = RH(rows);')
# ---- 6.2: шаблон M_20 — әр элементтің өз «Материалы:» бөлімі; кесте бос жоғарғы оң бұрышқа ----
i0 = s.index('    // ================= 6.2 (пандус, лоток, отмостка, крыльцо) =================')
i1 = s.index('    // ================= 7.1 (альбом бойынша) =================')
new62 = '''    // ================= 6.2 (пандус, лоток, отмостка, крыльцо) — шаблон M_20: элемент → позициялар → «Материалы:» → бетон (Поз. бос) =================
    { var S = "КЖ-6.2"; var sh = sheetsAll.First(x => x.SheetNumber == S);
      var sp = Carr(S + "/спец"); var mt = Carr(S + "/мат");
      var oS = OldInst(sh, S + " Спецификация к узлам 6-8") ?? OldInst(sh, S + " Спецификация элементов"); var oM = OldInst(sh, S + " Материалы"); var oV = OldInst(sh, S + " Ведомость расхода стали");
      foreach (var o in new[] { oS, oM, oV }.Where(q => q != null)) { var vid = o.ScheduleId; d.Delete(o.Id); try { d.Delete(vid); } catch { } }
      DelTitles(sh, new[] { "Спецификация к узлам 6-8", "Спецификация элементов", "Ведомость расхода стали, кг", "Материалы" });
      Func<string, string> Code = c => c.Contains("B30") ? " (212-101-1101)" : c.Contains("B25") ? " (212-101-0901)" : c.Contains("B20") ? " (212-101-0701)" : c.Contains("B15") ? " (212-101-0601)" : "";
      var qre = new System.Text.RegularExpressions.Regex(@",?\\s*(на 1 (шт|м)\\.?|\\d+ шт\\.)");
      // материалдар элемент бойынша (бос «элемент» ұяшығы — алдыңғы элементке жатады)
      var matBy = new List<Tuple<string, List<string[]>>>(); string cur = "";
      foreach (var m in mt) { if (!string.IsNullOrWhiteSpace(m[1])) cur = m[1].Trim(); var tp = matBy.FirstOrDefault(q => q.Item1 == cur); if (tp == null) { tp = Tuple.Create(cur, new List<string[]>()); matBy.Add(tp); } tp.Item2.Add(m); }
      Func<string[], string[]> MatRow = m => { bool conc = m[3].StartsWith("Бетон"); string nm = qre.Replace(m[3], "").Replace(" подготовка", "").Trim().TrimEnd(','); nm = conc ? "Класс бетона " + nm.Replace("Бетон кл.", "").Trim() : nm;
          return new[] { "", conc ? "ГОСТ 7473-2010" + Code(m[3]) : "", Wrap(nm + ", м³", 65), "", "", FV(Num(m[5])) }; };
      var rows = new List<string[]> { H6 }; var vrsRows = new List<string[]>(); var used = new HashSet<string>();
      foreach (var g in sp.GroupBy(r => r[0]))
      { string el = System.Text.RegularExpressions.Regex.Replace(g.Key, @"^\\d+\\.\\s*", ""); double tot = g.Sum(r => Num(r[6])); rows.Add(new[] { "", "", el, "", "", F2(tot) });
        foreach (var r in g) rows.Add(new[] { r[1], r[2], r[3], r[4], Dt(r[5]), F2(Num(r[6])) });
        var mb = matBy.FirstOrDefault(q => q.Item1 != "" && el.Contains(q.Item1)); if (mb != null) { rows.Add(new[] { "", "", "Материалы:", "", "", "" }); foreach (var m in mb.Item2) rows.Add(MatRow(m)); used.Add(mb.Item1); }
        double a6 = g.Where(r => r[3].Contains("Ø6 А240")).Sum(r => Num(r[6])), b10 = g.Where(r => r[3].Contains("Ø10 А500С")).Sum(r => Num(r[6]));
        var mkm = System.Text.RegularExpressions.Regex.Match(el, @"[А-ЯЁ][а-яё]{0,2}-\\d+.*$"); vrsRows.Add(new[] { mkm.Success ? mkm.Value : el, V(a6), V(a6), V(b10), V(b10), F2(a6 + b10) }); }
      foreach (var mb in matBy.Where(q => !used.Contains(q.Item1)))
      { var qm = mb.Item2.Select(m => qre.Match(m[3])).FirstOrDefault(x => x.Success); string nmE = mb.Item1 == "" ? "Прочие" : mb.Item1;
        rows.Add(new[] { "", "", nmE + (qm != null ? " (" + qm.Groups[1].Value + ")" : ""), "", "", "" }); rows.Add(new[] { "", "", "Материалы:", "", "", "" }); foreach (var m in mb.Item2) rows.Add(MatRow(m)); }
      var hh = RH(rows);
      var nv = HT(S + " Спецификация элементов", w6, rows, hh, new List<int[]>(), null);
      var tbb6 = new FilteredElementCollector(d, sh.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).FirstElement().get_BoundingBox(sh); double R6 = tbb6.Max.X / MM - 5, T6 = tbb6.Max.Y / MM - 5;
      var si = PutFreeF(sh, nv, (w, h) => new List<double[]> { new[] { R6 - 3 - w, T6 - 10 } }, null); var nb = SB(si, sh); Title(sh, nb[0], nb[2], nb[3], "Спецификация элементов");
      var vv = VRS(S + " Ведомость расхода стали", new[] { "6" }, new[] { "10" }, vrsRows);
      var sv = PutFreeF(sh, vv, (w, h) => new List<double[]> { new[] { nb[0], nb[1] - 14 }, new[] { nb[2] - w, nb[1] - 14 } }, nb); var bv = SB(sv, sh); Title(sh, bv[0], bv[2], bv[3], "Ведомость расхода стали, кг");
      log.Add(S + ": spec " + string.Join(",", nb.Select(q => Math.Round(q))) + " | ВРС " + string.Join(",", bv.Select(q => Math.Round(q)))); }
'''
s = s[:i0] + new62 + s[i1:]
# PutFreeF: орын үміткерлерін кестенің өлшемі бойынша есептейтін нұсқа
s = rep(s, '    var w6 = new[] { 15.0, 60, 65, 10, 15, 20 };',
        '    Func<ViewSheet, ViewSchedule, Func<double, double, List<double[]>>, double[], ScheduleSheetInstance> PutFreeF = (sh0, vs, candF, extra) =>\n'
        '    { var si0 = Put(sh0, vs, 0, 0); var b0 = SB(si0, sh0); double w = b0[2] - b0[0], h = b0[3] - b0[1]; d.Delete(si0.Id); d.Regenerate(); return PutFree(sh0, vs, candF(w, h), extra); };\n'
        '    var w6 = new[] { 15.0, 60, 65, 10, 15, 20 };')
# ---- 7.1: Примечание — жалпы масса (шаблон M_20: Кол. × Масса ед.), сандар нүктемен ----
s = rep(s, '        foreach (var r in g) rows.Add(new[] { r[1] == "-" ? "" : r[1], r[2], r[3], r[4], r[5], r[6] }); }',
        '        foreach (var r in g) { double n0 = Num(r[4]), m0 = Num(r[5]); rows.Add(new[] { r[1] == "-" ? "" : r[1], r[2], r[3], r[4], Dt(r[5]), n0 > 0 && m0 > 0 ? F2(n0 * m0) : "" }); } }')
s = rep(s, '"Класс бетона " + cls + ", м³", "", "", b[3] }); }\n      var hh = new List<double> { 15 }; for (int k = 1; k < rows.Count; k++) hh.Add(6.5);',
        '"Класс бетона " + cls + ", м³", "", "", FV(Num(b[3])) }); }\n      var hh = new List<double> { 15 }; for (int k = 1; k < rows.Count; k++) hh.Add(6.5);')
s = rep(s, '.Select(q => q == "-" ? "---" : q).ToArray()).ToList();',
        '.Select(q => q == "-" ? "---" : Dt(q)).ToArray()).ToList();')
save(p, s)
print("kz97 ok")
