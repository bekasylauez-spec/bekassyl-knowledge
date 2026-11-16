import io
p = r"D:/_claude_work/RMC/kzh/kz90_details.cs"
s = io.open(p, encoding="utf-8").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


rep("    View v = null;\n    Func<double, double, XYZ> P = (x, y) => new XYZ(x * MM, y * MM, 0);",
    "    View v = null;\n    Func<double, double, XYZ> P = (x, y) => new XYZ(x * MM, y * MM, 0);\n"
    "    // штрих аймағының шекара стилі — Revit рұқсат еткендерден (жаңа ішкі санат жарамсыз болуы мүмкін): аты бірдей → жуан/жіңішке баламасы → көрінбейтін\n"
    "    var validFR = FilledRegion.GetValidLineStyleIdsForFilledRegion(d).Select(q => d.GetElement(q) as GraphicsStyle).Where(q => q != null).ToList();\n"
    "    Func<GraphicsStyle, ElementId> FRS = gs => { if (gs == null) return (validFR.FirstOrDefault(q => q.Name == invis.Name) ?? validFR.First()).Id; var m = validFR.FirstOrDefault(q => q.Id == gs.Id) ?? validFR.FirstOrDefault(q => q.Name == gs.Name);\n"
    "        if (m == null) m = gs == gsMain ? validFR.FirstOrDefault(q => q.Name == \"БК_основная_толстая\") : validFR.FirstOrDefault(q => q.Name == \"БК_основная_тонкая\" || q.Name == \"<Тонкие линии>\"); return (m ?? validFR.First()).Id; };\n"
    "    log.Add(\"valid FR line styles \" + validFR.Count + \": \" + string.Join(\", \", validFR.Select(q => q.Name).Take(12)));")
rep("var r = FilledRegion.Create(d, FR[fr].Id, v.Id, new List<CurveLoop> { loop }); r.SetLineStyleId((gs ?? invis).Id); nReg++; };",
    "var r = FilledRegion.Create(d, FR[fr].Id, v.Id, new List<CurveLoop> { loop }); r.SetLineStyleId(FRS(gs)); nReg++; };")
rep("var rg = FilledRegion.Create(d, FR[\"герметик\"].Id, v.Id, new List<CurveLoop> { loop }); rg.SetLineStyleId(gsBar.Id); };",
    "var rg = FilledRegion.Create(d, FR[\"герметик\"].Id, v.Id, new List<CurveLoop> { loop }); rg.SetLineStyleId(FRS(gsThin)); };")
io.open(p, "w", encoding="utf-8").write(s)
print("ok")
