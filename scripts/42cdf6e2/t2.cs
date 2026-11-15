{ var expDoc = System.IO.File.ReadAllText(@"D:\Бекасыл КЖ КМ\3602_Порталы_КМ\_авто\_expect_doc.txt", System.Text.Encoding.UTF8).Trim(); if (document.Title != expDoc) return "WRONG DOC"; }
const double MM = 304.8; string R = "";
var vft3 = new FilteredElementCollector(document).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().First(x => x.ViewFamily == ViewFamily.ThreeDimensional);
var boxes = new[] { new { n = "A1", c = new[] { 3305.0, -340, 50 }, f = new[] { 0.6, 0.8, -0.5 } }, new { n = "A2", c = new[] { 3305.0, -340, 50 }, f = new[] { -0.6, -0.8, -0.5 } },
    new { n = "B1", c = new[] { 3305.0, 460, 13600 }, f = new[] { 0.6, 0.8, -0.5 } }, new { n = "B2", c = new[] { 3305.0, 460, 13600 }, f = new[] { -0.6, -0.8, -0.5 } },
    new { n = "C1", c = new[] { -415.0, -340, -150 }, f = new[] { 0.6, 0.8, -0.5 } } };
var ids = new List<ElementId>();
try {
  foreach (var b in boxes) {
    var v = View3D.CreateIsometric(document, vft3.Id); v.Name = "zz_tmp_chk_" + b.n; v.ViewTemplateId = ElementId.InvalidElementId;
    v.DetailLevel = ViewDetailLevel.Fine; v.DisplayStyle = DisplayStyle.ShadingWithEdges;
    v.IsSectionBoxActive = true; v.SetSectionBox(new BoundingBoxXYZ { Min = new XYZ(b.c[0] - 200, b.c[1] - 200, b.c[2] - 140) / MM, Max = new XYZ(b.c[0] + 200, b.c[1] + 200, b.c[2] + 140) / MM });
    var fwd = new XYZ(b.f[0], b.f[1], b.f[2]).Normalize(); var right = fwd.CrossProduct(XYZ.BasisZ).Normalize(); var up = right.CrossProduct(fwd).Normalize();
    v.SetOrientation(new ViewOrientation3D(XYZ.Zero - fwd * 1000, up, fwd));
    foreach (var c in new[] { BuiltInCategory.OST_Levels, BuiltInCategory.OST_Grids, BuiltInCategory.OST_SectionBox }) try { v.SetCategoryHidden(new ElementId(c), true); } catch { }
    ids.Add(v.Id); }
  var o = new ImageExportOptions { ExportRange = ExportRange.SetOfViews, FilePath = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\img\base", HLRandWFViewsFileType = ImageFileType.PNG, ShadowViewsFileType = ImageFileType.PNG, PixelSize = 1200, ZoomType = ZoomFitType.FitToPage, ImageResolution = ImageResolution.DPI_150 };
  o.SetViewsAndSheets(ids); document.ExportImage(o); R = "exported " + ids.Count;
} catch (Exception ex) { R = "ERR " + ex.Message; }
finally { foreach (var id in ids) { try { document.Delete(id); } catch { } } }
return R + "; left views: " + new FilteredElementCollector(document).OfClass(typeof(View3D)).Cast<View3D>().Count(v => v.Name.StartsWith("zz_tmp_chk"));