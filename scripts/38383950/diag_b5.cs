var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\38383950-ff15-462c-99ed-3b9b23e702df\scratchpad\diag_b5.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  try { var d = app.Documents.Cast<Document>().First(x => x.PathName.EndsWith("ВП-В109-КМ_Цех Блок 1.rvt"));
    var a = d.GetElement(new ElementId(2931981L)); var b = d.GetElement(new ElementId(2945954L));
    Func<Element, List<Solid>> S = el => el.get_Geometry(new Options()).OfType<Solid>().Where(q => q.Volume > 0).ToList();
    var sa = S(a); var sbs = S(b); sb.AppendLine(a.Name + " | " + b.Name + " " + sa.Count + "/" + sbs.Count);
    Func<Solid, string> BB = q => { var bb = q.GetBoundingBox(); var p = bb.Transform.OfPoint(bb.Min); var r = bb.Transform.OfPoint(bb.Max);
        return string.Format("[{0:0.0} {1:0.0} {2:0.0}]..[{3:0.0} {4:0.0} {5:0.0}]", p.X / MM, p.Y / MM, p.Z / MM, r.X / MM, r.Y / MM, r.Z / MM); };
    for (int i = 0; i < sa.Count; i++) for (int j = 0; j < sbs.Count; j++) { Solid x = null; try { x = BooleanOperationsUtils.ExecuteBooleanOperation(sa[i], sbs[j], BooleanOperationsType.Intersect); } catch { }
        if (x != null && x.Volume / (MM * MM * MM) > 1) sb.AppendLine("plate " + i + " " + BB(sa[i]) + "  weld " + j + " " + BB(sbs[j]) + "  x " + BB(x)); }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  System.IO.File.WriteAllText(log, sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
}
