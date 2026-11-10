var sb = new System.Text.StringBuilder(); var d = document; double M = 1 / 304.8;
foreach (var vn in new[] { "КМ Схема расположения баз колонн", "КМ Схема расположения колонн и вертикальных связей" }) {
  var v = new FilteredElementCollector(d).OfClass(typeof(ViewPlan)).Cast<View>().First(x => x.Name == vn);
  var dims = new FilteredElementCollector(d, v.Id).OfClass(typeof(Dimension)).Cast<Dimension>().ToList();
  var all = new FilteredElementCollector(d).OfClass(typeof(Dimension)).Cast<Dimension>().Where(x => x.OwnerViewId == v.Id).ToList();
  sb.AppendLine(vn + " visible dims " + dims.Count + " owned " + all.Count);
  foreach (var dm in all.Skip(4).Take(3)) { sb.AppendLine("  dim " + dm.Id + " refs " + dm.References.Size + " segs " + dm.Segments.Size); }
  var dl = new FilteredElementCollector(d).OfClass(typeof(CurveElement)).Cast<CurveElement>().Where(x => x.OwnerViewId == v.Id).Count(); sb.AppendLine("  detail lines " + dl);
}
return sb.ToString();
