k = open('km2.cs', encoding='utf-8').read()


def rep(a, b):
    global k
    assert a in k, a[:80]
    k = k.replace(a, b)


# plan bubbles: decide by the curve as shown in that view, put the bubble on the lower / left end
rep('''                        Line c = (Line)g.Curve;
                        bool vert = Math.Abs(c.Direction.Y) > 0.9;
                        XYZ a0 = c.GetEndPoint(0), a1 = c.GetEndPoint(1);
                        bool lowIs0 = vert ? a0.Y < a1.Y : a0.X < a1.X;
                        try { g.ShowBubbleInView(lowIs0 ? DatumEnds.End0 : DatumEnds.End1, V[k]); g.HideBubbleInView(lowIs0 ? DatumEnds.End1 : DatumEnds.End0, V[k]); }
                        catch (Exception ex) { L("bubble " + ex.Message); }''',
'''                        try
                        {
                            Curve c = g.GetCurvesInView(DatumExtentType.Model, V[k])[0];
                            XYZ a0 = c.GetEndPoint(0), a1 = c.GetEndPoint(1);
                            bool vert = Math.Abs(a0.X - a1.X) < Math.Abs(a0.Y - a1.Y);
                            bool lowIs0 = vert ? a0.Y < a1.Y : a0.X < a1.X;
                            g.HideBubbleInView(DatumEnds.End0, V[k]); g.HideBubbleInView(DatumEnds.End1, V[k]);
                            g.ShowBubbleInView(lowIs0 ? DatumEnds.End0 : DatumEnds.End1, V[k]);
                            if (k == "p3" && g.Name == "1") L("  bubble grid 1: end0 " + Math.Round(a0.Y / MM) + " end1 " + Math.Round(a1.Y / MM) + " show " + (lowIs0 ? "End0" : "End1") + " vis0 " + g.IsBubbleVisibleInView(DatumEnds.End0, V[k]) + " vis1 " + g.IsBubbleVisibleInView(DatumEnds.End1, V[k]));
                        }
                        catch (Exception ex) { L("bubble " + ex.Message); }''')
# level model extents: along X (seen in 3-3) and along Y (seen in 1-1), so both sections see the levels
rep('''                List<Level> levels = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().ToList();''',
'''                List<Level> levels = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().ToList();
                foreach (Level lv in levels)
                {
                    try
                    {
                        Curve c3 = lv.GetCurvesInView(DatumExtentType.Model, V["3-3"])[0];
                        double yy = c3.GetEndPoint(0).Y;
                        lv.SetCurveInView(DatumExtentType.Model, V["3-3"], Line.CreateBound(new XYZ(-4000 * MM, yy, lv.Elevation), new XYZ(28000 * MM, yy, lv.Elevation)));
                        Curve c1 = lv.GetCurvesInView(DatumExtentType.Model, V["1-1"])[0];
                        double xx = c1.GetEndPoint(0).X;
                        lv.SetCurveInView(DatumExtentType.Model, V["1-1"], Line.CreateBound(new XYZ(xx, -4000 * MM, lv.Elevation), new XYZ(xx, 12000 * MM, lv.Elevation)));
                    }
                    catch (Exception ex) { L("level model ext " + ex.Message); }
                }''')
rep('''                lvTop.Elevation = 4620 * MM; lvTop.Name = "Верх покрытия";''',
'''                lvTop.Elevation = 4620 * MM; lvTop.Name = "Верх покрытия";
                if (lvBase.GetTypeId() != lvTop.GetTypeId()) lvBase.ChangeTypeId(lvTop.GetTypeId());''')
open('km2.cs', 'w', encoding='utf-8').write(k)
print('patched')
