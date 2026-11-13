import io
A = r"D:\Бекасыл КЖ КМ\РМЦ_КМ\_авто" + "\\"
def edit(p, reps):
    s = io.open(A + p, encoding='utf-8').read()
    for old, new in reps:
        assert s.count(old) == 1, (p, old[:70], s.count(old))
        s = s.replace(old, new)
    io.open(A + p, 'w', encoding='utf-8', newline='').write(s)

# ---------- node lib
edit('rmc_node_lib.cs', [
('''    foreach (var o in c.Obst) {
        if (!Ovl(bx, o.B, 0.5)) continue;
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Difference); if (r != null) s = r; } catch { c.CleanFail++; }
        if (s.Volume < 1e-12) { removed = Cu(v0); return null; } }
    removed = Cu(v0 - s.Volume); return s; }''', '''    foreach (var o in c.Obst) {
        if (!Ovl(bx, o.B, 0.5)) continue;
        bool vs0, fl0; double ov0 = OvlVol(s, o.S, out vs0, out fl0); if (!fl0 && ov0 <= 0.3) continue;      // q20: ≤ 0,3 мм³ қиылысуды кеспейміз (сливер / жарамсыз солид болдырмау)
        try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(s, o.S, BooleanOperationsType.Difference); if (r != null) s = r; } catch { c.CleanFail++; }
        if (s.Volume < 1e-12) { removed = Cu(v0); return null; } }
    removed = Cu(v0 - s.Volume); return s; }
// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді
static bool VShape(Document d, Solid s) { var t = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel)); bool ok = false; try { ok = t.IsValidShape(new List<GeometryObject> { s }); } catch { } d.Delete(t.Id); return ok; }
// кедергілерді кішкентай ығыстырумен кесу; жарамды нәтиже болмаса null
static Solid CleanShifted(Ctx c, Solid s) {
    foreach (double tmm in new[] { 0.05, 0.1, 0.2, 0.4 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) }) {
        Solid cur = s; bool okAll = true; var bx = BBox(cur);
        foreach (var o in c.Obst) { if (!Ovl(bx, o.B, 0.5)) continue;
            try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(cur, ShiftS(o.S, dv.Normalize() * (tmm * MM)), BooleanOperationsType.Difference); if (r != null) cur = r; } catch { okAll = false; break; }
            if (cur.Volume < 1e-12) return null; }
        if (okAll && VShape(c.D, cur)) return cur; }
    return null; }'''),
('''    double rem; var s2 = Clean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + F(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 == null || s2.Volume < 1e-12) return false;''', '''    double rem; var s2 = Clean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + F(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 != null && rem > 1e-4 && !VShape(c.D, s2)) { var s3 = CleanShifted(c, s); if (s3 != null) { s2 = s3; c.L.AppendLine("  CLEANSHIFT «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — ығыстырылған кескішпен қайталанды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }
    if (s2 == null || s2.Volume < 1e-12) return false;'''),
])
# ---------- misc lib
edit('rmc_misc_lib.cs', [
('''    foreach (var o in c.Obst) {
        if (!QOvl(bx, o.B, 0.5)) continue;
        bool sh, fl; var r = QDiffRetry(s, o.S, out sh, out fl); if (fl) c.CleanFail++; else if (r != null) s = r;''', '''    foreach (var o in c.Obst) {
        if (!QOvl(bx, o.B, 0.5)) continue;
        bool vs0, fl0; double ov0 = QOvlVol(s, o.S, out vs0, out fl0); if (!fl0 && ov0 <= 0.3) continue;      // q20: ≤ 0,3 мм³ қиылысуды кеспейміз (сливер / жарамсыз солид болдырмау)
        bool sh, fl; var r = QDiffRetry(s, o.S, out sh, out fl); if (fl) c.CleanFail++; else if (r != null) s = r;'''),
('''    double rem; var s2 = QClean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + QF(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 == null || s2.Volume < 1e-12) return false;''', '''    double rem; var s2 = QClean(c, s, out rem); if (rem > 1) { c.L.AppendLine("  CLEAN «" + p.Title + "»: " + QF(rem) + " мм3 алынды (каркас/бұрынғы бөлшекпен қиылысу)"); c.Removed += rem; }
    if (s2 != null && rem > 1e-4 && !QVShape(c.D, s2)) { var s3 = QCleanShifted(c, s); if (s3 != null) { s2 = s3; c.L.AppendLine("  CLEANSHIFT «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — ығыстырылған кескішпен қайталанды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }
    if (s2 == null || s2.Volume < 1e-12) return false;'''),
('// hard = true: бөлшек каркаспен >50 мм³ қиылысса және Mode=="SKIP" болса — салынбайды (false қайтарады); әйтпесе тазаланады (CLEAN)', '''// q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді); уақытша DS жасап тексереді
static bool QVShape(Document d, Solid s) { var t = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel)); bool ok = false; try { ok = t.IsValidShape(new List<GeometryObject> { s }); } catch { } d.Delete(t.Id); return ok; }
static Solid QCleanShifted(QCtx c, Solid s) {
    foreach (double tmm in new[] { 0.05, 0.1, 0.2, 0.4 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) }) {
        Solid cur = s; bool okAll = true; var bx = QBBox(cur);
        foreach (var o in c.Obst) { if (!QOvl(bx, o.B, 0.5)) continue;
            try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(cur, QShiftS(o.S, dv.Normalize() * (tmm * QMM)), BooleanOperationsType.Difference); if (r != null) cur = r; } catch { okAll = false; break; }
            if (cur.Volume < 1e-12) return null; }
        if (okAll && QVShape(c.D, cur)) return cur; }
    return null; }
// hard = true: бөлшек каркаспен >50 мм³ қиылысса және Mode=="SKIP" болса — салынбайды (false қайтарады); әйтпесе тазаланады (CLEAN)'''),
])
# ---------- brace lib
edit('rmc_brace_lib.cs', [
('''        if (s2 == null || s2.Volume < 1e-12) { c.Skipped++; return false; }
        p.G.Add(s2); if (obstacle)''', '''        if (s2 != null && rem > 1e-4 && !VShape(c.D, s2)) { var s3 = CleanShifted(c, s); if (s3 != null) { s2 = s3; c.L.AppendLine("  CLEANSHIFT «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз еді — ығыстырылған кескішпен қайталанды"); } else { s2 = s; c.L.AppendLine("  WARN «" + p.Title + "»: булев нәтижесі DS-ке жарамсыз, кесілмеген дене салынды"); } }
        if (s2 == null || s2.Volume < 1e-12) { c.Skipped++; return false; }
        p.G.Add(s2); if (obstacle)'''),
('''    public static bool Put(BCtx c, BPart p, Solid s, bool obstacle)''', '''    // q20: DirectShape жарамдылығы (булев кейде IsValidShape өтпейтін солид береді)
    public static bool VShape(Document d, Solid s) { var t = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel)); bool ok = false; try { ok = t.IsValidShape(new List<GeometryObject> { s }); } catch { } d.Delete(t.Id); return ok; }
    public static Solid CleanShifted(BCtx c, Solid s)
    {
        foreach (double tmm in new[] { 0.05, 0.1, 0.2, 0.4 }) foreach (var dv in new[] { new XYZ(1, 0.618, 0.382), new XYZ(-0.7, 0.3, 0.9), new XYZ(0.2, -0.9, 0.4) })
        {
            Solid cur = s; bool okAll = true; var bx = BBox(cur);
            foreach (var o in c.Obst) { if (!Ovl(bx, o.B, 0.5)) continue; try { var r = BooleanOperationsUtils.ExecuteBooleanOperation(cur, ShiftS(o.S, dv.Normalize() * (tmm * MM)), BooleanOperationsType.Difference); if (r != null) cur = r; } catch { okAll = false; break; } if (cur.Volume < 1e-12) return null; }
            if (okAll && VShape(c.D, cur)) return cur;
        }
        return null;
    }
    public static bool Put(BCtx c, BPart p, Solid s, bool obstacle)'''),
])
print('ok')
