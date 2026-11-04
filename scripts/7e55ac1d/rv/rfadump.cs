using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Collections.Generic;
using Autodesk.Revit.DB;
using Autodesk.Revit.ApplicationServices;

namespace RB
{
    public static class RfaDumper
    {
        public static void Dump(Application app, string[] files, string outTxt)
        {
            StringBuilder sb = new StringBuilder();
            foreach (string f in files)
            {
                sb.AppendLine("=== " + Path.GetFileName(f));
                try
                {
                    Document d = app.OpenDocumentFile(f);
                    if (!d.IsFamilyDocument)
                    {
                        foreach (ViewFamilyType vt in new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().Where(v => v.ViewFamily == ViewFamily.Section || v.ViewFamily == ViewFamily.Detail))
                            foreach (Parameter p in vt.Parameters) if (p.StorageType == StorageType.ElementId) sb.AppendLine("  VFT " + vt.Name + " " + p.Definition.Name + " = " + (d.GetElement(p.AsElementId()) != null ? d.GetElement(p.AsElementId()).Name : "-"));
                        foreach (ElementType et in new FilteredElementCollector(d).OfClass(typeof(ElementType)).Cast<ElementType>().Where(t => t.Name.StartsWith("КМ_")))
                            foreach (Parameter p in et.Parameters) sb.AppendLine("  TYPE " + et.GetType().Name + " " + et.Name + " | " + p.Definition.Name + " = " + (p.StorageType == StorageType.ElementId && d.GetElement(p.AsElementId()) != null ? d.GetElement(p.AsElementId()).Name : p.AsValueString()));
                        foreach (ViewSection vs in new FilteredElementCollector(d).OfClass(typeof(ViewSection)).Cast<ViewSection>().Where(v => !v.IsTemplate))
                            sb.AppendLine("  SEC " + vs.Name + " type " + d.GetElement(vs.GetTypeId()).Name + " hide " + (vs.get_Parameter(BuiltInParameter.SECTION_COARSER_SCALE_PULLDOWN_METRIC) != null ? vs.get_Parameter(BuiltInParameter.SECTION_COARSER_SCALE_PULLDOWN_METRIC).AsValueString() : "?"));
                        foreach (View pv in new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<View>().Where(v => !v.IsTemplate && v.Name.Contains("нижним")))
                        {
                            List<Element> sg = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().Where(e => e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == "СГ1").ToList();
                            List<ElementId> inView = new FilteredElementCollector(d, pv.Id).OfCategory(BuiltInCategory.OST_StructuralFraming).ToElementIds().ToList();
                            sb.AppendLine("  PLAN " + pv.Name + " SG1 total " + sg.Count + " in view " + sg.Count(e => inView.Contains(e.Id)));
                            foreach (Element e in sg.Take(3))
                            {
                                FamilyInstance fi = (FamilyInstance)e;
                                sb.AppendLine("    id " + e.Id + " type " + fi.Symbol.Name + " hidden " + e.IsHidden(pv) + " structType " + fi.StructuralType + " zj " + e.get_Parameter(BuiltInParameter.Z_JUSTIFICATION).AsValueString() + " bb " + (e.get_BoundingBox(pv) != null));
                                foreach (ElementId fid in pv.GetFilters()) if (d.GetElement(fid).Name == "КМ_СГ1") sb.AppendLine("    filter vis " + pv.GetFilterVisibility(fid) + " applied");
                            }
                            using (Transaction t = new Transaction(d, "test"))
                            {
                                t.Start();
                                FamilyInstance f0 = (FamilyInstance)sg[0];
                                FamilySymbol baseSym = f0.Symbol.Family.GetFamilySymbolIds().Select(i => (FamilySymbol)d.GetElement(i)).First(x => x.Name.StartsWith("Труба"));
                                f0.ChangeTypeId(baseSym.Id); d.Regenerate();
                                sb.AppendLine("    base type -> bb " + (f0.get_BoundingBox(pv) != null));
                                FamilyInstance f1 = (FamilyInstance)sg[1];
                                f1.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).Set("X"); d.Regenerate();
                                sb.AppendLine("    mark X -> bb " + (f1.get_BoundingBox(pv) != null));
                                foreach (ElementId fid in pv.GetFilters()) pv.RemoveFilter(fid);
                                d.Regenerate();
                                sb.AppendLine("    no filters -> bb " + (((FamilyInstance)sg[2]).get_BoundingBox(pv) != null));
                                Element nf = new FilteredElementCollector(d).OfCategory(BuiltInCategory.OST_StructuralFraming).WhereElementIsNotElementType().First(e => e.get_Parameter(BuiltInParameter.ALL_MODEL_MARK).AsString() == "НП1");
                                sb.AppendLine("    НП1 bb " + (nf.get_BoundingBox(pv) != null) + " Р1 cat hidden " + pv.GetCategoryHidden(new ElementId(BuiltInCategory.OST_StructuralFraming)));
                                foreach (Category sc in Category.GetCategory(d, BuiltInCategory.OST_StructuralFraming).SubCategories) sb.AppendLine("    subcat " + sc.Name + " hidden " + pv.GetCategoryHidden(sc.Id));
                                sb.AppendLine("    detail " + pv.DetailLevel + " template " + pv.ViewTemplateId + " discipline " + pv.Discipline);
                                Element s3 = sg[3];
                                foreach (Category sc in Category.GetCategory(d, BuiltInCategory.OST_StructuralFraming).SubCategories)
                                    if (pv.GetCategoryHidden(sc.Id)) { try { pv.SetCategoryHidden(sc.Id, false); d.Regenerate(); sb.AppendLine("    unhide " + sc.Name + " -> bb " + (s3.get_BoundingBox(pv) != null)); } catch (Exception ex) { sb.AppendLine("    unhide " + sc.Name + " ERR " + ex.Message); } }
                                foreach (ViewDetailLevel dl in new[] { ViewDetailLevel.Coarse, ViewDetailLevel.Medium, ViewDetailLevel.Fine })
                                { try { pv.DetailLevel = dl; d.Regenerate(); sb.AppendLine("    detail " + dl + " -> bb " + (s3.get_BoundingBox(pv) != null)); } catch (Exception ex) { sb.AppendLine("    detail ERR " + ex.Message); } }
                                t.RollBack();
                            }
                            foreach (Parameter p in pv.Parameters) if (p.Definition.Name.Contains("аскос") || p.Definition.Name.Contains("Brace") || p.Definition.Name.Contains("изуал")) sb.AppendLine("   view " + p.Definition.Name + " = " + p.AsValueString());
                        }
                        d.Close(false); continue;
                    }
                    sb.AppendLine("  category " + d.OwnerFamily.FamilyCategory.Name);
                    foreach (Parameter p in d.OwnerFamily.Parameters) sb.AppendLine("  fam param " + p.Definition.Name + " = " + p.AsValueString());
                    foreach (CurveElement c in new FilteredElementCollector(d).OfClass(typeof(CurveElement)).Cast<CurveElement>())
                    {
                        Curve g = c.GeometryCurve;
                        Parameter vis = c.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM);
                        sb.AppendLine("  curve " + c.GetType().Name + " " + g.GetType().Name + " " + R(g.GetEndPoint(0)) + "->" + R(g.GetEndPoint(1)) + " style " + (c.LineStyle != null ? c.LineStyle.Name : "-") + " vis " + (vis != null ? vis.AsValueString() : "?"));
                    }
                    foreach (FilledRegion fr in new FilteredElementCollector(d).OfClass(typeof(FilledRegion)).Cast<FilledRegion>()) sb.AppendLine("  filled " + fr.Id);
                    foreach (TextElement t in new FilteredElementCollector(d).OfClass(typeof(TextElement)).Cast<TextElement>())
                    {
                        Parameter vis = t.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM);
                        ElementType tt = (ElementType)d.GetElement(t.GetTypeId());
                        sb.AppendLine("  text '" + t.Text + "' " + R(t.Coord) + " type " + tt.Name + " size " + tt.get_Parameter(BuiltInParameter.TEXT_SIZE).AsValueString() + " vis " + (vis != null ? vis.AsValueString() + (vis.IsReadOnly ? "" : "") : "?") + " ha " + t.HorizontalAlignment);
                        foreach (Parameter p in t.Parameters) if (p.Definition.Name.Contains("Вид") || p.Definition.Name.Contains("Метк")) sb.AppendLine("     " + p.Definition.Name + " = " + p.AsValueString());
                    }
                    d.Close(false);
                }
                catch (Exception ex) { sb.AppendLine("  ERR " + ex.Message); }
            }
            File.WriteAllText(outTxt, sb.ToString(), Encoding.UTF8);
        }
        static string R(XYZ p) { return "(" + Math.Round(p.X * 304.8, 2) + "," + Math.Round(p.Y * 304.8, 2) + ")"; }
    }
}
