var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\diag_loc.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    foreach (var id in new long[]{2974449L, 2964451L}) { var el = d.GetElement(new ElementId(id));
      sb.AppendLine(id + " " + el.Category?.Name + " " + el.Name + " " + (el as FamilyInstance)?.Symbol?.Family?.Name);
      var lp = el.Location as LocationPoint; var lc = el.Location as LocationCurve;
      if (lp != null) sb.AppendLine(" pt " + lp.Point.X/MM + " " + lp.Point.Y/MM + " " + lp.Point.Z/MM + " rot " + lp.Rotation);
      if (lc != null) sb.AppendLine(" crv " + lc.Curve.GetEndPoint(0)/MM + " " + lc.Curve.GetEndPoint(1)/MM);
      var bb = el.get_BoundingBox(null); sb.AppendLine(" bb " + bb.Min/MM + " " + bb.Max/MM);
      var fi = el as FamilyInstance; if (fi != null) { sb.AppendLine(" cutby " + string.Join(",", JoinGeometryUtils.GetJoinedElements(d, el).Select(q=>q.Value)) );
        foreach (Parameter p in fi.Parameters) if (p.Definition.Name.Contains("мещ") || p.Definition.Name.Contains("ффсет") || p.Definition.Name.Contains("Смещ")) sb.AppendLine("  " + p.Definition.Name + "=" + p.AsValueString()); } }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
