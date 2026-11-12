import io
def patch(p, pairs):
    s = io.open(p, encoding="utf-8-sig").read()
    for o, n in pairs:
        if o not in s: print("MISSING in", p[-25:], ":", o[:90]); continue
        s = s.replace(o, n, 1)
    io.open(p, "w", encoding="utf-8").write(s)
A = "D:/Бекасыл КЖ КМ/Завод_В113_КМ/_авто/"
patch(A + "v113_3d.cs", [
 ('        double slotH = (yTop - yBot) / mains.Count;',
  '        if (sn <= 15) { x0 = tbb.Min.X + 302 * M; x1 = tbb.Max.X - 10 * M; yTop = tbb.Min.Y + 158 * M; yBot = tbb.Min.Y + 66 * M; }   // 12.11 (тексеріс №31): the free box right of Разрез 2-2, over the stamp\n        double slotH = (yTop - yBot) / mains.Count;'),
])
patch(A + "v113_bases_sheets.cs", [
 # 1. RC foundation stays in the sections (тексеріс №32), grey
 ('&& !x.Name.StartsWith("Узел 4") && !x.Name.StartsWith("шов узел 4") && x.CanBeHidden(v)).Select(x => x.Id).ToList(); if (oth.Count > 0) v.HideElements(oth);',
  '&& !x.Name.StartsWith("Узел 4") && !x.Name.StartsWith("шов узел 4") && !(i > 0 && x is DirectShape && ((DirectShape)x).ApplicationId == "БК_ЖБ") && x.CanBeHidden(v)).Select(x => x.Id).ToList(); if (oth.Count > 0) v.HideElements(oth);'),
 # 2. anchor text: type, length (model), ГОСТ
 ('string ancTxt = anc == null ? "Болт" : System.Text.RegularExpressions.Regex.Match(anc.Name, @"М\\d+").Value;',
  'string ancTxt = anc == null ? "Болт" : System.Text.RegularExpressions.Regex.Match(anc.Name, @"М\\d+").Value; if (anc != null) { var ab = anc.get_BoundingBox(null); double aL = Math.Round((ab.Max.Z - ab.Min.Z) / M / 10) * 10; ancTxt = "2.1 " + ancTxt + "×" + aL; }'),
])
s = io.open(A + "v113_bases_sheets.cs", encoding="utf-8-sig").read()
# 3. in the sections: plate bottom −0.400, foundation top −0.450 (подливка 50), chain 50 and a leader for the grout
o = '            spot(zPlTop, 1, be[0] + 20); spot(zPlTop + (m.Success ? double.Parse(m.Groups[6].Value) : 300), 1, be[0] + 60);'
n = o + '''
            {   // 12.11 (тексеріс №32): plate bottom, foundation top −0.450 under the 50 mm grout, the grout itself
              var zF = L(new XYZ(cx, cy, -450) * M).Y; var dl = d.Create.NewDetailCurve(v, Line.CreateBound(W(be[0] - 150, zF), W(be[1] + 150, zF)));
              dim(new List<XYZ> { new XYZ(be[1], zF, 0), new XYZ(be[1], zb0, 0) }, false, be[1] + 90);
              var o3 = new TextNoteOptions(txtT.Id) { HorizontalAlignment = HorizontalTextAlignment.Left, VerticalAlignment = VerticalTextAlignment.Top };
              TextNote.Create(d, v.Id, W(be[1] + 160, zF - 20), "Верх фундамента -0,450", o3);
              leader(new XYZ(be[0] + 60, (zF + zb0) / 2, 0), -10, -6, "Подливка 50", "бетон В25", true); }'''
if o in s: s = s.replace(o, n, 1)
else: print("MISSING spot line")
# 4. plan: binding of the column to the axis of the row (outer face 210, axis offset 16) — №103
o2 = '            double topY = be[3] + 90 + 80 * Math.Max(nT - 1, 0);'
n2 = o2 + '''
            if (Math.Abs(cy - 6000) > 1000) {   // rows А / В
              double axY = cy < 6000 ? 0 : 12000; var axL = L(new XYZ(cx, axY, 0) * M); var faceL = L(new XYZ(cx, cy + (cy < 6000 ? -194 : 194), 0) * M);
              var dl = d.Create.NewDetailCurve(v, Line.CreateBound(W(be[0] - 470, axL.Y), W(be[1] + 470, axL.Y)));
              var cen = new FilteredElementCollector(d).OfClass(typeof(GraphicsStyle)).Cast<GraphicsStyle>().FirstOrDefault(x => x.Name.Contains("Осев") || x.Name.Contains("Center")); if (cen != null) dl.LineStyle = cen;
              dim(new List<XYZ> { new XYZ(be[0] - 430, axL.Y, 0), new XYZ(be[0] - 430, ctr0.Y, 0), new XYZ(be[0] - 430, faceL.Y, 0) }, false, be[0] - 430);
              var o4 = new TextNoteOptions(txtT.Id) { HorizontalAlignment = HorizontalTextAlignment.Left, VerticalAlignment = VerticalTextAlignment.Bottom };
              TextNote.Create(d, v.Id, W(be[1] + 300, axL.Y + 15), "ось " + (cy < 6000 ? "А" : "В"), o4); }'''
if o2 in s: s = s.replace(o2, n2, 1)
else: print("MISSING topY")
io.open(A + "v113_bases_sheets.cs", "w", encoding="utf-8").write(s)
print("ok")
