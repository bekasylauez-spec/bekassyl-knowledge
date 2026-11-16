import io, re
p = r"D:/_claude_work/RMC/kzh/kz87_slab.cs"
s = io.open(p, encoding="utf-8").read()
lines = s.split("\n")
out = []
for ln in lines:
    if ln.startswith("var carrierSym = ") or ln.startswith('log.Add("carrier family'):
        continue
    out.append(ln)
s = "\n".join(out)


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# тасымалдаушы — геометриясыз DirectShape (Обобщённые модели): деталь элементінің семействосы модельде жоқ
rep("cs.Insert(Category.GetCategory(d, BuiltInCategory.OST_DetailComponents));", "cs.Insert(Category.GetCategory(d, BuiltInCategory.OST_GenericModel));")
i0 = s.index("    if (!carrierSym.IsActive) carrierSym.Activate();")
i1 = s.index("    Func<string, string, string[], double[], bool, ViewSchedule> Sched")
s = s[:i0] + (
    "    // жолдар: [топ, т1…]; тасымалдаушы — геометриясыз DirectShape «Обобщённые модели», Comments «RMC:tbl:…» (КМ көріністерінде сүзгі жасырады)\n"
    "    Action<string, List<string[]>> Rows = (tid, rows) =>\n"
    "    { foreach (var e in new FilteredElementCollector(d).OfClass(typeof(DirectShape)).WhereElementIsNotElementType().ToElements().Where(e => (e.LookupParameter(\"КЖ_т0\")?.AsString() ?? \"\") == tid).ToList()) d.Delete(e.Id);\n"
    "      int k = 0; foreach (var r in rows) { var ds = DirectShape.CreateElement(d, new ElementId(BuiltInCategory.OST_GenericModel)); ds.ApplicationId = \"RMC_KZH\"; ds.ApplicationDataId = \"tbl\";\n"
    "        ds.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.Set(\"RMC:tbl:\" + tid); ds.LookupParameter(\"КЖ_т0\").Set(tid); ds.LookupParameter(\"КЖ_т00\").Set(k.ToString(\"D3\")); ds.LookupParameter(\"КЖ_тгр\").Set(r[0]); for (int c = 1; c < r.Length; c++) ds.LookupParameter(\"КЖ_т\" + c).Set(r[c]); k++; } };\n"
) + s[i1:]
rep("var vs = ViewSchedule.CreateSchedule(d, new ElementId(BuiltInCategory.OST_DetailComponents));", "var vs = ViewSchedule.CreateSchedule(d, new ElementId(BuiltInCategory.OST_GenericModel));")
io.open(p, "w", encoding="utf-8").write(s)
print("ok", "carrierSym" in s, "dv.Id" in s)
