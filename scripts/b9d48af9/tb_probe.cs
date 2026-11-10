var app = document.Application; var uiapp = new UIApplication(app);
string outd = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz_probe\";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder(); Document d = null; double M = 1 / 304.8;
  try {
    d = app.OpenDocumentFile(outd + @"fam\БК_штамп.rfa"); var fm = d.FamilyManager;
    foreach (FamilyParameter p in fm.Parameters) sb.AppendLine("PARAM " + p.Definition.Name + " inst " + p.IsInstance + " f " + p.Formula + " assoc " + p.AssociatedParameters.Size);
    foreach (FamilyType t in fm.Types) sb.AppendLine("TYPE " + t.Name);
    foreach (var el in new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements()) {
      var vp = el.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM); string vis = "";
      if (vp != null) { var fp = fm.GetAssociatedFamilyParameter(vp); vis = fp == null ? "" : fp.Definition.Name; }
      string g = "";
      if (el is CurveElement ce) { var c = ce.GeometryCurve; if (!c.IsBound) continue; g = Math.Round(c.GetEndPoint(0).X / M, 1) + "," + Math.Round(c.GetEndPoint(0).Y / M, 1) + " -> " + Math.Round(c.GetEndPoint(1).X / M, 1) + "," + Math.Round(c.GetEndPoint(1).Y / M, 1) + " " + ce.LineStyle?.Name; }
      else if (el is TextElement te) g = "txt '" + te.Text.Trim() + "' " + Math.Round(te.Coord.X / M, 1) + "," + Math.Round(te.Coord.Y / M, 1);
      else if (el is FamilyInstance fi) { var lp = (fi.Location as LocationPoint)?.Point; g = "inst " + fi.Symbol.FamilyName + ":" + fi.Name + (lp != null ? " @" + Math.Round(lp.X / M, 1) + "," + Math.Round(lp.Y / M, 1) : ""); }
      else if (el is FilledRegion) g = "region";
      else if (el is ImageInstance) g = "image";
      else continue;
      sb.AppendLine(el.GetType().Name + " #" + el.Id + " vis[" + vis + "] " + g);
    }
  } catch (Exception ex) { sb.AppendLine("ERR " + ex); }
  try { if (d != null) d.Close(false); } catch { }
  System.IO.File.WriteAllText(outd + "tb.txt", sb.ToString()); };
uiapp.Idling += hnd; return "queued";
