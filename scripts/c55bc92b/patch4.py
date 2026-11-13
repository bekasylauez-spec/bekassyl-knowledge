P = r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\rmc_02_frame.cs'
s = open(r'D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто\_v1\rmc_02_frame.cs', encoding='utf-8').read()
def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:70])
    s = s.replace(old, new)
rep("// РМЦ КМ каркасы: осьтер 1…11 / A…G, деңгейлер, типтер (тип атауы = марка), материал «КМ_<марка> (сталь)», members.tsv бойынша элементтер.",
    "// РМЦ КМ каркасы (v2, 13.11.2026): осьтер 1…11 / A…G, деңгейлер, типтер (тип атауы = марка), материал «КМ_<марка> (сталь)», members.tsv бойынша элементтер.\n// v2: ригель Б1/Б2/Б3 және Б5 — rmc_01b_fams.cs семействолары (номинал ұзындыққа тұрақты геометрия: сынық табан, тік ұштар, Б5 ойығы); Б5 ұзындығы бойынша екі семейство (members: fam = b5_<ұзындық>).")
rep("""var Fi = new Dictionary<string, Family>(); foreach (var n in new[] { "Б1", "Б2", "Б3", "КБ1", "ПБ1", "Б4", "Б5" }) Fi[n] = Load(d, famMy + "РМЦ_" + n + "_двутавр_сварной.rfa");""",
    """var Fi = new Dictionary<string, Family>(); foreach (var n in new[] { "Б1", "Б2", "Б3", "КБ1", "ПБ1", "Б4" }) Fi[n] = Load(d, famMy + "РМЦ_" + n + "_двутавр_сварной.rfa");
        var Fb5 = new Dictionary<string, Family>(); foreach (var L5 in new[] { "5954", "5804" }) Fb5["b5_" + L5] = Load(d, famMy + "РМЦ_Б5L" + L5 + "_двутавр_сварной.rfa");
        var oldB5 = new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().FirstOrDefault(x => x.Name == "РМЦ_Б5_двутавр_сварной");""")
rep("""var mine = new List<ElementId> { Fcol.Id, Ftube.Id, Fch.Id }; mine.AddRange(Fi.Values.Select(f => f.Id));""",
    """var mine = new List<ElementId> { Fcol.Id, Ftube.Id, Fch.Id }; mine.AddRange(Fi.Values.Select(f => f.Id)); mine.AddRange(Fb5.Values.Select(f => f.Id)); if (oldB5 != null) mine.Add(oldB5.Id);""")
rep("""        if (old.Count > 0) { d.Delete(old); sb.AppendLine("removed " + old.Count + " members of the previous run"); }""",
    """        if (old.Count > 0) { d.Delete(old); sb.AppendLine("removed " + old.Count + " members of the previous run"); }
        if (oldB5 != null) { try { d.Delete(oldB5.Id); sb.AppendLine("old family РМЦ_Б5_двутавр_сварной removed"); } catch (Exception ex) { sb.AppendLine("old Б5 family not removed: " + ex.Message.Split((char)10)[0]); } }""")
rep("""        foreach (var mk in rows.Select(r => r[1]).Distinct())
        {
            FamilySymbol s;""", """        foreach (var sk in rows.Select(r => r[3].StartsWith("b5_") ? r[3] : r[1]).Distinct())
        {
            string mk = sk.StartsWith("b5_") ? "Б5" : sk;
            FamilySymbol s;""")
rep("""            else if (mk == "Пр1") { s = d.GetElement(Fch.GetFamilySymbolIds().First()) as FamilySymbol; if (s.Name != "Пр1") s.Name = "Пр1"; }""",
    """            else if (mk == "Пр1") { s = d.GetElement(Fch.GetFamilySymbolIds().First()) as FamilySymbol; if (s.Name != "Пр1") s.Name = "Пр1"; }
            else if (sk.StartsWith("b5_")) { s = d.GetElement(Fb5[sk].GetFamilySymbolIds().First()) as FamilySymbol; if (s.Name != "Б5") s.Name = "Б5"; }""")
rep("""            s.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set(mk); if (!s.IsActive) s.Activate(); syms[mk] = s;
            mats[mk] = MarkMat(d, mk, col.ContainsKey(mk) ? col[mk] : new Color(128, 128, 128));""",
    """            s.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).Set(mk); if (!s.IsActive) s.Activate(); syms[sk] = s;
            if (!mats.ContainsKey(mk)) mats[mk] = MarkMat(d, mk, col.ContainsKey(mk) ? col[mk] : new Color(128, 128, 128));""")
rep("""int id = int.Parse(r[0]); string mk = r[1], kind = r[2], fam = r[3]; var sym = syms[mk];""",
    """int id = int.Parse(r[0]); string mk = r[1], kind = r[2], fam = r[3]; var sym = syms[fam.StartsWith("b5_") ? fam : mk];""")
open(P, 'w', encoding='utf-8').write(s)
print('ok')
