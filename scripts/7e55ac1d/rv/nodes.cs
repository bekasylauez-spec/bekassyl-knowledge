using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;

namespace RB
{
    // node sheets 11/12 like the DWG: outline drawing (section colours on the lines, no fill), crop and scale per node,
    // shelf marks at the member ends, width dims, plate notes, concrete + level under the bases, sheet layout and node bubbles
    public partial class App
    {
        class NCtx
        {
            public View V; public XYZ O, R, Up; public double S;
            public XYZ P(double u, double w) { return O + R * (u * MM) + Up * (w * MM); }
            public double U(XYZ p) { return (p - O).DotProduct(R) / MM; }
            public double W(XYZ p) { return (p - O).DotProduct(Up) / MM; }
        }

        // node, world centre (mm), crop width x height (mm, model), scale
        static readonly object[][] NodeSpec = {
            new object[]{ "1", new XYZ(4350, 0, 950), 620.0, 620.0, 10 },
            new object[]{ "2", new XYZ(4350, 8800, 950), 560.0, 620.0, 10 },
            new object[]{ "3", new XYZ(4350, 0, 4030), 750.0, 750.0, 15 },
            new object[]{ "4", new XYZ(4350, 3650, 4125), 1000.0, 800.0, 15 },
            new object[]{ "5", new XYZ(4350, 5200, 3150), 1000.0, 900.0, 15 },
            new object[]{ "6", new XYZ(4350, 6975, 2400), 1500.0, 1900.0, 20 },
            new object[]{ "7", new XYZ(4350, 8775, 2025), 700.0, 600.0, 10 },
            new object[]{ "14", new XYZ(4350, -550, 4325), 800.0, 900.0, 15 },
            new object[]{ "8", new XYZ(11550, 7300, 0), 900.0, 900.0, 15 },
            new object[]{ "9", new XYZ(11550, 3650, 0), 900.0, 900.0, 15 },
            new object[]{ "10", new XYZ(9150, 7300, 2250), 900.0, 900.0, 15 },
            new object[]{ "11", new XYZ(10350, 7300, 1550), 900.0, 900.0, 15 },
            new object[]{ "12", new XYZ(10350, 7300, 2550), 1300.0, 700.0, 15 },
            new object[]{ "13", new XYZ(11550, 0, 975), 900.0, 900.0, 15 } };

        static NCtx NodeCtx(View v)
        {
            return new NCtx { V = v, O = v.Origin, R = v.RightDirection, Up = v.UpDirection, S = v.Scale };
        }

        // outside width of a tube as seen in the view: «□80х3» -> 80; «□140х100х4» -> 140 seen across the rows (1-1 views), 100 along them
        static double TubeWidth(FamilyInstance f, NCtx c)
        {
            Parameter p = f.LookupParameter("КМ_Сечение");
            string s = p != null ? (p.AsString() ?? "") : "";
            string[] parts = s.Replace("□", "").Replace("x", "х").Split('х');
            double a, b;
            if (parts.Length < 2 || !double.TryParse(parts[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out a)) return 0;
            if (parts.Length == 3 && double.TryParse(parts[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out b))
                return Math.Abs(c.R.Y) > 0.5 ? a : b;
            return a;
        }

        static void SetCropNode(View v, NCtx c, double cu, double cw, double w, double h)
        {
            BoundingBoxXYZ cb = v.CropBox;
            Transform inv = cb.Transform.Inverse;
            XYZ a = inv.OfPoint(c.P(cu - w / 2, cw - h / 2)), b = inv.OfPoint(c.P(cu + w / 2, cw + h / 2));
            cb.Min = new XYZ(Math.Min(a.X, b.X), Math.Min(a.Y, b.Y), cb.Min.Z);
            cb.Max = new XYZ(Math.Max(a.X, b.X), Math.Max(a.Y, b.Y), cb.Max.Z);
            v.CropBox = cb;
        }

        // segment of a member clipped to the crop rectangle (view coords), or null
        static double[] Clip(double u0, double w0, double u1, double w1, double minU, double maxU, double minW, double maxW)
        {
            double t0 = 0, t1 = 1, du = u1 - u0, dw = w1 - w0;
            double[] p = { -du, du, -dw, dw }, q = { u0 - minU, maxU - u0, w0 - minW, maxW - w0 };
            for (int i = 0; i < 4; i++)
            {
                if (Math.Abs(p[i]) < 1e-9) { if (q[i] < 0) return null; continue; }
                double r = q[i] / p[i];
                if (p[i] < 0) { if (r > t1) return null; if (r > t0) t0 = r; }
                else { if (r < t0) return null; if (r < t1) t1 = r; }
            }
            return new[] { u0 + t0 * du, w0 + t0 * dw, u0 + t1 * du, w0 + t1 * dw };
        }

        static void NodesLikeDwg(Document doc)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            DimensionType dimT = Find<DimensionType>(doc, x => x.Name == "КМ_СПДС");
            FilledRegionType ft = HatchType(doc);
            ViewSection v1 = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().First(x => x.Name == "1");
            Level l870 = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().FirstOrDefault(l => Math.Abs(l.Elevation / MM - 870) < 1);
            foreach (object[] ns in NodeSpec)
            {
                string nn = (string)ns[0];
                View v = new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>().FirstOrDefault(x => !x.IsTemplate && x.Name == "Узел " + nn);
                if (v == null) { L("  no node " + nn); continue; }
                try { v.Scale = (int)ns[4]; } catch (Exception ex) { L("  scale " + nn + " " + ex.Message); }
                NCtx c = NodeCtx(v);
                XYZ cen = ((XYZ)ns[1]) * MM;
                double cu = c.U(cen), cw = c.W(cen), w = (double)ns[2], h = (double)ns[3];
                bool plan = v is ViewPlan;
                if (plan) cw = c.W(new XYZ(cen.X, cen.Y, c.O.Z));
                SetCropNode(v, c, cu, cw, w, h);
                try { v.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE).Set(1); ViewCropRegionShapeManager sm = v.GetCropRegionShapeManager(); sm.LeftAnnotationCropOffset = 10 * MM; sm.RightAnnotationCropOffset = 10 * MM; sm.TopAnnotationCropOffset = 9 * MM; sm.BottomAnnotationCropOffset = 9 * MM; } catch { }
                // outline drawing: section colour on the lines only
                foreach (ElementId fid in v.GetFilters())
                {
                    OverrideGraphicSettings o0 = v.GetFilterOverrides(fid);
                    Color col = o0.ProjectionLineColor;
                    if (!col.IsValid) continue;
                    OverrideGraphicSettings o = new OverrideGraphicSettings();
                    o.SetProjectionLineColor(col); o.SetCutLineColor(col);
                    v.SetFilterOverrides(fid, o);
                }
                // old marks / notes / dims / hatch in the view
                foreach (ElementId id in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().Where(e => e is IndependentTag || e is TextNote || e is Dimension || e is FilledRegion || e is DetailCurve).Select(e => e.Id).ToList())
                    if (doc.GetElement(id) != null) doc.Delete(id);
                doc.Regenerate();
                double minU = cu - w / 2, maxU = cu + w / 2, minW = cw - h / 2, maxW = cw + h / 2;
                // members in the crop, as 2D segments
                List<KeyValuePair<FamilyInstance, double[]>> segs = new List<KeyValuePair<FamilyInstance, double[]>>();
                foreach (FamilyInstance f in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().OfType<FamilyInstance>()
                    .Where(f => f.Category != null && (f.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || f.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)))
                {
                    if (f.IsHidden(v) || string.IsNullOrEmpty(Mk(f))) continue;
                    XYZ a, b;
                    if (f.Location is LocationCurve) { a = ((LocationCurve)f.Location).Curve.GetEndPoint(0); b = ((LocationCurve)f.Location).Curve.GetEndPoint(1); }
                    else { BoundingBoxXYZ bb = f.get_BoundingBox(null); XYZ p = ((LocationPoint)f.Location).Point; a = new XYZ(p.X, p.Y, bb.Min.Z); b = new XYZ(p.X, p.Y, bb.Max.Z); }
                    double[] s = Clip(c.U(a), c.W(a), c.U(b), c.W(b), minU, maxU, minW, maxW);
                    if (s == null) continue;
                    double len = Math.Sqrt(Math.Pow(s[2] - s[0], 2) + Math.Pow(s[3] - s[1], 2));
                    if (len < 0.15 * Math.Min(w, h)) continue;
                    segs.Add(new KeyValuePair<FamilyInstance, double[]>(f, s));
                }
                // shelf marks at the member ends (one per mark and side), leader to the member
                List<double[]> placed = new List<double[]>();
                HashSet<string> dimDone = new HashSet<string>();
                List<double[]> dimAt = new List<double[]>();
                int nm = 0, nd = 0;
                foreach (var kv in segs.OrderBy(k => Mk(k.Key).StartsWith("СВ") ? 0 : 1).ThenBy(k => Mk(k.Key)))
                {
                    double[] s = kv.Value;
                    // the end farther from the node centre
                    bool firstFar = Math.Pow(s[0] - cu, 2) + Math.Pow(s[1] - cw, 2) > Math.Pow(s[2] - cu, 2) + Math.Pow(s[3] - cw, 2);
                    double eu = firstFar ? s[0] : s[2], ew = firstFar ? s[1] : s[3], iu = firstFar ? s[2] : s[0], iw = firstFar ? s[3] : s[1];
                    double dU = eu - iu, dW = ew - iw, L0 = Math.Sqrt(dU * dU + dW * dW); dU /= L0; dW /= L0;
                    double nU0 = -dW, nW0 = dU;
                    string mk = Mk(kv.Key);
                    // the same member line already labelled (coincident members, e.g. РС1 under СВ3): skip
                    if (placed.Any(p => p.Length > 5 && Math.Abs(p[3] - (iu + eu) / 2) < 30 && Math.Abs(p[4] - (iw + ew) / 2) < 30 && Math.Abs(p[5] * dU + p[6] * dW) > 0.98)) continue;
                    // candidates: away from the centre / the other side, at 72 %, 50 %, 88 % of the way out; first one free of other labels
                    double au = 0, aw = 0, tu = 0, tw = 0; bool found = false;
                    foreach (double fr in new[] { 0.72, 0.5, 0.88 })
                    {
                        double cau = iu + (eu - iu) * fr, caw = iw + (ew - iw) * fr;
                        double sgn = (cau - cu) * nU0 + (caw - cw) * nW0 < 0 ? -1 : 1;
                        foreach (double side in new[] { sgn, -sgn })
                        {
                            double nU = nU0 * side, nW = nW0 * side;
                            if (Math.Abs(nU) < 0.2 && Math.Abs(nW) > 0.9) nU = side * 0.8;   // vertical member: text beside it
                            double ctu = cau + (nU * 9 + dU * 3) * c.S, ctw = caw + (nW * 7 + dW * 3) * c.S;
                            if (placed.Any(p => Math.Abs(p[0] - ctu) < 13 * c.S && Math.Abs(p[1] - ctw) < 6 * c.S)) continue;
                            au = cau; aw = caw; tu = ctu; tw = ctw; found = true; break;
                        }
                        if (found) break;
                    }
                    if (!found) continue;
                    if (t25 != null)
                    {
                        TextNoteOptions o = new TextNoteOptions(t25.Id);
                        o.HorizontalAlignment = tu >= au ? HorizontalTextAlignment.Left : HorizontalTextAlignment.Right; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                        TextNote tn = TextNote.Create(doc, v.Id, c.P(tu, tw), mk, o);
                        FormattedText fmt = tn.GetFormattedText(); fmt.SetUnderlineStatus(true); tn.SetFormattedText(fmt);
                        try { Leader ld = tn.AddLeader(tu >= au ? TextNoteLeaderTypes.TNLT_STRAIGHT_L : TextNoteLeaderTypes.TNLT_STRAIGHT_R); ld.End = c.P(au, aw); } catch { }
                        placed.Add(new[] { tu, tw, mk.GetHashCode(), (iu + eu) / 2, (iw + ew) / 2, dU, dW }); nm++;
                    }
                    // width dim across the member near its end (once per mark)
                    // (the tube families' side planes are the template's, so the width comes from the section: two short lines on the tube faces)
                    double width = TubeWidth(kv.Key, c);
                    double pu = iu + (eu - iu) * 0.86, pw = iw + (ew - iw) * 0.86, hl = 1.5 * c.S;
                    bool dimFree = !dimAt.Any(p => Math.Abs(p[0] - pu) < 8 * c.S && Math.Abs(p[1] - pw) < 8 * c.S);
                    if (dimT != null && !plan && width > 0 && !dimDone.Contains(mk) && dimFree)
                    {
                        dimAt.Add(new[] { pu, pw });
                        double mU = -dW, mW = dU;   // unit normal to the member in the view
                        try
                        {
                            ReferenceArray ra = new ReferenceArray();
                            foreach (double sg in new[] { -1.0, 1.0 })
                            {
                                double qu = pu + mU * sg * width / 2, qw = pw + mW * sg * width / 2;
                                DetailCurve dc = doc.Create.NewDetailCurve(v, Line.CreateBound(c.P(qu - dU * hl, qw - dW * hl), c.P(qu + dU * hl, qw + dW * hl)));
                                ra.Append(dc.GeometryCurve.Reference);
                            }
                            doc.Create.NewDimension(v, Line.CreateBound(c.P(pu + dU * 4 * c.S, pw + dW * 4 * c.S), c.P(pu + dU * 4 * c.S + mU * 100, pw + dW * 4 * c.S + mW * 100)), ra, dimT);
                            dimDone.Add(mk); nd++;
                        }
                        catch (Exception ex) { L("  width dim " + mk + " " + ex.Message.Split('\n')[0]); }
                    }
                }
                // plates: «-tN / С245» once per kind, leader to the plate
                foreach (var g in new FilteredElementCollector(doc, v.Id).OfCategory(BuiltInCategory.OST_GenericModel).WhereElementIsNotElementType().Where(e => !e.IsHidden(v))
                    .Where(e => { BoundingBoxXYZ bb = e.get_BoundingBox(null); if (bb == null) return false; XYZ m = (bb.Min + bb.Max) / 2; return c.U(m) > minU && c.U(m) < maxU && (plan || (c.W(m) > minW && c.W(m) < maxW)); })
                    .GroupBy(e => Mk(e) ?? ""))
                {
                    if (!g.Key.StartsWith("-t") || t25 == null) continue;
                    BoundingBoxXYZ bb = g.First().get_BoundingBox(null); XYZ m = (bb.Min + bb.Max) / 2;
                    double pu = c.U(m), pw = plan ? cw : c.W(m);
                    double tu = pu + (pu < cu ? -14 : 12) * c.S, tw = pw + 9 * c.S;
                    for (int k = 0; k < 6 && placed.Any(p => Math.Abs(p[0] - tu) < 13 * c.S && Math.Abs(p[1] - tw) < 9 * c.S); k++) tw -= 11 * c.S;   // stack under the others
                    placed.Add(new[] { tu, tw, 0, 1e9, 1e9 });
                    TextNoteOptions o = new TextNoteOptions(t25.Id);
                    o.HorizontalAlignment = tu >= pu ? HorizontalTextAlignment.Left : HorizontalTextAlignment.Right; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                    string txt = "-" + g.Key.Substring(1) + "\rС245";
                    TextNote tn = TextNote.Create(doc, v.Id, c.P(tu, tw), txt, o);
                    FormattedText fmt = tn.GetFormattedText(); fmt.SetUnderlineStatus(new TextRange(0, txt.IndexOf('\r')), true); tn.SetFormattedText(fmt);
                    try { Leader ld = tn.AddLeader(tu >= pu ? TextNoteLeaderTypes.TNLT_STRAIGHT_L : TextNoteLeaderTypes.TNLT_STRAIGHT_R); ld.End = c.P(pu, pw); } catch { }
                    nm++;
                }
                // bases: concrete under the column and the +0,870 level
                if (nn == "1" || nn == "2" || nn == "13")
                {
                    FamilyInstance col = segs.Select(k => k.Key).FirstOrDefault(f => f.Location is LocationPoint);
                    if (col != null)
                    {
                        double ux = c.U(((LocationPoint)col.Location).Point), zb = c.W(new XYZ(c.O.X, c.O.Y, col.get_BoundingBox(null).Min.Z));
                        double w870 = c.W(new XYZ(c.O.X, c.O.Y, 870 * MM));
                        double half = nn == "1" ? 140 : nn == "2" ? 90 : 125;
                        CurveLoop cl = new CurveLoop();
                        XYZ a0 = c.P(ux - half, zb - 250), a1 = c.P(ux + half, zb - 250), a2 = c.P(ux + half, zb), a3 = c.P(ux - half, zb);
                        cl.Append(Line.CreateBound(a0, a1)); cl.Append(Line.CreateBound(a1, a2)); cl.Append(Line.CreateBound(a2, a3)); cl.Append(Line.CreateBound(a3, a0));
                        try { FilledRegion.Create(doc, ft.Id, v.Id, new List<CurveLoop> { cl }); } catch (Exception ex) { L("  concrete " + nn + " " + ex.Message); }
                        if (l870 != null)
                        {
                            try
                            {
                                v.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), false);
                                List<ElementId> other = new FilteredElementCollector(doc, v.Id).OfClass(typeof(Level)).ToElementIds().Where(id => id != l870.Id).ToList();
                                if (other.Count > 0) v.HideElements(other);
                                if (l870.IsHidden(v)) v.UnhideElements(new List<ElementId> { l870.Id });
                                l870.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific); l870.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific);
                                Curve cur = l870.GetCurvesInView(DatumExtentType.ViewSpecific, v)[0];
                                XYZ pa = c.P(ux - half - 150, w870), pb = c.P(ux - half - 30, w870);
                                bool same = (cur.GetEndPoint(1) - cur.GetEndPoint(0)).DotProduct(pb - pa) > 0;
                                l870.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(pa, pb) : Line.CreateBound(pb, pa));
                                DatumEnds le = same ? DatumEnds.End0 : DatumEnds.End1, re = same ? DatumEnds.End1 : DatumEnds.End0;
                                l870.ShowBubbleInView(le, v); l870.HideBubbleInView(re, v);
                            }
                            catch (Exception ex) { L("  level " + nn + " " + ex.Message.Split('\n')[0]); }
                        }
                    }
                }
                L("  node " + nn + ": members " + segs.Count + ", marks " + nm + ", dims " + nd);
            }
            foreach (string sn in new[] { "Разрез а-а", "Разрез б-б" })
            {
                View sv = new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>().FirstOrDefault(x => !x.IsTemplate && x.Name == sn);
                if (sv != null) try { sv.Scale = 15; } catch { }
            }
            doc.Regenerate();
            NodeSheets(doc);
        }

        // sheets 11/12: rows of nodes with the drawn bubble (number / parent sheet) over each
        static void NodeSheets(Document doc)
        {
            TextNoteType tTitle = new FilteredElementCollector(doc).OfClass(typeof(TextNoteType)).Cast<TextNoteType>().FirstOrDefault(x => x.Name.StartsWith("КМ_Заголовок")) ?? Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            Dictionary<string, string> par = new Dictionary<string, string> { { "8", "5" }, { "9", "5" }, { "10", "9" }, { "11", "9" }, { "12", "9" }, { "13", "9" } };
            foreach (object[] sd in new[] { new object[] { "11", new[] { "Узел 1", "Разрез а-а", "Узел 2", "Разрез б-б", "Узел 3", "|", "Узел 6", "Узел 4", "Узел 5" } },
                                            new object[] { "12", new[] { "Узел 7", "Узел 8", "Узел 9", "Узел 10", "|", "Узел 11", "Узел 12", "Узел 13", "Узел 14" } } })
            {
                ViewSheet sh = Sheet(doc, (string)sd[0]);
                if (sh == null) continue;
                // old bubbles: detail curves and the small number texts outside the stamp
                foreach (Element e in new FilteredElementCollector(doc, sh.Id).WhereElementIsNotElementType().ToList())
                {
                    if (e is DetailCurve) { doc.Delete(e.Id); continue; }
                    TextNote t = e as TextNote;
                    if (t == null) continue;
                    string s = (t.Text ?? "").Trim();
                    bool stamp = t.Coord.X / MM > 228 && t.Coord.Y / MM < 55;
                    if (!stamp && s.Length <= 2 && s.All(char.IsDigit)) doc.Delete(e.Id);
                }
                List<Viewport> vps = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(Viewport)).Cast<Viewport>().ToList();
                double x = 28, top = 270, rowH = 0;
                foreach (string name in (string[])sd[1])
                {
                    if (name == "|") { x = 28; top -= rowH + 30; rowH = 0; continue; }
                    Viewport vp = vps.FirstOrDefault(q => ((View)doc.GetElement(q.ViewId)).Name == name || ((View)doc.GetElement(q.ViewId)).Name == name.Replace("-", " - "));
                    if (vp == null) { L("  no viewport " + name); continue; }
                    Outline o = vp.GetBoxOutline();
                    double wv = (o.MaximumPoint.X - o.MinimumPoint.X) / MM, hv = (o.MaximumPoint.Y - o.MinimumPoint.Y) / MM;
                    if (x + wv > 412 && x > 30) { x = 28; top -= rowH + 30; rowH = 0; }   // wrap
                    ElementTransformUtils.MoveElement(doc, vp.Id, new XYZ(x * MM - o.MinimumPoint.X, top * MM - o.MaximumPoint.Y, 0));
                    o = vp.GetBoxOutline();
                    double cx = (o.MinimumPoint.X + o.MaximumPoint.X) / 2 / MM, ty = o.MaximumPoint.Y / MM;
                    if (name.StartsWith("Узел"))
                    {
                        string nn = name.Substring(5), ps = par.ContainsKey(nn) ? par[nn] : "7";
                        XYZ cc = new XYZ(cx * MM, (ty + 9) * MM, 0);
                        doc.Create.NewDetailCurve(sh, Arc.Create(cc, 6 * MM, 0, 2 * Math.PI, XYZ.BasisX, XYZ.BasisY));
                        doc.Create.NewDetailCurve(sh, Line.CreateBound(new XYZ((cx - 6) * MM, (ty + 9) * MM, 0), new XYZ((cx + 6) * MM, (ty + 9) * MM, 0)));
                        Txt(doc, sh.Id, cx, ty + 12, nn, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                        Txt(doc, sh.Id, cx, ty + 6, ps, tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                    }
                    else
                    {
                        string tt = name.Replace("-", " - ");
                        TextNote title = new FilteredElementCollector(doc, sh.Id).OfClass(typeof(TextNote)).Cast<TextNote>().FirstOrDefault(t => (t.Text ?? "").Trim() == tt);
                        if (title != null) ElementTransformUtils.MoveElement(doc, title.Id, new XYZ(cx * MM, (ty + 4) * MM, 0) - title.Coord);
                    }
                    L("  sheet " + sd[0] + " " + name + " " + Math.Round(wv) + "x" + Math.Round(hv) + " at " + Math.Round(x) + "," + Math.Round(top));
                    x += wv + 10; rowH = Math.Max(rowH, hv);
                }
            }
        }
    }
}
