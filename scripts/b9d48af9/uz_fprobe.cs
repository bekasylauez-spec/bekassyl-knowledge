var app = document.Application; var uiapp = new UIApplication(app);
string outd = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\uz_probe\";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; var sb = new System.Text.StringBuilder();
  foreach (var fn in new[] { "БК_типовая_аннотация_текст_с_выноской", "БК_марка_разрез", "БК_заголовок_наименование_вида_курсив" }) {
  Document d = null;
  try {
    d = app.OpenDocumentFile(outd + @"fam\" + fn + ".rfa"); sb.AppendLine("== " + fn + " cat " + d.OwnerFamily.FamilyCategory?.Name);
    foreach (var el in new FilteredElementCollector(d).WhereElementIsNotElementType().ToElements()) {
      string g = "";
      if (el is CurveElement ce) { var c = ce.GeometryCurve; g = (c is Arc ? "ARC r" + Math.Round(((Arc)c).Radius*304.8,2) + " " : "") + Math.Round(c.GetEndPoint(0).X*304.8,2) + "," + Math.Round(c.GetEndPoint(0).Y*304.8,2) + " -> " + Math.Round(c.GetEndPoint(1).X*304.8,2) + "," + Math.Round(c.GetEndPoint(1).Y*304.8,2) + " ls " + ce.LineStyle?.Name; }
      else if (el is TextElement te) g = "txt '" + te.Text + "' at " + Math.Round(te.Coord.X*304.8,2) + "," + Math.Round(te.Coord.Y*304.8,2) + " type " + d.GetElement(te.GetTypeId())?.Name;
      else if (el is FilledRegion) g = "filled";
      if (el.Category == null && g == "") continue;
      sb.AppendLine("  " + el.GetType().Name + " #" + el.Id + " " + el.Category?.Name + " " + el.Name + " " + g);
    }
    var fm = d.FamilyManager;
    foreach (FamilyParameter p in fm.Parameters) sb.AppendLine("  PARAM " + p.Definition.Name + " inst " + p.IsInstance + " type " + p.Definition.GetDataType().TypeId + " f " + p.Formula);
    foreach (FamilyType t in fm.Types) sb.AppendLine("  TYPE " + t.Name);
    foreach (Category sc in d.OwnerFamily.FamilyCategory.SubCategories) sb.AppendLine("  SUBCAT " + sc.Name + " w " + sc.GetLineWeight(GraphicsStyleType.Projection));
  } catch (Exception ex) { sb.AppendLine("ERR " + ex.Message); }
  try { if (d != null) d.Close(false); } catch {} }
  System.IO.File.WriteAllText(outd + "fprobe.txt", sb.ToString()); };
uiapp.Idling += hnd;
return "queued";
