using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    public static class Dumper
    {
        public static void Dump(Application app, string src, string outTxt)
        {
            StringBuilder sb = new StringBuilder();
            ModelPath mp = ModelPathUtils.ConvertUserVisiblePathToModelPath(src);
            OpenOptions oo = new OpenOptions();
            BasicFileInfo bfi = BasicFileInfo.Extract(src);
            sb.AppendLine("version " + bfi.Format + " workshared " + bfi.IsWorkshared);
            if (bfi.IsWorkshared) oo.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets;
            Document d = app.OpenDocumentFile(mp, oo);
            try
            {
                sb.AppendLine("== categories with model elements");
                foreach (var g in new FilteredElementCollector(d).WhereElementIsNotElementType().Where(e => e.Category != null && e.Category.CategoryType == CategoryType.Model).GroupBy(e => e.Category.Name).OrderByDescending(g => g.Count()))
                    sb.AppendLine("  " + g.Key + " " + g.Count());
                sb.AppendLine("== titleblocks");
                foreach (FamilySymbol s in new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().Cast<FamilySymbol>())
                    sb.AppendLine("  " + s.FamilyName + " : " + s.Name + " id " + s.Id);
                sb.AppendLine("== sheets");
                foreach (ViewSheet vs in new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().OrderBy(v => v.SheetNumber))
                {
                    var tb = new FilteredElementCollector(d, vs.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).FirstOrDefault() as FamilyInstance;
                    sb.AppendLine("  [" + vs.SheetNumber + "] " + vs.Name + " | tb " + (tb != null ? tb.Symbol.FamilyName + ":" + tb.Symbol.Name : "-") + " | views: " +
                        string.Join("; ", vs.GetAllPlacedViews().Select(i => d.GetElement(i)).Select(v => ((View)v).ViewType + ":" + v.Name + " 1:" + ((View)v).Scale)));
                    foreach (ElementId sid in vs.GetAllPlacedViews()) { }
                }
                sb.AppendLine("== levels");
                foreach (Level l in new FilteredElementCollector(d).OfClass(typeof(Level)).Cast<Level>().OrderBy(x => x.Elevation)) sb.AppendLine("  " + l.Name + " @" + Math.Round(l.Elevation * 304.8) + " type " + d.GetElement(l.GetTypeId()).Name);
                sb.AppendLine("== grid types");
                foreach (GridType g in new FilteredElementCollector(d).OfClass(typeof(GridType)).Cast<GridType>()) sb.AppendLine("  " + g.Name);
                sb.AppendLine("== sheet 001 params");
                ViewSheet s1 = new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().FirstOrDefault(v => v.SheetNumber == "021.2");
                if (s1 != null) { foreach (Parameter p in s1.Parameters) sb.AppendLine("  " + p.Definition.Name + " = " + (p.StorageType == StorageType.String ? p.AsString() : p.AsValueString())); var tbi = new FilteredElementCollector(d, s1.Id).OfCategory(BuiltInCategory.OST_TitleBlocks).FirstOrDefault(); if (tbi != null) { sb.AppendLine("  -- tb instance"); foreach (Parameter p in tbi.Parameters) sb.AppendLine("    " + p.Definition.Name + " = " + (p.StorageType == StorageType.String ? p.AsString() : p.AsValueString())); BoundingBoxXYZ bb = tbi.get_BoundingBox(s1); sb.AppendLine("    bbox " + Math.Round(bb.Min.X*304.8) + "," + Math.Round(bb.Min.Y*304.8) + " - " + Math.Round(bb.Max.X*304.8) + "," + Math.Round(bb.Max.Y*304.8)); foreach (ElementId vp in s1.GetAllViewports()) { Viewport v = (Viewport)d.GetElement(vp); sb.AppendLine("    vp " + d.GetElement(v.ViewId).Name + " at " + Math.Round(v.GetBoxCenter().X*304.8) + "," + Math.Round(v.GetBoxCenter().Y*304.8) + " type " + d.GetElement(v.GetTypeId()).Name); } } }
                sb.AppendLine("== schedules");
                foreach (ViewSchedule s in new FilteredElementCollector(d).OfClass(typeof(ViewSchedule)).Cast<ViewSchedule>().Where(s => !s.IsTitleblockRevisionSchedule && !s.IsTemplate))
                    sb.AppendLine("  " + s.Name + " | cat " + (Category.GetCategory(d, s.Definition.CategoryId) != null ? Category.GetCategory(d, s.Definition.CategoryId).Name : "-") + " | fields " + string.Join(", ", Enumerable.Range(0, s.Definition.GetFieldCount()).Select(i => s.Definition.GetField(i).GetName())));
                sb.AppendLine("== view templates");
                foreach (View v in new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => v.IsTemplate).OrderBy(v => v.Name))
                    sb.AppendLine("  " + v.ViewType + " | " + v.Name + " | scale " + v.Scale + " | detail " + v.DetailLevel + " | style " + v.DisplayStyle + " | filters " + (v.AreGraphicsOverridesAllowed() ? string.Join(", ", v.GetFilters().Select(f => d.GetElement(f).Name)) : "n/a"));
                sb.AppendLine("== views (non-template)");
                foreach (View v in new FilteredElementCollector(d).OfClass(typeof(View)).Cast<View>().Where(v => !v.IsTemplate && v.ViewType != ViewType.DrawingSheet && v.ViewType != ViewType.Schedule && v.ViewType != ViewType.ProjectBrowser && v.ViewType != ViewType.SystemBrowser && v.ViewType != ViewType.Internal).OrderBy(v => v.ViewType.ToString()).ThenBy(v => v.Name))
                {
                    Element t = d.GetElement(v.ViewTemplateId);
                    sb.AppendLine("  " + v.ViewType + " | " + v.Name + " | 1:" + v.Scale + " | tpl " + (t != null ? t.Name : "-") + " | " + v.DetailLevel + " " + v.DisplayStyle + " | filters " + (!v.AreGraphicsOverridesAllowed() ? "n/a" : string.Join(", ", v.GetFilters().Select(f => d.GetElement(f).Name + (v.GetFilterOverrides(f).ProjectionLineColor.IsValid ? "(" + v.GetFilterOverrides(f).ProjectionLineColor.Red + "," + v.GetFilterOverrides(f).ProjectionLineColor.Green + "," + v.GetFilterOverrides(f).ProjectionLineColor.Blue + ")" : "") + (v.GetFilterOverrides(f).SurfaceForegroundPatternColor.IsValid ? "[" + v.GetFilterOverrides(f).SurfaceForegroundPatternColor.Red + "," + v.GetFilterOverrides(f).SurfaceForegroundPatternColor.Green + "," + v.GetFilterOverrides(f).SurfaceForegroundPatternColor.Blue + "]" : "")))));
                }
                sb.AppendLine("== filters");
                foreach (ParameterFilterElement f in new FilteredElementCollector(d).OfClass(typeof(ParameterFilterElement)).Cast<ParameterFilterElement>())
                    sb.AppendLine("  " + f.Name + " | cats " + string.Join(",", f.GetCategories().Select(c => Category.GetCategory(d, c) != null ? Category.GetCategory(d, c).Name : c.ToString())));
                sb.AppendLine("== text types");
                foreach (TextNoteType t in new FilteredElementCollector(d).OfClass(typeof(TextNoteType)).Cast<TextNoteType>()) sb.AppendLine("  " + t.Name);
                sb.AppendLine("== dimension types");
                foreach (DimensionType t in new FilteredElementCollector(d).OfClass(typeof(DimensionType)).Cast<DimensionType>()) sb.AppendLine("  " + t.StyleType + " " + t.Name);
                sb.AppendLine("== families (annotation/generic)");
                foreach (Family f in new FilteredElementCollector(d).OfClass(typeof(Family)).Cast<Family>().OrderBy(f => f.FamilyCategory != null ? f.FamilyCategory.Name : ""))
                    sb.AppendLine("  " + (f.FamilyCategory != null ? f.FamilyCategory.Name : "?") + " | " + f.Name);
                sb.AppendLine("== project info");
                foreach (Parameter p in d.ProjectInformation.Parameters) sb.AppendLine("  " + p.Definition.Name + " = " + p.AsValueString() + " " + p.AsString());
            }
            catch (Exception ex) { sb.AppendLine("ERR " + ex); }
            File.WriteAllText(outTxt, sb.ToString(), Encoding.UTF8);
            d.Close(false);
        }
    }
}
