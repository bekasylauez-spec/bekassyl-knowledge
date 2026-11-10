var sb = new System.Text.StringBuilder(); var d = document; double M = 1 / 304.8;
foreach (var vn in new[] { "КМ Схема расположения баз колонн", "КМ Схема распорок и вертикальных связей", "КМ Схема распорок пристройки +5.750" }) {
  var v = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<View>().First(x => x.Name == vn);
  var g = new FilteredElementCollector(d, v.Id).OfClass(typeof(Grid)).GetElementCount(); var dm = new FilteredElementCollector(d, v.Id).OfClass(typeof(Dimension)).GetElementCount();
  var cat = d.Settings.Categories.Cast<Category>().First(c => c.Id.Value == (long)BuiltInCategory.OST_Grids);
  sb.AppendLine(vn + " grids " + g + " dims " + dm + " gridcat hidden " + v.GetCategoryHidden(cat.Id) + " scale " + v.Scale + " crop " + v.CropBox.Min / M + " .. " + v.CropBox.Max / M + " vg filters " + v.GetFilters().Count + " tmpl " + v.ViewTemplateId);
  var any = new FilteredElementCollector(d).OfClass(typeof(Grid)).Cast<Grid>().First(); sb.AppendLine("   grid1 hidden " + any.IsHidden(v));
}
return sb.ToString();
