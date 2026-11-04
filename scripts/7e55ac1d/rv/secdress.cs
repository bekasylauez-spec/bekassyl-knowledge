using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;

namespace RB
{
    // sections 1-1 .. 4-4 dressed like the DWG (sheets 7-9): level set per view (left/right heads), level dim chains,
    // member marks (shelf tags in 1-1/2-2, marks along members in 3-3/4-4), foundation hatch
    public partial class App
    {
        // elevations (mm) shown per section, heads on the left (L) or right (R); 870 = both sides in 1-1 / 2-2
        static readonly Dictionary<string, string> SecLevels = new Dictionary<string, string> {
            { "1", "L:4620,4040,870;R:2810,2300,2030,870" },
            { "2", "L:4620,4040,870;R:2810,870" },
            { "3", "L:2920,2300,870" },
            { "4", "L:4620,4040,870" },
            { "СВ1", "R:2300,870" }, { "СВ2", "R:4040,870" }, { "СВ3", "" } };
        static readonly Dictionary<string, string> SecDims = new Dictionary<string, string> {
            { "1", "L:870,4040,4620|870,4620;R:870,2030,2300,2810|870,2810" },
            { "2", "L:870,4040,4620|870,4620;R:870,2810" },
            { "3", "L:870,2300,2920" },
            { "4", "L:870,4040,4620" },
            { "СВ1", "R:870,2300" }, { "СВ2", "R:870,4040" }, { "СВ3", "" } };

        class SecCtx
        {
            public ViewSection V; public XYZ O, R; public double S;   // origin on the cut plane, screen right, mm per paper mm
            public XYZ P(double u, double z) { return O + R * (u * MM) + new XYZ(0, 0, z * MM - O.Z); }
            public double U(XYZ p) { return (p - O).DotProduct(R) / MM; }
        }

        static Level LevelAt(Document doc, double mm, ElementId typeId)
        {
            Level l = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().FirstOrDefault(x => Math.Abs(x.Elevation / MM - mm) < 1);
            if (l != null) return l;
            l = Level.Create(doc, mm * MM);
            try { l.Name = "Отм. " + (mm / 1000).ToString("0.000").Replace(".", ","); } catch { }
            if (typeId != null && l.GetTypeId() != typeId) l.ChangeTypeId(typeId);
            L("  level " + mm + " created");
            return l;
        }

        static FilledRegionType HatchType(Document doc)
        {
            FilledRegionType ft = Find<FilledRegionType>(doc, x => x.Name == "КМ_Бетон");
            if (ft != null) return ft;
            FillPatternElement fp = Find<FillPatternElement>(doc, x => x.Name == "КМ_Штриховка 45");
            if (fp == null)
            {
                FillPattern pat = new FillPattern("КМ_Штриховка 45", FillPatternTarget.Drafting, FillPatternHostOrientation.ToView, Math.PI / 4, 1.5 * MM);
                fp = FillPatternElement.Create(doc, pat);
            }
            FilledRegionType b = Find<FilledRegionType>(doc, x => true);
            ft = (FilledRegionType)b.Duplicate("КМ_Бетон");
            ft.ForegroundPatternId = fp.Id;
            ft.ForegroundPatternColor = new Color(0, 0, 0);
            try { ft.BackgroundPatternId = ElementId.InvalidElementId; } catch { }
            try { ft.IsMasking = false; } catch { }
            return ft;
        }

        static void HatchRect(Document doc, SecCtx c, FilledRegionType ft, double u0, double u1, double z0, double z1)
        {
            CurveLoop cl = new CurveLoop();
            XYZ a = c.P(u0, z0), b = c.P(u1, z0), d = c.P(u1, z1), e = c.P(u0, z1);
            cl.Append(Line.CreateBound(a, b)); cl.Append(Line.CreateBound(b, d)); cl.Append(Line.CreateBound(d, e)); cl.Append(Line.CreateBound(e, a));
            FilledRegion.Create(doc, ft.Id, c.V.Id, new List<CurveLoop> { cl });
        }

        static TextNote SecText(Document doc, SecCtx c, TextNoteType tt, double u, double z, string s, double rot, HorizontalTextAlignment ha, VerticalTextAlignment va, bool underline)
        {
            TextNoteOptions o = new TextNoteOptions(tt.Id); o.HorizontalAlignment = ha; o.VerticalAlignment = va; o.Rotation = rot;
            TextNote tn = TextNote.Create(doc, c.V.Id, c.P(u, z), s, o);
            if (underline) { FormattedText f = tn.GetFormattedText(); f.SetUnderlineStatus(true); tn.SetFormattedText(f); }
            return tn;
        }

        static void SecDress(Document doc, FamilySymbol inlineUp)
        {
            TextNoteType t25 = Find<TextNoteType>(doc, x => x.Name == "КМ_ISOCPEUR 2,5");
            DimensionType dimT = Find<DimensionType>(doc, x => x.Name == "КМ_СПДС") ?? Find<DimensionType>(doc, x => x.StyleType == DimensionStyleType.Linear);
            FamilySymbol tagCol = new FilteredElementCollector(doc).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "КМ_Марка колонны");
            FamilySymbol tagBeam = new FilteredElementCollector(doc).OfClass(typeof(FamilySymbol)).Cast<FamilySymbol>().FirstOrDefault(x => x.FamilyName == "КМ_Марка каркаса");
            Level top = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().OrderByDescending(x => x.Elevation).First();
            FilledRegionType ft = HatchType(doc);
            foreach (double mm in new[] { 4040.0, 2920, 2810, 2300, 2030 }) LevelAt(doc, mm, top.GetTypeId());
            doc.Regenerate();
            List<Level> levels = new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>().ToList();
            // model extents long enough for every section (as the build does for the two original levels)
            ViewSection v1 = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => x.Name == "1");
            ViewSection v3 = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => x.Name == "3");
            foreach (Level lv in levels)
            {
                try
                {
                    Curve c3 = lv.GetCurvesInView(DatumExtentType.Model, v3)[0]; double yy = c3.GetEndPoint(0).Y;
                    lv.SetCurveInView(DatumExtentType.Model, v3, Line.CreateBound(new XYZ(-4000 * MM, yy, lv.Elevation), new XYZ(28000 * MM, yy, lv.Elevation)));
                    Curve c1 = lv.GetCurvesInView(DatumExtentType.Model, v1)[0]; double xx = c1.GetEndPoint(0).X;
                    lv.SetCurveInView(DatumExtentType.Model, v1, Line.CreateBound(new XYZ(xx, -4000 * MM, lv.Elevation), new XYZ(xx, 12000 * MM, lv.Elevation)));
                    Curve m1 = lv.GetCurvesInView(DatumExtentType.Model, v1)[0];
                    L("  level " + Math.Round(lv.Elevation / MM) + " model in 1: " + P3(m1.GetEndPoint(0)) + "->" + P3(m1.GetEndPoint(1)) + " ends " + lv.GetDatumExtentTypeInView(DatumEnds.End0, v1) + "/" + lv.GetDatumExtentTypeInView(DatumEnds.End1, v1));
                }
                catch (Exception ex) { L("  level model ext " + lv.Name + ": " + ex.Message); }
            }
            doc.Regenerate();

            foreach (string key in SecLevels.Keys)
            {
                ViewSection v = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().FirstOrDefault(x => !x.IsTemplate && x.Name == key);
                if (v == null) { L("  no section " + key); continue; }
                SecCtx c = new SecCtx { V = v, O = v.Origin, R = v.RightDirection, S = v.Scale };
                bool det = key.StartsWith("СВ");
                // members seen in this view
                List<FamilyInstance> mem = new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType().OfType<FamilyInstance>()
                    .Where(e => e.Category != null && (e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns)).Where(e => !e.IsHidden(v)).ToList();
                // СГ1 is not drawn on 3-3 / 4-4
                if (key == "3" || key == "4")
                {
                    ParameterFilterElement fsg = Find<ParameterFilterElement>(doc, x => x.Name == "КМ_СГ1");
                    if (fsg != null && v.IsFilterApplied(fsg.Id)) v.SetFilterVisibility(fsg.Id, false);
                    mem = mem.Where(e => Mk(e) != "СГ1").ToList();
                }
                Func<FamilyInstance, XYZ[]> ends = e => e.Location is LocationCurve ? new[] { ((LocationCurve)e.Location).Curve.GetEndPoint(0), ((LocationCurve)e.Location).Curve.GetEndPoint(1) }
                    : new[] { ((LocationPoint)e.Location).Point, ((LocationPoint)e.Location).Point };
                List<FamilyInstance> cols = mem.Where(e => e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns).ToList();
                Func<FamilyInstance, double[]> colZ = e => { BoundingBoxXYZ bb = e.get_BoundingBox(null); return new[] { bb.Min.Z / MM, bb.Max.Z / MM }; };
                if (mem.Count == 0) { L("  section " + key + ": nothing visible"); continue; }
                double uMin = mem.SelectMany(e => ends(e)).Min(p => c.U(p)), uMax = mem.SelectMany(e => ends(e)).Max(p => c.U(p));
                // the crop must leave room for the right-hand level marks and dims (levels cannot run past the crop)
                if (SecLevels[key].Contains("R:"))
                {
                    BoundingBoxXYZ cb = v.CropBox;
                    double need = uMax + (det ? 550 : 1100) + 20 * v.Scale + (det ? 100 : 300);
                    XYZ wMax = cb.Transform.OfPoint(cb.Max), wMin = cb.Transform.OfPoint(cb.Min);
                    double cropR = Math.Max(c.U(wMax), c.U(wMin));
                    if (cropR < need)
                    {
                        bool maxIsRight = c.U(wMax) > c.U(wMin);
                        double add = (need - cropR) * MM;
                        if (maxIsRight == (cb.Transform.BasisX.DotProduct(c.R) > 0)) cb.Max = cb.Max + new XYZ(add, 0, 0); else cb.Min = cb.Min - new XYZ(add, 0, 0);
                        v.CropBox = cb;
                        L("  crop " + key + " widened by " + Math.Round(add / MM));
                    }
                }
                L("  section " + key + ": members " + mem.Count + ", columns " + cols.Count + ", u " + Math.Round(uMin) + ".." + Math.Round(uMax));

                // old level dims and old marks/notes/hatch in this view
                foreach (Dimension d in new FilteredElementCollector(doc, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>().ToList())
                {
                    bool lv = true; foreach (Reference r in d.References) if (!(doc.GetElement(r.ElementId) is Level)) lv = false;
                    if (lv) doc.Delete(d.Id);
                }
                foreach (IndependentTag tg in new FilteredElementCollector(doc, v.Id).OfClass(typeof(IndependentTag)).ToElements().ToList()) doc.Delete(tg.Id);
                foreach (TextNote tn in new FilteredElementCollector(doc, v.Id).OfClass(typeof(TextNote)).Cast<TextNote>().ToList()) doc.Delete(tn.Id);
                foreach (FilledRegion fr in new FilteredElementCollector(doc, v.Id).OfClass(typeof(FilledRegion)).ToElements().ToList()) doc.Delete(fr.Id);

                // levels: wanted ones get a short line at the side, the others are hidden here
                Dictionary<double, string> want = new Dictionary<double, string>();
                foreach (string part in SecLevels[key].Split(';').Where(s => s.Length > 2))
                    foreach (string z in part.Substring(2).Split(',')) { double zz = double.Parse(z); want[zz] = want.ContainsKey(zz) ? "B" : part.Substring(0, 1); }
                List<ElementId> hideLv = new List<ElementId>();
                double gap = det ? 400 : 900, gapR = det ? 550 : key == "2" ? 700 : 1100, len = 20 * c.S;
                foreach (Level lv in levels)
                {
                    double el = Math.Round(lv.Elevation / MM);
                    if (!want.ContainsKey(el)) { if (lv.CanBeHidden(v) && !lv.IsHidden(v)) hideLv.Add(lv.Id); continue; }
                    if (lv.IsHidden(v)) v.UnhideElements(new List<ElementId> { lv.Id });
                    try
                    {
                        lv.SetDatumExtentType(DatumEnds.End0, v, DatumExtentType.ViewSpecific);
                        lv.SetDatumExtentType(DatumEnds.End1, v, DatumExtentType.ViewSpecific);
                        string side = want[el];
                        XYZ pa, pb;
                        if (side == "L") { pa = c.P(uMin - gap - len, el); pb = c.P(uMin - gap, el); }
                        else if (side == "R") { pa = c.P(uMax + gapR, el); pb = c.P(uMax + gapR + len, el); }
                        else { pa = c.P(uMin - gap - len, el); pb = c.P(uMax + gapR + len, el); }
                        // the view-specific curve must keep the datum's own direction
                        IList<Curve> cs = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v);
                        if (cs.Count == 0) cs = lv.GetCurvesInView(DatumExtentType.Model, v);
                        if (cs.Count == 0) { L("  level " + el + " in " + key + ": no curve"); continue; }
                        Curve cur = cs[0];
                        bool same = (cur.GetEndPoint(1) - cur.GetEndPoint(0)).DotProduct(pb - pa) > 0;
                        if (side == "R")
                        {
                            // a short line far from the old one is refused: first span the whole view, then shrink it to the right side
                            try { lv.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(pa, pb) : Line.CreateBound(pb, pa)); }
                            catch
                            {
                                XYZ fa = c.P(uMin - gap - len, el), fb = c.P(uMax + gapR + len, el);
                                lv.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(fa, fb) : Line.CreateBound(fb, fa));
                                try { lv.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(pa, pb) : Line.CreateBound(pb, pa)); }
                                catch (Exception ex2) { L("  level " + el + " R shrink: " + ex2.Message.Split('\n')[0]); }
                            }
                            IList<Curve> now = lv.GetCurvesInView(DatumExtentType.ViewSpecific, v);
                            if (det && now.Count > 0) L("  level " + el + " in " + key + ": u " + Math.Round(c.U(now[0].GetEndPoint(0))) + ".." + Math.Round(c.U(now[0].GetEndPoint(1))));
                        }
                        else lv.SetCurveInView(DatumExtentType.ViewSpecific, v, same ? Line.CreateBound(pa, pb) : Line.CreateBound(pb, pa));
                        // bubble at the outer end: left end for L, right end for R
                        DatumEnds leftEnd = same ? DatumEnds.End0 : DatumEnds.End1, rightEnd = same ? DatumEnds.End1 : DatumEnds.End0;
                        if (side == "L" || side == "B") lv.ShowBubbleInView(leftEnd, v); else lv.HideBubbleInView(leftEnd, v);
                        if (side == "R" || side == "B") lv.ShowBubbleInView(rightEnd, v); else lv.HideBubbleInView(rightEnd, v);
                    }
                    catch (Exception ex)
                    {
                        string dbg = "";
                        try { foreach (DatumExtentType t in new[] { DatumExtentType.Model, DatumExtentType.ViewSpecific }) foreach (Curve cc in lv.GetCurvesInView(t, v)) dbg += " " + t + " " + P3(cc.GetEndPoint(0)) + "->" + P3(cc.GetEndPoint(1)); } catch { }
                        L("  level " + el + " in " + key + ": " + ex.Message.Split('\n')[0] + " |" + dbg + " | want u " + Math.Round(uMax + gap) + ".." + Math.Round(uMax + gap + len) + " O " + P3(c.O) + " R " + P3(c.R * 1000 * MM));
                    }
                }
                if (hideLv.Count > 0) v.HideElements(hideLv);

                // level dim chains, left and right of the structure
                if (dimT != null)
                    foreach (string part in SecDims[key].Split(';').Where(s => s.Length > 2))
                    {
                        bool left = part.StartsWith("L");
                        string[] chains = part.Substring(2).Split('|');
                        for (int i = 0; i < chains.Length; i++)
                        {
                            ReferenceArray ra = new ReferenceArray();
                            foreach (string z in chains[i].Split(','))
                            {
                                Level lv = levels.FirstOrDefault(x => Math.Abs(x.Elevation / MM - double.Parse(z)) < 1);
                                if (lv != null) ra.Append(new Reference(lv));
                            }
                            double off = (300 + 400 * i) * c.S / 50;
                            double u = left ? uMin - off : uMax + (det ? 300 : 300) + off;
                            try { doc.Create.NewDimension(v, Line.CreateBound(c.P(u, 0), c.P(u, 1000)), ra, dimT); }
                            catch (Exception ex) { L("  dim " + key + " " + chains[i] + ": " + ex.Message); }
                        }
                    }

                if (det) { if (t25 != null) BraceNotes(doc, c, t25, mem); continue; }
                // foundation: pedestals under the columns (1-1, 2-2), a strip along the row (3-3, 4-4)
                double zb = cols.Count > 0 ? cols.Min(e => colZ(e)[0]) : 870;
                if (key == "1" || key == "2")
                    foreach (double cu in cols.Select(e => Math.Round(c.U(ends(e)[0]))).Distinct()) HatchRect(doc, c, ft, cu - 200, cu + 200, zb - 500, zb);
                else if (cols.Count > 0)
                    HatchRect(doc, c, ft, cols.Min(e => c.U(ends(e)[0])) - 700, cols.Max(e => c.U(ends(e)[0])) + 700, zb - 500, zb);
                // horizontal dim chains go under the foundation (DWG), 9 mm apart; grid bubbles under the last chain
                List<Dimension> hd = new FilteredElementCollector(doc, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>()
                    .Where(d => d.Curve is Line && Math.Abs(((Line)d.Curve).Direction.Z) < 0.01).OrderByDescending(d => d.Curve.Evaluate(0, false).Z)
                    .ToList();
                double zLast = zb - 500;
                double zTopAll = mem.SelectMany(e => ends(e)).Max(p => p.Z / MM);
                // 1-1 / 2-2: the panel chain (many refs) stays over the truss
                List<Dimension> panel = (key == "1" || key == "2") ? hd.Where(d => d.References.Size >= 6).ToList() : new List<Dimension>();
                foreach (Dimension d in panel)
                {
                    double zNow = d.Curve.Evaluate(0, false).Z / MM, zWant = zTopAll + 8 * c.S;
                    if (Math.Abs(zNow - zWant) > 1) ElementTransformUtils.MoveElement(doc, d.Id, new XYZ(0, 0, (zWant - zNow) * MM));
                }
                hd = hd.Where(d => !panel.Contains(d)).ToList();
                for (int i = 0; i < hd.Count; i++)
                {
                    double zNow = hd[i].Curve.Evaluate(0, false).Z / MM;
                    double zWant = zb - 500 - 7 * c.S - 9 * c.S * i;
                    if (Math.Abs(zNow - zWant) > 1) ElementTransformUtils.MoveElement(doc, hd[i].Id, new XYZ(0, 0, (zWant - zNow) * MM));
                    zLast = zWant;
                }
                foreach (Grid g in new FilteredElementCollector(doc, v.Id).OfClass(typeof(Grid)).Cast<Grid>())
                {
                    try
                    {
                        IList<Curve> gc = g.GetCurvesInView(DatumExtentType.ViewSpecific, v);
                        if (gc.Count == 0) continue;
                        XYZ a = gc[0].GetEndPoint(0), b = gc[0].GetEndPoint(1);
                        XYZ lo = a.Z < b.Z ? a : b, hi = a.Z < b.Z ? b : a;
                        XYZ nlo = new XYZ(lo.X, lo.Y, (zLast - 8 * c.S) * MM);
                        if (key == "1" || key == "2") hi = new XYZ(hi.X, hi.Y, (zb - 100) * MM);   // no grid line through the frame (DWG)
                        g.SetCurveInView(DatumExtentType.ViewSpecific, v, a.Z < b.Z ? Line.CreateBound(nlo, hi) : Line.CreateBound(hi, nlo));
                    }
                    catch (Exception ex) { L("  grid " + g.Name + " in " + key + ": " + ex.Message.Split('\n')[0]); }
                }

                if (t25 == null) continue;
                if (key == "1" || key == "2")
                {
                    // shelf marks as in the DWG: К1, К2, Пк1 (one per member) — underlined text on a shelf, leader to the member,
                    // set off to the free side (away from the node marks)
                    double uc = (uMin + uMax) / 2;
                    foreach (FamilyInstance e in mem.Where(e => Mk(e) == "К1" || Mk(e) == "К2" || Mk(e) == "Пк1").GroupBy(e => Mk(e) + Math.Round(c.U(ends(e)[0]) / 100)).Select(g => g.First()))
                    {
                        XYZ[] p = ends(e);
                        string mk = Mk(e);
                        bool leftM = c.U((p[0] + p[1]) / 2) < uc;
                        double mu, mz, du, dz;
                        if (e.Location is LocationPoint)
                        {
                            double[] zz = colZ(e); mu = c.U(p[0]);
                            mz = zz[0] + (zz[1] - zz[0]) * (mk == "К2" ? 0.7 : leftM ? 0.4 : 0.4);
                            du = mk == "К2" ? -14 : leftM ? 10 : -14; dz = 5;
                        }
                        else
                        {
                            XYZ m = p[0] + (p[1] - p[0]) * 0.5; mu = c.U(m); mz = m.Z / MM;
                            du = leftM ? 14 : -16; dz = -13;
                        }
                        TextNote tn = SecText(doc, c, t25, mu + du * c.S, mz + dz * c.S, mk, 0, du > 0 ? HorizontalTextAlignment.Left : HorizontalTextAlignment.Right, VerticalTextAlignment.Bottom, true);
                        try { Leader ld = tn.AddLeader(du > 0 ? TextNoteLeaderTypes.TNLT_STRAIGHT_L : TextNoteLeaderTypes.TNLT_STRAIGHT_R); ld.End = c.P(mu, mz); }
                        catch (Exception ex) { L("  leader " + mk + " " + ex.Message); }
                    }
                    FamilyInstance np = mem.Where(e => Mk(e) == "НП1").OrderBy(e => Math.Abs(c.U((ends(e)[0] + ends(e)[1]) / 2) - uc)).FirstOrDefault();
                    if (np != null)
                    {
                        XYZ m = (ends(np)[0] + ends(np)[1]) / 2;
                        double mu = c.U(m), mz = m.Z / MM;
                        TextNote tn = SecText(doc, c, t25, mu - 12 * c.S, mz - 9 * c.S, key == "1" ? "Ф1" : "Ф2", 0, HorizontalTextAlignment.Left, VerticalTextAlignment.Bottom, true);
                        Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_R); ld.End = c.P(mu, mz);
                    }
                    continue;
                }

                // 3-3 / 4-4: bays between the columns
                List<double> cu2 = cols.Select(e => c.U(ends(e)[0])).Distinct().OrderBy(x => x).ToList();
                cu2 = cu2.Where((x, i) => i == 0 || x - cu2[i - 1] > 100).ToList();
                double zColTop = cols.Count > 0 ? cols.Max(e => colZ(e)[1]) : 0;
                double zTop = mem.SelectMany(e => ends(e)).Max(p => p.Z / MM);
                // К1 along each column, Ф1/Ф2 along each truss end
                foreach (double u in cu2)
                {
                    SecText(doc, c, t25, u - 1.0 * c.S, (zb + zColTop) / 2, "К1", Math.PI / 2, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, false);
                    double x = Math.Abs(c.R.X) > 0.5 ? (c.O.X / MM + u * c.R.X) : 0;
                    double xw = c.U(new XYZ(9150 * MM, 0, 0)) ;
                    bool f1 = c.R.X > 0 ? u <= xw + 1 : u >= xw - 1;
                    SecText(doc, c, t25, u - 1.0 * c.S, (zColTop + zTop) / 2, f1 ? "Ф1" : "Ф2", Math.PI / 2, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, false);
                }
                Func<double, int> bay = u => cu2.Count(x => x < u);
                HashSet<int> sv3 = new HashSet<int>(mem.Where(e => Mk(e) == "СВ3").Select(e => bay(c.U((ends(e)[0] + ends(e)[1]) / 2))));
                // П1 / РС1: one mark per bay over its line
                foreach (string mk in new[] { "П1", "РС1" })
                    foreach (var g in mem.Where(e => Mk(e) == mk).GroupBy(e => bay(c.U((ends(e)[0] + ends(e)[1]) / 2))))
                    {
                        if (mk == "РС1" && sv3.Contains(g.Key)) continue;
                        FamilyInstance e = g.OrderByDescending(x => (ends(x)[0].Z + ends(x)[1].Z)).First();
                        XYZ m = (ends(e)[0] + ends(e)[1]) / 2;
                        double u = g.Key > 0 && g.Key < cu2.Count ? (cu2[g.Key - 1] + cu2[g.Key]) / 2 : c.U(m);
                        if (inlineUp == null) continue;
                        if (!inlineUp.IsActive) inlineUp.Activate();
                        try { IndependentTag tg = IndependentTag.Create(doc, inlineUp.Id, v.Id, new Reference(e), false, TagOrientation.Horizontal, c.P(u, m.Z / MM)); tg.TagHeadPosition = c.P(u, m.Z / MM); }
                        catch (Exception ex) { L("  inline " + mk + " " + ex.Message); }
                    }
                // braces: one note per bay with a leader to each diagonal
                foreach (string mk in new[] { "СВ1", "СВ2", "СВ3" })
                    foreach (var g in mem.Where(e => Mk(e) == mk).GroupBy(e => bay(c.U((ends(e)[0] + ends(e)[1]) / 2))))
                    {
                        List<FamilyInstance> ds = g.GroupBy(e => Math.Round(c.U(ends(e)[0]) / 50) + "_" + Math.Round(c.U(ends(e)[1]) / 50)).Select(x => x.First()).ToList();
                        double u = g.Key > 0 && g.Key < cu2.Count ? (cu2[g.Key - 1] + cu2[g.Key]) / 2 : ds.Average(e => c.U((ends(e)[0] + ends(e)[1]) / 2));
                        double zmin = ds.SelectMany(e => ends(e)).Min(p => p.Z / MM), zmax = ds.SelectMany(e => ends(e)).Max(p => p.Z / MM);
                        bool up = mk == "СВ3";
                        double tz = up ? zmax + 8 * c.S : zmin + 4 * c.S;
                        TextNote tn = SecText(doc, c, t25, u, tz, mk, 0, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, true);
                        foreach (FamilyInstance e in ds.Take(2))
                        {
                            XYZ a = ends(e)[0], b = ends(e)[1];
                            XYZ hi = a.Z > b.Z ? a : b, lo = a.Z > b.Z ? b : a;
                            XYZ pt = up ? hi + (lo - hi) * 0.5 : lo + (hi - lo) * 0.3;
                            try { Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = c.P(c.U(pt), pt.Z / MM); } catch (Exception ex) { L("  leader " + mk + " " + ex.Message); }
                        }
                    }
            }
        }
    }
}
