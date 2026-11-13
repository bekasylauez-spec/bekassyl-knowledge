var d = document; var sb = new System.Text.StringBuilder();
sb.AppendLine("IsModified=" + d.IsModified + " ReadOnly=" + d.IsReadOnly + " Workshared=" + d.IsWorkshared + " units=" + d.GetUnits().GetFormatOptions(SpecTypeId.Length).GetUnitTypeId().TypeId);
var el = d.GetElement(new ElementId(2830228L)); sb.AppendLine("К1-26 " + el.Name + " ver last-changed: " + (WorksharingUtils.GetWorksharingTooltipInfo(d, el.Id)?.LastChangedBy));
sb.AppendLine("active view " + d.ActiveView.Name + " " + d.ActiveView.ViewType);
foreach (var v in new FilteredElementCollector(d).OfClass(typeof(View3D)).Cast<View3D>().Where(x => !x.IsTemplate)) sb.AppendLine("3D " + v.Name + " detail=" + v.DetailLevel + " style=" + v.DisplayStyle + " disc=" + v.Discipline);
sb.AppendLine("vft: " + string.Join(", ", new FilteredElementCollector(d).OfClass(typeof(ViewFamilyType)).Cast<ViewFamilyType>().Select(x => x.ViewFamily + ":" + x.Name)));
sb.AppendLine("version " + d.Application.VersionNumber);
return sb.ToString();
