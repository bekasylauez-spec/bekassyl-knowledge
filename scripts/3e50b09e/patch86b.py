import io
p = r"D:/_claude_work/RMC/kzh/kz86_rb.cs"
s = io.open(p, encoding="utf-8-sig").read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (a[:90], s.count(a))
    s = s.replace(a, b)


# 1) 1-1 белгісіндегі нөмір = 1-1 көрінісінің парақтағы нөмірі
rep('vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set((i + 1).ToString());',
    'vp.get_Parameter(BuiltInParameter.VIEWPORT_DETAIL_NUMBER).Set(i == 0 ? "10" : "1");')
# 2) 1-1 ростверк қырынан 125 мм: белгі нөмірі хомут шагы мәтінінен алыс; көрінетін хомут — a+50
rep("rr.s1 = rr.a + 175;", "rr.s1 = rr.a + 125;")
rep("- (ri.s1 - 25)); }).First(); var bb0 = BB3(h0);", "- (ri.s1 - 75)); }).First(); var bb0 = BB3(h0);")
rep("- (ri.s1 - 25)); }).First(); var pb = BB3(pn);", "- (ri.s1 - 75)); }).First(); var pb = BB3(pn);")
# 3) төменгі маркалар 1-1-де жоғарырақ (ішкі көлденең тізбектің «51» мәтінімен түйіспесін)
rep("-1400 - Sc(6) - gi * Sc(5)", "-1400 - Sc(4) - gi * Sc(4)")
# 4) аннотация кропы екі көріністе де соңында өшеді (Revit кроп шекарасына тиген аннотацияны түгел жасырады: 1-1-дегі 2* және «800»);
#    атау мәтіні белгі қорабының жоғарғы жағында → қораптың үсті = сызба қорабы + 7 мм
rep("    try { views[0].get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(0); } catch { }\n    d.Regenerate();",
    "    foreach (var vw in views) try { vw.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(0); } catch { }\n    d.Regenerate();")
rep("titleT[vp.Id.Value] = new XYZ((ob.MinimumPoint.X + ob.MaximumPoint.X) / 2, ob.MaximumPoint.Y + 1 * MM, 0); }",
    "titleT[vp.Id.Value] = new XYZ((ob.MinimumPoint.X + ob.MaximumPoint.X) / 2, ob.MaximumPoint.Y + 7 * MM, 0); }")
rep("vp.LabelOffset = vp.LabelOffset + new XYZ(tg.X - (lo.MinimumPoint.X + lo.MaximumPoint.X) / 2, tg.Y - lo.MinimumPoint.Y, 0); d.Regenerate();",
    "vp.LabelOffset = vp.LabelOffset + new XYZ(tg.X - (lo.MinimumPoint.X + lo.MaximumPoint.X) / 2, tg.Y - lo.MaximumPoint.Y, 0); d.Regenerate();")
io.open(p, "w", encoding="utf-8-sig").write(s)
print("ok")
