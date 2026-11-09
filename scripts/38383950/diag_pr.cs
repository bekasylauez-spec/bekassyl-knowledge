var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\diag_pr.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    foreach (var el in new FilteredElementCollector(d).OfClass(typeof(FamilyInstance)).Cast<FamilyInstance>().Where(f => f.Location is LocationCurve && (f.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)?.AsString() ?? "") == "Пр1" && ((LocationCurve)f.Location).Curve.GetEndPoint(0).X < -0.3).Take(2))
    { var id = el.Id.Value;
      var c = (el.Location as LocationCurve).Curve; sb.AppendLine(id + " " + el.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).AsString() + " a " + (c.GetEndPoint(0) / MM) + " roll " + el.get_Parameter(BuiltInParameter.STRUCTURAL_BEND_DIR_ANGLE).AsDouble() * 180 / Math.PI);
      foreach (var so in el.get_Geometry(new Options()).OfType<GeometryInstance>().SelectMany(g => g.GetInstanceGeometry().OfType<Solid>()).Where(q => q.Volume > 0))
        foreach (PlanarFace f in so.Faces.OfType<PlanarFace>()) if (f.Area / (MM * MM) > 100000) sb.AppendLine("  face n " + f.FaceNormal + " o " + (f.Origin / MM) + " area " + Math.Round(f.Area / (MM * MM))); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
