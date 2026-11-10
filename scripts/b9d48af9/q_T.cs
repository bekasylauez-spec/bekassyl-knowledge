double M = 1 / 304.8; var sb = new System.Text.StringBuilder(); var d = document;
var sh = new FilteredElementCollector(d).OfClass(typeof(ViewSheet)).Cast<ViewSheet>().First(x => x.SheetNumber == "21");
foreach (var id in sh.GetAllViewports()) { var vp = (Viewport)d.GetElement(id); var v = (View)d.GetElement(vp.ViewId);
  var cb = v.CropBox; var T = vp.GetProjectionToSheetTransform(); var tr = cb.Transform;
  var a = tr.OfPoint(new XYZ(cb.Min.X, cb.Min.Y, 0)); var b = tr.OfPoint(new XYZ(cb.Max.X, cb.Max.Y, 0));
  Func<XYZ, string> f = p => Math.Round(p.X / M, 1) + "," + Math.Round(p.Y / M, 1);
  var ob = vp.GetBoxOutline();
  sb.AppendLine(v.Name + " outline " + f(ob.MinimumPoint) + " .. " + f(ob.MaximumPoint) + " | T.origin " + f(T.Origin) + " bx " + Math.Round(T.BasisX.X,4) + "," + Math.Round(T.BasisX.Y,4) + "," + Math.Round(T.BasisX.Z,4) + " by " + Math.Round(T.BasisY.X,4) + "," + Math.Round(T.BasisY.Y,4) + "," + Math.Round(T.BasisY.Z,4) + " bz " + Math.Round(T.BasisZ.X,4) + "," + Math.Round(T.BasisZ.Y,4) + "," + Math.Round(T.BasisZ.Z,4) + " scale " + v.Scale
    + " | Tworld a " + f(T.OfPoint(a)) + " b " + f(T.OfPoint(b))
    + " | Tloc a " + f(T.OfPoint(new XYZ(cb.Min.X, cb.Min.Y, 0))) + " b " + f(T.OfPoint(new XYZ(cb.Max.X, cb.Max.Y, 0)))); }
return sb.ToString();
