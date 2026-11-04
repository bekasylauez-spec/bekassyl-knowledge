using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.DB.Structure;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // node plates (3D), node callouts, «Общие данные», technical specification — all for the КМ album in DWG style
    public partial class App
    {
        static int plateCount = 0;

        static DirectShape SolidDS(Document doc, Solid s, string mark, string sec, string name, double massKg, int order)
        {
            DirectShape ds = DirectShape.CreateElement(doc, new ElementId(BuiltInCategory.OST_GenericModel));
            ds.SetShape(new List<GeometryObject> { s });
            try { ds.SetName(mark); } catch { }
            SetP(ds, BuiltInParameter.ALL_MODEL_MARK, mark);
            SetParam(ds, "КМ_Наименование", name);
            SetParam(ds, "КМ_Сечение", sec);
            SetParam(ds, "КМ_Масса_кг", Math.Round(massKg, 2));
            SetParam(ds, "КМ_Порядок", (double)order);
            plateCount++;
            return ds;
        }

        // flat polygon (points in mm-world feet) extruded along its normal by t (ft), centred on the polygon plane
        static Solid Slab(IList<XYZ> pts, XYZ n, double t)
        {
            CurveLoop cl = new CurveLoop();
            for (int i = 0; i < pts.Count; i++) cl.Append(Line.CreateBound(pts[i] - n * (t / 2), pts[(i + 1) % pts.Count] - n * (t / 2)));
            return GeometryCreationUtilities.CreateExtrusionGeometry(new List<CurveLoop> { cl }, n, t);
        }

        static Solid Box(XYZ c, XYZ ax, XYZ ay, double a, double b, double t)
        {
            XYZ n = ax.CrossProduct(ay).Normalize();
            return Slab(new List<XYZ> { c - ax * (a / 2) - ay * (b / 2), c + ax * (a / 2) - ay * (b / 2), c + ax * (a / 2) + ay * (b / 2), c - ax * (a / 2) + ay * (b / 2) }, n, t);
        }

        static double Kg(Solid s) { return s.Volume * Math.Pow(0.3048, 3) * 7850; }

        static void AddPlates(Document doc, Level lvBase, Level lvTop)
        {
            List<FamilyInstance> cols = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralColumns).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
            List<FamilyInstance> fr = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().ToList();
            Func<Element, string> Mk = e => e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() ?? "";
            Func<FamilyInstance, Line> Ln = f => (Line)((LocationCurve)f.Location).Curve;
            double t10 = 10 * MM, t8 = 8 * MM, t4 = 4 * MM;
            foreach (FamilyInstance c in cols)
            {
                XYZ p = ((LocationPoint)c.Location).Point;
                string mk = Mk(c);
                double zb = lvBase.Elevation + c.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).AsDouble();
                double zt = lvTop.Elevation + c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).AsDouble();
                // ribs -t8 on the К1 base (узел 1): along Y from the column face to the plate edge, 150 high, 15 at the top
                if (mk == "К1")
                    foreach (int sgn in new[] { -1, 1 })
                    {
                        double y0 = p.Y + sgn * 70 * MM, y1 = p.Y + sgn * 140 * MM;
                        List<XYZ> poly = new List<XYZ> { new XYZ(p.X, y0, zb), new XYZ(p.X, y1, zb), new XYZ(p.X, y0 + sgn * 15 * MM, zb + 150 * MM), new XYZ(p.X, y0, zb + 150 * MM) };
                        Solid s = Slab(poly, XYZ.BasisX, t8);
                        SolidDS(doc, s, "-t8", "-8", "Ребро базы стойки", Kg(s), 30);
                    }
                // cap -t10 under the chord (узлы 3, 6, 7); the column is cut to the cap
                FamilyInstance chord = fr.Where(f => (Mk(f) == "НП1" || Mk(f) == "ВП1") && (Ln(f).GetEndPoint(0).DistanceTo(new XYZ(p.X, p.Y, zt)) < 0.01 || Ln(f).GetEndPoint(1).DistanceTo(new XYZ(p.X, p.Y, zt)) < 0.01))
                    .OrderBy(f => Mk(f) == "НП1" && mk == "К1" && Math.Abs(p.Y) < 0.01 ? 0 : 1).ThenBy(f => Math.Abs(Ln(f).Direction.Z)).FirstOrDefault();
                if (chord == null) { L("  no chord over " + mk + " at " + Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM)); continue; }
                XYZ d = Ln(chord).Direction; if (d.Y < 0) d = d.Negate();
                XYZ nUp = XYZ.BasisX.CrossProduct(d).Normalize(); if (nUp.Z < 0) nUp = nUp.Negate();
                double cos = Math.Sqrt(d.X * d.X + d.Y * d.Y);
                double half = (Mk(chord) == "НП1" || Mk(chord) == "ВП1") ? 40 * MM : 40 * MM;
                XYZ node = new XYZ(p.X, p.Y, zt);
                double a = mk == "К1" ? 160 * MM : 100 * MM, b = mk == "К1" ? 120 * MM : 100 * MM;
                Solid cap = Box(node - nUp * (half + t10 / 2), d, XYZ.BasisX, a / Math.Max(cos, 0.5) * cos + (1 - cos) * a, b, t10);
                SolidDS(doc, cap, "-t10", "-10", "Пластина (оголовки, фасонки)", Kg(cap), 31);
                double newTop = zt - (half + t10) / Math.Max(cos, 0.5);
                c.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).Set(newTop - lvTop.Elevation);
                Tag(c, mk, mk == "К1" ? "Труба 140x100x4" : "Труба 80x3", (newTop - zb) / MM / 1000.0, c.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString());
            }
            // end caps -t4 on free ends of chords and purlins (узлы 7, 14; примечание листа 12)
            List<XYZ> colPts = cols.Select(c => ((LocationPoint)c.Location).Point).ToList();
            foreach (string grp in new[] { "П", "Ф" })
            {
                List<FamilyInstance> set = fr.Where(f => grp == "П" ? Mk(f) == "П1" : (Mk(f) == "ВП1" || Mk(f) == "НП1")).ToList();
                Dictionary<string, int> deg = new Dictionary<string, int>();
                Func<XYZ, string> key = q => Math.Round(q.X / MM) + "," + Math.Round(q.Y / MM) + "," + Math.Round(q.Z / MM / 5);
                foreach (FamilyInstance f in set) foreach (int e in new[] { 0, 1 }) { string kk = key(Ln(f).GetEndPoint(e)); deg[kk] = deg.ContainsKey(kk) ? deg[kk] + 1 : 1; }
                foreach (FamilyInstance f in set)
                    foreach (int e in new[] { 0, 1 })
                    {
                        XYZ q = Ln(f).GetEndPoint(e);
                        if (deg[key(q)] > 1) continue;
                        bool onCol = colPts.Any(cp => Math.Abs(cp.X - q.X) < 0.05 && Math.Abs(cp.Y - q.Y) < 0.05) && Mk(f) == "НП1";
                        if (onCol) continue;
                        XYZ dout = e == 0 ? Ln(f).Direction.Negate() : Ln(f).Direction;
                        double s = Mk(f) == "П1" ? 60 * MM : 80 * MM;
                        XYZ ax = Math.Abs(dout.Z) > 0.99 ? XYZ.BasisX : XYZ.BasisZ.CrossProduct(dout).Normalize();
                        XYZ ay = dout.CrossProduct(ax).Normalize();
                        XYZ cc = q + dout * (t4 / 2);
                        if (Mk(f) == "П1") cc = cc + ay * (Math.Sign(ay.Z) * (40 + 30) * MM);
                        Solid sl = Box(cc, ax, ay, s, s, t4);
                        SolidDS(doc, sl, "-t4", "-4", "Заглушка", Kg(sl), 32);
                    }
            }
            // gusset -t10 160x200 under НП1 where СВ3 and СГ1 meet on axis 3 (узел 8)
            foreach (double yy in new[] { 7300.0, 0.0, -680.0 })
            {
                FamilyInstance f = fr.FirstOrDefault(x => Mk(x) == "НП1" && (Ln(x).GetEndPoint(0).DistanceTo(new XYZ(11550 * MM, yy * MM, Ln(x).GetEndPoint(0).Z)) < 0.01 || Ln(x).GetEndPoint(1).DistanceTo(new XYZ(11550 * MM, yy * MM, Ln(x).GetEndPoint(1).Z)) < 0.01));
                if (f == null) continue;
                XYZ q = Ln(f).GetEndPoint(0).DistanceTo(new XYZ(11550 * MM, yy * MM, Ln(f).GetEndPoint(0).Z)) < 0.01 ? Ln(f).GetEndPoint(0) : Ln(f).GetEndPoint(1);
                Solid g = Box(q - XYZ.BasisZ * (40 * MM + t10 / 2), XYZ.BasisX, XYZ.BasisY, 160 * MM, 200 * MM, t10);
                SolidDS(doc, g, "-t10", "-10", "Пластина (оголовки, фасонки)", Kg(g), 31);
            }
            L("plates " + plateCount);
        }

        // node callouts: name, parent, model corners (mm), scale
        static Dictionary<string, View> NodeViews(Document doc, Dictionary<string, View> V, ElementId detailType, ElementId planType, Level lvBase)
        {
            object[][] nodes = {
                new object[]{ "1", "1-1", new double[]{ 4350, -320, 650, 4350, 320, 1150 }, 10 },
                new object[]{ "2", "1-1", new double[]{ 4350, 8550, 650, 4350, 9050, 1150 }, 10 },
                new object[]{ "3", "1-1", new double[]{ 4350, -260, 3850, 4350, 260, 4200 }, 10 },
                new object[]{ "4", "1-1", new double[]{ 4350, 3300, 3900, 4350, 4000, 4350 }, 10 },
                new object[]{ "5", "1-1", new double[]{ 4350, 4850, 2850, 4350, 5550, 3450 }, 10 },
                new object[]{ "6", "1-1", new double[]{ 4350, 6300, 1650, 4350, 7650, 3150 }, 20 },
                new object[]{ "7", "1-1", new double[]{ 4350, 8450, 1800, 4350, 9100, 2250 }, 10 },
                new object[]{ "14", "1-1", new double[]{ 4350, -900, 3900, 4350, -200, 4750 }, 20 },
                new object[]{ "8", "p5", new double[]{ 11150, 6950, 0, 11950, 7650, 0 }, 10 },
                new object[]{ "9", "p5", new double[]{ 11150, 3300, 0, 11950, 4000, 0 }, 10 },
                new object[]{ "10", "3-3", new double[]{ 8850, 7300, 1900, 9450, 7300, 2600 }, 15 },
                new object[]{ "11", "3-3", new double[]{ 10050, 7300, 1250, 10650, 7300, 1850 }, 10 },
                new object[]{ "12", "3-3", new double[]{ 9950, 7300, 2150, 10750, 7300, 2950 }, 15 },
                new object[]{ "13", "4-4", new double[]{ 11250, 0, 650, 11850, 0, 1300 }, 15 },
                new object[]{ "а-а", "p3", new double[]{ -330, -330, 0, 330, 330, 0 }, 10 },
                new object[]{ "б-б", "p3", new double[]{ -250, 8550, 0, 250, 9050, 0 }, 10 } };
            Dictionary<string, View> N = new Dictionary<string, View>();
            foreach (object[] n in nodes)
            {
                string name = (string)n[0], parent = (string)n[1];
                double[] c = (double[])n[2];
                bool plan = parent.StartsWith("p");
                try
                {
                    View v = ViewSection.CreateCallout(doc, V[parent].Id, plan ? planType : detailType,
                        new XYZ(c[0] * MM, c[1] * MM, c[2] * MM), new XYZ(c[3] * MM, c[4] * MM, c[5] * MM));
                    v.Name = name.Contains("-") ? "Разрез " + name : "Узел " + name;
                    v.Scale = (int)n[3];
                    v.get_Parameter(BuiltInParameter.VIEW_DESCRIPTION).Set(name.Contains("-") ? "Разрез " + name.Replace("-", " - ") : name);
                    v.DetailLevel = ViewDetailLevel.Fine;
                    v.DisplayStyle = DisplayStyle.HLR;
                    if (v is ViewPlan && name.Contains("-"))
                    {
                        ViewPlan vp = (ViewPlan)v;
                        PlanViewRange pr = vp.GetViewRange();
                        pr.SetLevelId(PlanViewPlane.TopClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.TopClipPlane, 400 * MM);
                        pr.SetLevelId(PlanViewPlane.CutPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.CutPlane, 100 * MM);
                        pr.SetLevelId(PlanViewPlane.BottomClipPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.BottomClipPlane, -100 * MM);
                        pr.SetLevelId(PlanViewPlane.ViewDepthPlane, lvBase.Id); pr.SetOffset(PlanViewPlane.ViewDepthPlane, -100 * MM);
                        vp.SetViewRange(pr);
                    }
                    try { v.SetCategoryHidden(new ElementId(BuiltInCategory.OST_Levels), true); } catch { }
                    v.CropBoxVisible = false;
                    N[name] = v;
                }
                catch (Exception ex) { L("callout " + name + " " + ex.Message); }
            }
            return N;
        }

        // one text with a leader per mark inside a node view
        static void NodeMarks(Document doc, View v, TextNoteType tt)
        {
            BoundingBoxXYZ cb = v.CropBox;
            Transform tr = cb.Transform;
            XYZ cen = tr.OfPoint((cb.Min + cb.Max) / 2);
            XYZ right = v.RightDirection, up = v.UpDirection, dirV = v.ViewDirection;
            double halfW = (cb.Max.X - cb.Min.X) / 2, halfH = (cb.Max.Y - cb.Min.Y) / 2;
            Func<XYZ, XYZ> toPlane = q => q - dirV * (q - cen).DotProduct(dirV);
            HashSet<string> done = new HashSet<string>();
            List<XYZ> heads = new List<XYZ>();
            List<Element> els = new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType()
                .Where(e => e.Category != null && (e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns || e.Category.Id.Value == (long)BuiltInCategory.OST_GenericModel)).ToList();
            foreach (Element e in els)
            {
                string mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString();
                if (string.IsNullOrEmpty(mk) || done.Contains(mk)) continue;
                XYZ a;
                if (e.Location is LocationCurve)
                {
                    Curve c = ((LocationCurve)e.Location).Curve;
                    a = c.Project(cen).XYZPoint;
                }
                else if (e.Location is LocationPoint && e is FamilyInstance)
                {
                    XYZ p = ((LocationPoint)e.Location).Point;
                    a = new XYZ(p.X, p.Y, Math.Max(cen.Z, p.Z));
                }
                else { BoundingBoxXYZ bb = e.get_BoundingBox(null); if (bb == null) continue; a = (bb.Min + bb.Max) / 2; }
                a = toPlane(a);
                double u = (a - cen).DotProduct(right), w = (a - cen).DotProduct(up);
                if (Math.Abs(u) > halfW * 0.95 || Math.Abs(w) > halfH * 0.95) continue;
                done.Add(mk);
                double sc = v.Scale;
                XYZ head = null;
                double[] angs = { 45, 135, -45, -135, 90, -90, 0, 180, 60, 120, -60, -120 };
                foreach (double ag in angs)
                {
                    double r = ag * Math.PI / 180;
                    XYZ h2 = a + (right * Math.Cos(r) + up * Math.Sin(r)) * (16 * MM * sc);
                    double hu = (h2 - cen).DotProduct(right), hw = (h2 - cen).DotProduct(up);
                    if (Math.Abs(hu) > halfW + 18 * MM * sc || Math.Abs(hw) > halfH + 18 * MM * sc) continue;
                    if (heads.Any(q => q.DistanceTo(h2) < 11 * MM * sc)) continue;
                    head = h2; break;
                }
                if (head == null) head = a + (right + up).Normalize() * (16 * MM * sc);
                heads.Add(head);
                string txt = mk.StartsWith("-t") ? "-" + mk.Substring(1) + "\rС245" : mk;
                try
                {
                    bool member = e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns;
                    FamilySymbol ts = e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns ? TagColSym : TagBeamSym;
                    if (member && ts != null)
                    {
                        IndependentTag tg = IndependentTag.Create(doc, ts.Id, v.Id, new Reference(e), true, TagOrientation.Horizontal, head);
                        if (tg.TagText == mk) continue;
                        doc.Delete(tg.Id);
                    }
                    TextNoteOptions o = new TextNoteOptions(tt.Id); o.HorizontalAlignment = HorizontalTextAlignment.Left; o.VerticalAlignment = VerticalTextAlignment.Bottom;
                    TextNote tn = TextNote.Create(doc, v.Id, head, txt, o);
                    FormattedText ft = tn.GetFormattedText();
                    int n1 = txt.IndexOf('\r'); ft.SetUnderlineStatus(new TextRange(0, n1 > 0 ? n1 : txt.Length), true);
                    tn.SetFormattedText(ft);
                    Leader ld = tn.AddLeader(TextNoteLeaderTypes.TNLT_STRAIGHT_L); ld.End = a;
                }
                catch (Exception ex) { L("node mark " + v.Name + " " + mk + " " + ex.Message); }
            }
        }

        // «Общие данные»: DWG texts in their places, sheet list, reference documents table, ГИП box
        static void OdSheet(Document doc, ViewSheet vs, string odJson, TextNoteType t25, TextNoteType t35, TextNoteType tTitle, ViewSchedule sheetList, string sigGip)
        {
            string[] lines = File.ReadAllLines(odJson, Encoding.UTF8);
            // od.txt format: x|y|width|text (sheet mm, top-left), \r for new paragraphs
            foreach (string ln in lines)
            {
                string[] f = ln.Split(new[] { '|' }, 4);
                if (f.Length < 4) continue;
                Txt(doc, vs.Id, D(f[0]), D(f[1]), f[3].Replace("¶", "\r"), t25, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, D(f[2]));
            }
            ScheduleSheetInstance.Create(doc, vs.Id, sheetList.Id, new XYZ(397 * MM, 412 * MM, 0));
            // reference documents table (drawn on the sheet)
            string[][] refs = {
                new[]{ "СП РК EN 1998-1:2004/2012", "Проектирование сейсмостойких конструкций. Часть 1" },
                new[]{ "НТП РК 08-01.1-2017", "Сейсмические воздействия (к СП РК EN 1998-1)" },
                new[]{ "НТП РК 01-01-3.1(4.1)-2017", "Снеговые нагрузки. Ветровые воздействия" },
                new[]{ "СП РК EN 1993-1-1:2005/2011", "Проектирование стальных конструкций. Часть 1-1" },
                new[]{ "СН РК 5.03-07-2013", "Несущие и ограждающие конструкции" },
                new[]{ "ГОСТ 23118-2019", "Конструкции стальные строительные. ОТУ" },
                new[]{ "ГОСТ 27772-2021", "Прокат для строительных стальных конструкций" },
                new[]{ "ГОСТ 30245-2003", "Профили стальные гнутые замкнутые сварные" },
                new[]{ "ГОСТ 10704-91", "Трубы стальные электросварные прямошовные" },
                new[]{ "СН РК 2.01-01-2013", "Защита строительных конструкций от коррозии" } };
            double x0 = 397, x1 = 457, x2 = 552, x3 = 589, yTop = 233, hh = 15, rh = 8;
            Txt(doc, vs.Id, (x0 + x3) / 2, yTop + 8, "Ведомость ссылочных и прилагаемых документов", tTitle, HorizontalTextAlignment.Center, VerticalTextAlignment.Bottom, 0);
            double yb = yTop - hh - rh * refs.Length;
            Action<double, double, double, double> L2 = (a, b, c2, d2) => doc.Create.NewDetailCurve(vs, Line.CreateBound(new XYZ(a * MM, b * MM, 0), new XYZ(c2 * MM, d2 * MM, 0)));
            foreach (double x in new[] { x0, x1, x2, x3 }) L2(x, yTop, x, yb);
            L2(x0, yTop, x3, yTop); L2(x0, yTop - hh, x3, yTop - hh);
            for (int i = 1; i <= refs.Length; i++) L2(x0, yTop - hh - rh * i, x3, yTop - hh - rh * i);
            Txt(doc, vs.Id, (x0 + x1) / 2, yTop - hh / 2, "Обозначение", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
            Txt(doc, vs.Id, (x1 + x2) / 2, yTop - hh / 2, "Наименование", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
            Txt(doc, vs.Id, (x2 + x3) / 2, yTop - hh / 2, "Примечание", t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
            for (int i = 0; i < refs.Length; i++)
            {
                double y = yTop - hh - rh * i - rh / 2;
                Txt(doc, vs.Id, (x0 + x1) / 2, y, refs[i][0], t25, HorizontalTextAlignment.Center, VerticalTextAlignment.Middle, 0);
                Txt(doc, vs.Id, x1 + 1.5, y, refs[i][1], t25, HorizontalTextAlignment.Left, VerticalTextAlignment.Middle, 0);
            }
            // ГИП box
            L2(25, 5, 25, 50); L2(25, 50, 205, 50); L2(205, 50, 205, 5);
            Txt(doc, vs.Id, 30, 45, "Настоящий рабочий проект выполнен в соответствии с государственными нормами, правилами, стандартами и межгосударственными нормативами, действующими на территории Республики Казахстан.", t35, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, 170);
            Txt(doc, vs.Id, 30, 13, "Главный инженер проекта", t35, HorizontalTextAlignment.Left, VerticalTextAlignment.Middle, 0);
            Txt(doc, vs.Id, 160, 13, "Казангапов А", t35, HorizontalTextAlignment.Left, VerticalTextAlignment.Middle, 0);
            if (File.Exists(sigGip))
            {
                ImageType it = ImageType.Create(doc, new ImageTypeOptions(sigGip, false, ImageTypeSource.Import));
                ImageInstance ii = ImageInstance.Create(doc, vs, it.Id, new ImagePlacementOptions(new XYZ(122 * MM, 13 * MM, 0), BoxPlacement.Center));
                ii.Width = 26 * MM;
            }
        }

        // «Техническая спецификация металла» as on DWG sheet 2: masses (t) by profile and by element group, taken from the model
        static void TechSpec(Document doc, ViewSheet vs, TextNoteType t25, TextNoteType t30)
        {
            string[] grpNames = { "Стойки", "Фермы", "Связи вертикальные", "Связи горизонт. и распорки", "Прогоны" };
            Func<string, int> G = mk => mk == "К1" || mk == "К2" || mk == "Пк1" ? 0 : mk == "ВП1" || mk == "НП1" || mk == "Р1" ? 1 : mk.StartsWith("СВ") ? 2 : mk == "СГ1" || mk == "РС1" ? 3 : mk == "П1" ? 4 : -1;
            string[] profs = new[] { "□140x100x4", "□80x3", "□60x2.5", "□50x2.5" }.Select(p => p.Replace("x", "х")).ToArray();
            string[] plates = { "-10", "-8", "-4" };
            double[,] mp = new double[4, 5]; double[,] mpl = new double[3, 5];
            List<Element> all = new FilteredElementCollector(doc).WhereElementIsNotElementType().Where(e => e.Category != null && (e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralFraming || e.Category.Id.Value == (long)BuiltInCategory.OST_StructuralColumns || e.Category.Id.Value == (long)BuiltInCategory.OST_GenericModel)).ToList();
            foreach (Element e in all)
            {
                Parameter pm = e.LookupParameter("КМ_Масса_кг"), ps = e.LookupParameter("КМ_Сечение");
                if (pm == null || ps == null || pm.AsDouble() <= 0) continue;
                string mk = e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() ?? "", sec = (ps.AsString() ?? "").Replace("x", "х");
                double t = pm.AsDouble() / 1000.0;
                int pi = Array.IndexOf(profs, sec), pl = Array.IndexOf(plates, sec);
                if (pi >= 0) { int g = G(mk); if (g >= 0) mp[pi, g] += t; }
                else if (pl >= 0)
                {
                    string nm = e.LookupParameter("КМ_Наименование").AsString() ?? "";
                    int g = (nm.StartsWith("Пластина") && e.get_BoundingBox(null).Max.Z - e.get_BoundingBox(null).Min.Z < 15 * MM && Math.Abs((e.get_BoundingBox(null).Max.Y - e.get_BoundingBox(null).Min.Y) / MM - 200) < 3) ? 3 : nm.StartsWith("Заглушка") ? (e.get_BoundingBox(null).Max.X - e.get_BoundingBox(null).Min.X > 0.5 * 0 + 0 && IsPurlinCap(e) ? 4 : 1) : 0;
                    mpl[pl, g] += t;
                }
            }
            double[] cw = { 38, 23, 27, 9, 13.5, 13.5, 13.5, 13.5, 13.5, 20, 35 };
            double X0 = 25, yTop = 405, hh1 = 15, hh2 = 34, hn = 7, rh = 8;
            double[] xs = new double[cw.Length + 1]; xs[0] = X0; for (int i = 0; i < cw.Length; i++) xs[i + 1] = xs[i] + cw[i];
            Action<double, double, double, double> L2 = (a, b, c2, d2) => doc.Create.NewDetailCurve(vs, Line.CreateBound(new XYZ(a * MM, b * MM, 0), new XYZ(c2 * MM, d2 * MM, 0)));
            Action<double, double, string, bool> T = (x, y, s, rot) =>
            {
                TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
                if (rot) { o.Rotation = Math.PI / 2; TextNote.Create(doc, vs.Id, new XYZ(x * MM, y * MM, 0), 26 * MM, s, o); }
                else TextNote.Create(doc, vs.Id, new XYZ(x * MM, y * MM, 0), s, o);
            };
            double yH = yTop - hh1 - hh2, yN = yH - hn;
            List<string[]> body = new List<string[]>();
            Func<double, string> F = v => v > 0.0005 ? v.ToString("0.000").Replace(".", ",") : "";
            Func<double, string> F2 = v => v > 0.0005 ? v.ToString("0.00").Replace(".", ",") : "";
            double[] totP = new double[6], totL = new double[6];
            for (int i = 0; i < 4; i++)
            {
                double s = 0; for (int g = 0; g < 5; g++) { s += mp[i, g]; totP[g] += mp[i, g]; }
                totP[5] += s;
                body.Add(new[] { i == 0 ? "Профили квадратные и прямоугольные по ГОСТ 30245-2003" : "", i == 0 ? "Сталь С245, ГОСТ 27772-2021" : "", "Тр. " + profs[i], "", F2(mp[i, 0]), F2(mp[i, 1]), F2(mp[i, 2]), F2(mp[i, 3]), F2(mp[i, 4]), F(s), "" });
            }
            body.Add(new[] { "Всего профиля", "Итого", "", "", F(totP[0]), F(totP[1]), F(totP[2]), F(totP[3]), F(totP[4]), F(totP[5]), "" });
            for (int i = 0; i < 3; i++)
            {
                double s = 0; for (int g = 0; g < 5; g++) { s += mpl[i, g]; totL[g] += mpl[i, g]; }
                totL[5] += s;
                body.Add(new[] { i == 0 ? "Прокат листовой горячекатаный по ГОСТ 19903-2015" : "", i == 0 ? "Сталь С245, ГОСТ 27772-2021" : "", "t" + plates[i].Substring(1), "", F(mpl[i, 0]), F(mpl[i, 1]), F(mpl[i, 2]), F(mpl[i, 3]), F(mpl[i, 4]), F(s), "" });
            }
            body.Add(new[] { "Всего листа", "Итого", "", "", F(totL[0]), F(totL[1]), F(totL[2]), F(totL[3]), F(totL[4]), F(totL[5]), "" });
            body.Add(new[] { "Всего масса металла", "", "", "", F(totP[0] + totL[0]), F(totP[1] + totL[1]), F(totP[2] + totL[2]), F(totP[3] + totL[3]), F(totP[4] + totL[4]), F(totP[5] + totL[5]), "" });
            double yb = yN - rh * body.Count;
            // grid
            L2(xs[0], yTop, xs[cw.Length], yTop);
            L2(xs[4], yTop - hh1, xs[9], yTop - hh1);
            L2(xs[0], yH, xs[cw.Length], yH); L2(xs[0], yN, xs[cw.Length], yN);
            for (int r = 1; r <= body.Count; r++)
            {
                bool full = r == 4 || r == 5 || r == 8 || r == 9 || r == body.Count;
                L2(full ? xs[0] : xs[2], yN - rh * r, xs[cw.Length], yN - rh * r);
            }
            for (int i = 0; i <= cw.Length; i++) L2(xs[i], (i > 4 && i < 9) ? yTop - hh1 : yTop, xs[i], yb);
            string[] head = { "Вид профиля ГОСТ, ТУ", "Марка металла, ГОСТ", "Обозначение и размер профиля, мм", "№ по порядку", "", "", "", "", "", "Общая масса, т", "Примечания" };
            for (int i = 0; i < cw.Length; i++)
            {
                if (i >= 4 && i <= 8) T((xs[i] + xs[i + 1]) / 2, yTop - hh1 - hh2 / 2, grpNames[i - 4], true);
                else if (i == 3) T((xs[i] + xs[i + 1]) / 2, yH + (hh1 + hh2) / 2, head[i], true);
                else
                {
                    TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
                    TextNote.Create(doc, vs.Id, new XYZ((xs[i] + xs[i + 1]) / 2 * MM, (yH + (hh1 + hh2) / 2) * MM, 0), (cw[i] - 3) * MM, head[i], o);
                }
                T((xs[i] + xs[i + 1]) / 2, yN + hn / 2, (i + 1).ToString(), false);
            }
            {
                TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
                TextNote.Create(doc, vs.Id, new XYZ((xs[4] + xs[9]) / 2 * MM, (yTop - hh1 / 2) * MM, 0), 60 * MM, "Масса металла по элементам конструкций, т", o);
            }
            for (int r = 0; r < body.Count; r++)
                for (int i = 0; i < cw.Length; i++)
                {
                    string s = body[r][i];
                    if (string.IsNullOrEmpty(s)) continue;
                    double y = yN - rh * r - rh / 2;
                    if ((i == 0 || i == 1) && (r == 0 || r == 5)) y = yN - rh * r - rh * (r == 0 ? 4 : 3) / 2.0;
                    TextNoteOptions o = new TextNoteOptions(t25.Id); o.HorizontalAlignment = HorizontalTextAlignment.Center; o.VerticalAlignment = VerticalTextAlignment.Middle;
                    TextNote.Create(doc, vs.Id, new XYZ((xs[i] + xs[i + 1]) / 2 * MM, y * MM, 0), (cw[i] - 2) * MM, s, o);
                }
            Txt(doc, vs.Id, 105, 108, "1. Общие данные см. на листе 1.\r2. Масса металла, приведенная в данной спецификации, определена без учета массы наплавленного металла сварных швов в размере 1% и 3% на уточнение массы при разработке чертежей КМД.\r3. Длины элементов приняты по осям расчетной схемы (масса подсчитана по 3D-модели).", t30, HorizontalTextAlignment.Left, VerticalTextAlignment.Top, 185);
            L("tech spec: profiles " + F(totP[5]) + " t, plates " + F(totL[5]) + " t");
        }

        static bool IsPurlinCap(Element e)
        {
            BoundingBoxXYZ bb = e.get_BoundingBox(null);
            double dz = (bb.Max.Z - bb.Min.Z) / MM, dy = (bb.Max.Y - bb.Min.Y) / MM;
            return dz < 70 && dy < 70;
        }
    }
}
