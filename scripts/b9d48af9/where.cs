var uidoc = new UIApplication(document.Application).ActiveUIDocument; var sb = new System.Text.StringBuilder();
var v = uidoc.ActiveView; sb.AppendLine("view " + v.Name);
foreach (var id in uidoc.Selection.GetElementIds()) { var e = document.GetElement(id); var bb = e.get_BoundingBox(null); sb.AppendLine(id + " " + e.Category?.Name + " | " + e.Name + " | " + (bb == null ? "" : (bb.Min*304.8).ToString() + " - " + (bb.Max*304.8).ToString())); }
if (v is View3D v3) { var o = v3.GetOrientation(); sb.AppendLine("eye " + (o.EyePosition*304.8) + " fwd " + o.ForwardDirection); if (v3.IsSectionBoxActive) { var b = v3.GetSectionBox(); sb.AppendLine("sbox " + (b.Transform.OfPoint(b.Min)*304.8) + " - " + (b.Transform.OfPoint(b.Max)*304.8)); } }
foreach (var uv in uidoc.GetOpenUIViews()) { var r = uv.GetZoomCorners(); sb.AppendLine("uiview " + document.GetElement(uv.ViewId).Name + " " + (r[0]*304.8) + " - " + (r[1]*304.8)); }
return sb.ToString();
