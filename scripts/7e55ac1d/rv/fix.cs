using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    // in-place fixes on the user's album file (keeps their manual edits)
    public partial class App
    {
        // all braces (StructuralType.Brace) draw through the framing sub-category «Вертикальные раскосы»; the RU plan views hide it
        static void ShowBraces(Document doc, View v)
        {
            foreach (Category sc in Category.GetCategory(doc, BuiltInCategory.OST_StructuralFraming).SubCategories)
                if (sc.Name.Contains("раскос")) { try { if (v.GetCategoryHidden(sc.Id)) v.SetCategoryHidden(sc.Id, false); } catch { } }
        }

        // mark shelves that sit on top of each other (|dx| < 400, |dy| < 250 mm in plan): lift the later one by 6 mm on paper
        static void Declutter(Document doc, string viewKey)
        {
            foreach (View v in new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<View>().Where(x => !x.IsTemplate && x.Name.Contains(viewKey)))
            {
                List<IndependentTag> tags = new FilteredElementCollector(doc, v.Id).OfClass(typeof(IndependentTag)).Cast<IndependentTag>().ToList();
                L("  view " + v.Name + " tags " + tags.Count);
                double lift = 6 * MM * v.Scale;
                List<XYZ> placed = new List<XYZ>();
                foreach (IndependentTag tg in tags.OrderBy(t => t.TagHeadPosition.Y).ThenBy(t => t.TagHeadPosition.X))
                {
                    XYZ h = tg.TagHeadPosition;
                    XYZ h0 = h;
                    for (int guard = 0; guard < 4 && placed.Any(p => Math.Abs(p.X - h.X) < 400 * MM && Math.Abs(p.Y - h.Y) < 250 * MM); guard++)
                        h = h + new XYZ(0, lift, 0);
                    if (!h.IsAlmostEqualTo(h0))
                    {
                        tg.TagHeadPosition = h;
                        L("    lift " + tg.TagText + " at " + Math.Round(h0.X / MM) + "," + Math.Round(h0.Y / MM) + " -> y " + Math.Round(h.Y / MM));
                    }
                    placed.Add(h);
                }
            }
        }

        // one colour per section (КМ_Сечение); the mark filters keep only their visibility role
        static readonly string[] SecList = { "□140х100х4", "□80х3", "□60х2.5", "□50х2.5", "-10", "-8", "-4" };
        static readonly int[][] SecRgb = { new[]{200,30,30}, new[]{30,80,210}, new[]{40,160,60}, new[]{225,0,170}, new[]{235,120,0}, new[]{120,70,20}, new[]{0,150,150} };

        static void ColorBySection(Document doc)
        {
            ParameterElement pe = Find<ParameterElement>(doc, p => p.GetDefinition() != null && p.GetDefinition().Name == "КМ_Сечение");
            if (pe == null) { L("no КМ_Сечение"); return; }
            List<ElementId> cats = new List<ElementId> { new ElementId(BuiltInCategory.OST_StructuralFraming), new ElementId(BuiltInCategory.OST_StructuralColumns), new ElementId(BuiltInCategory.OST_GenericModel) };
            // values actually present in the model
            HashSet<string> vals = new HashSet<string>();
            foreach (ElementId c in cats)
                foreach (Element e in new FilteredElementCollector(doc).OfCategoryId(c).WhereElementIsNotElementType())
                { Parameter p = e.LookupParameter("КМ_Сечение"); if (p != null && !string.IsNullOrEmpty(p.AsString())) vals.Add(p.AsString()); }
            L("  sections in model: " + string.Join(" ", vals));
            List<string> order = SecList.Where(vals.Contains).Concat(vals.Where(x => !SecList.Contains(x)).OrderBy(x => x)).ToList();
            Dictionary<string, ElementId> sf = new Dictionary<string, ElementId>();
            foreach (string s in order)
            {
                string nm = "КМ_Сечение " + s;
                ParameterFilterElement f = Find<ParameterFilterElement>(doc, x => x.Name == nm);
                if (f == null) f = ParameterFilterElement.Create(doc, nm, cats, new ElementParameterFilter(ParameterFilterRuleFactory.CreateEqualsRule(pe.Id, s)));
                sf[s] = f.Id;
            }
            ElementId solid = Find<FillPatternElement>(doc, x => x.GetFillPattern().IsSolidFill).Id;
            HashSet<ElementId> markF = new HashSet<ElementId>(new FilteredElementCollector(doc).OfClass(typeof(ParameterFilterElement)).Where(x => x.Name.StartsWith("КМ_") && !x.Name.StartsWith("КМ_Сечение")).Select(x => x.Id));
            int nv = 0;
            foreach (View v in new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>())
            {
                if (v.IsTemplate || !v.AreGraphicsOverridesAllowed()) continue;
                List<ElementId> applied = v.GetFilters().Where(markF.Contains).ToList();
                if (applied.Count == 0) continue;
                foreach (ElementId id in applied) v.SetFilterOverrides(id, new OverrideGraphicSettings());
                for (int i = 0; i < order.Count; i++)
                {
                    int[] c = SecRgb[i % SecRgb.Length];
                    Color col = new Color((byte)c[0], (byte)c[1], (byte)c[2]);
                    OverrideGraphicSettings o = new OverrideGraphicSettings();
                    o.SetProjectionLineColor(col);
                    o.SetSurfaceForegroundPatternId(solid); o.SetSurfaceForegroundPatternColor(col);
                    o.SetCutLineColor(col);
                    o.SetCutForegroundPatternId(solid); o.SetCutForegroundPatternColor(col);
                    ElementId id = sf[order[i]];
                    if (!v.IsFilterApplied(id)) v.AddFilter(id);
                    v.SetFilterOverrides(id, o);
                }
                nv++;
            }
            for (int i = 0; i < order.Count; i++) L("  colour " + order[i] + " = " + string.Join(",", SecRgb[i % SecRgb.Length]));
            L("  views coloured by section " + nv);
        }

        static string FixInPlace(Application app, Dictionary<string, string> J)
        {
            string path = J["file"];
            Document doc = app.OpenDocumentFile(path);
            ApplyFixes(doc, J);
            doc.Save();
            doc.Close(false);
            L("saved " + path);
            return path;
        }

        // live: the same fixes on the document open in the user's Revit (RBLive shim loads this assembly per job)
        public static string LiveRun(Autodesk.Revit.UI.UIApplication ui, Dictionary<string, string> J)
        {
            Log.Clear();
            try
            {
                Document doc = ui.ActiveUIDocument.Document;
                L("live on " + doc.Title);
                if (J.ContainsKey("show"))
                {
                    ViewSheet sh = new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().FirstOrDefault(s => s.SheetNumber == J["show"]);
                    if (sh != null) { try { ui.ActiveUIDocument.ActiveView = sh; } catch (Exception ex) { L("show " + ex.Message); } }
                }
                if (J.ContainsKey("probe")) Probe(doc, J["probe"]);
                else if (J.ContainsKey("secprobe")) SecProbe(doc);
                else if (J.ContainsKey("catprobe"))
                {
                    View v = new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>().First(x => !x.IsTemplate && x.Name.Contains(J["catprobe"]));
                    foreach (Element e in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType())
                        if (e.Category == null || !(e.Category.Name.StartsWith("Несущ") || e.Category.Name.StartsWith("Обобщ") || e.Category.Name.StartsWith("Оси") || e.Category.Name.StartsWith("Размеры") || e is TextNote))
                            L("  " + e.Id + " " + e.GetType().Name + " cat " + (e.Category != null ? e.Category.Name + " (" + e.Category.Id + ")" : "-") + " name " + e.Name);
                    foreach (View cv in new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>().Where(x => x.Name.StartsWith("Разрез а") || x.Name.StartsWith("Разрез б")))
                        L("  view " + cv.Name + " id " + cv.Id + " type " + cv.ViewType + " parent " + (cv.GetPrimaryViewId() != null ? cv.GetPrimaryViewId().ToString() : "-"));
                }
                else if (J.ContainsKey("lvprobe"))
                {
                    ViewSection v = new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().First(x => x.Name == J["lvprobe"]);
                    BoundingBoxXYZ cb = v.CropBox;
                    L("crop world " + P3(cb.Transform.OfPoint(cb.Min)) + " .. " + P3(cb.Transform.OfPoint(cb.Max)) + " O " + P3(v.Origin) + " R " + P3(v.RightDirection * 1000 * MM));
                    foreach (Level lv in new FilteredElementCollector(doc).OfClass(typeof(Level)).Cast<Level>())
                    {
                        string s = "level " + lv.Name + " hidden " + lv.IsHidden(v);
                        foreach (DatumExtentType t in new[] { DatumExtentType.Model, DatumExtentType.ViewSpecific })
                            try { foreach (Curve cc in lv.GetCurvesInView(t, v)) s += " " + t + " " + P3(cc.GetEndPoint(0)) + "->" + P3(cc.GetEndPoint(1)); } catch (Exception ex) { s += " " + t + " ERR"; }
                        L(s);
                    }
                    Viewport vp = new FilteredElementCollector(doc).OfClass(typeof(Viewport)).Cast<Viewport>().First(x => x.ViewId == v.Id);
                    Outline o = vp.GetBoxOutline(); L("vp outline " + P3(o.MinimumPoint) + " .. " + P3(o.MaximumPoint));
                    foreach (ViewSheet sh in new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().Where(s => s.SheetNumber == "7" || s.SheetNumber == "8"))
                        foreach (Element e in new FilteredElementCollector(doc, sh.Id).WhereElementIsNotElementType())
                        {
                            BoundingBoxXYZ bb = e.get_BoundingBox(sh);
                            if (bb != null && (bb.Max.X / MM > 416 || bb.Min.Y / MM < -1 || bb.Max.Y / MM > 298)) L("  sheet " + sh.SheetNumber + " outside: " + (e.Category != null ? e.Category.Name : e.GetType().Name) + " " + e.Id + " " + P3(bb.Min) + ".." + P3(bb.Max) + (e is TextNote ? " '" + ((TextNote)e).Text.Trim() + "'" : ""));
                        }
                    foreach (Element e in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType()) { BoundingBoxXYZ bb = e.get_BoundingBox(v); if (bb != null && e.Category != null && (bb.Max - bb.Min).GetLength() > 3000 * MM) L("  big " + e.Category.Name + " " + e.Id + " " + P3(bb.Min) + ".." + P3(bb.Max)); }
                }
                else ApplyFixes(doc, J);
                if (J.ContainsKey("save")) { doc.Save(); L("saved " + doc.PathName); }
            }
            catch (Exception ex) { L("ERROR " + ex); }
            return Log.ToString();
        }

        // members beyond row М (Y > 7400) and how the given plan sees them
        static void Probe(Document doc, string viewKey)
        {
            View v = new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<View>().First(x => !x.IsTemplate && x.Name.Contains(viewKey));
            BoundingBoxXYZ cb = v.CropBox;
            L("view " + v.Name + " crop " + v.CropBoxActive + " " + Math.Round(cb.Min.X / MM) + "," + Math.Round(cb.Min.Y / MM) + " .. " + Math.Round(cb.Max.X / MM) + "," + Math.Round(cb.Max.Y / MM));
            PlanViewRange vr = ((ViewPlan)v).GetViewRange();
            foreach (PlanViewPlane pp in new[] { PlanViewPlane.TopClipPlane, PlanViewPlane.CutPlane, PlanViewPlane.BottomClipPlane, PlanViewPlane.ViewDepthPlane })
                L("  range " + pp + " lvl " + (doc.GetElement(vr.GetLevelId(pp)) != null ? doc.GetElement(vr.GetLevelId(pp)).Name + " " + Math.Round(((Level)doc.GetElement(vr.GetLevelId(pp))).Elevation / MM) : "-") + " off " + Math.Round(vr.GetOffset(pp) / MM));
            HashSet<ElementId> inView = new HashSet<ElementId>(new FilteredElementCollector(doc, v.Id).ToElementIds());
            foreach (FamilyInstance f in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().Where(f => f.Location is LocationCurve))
            {
                Curve c = ((LocationCurve)f.Location).Curve; XYZ a = c.GetEndPoint(0), b = c.GetEndPoint(1);
                if (Math.Max(a.Y, b.Y) / MM < 7400) continue;
                L("  " + Mk(f) + " " + Math.Round(a.X / MM) + "," + Math.Round(a.Y / MM) + "," + Math.Round(a.Z / MM) + " -> " + Math.Round(b.X / MM) + "," + Math.Round(b.Y / MM) + "," + Math.Round(b.Z / MM) + " inView " + inView.Contains(f.Id) + " bb " + (f.get_BoundingBox(v) != null));
            }
        }

        // lower-chord plan: the Ф1 trusses run on past row М to the К2 row (DWG sheet 5) — show the ВП1 there and the П1 on the К2 row,
        // keep every other ВП1/П1 hidden in this view
        static void Overhang(Document doc, string viewKey)
        {
            View v = new FilteredElementCollector(doc).OfClass(typeof(ViewPlan)).Cast<View>().First(x => !x.IsTemplate && x.Name.Contains(viewKey));
            foreach (string mk in new[] { "ВП1", "П1" })
            {
                ParameterFilterElement f = Find<ParameterFilterElement>(doc, x => x.Name == "КМ_" + mk);
                if (f != null && v.IsFilterApplied(f.Id)) v.SetFilterVisibility(f.Id, true);
            }
            List<ElementId> hide = new List<ElementId>();
            int shown = 0;
            foreach (FamilyInstance f in new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Cast<FamilyInstance>().Where(x => x.Location is LocationCurve))
            {
                string mk = Mk(f);
                if (mk != "ВП1" && mk != "П1") continue;
                Curve c = ((LocationCurve)f.Location).Curve; XYZ a = c.GetEndPoint(0), b = c.GetEndPoint(1);
                bool keep = mk == "ВП1" ? Math.Min(a.Y, b.Y) / MM > 7250 : (Math.Abs(a.Y / MM - 8800) < 50 && Math.Abs(b.Y / MM - 8800) < 50);
                if (keep) shown++; else if (f.CanBeHidden(v) && !f.IsHidden(v)) hide.Add(f.Id);
            }
            if (hide.Count > 0) v.HideElements(hide);
            L("  overhang: shown " + shown + ", hidden " + hide.Count);
        }

        static string P3(XYZ p) { return Math.Round(p.X / MM) + "," + Math.Round(p.Y / MM) + "," + Math.Round(p.Z / MM); }

        // sections: orientation, crop, far clip, sheet, annotations in them
        static void SecProbe(Document doc)
        {
            foreach (ViewSection v in new FilteredElementCollector(doc).OfClass(typeof(ViewSection)).Cast<ViewSection>().Where(x => !x.IsTemplate))
            {
                BoundingBoxXYZ cb = v.CropBox;
                Parameter far = v.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR);
                L("SEC '" + v.Name + "' type " + v.ViewType + " scale " + v.Scale + " origin " + P3(cb.Transform.Origin) + " right " + P3(cb.Transform.BasisX * 1000 * MM) + " view " + P3(v.ViewDirection * 1000 * MM)
                  + " crop " + Math.Round(cb.Min.X / MM) + "," + Math.Round(cb.Min.Y / MM) + ".." + Math.Round(cb.Max.X / MM) + "," + Math.Round(cb.Max.Y / MM) + " far " + (far != null ? Math.Round(far.AsDouble() / MM).ToString() : "?")
                  + " sheet " + (v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER) != null ? v.get_Parameter(BuiltInParameter.VIEWER_SHEET_NUMBER).AsString() : "-"));
                Element viewer = new FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Viewers).FirstOrDefault(e => e.Name == v.Name);
                L("   viewer " + (viewer != null ? viewer.Id.ToString() : "none"));
                Dictionary<string, int> cnt = new Dictionary<string, int>();
                foreach (Element e in new FilteredElementCollector(doc, v.Id).WhereElementIsNotElementType())
                {
                    if (e.Category == null) continue;
                    string k = e.Category.Name + (e is TextNote ? " '" + ((TextNote)e).Text.Trim() + "'" : "");
                    cnt[k] = cnt.ContainsKey(k) ? cnt[k] + 1 : 1;
                }
                foreach (var kv in cnt.Where(k => !k.Key.StartsWith("Несущ") && !k.Key.StartsWith("Обобщ"))) L("     " + kv.Key + " x" + kv.Value);
            }
        }

        static void ApplyFixes(Document doc, Dictionary<string, string> J)
        {
            int n = 0;
            Tx(doc, "braces visible", delegate
            {
                foreach (View v in new FilteredElementCollector(doc).OfClass(typeof(View)).Cast<View>())
                {
                    if (v.IsTemplate || v is ViewSheet || v is ViewSchedule || v.ViewType == ViewType.DrawingSheet || v.ViewType == ViewType.Legend) continue;
                    if (!v.CanCategoryBeHidden(new ElementId(BuiltInCategory.OST_StructuralFraming))) continue;
                    bool was = Category.GetCategory(doc, BuiltInCategory.OST_StructuralFraming).SubCategories.Cast<Category>().Any(sc => sc.Name.Contains("раскос") && v.GetCategoryHidden(sc.Id));
                    ShowBraces(doc, v);
                    if (was) { n++; L("  braces on: " + v.Name); }
                }
            });
            L("views fixed " + n);
            if (J.ContainsKey("bysection")) Tx(doc, "colour by section", delegate { ColorBySection(doc); });
            if (J.ContainsKey("overhang")) Tx(doc, "overhang", delegate { Overhang(doc, J["overhang"]); });
            if (J.ContainsKey("inline"))
            {
                FamilySymbol up = InlineTagFamily(doc, "КМ_Марка по оси", false, J["famdir"]);
                FamilySymbol dn = InlineTagFamily(doc, "КМ_Марка по оси низ", true, J["famdir"]);
                Tx(doc, "inline marks", delegate { InlineMarks(doc, up, dn); });
            }
            if (J.ContainsKey("braces")) Tx(doc, "brace details", delegate { BraceDetails(doc); });
            if (J.ContainsKey("secdress"))
            {
                FamilySymbol up = InlineTagFamily(doc, "КМ_Марка по оси", false, J["famdir"]);
                Tx(doc, "sections like the DWG", delegate { SecDress(doc, up); });
            }
            if (J.ContainsKey("sheet10"))
            {
                FamilySymbol up = InlineTagFamily(doc, "КМ_Марка по оси", false, J["famdir"]);
                FamilySymbol dn = InlineTagFamily(doc, "КМ_Марка по оси низ", true, J["famdir"]);
                Tx(doc, "sheet 10 like the DWG", delegate { Sheet10(doc, up, dn); });
            }
            if (J.ContainsKey("sheet3")) Tx(doc, "sheet 3 like the DWG", delegate { Sheet3(doc); });
            if (J.ContainsKey("nodes")) Tx(doc, "nodes like the DWG", delegate { NodesLikeDwg(doc); });
            if (J.ContainsKey("braces")) Tx(doc, "detail levels", delegate { DetailLevels(doc); });
            if (J.ContainsKey("braces")) Tx(doc, "sheets 7-8 layout", delegate { SheetLayout78(doc); });
            if (J.ContainsKey("declutter")) Tx(doc, "declutter marks", delegate { Declutter(doc, J["declutter"]); });
            List<ViewSheet> sheets = new FilteredElementCollector(doc).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().Where(s => !s.IsPlaceholder).ToList();
            if (!J.ContainsKey("noimg")) try
            {
                ImageExportOptions io = new ImageExportOptions();
                io.ExportRange = ExportRange.SetOfViews;
                io.SetViewsAndSheets(sheets.Select(s => s.Id).ToList());
                io.FilePath = Path.Combine(JobDir, "fx");
                io.ZoomType = ZoomFitType.FitToPage;
                io.PixelSize = 3200;
                io.HLRandWFViewsFileType = ImageFileType.PNG;
                io.ShadowViewsFileType = ImageFileType.PNG;
                io.ImageResolution = ImageResolution.DPI_150;
                doc.ExportImage(io);
            }
            catch (Exception ex) { L("image " + ex.Message); }
            if (J.ContainsKey("pdf"))
            {
                try
                {
                    PDFExportOptions po = new PDFExportOptions();
                    po.Combine = true;
                    po.FileName = Path.GetFileNameWithoutExtension(J["pdf"]);
                    po.PaperFormat = ExportPaperFormat.Default;
                    po.ZoomType = ZoomType.Zoom; po.ZoomPercentage = 100;
                    po.ColorDepth = ColorDepthType.Color;
                    po.RasterQuality = RasterQualityType.High;
                    int k;
                    doc.Export(Path.GetDirectoryName(J["pdf"]), sheets.OrderBy(s => int.TryParse(s.SheetNumber, out k) ? k : 999).Select(s => s.Id).ToList(), po);
                    L("pdf " + J["pdf"]);
                }
                catch (Exception ex) { L("pdf " + ex.Message); }
            }
        }
    }
}
