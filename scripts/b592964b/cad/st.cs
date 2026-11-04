using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Application = Autodesk.AutoCAD.ApplicationServices.Core.Application;

[assembly: CommandClass(typeof(St.Cmds))]
namespace St
{
    // ops from %TEMP%\st_ops.json:
    //   {op:"scan", box:[x0,y0,x1,y1]}            — список объектов модели в рамке
    //   {op:"pts", h, closed, pts:[[x,y],...]}     — заменить вершины полилинии
    //   {op:"dim", h, p1:[x,y], p2:[x,y]}          — точки выносных линий размера (ассоциативность снимается)
    public class Cmds
    {
        static Point3d P(object o) { var a = (IList)o; return new Point3d(Convert.ToDouble(a[0]), Convert.ToDouble(a[1]), 0); }

        [CommandMethod("STAPPLY")]
        public static void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            var log = new StringBuilder();
            string tmp = Environment.GetEnvironmentVariable("TEMP");
            try
            {
                var ops = (IList)new JavaScriptSerializer().DeserializeObject(File.ReadAllText(Path.Combine(tmp, "st_ops.json"), Encoding.UTF8));
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (Dictionary<string, object> o in ops)
                    {
                        string op = (string)o["op"];
                        if (op == "scan")
                        {
                            var b = (IList)o["box"];
                            double x0 = Convert.ToDouble(b[0]), y0 = Convert.ToDouble(b[1]), x1 = Convert.ToDouble(b[2]), y1 = Convert.ToDouble(b[3]);
                            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                            foreach (ObjectId id in ms)
                            {
                                var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                                if (e == null) continue;
                                Extents3d ex;
                                try { ex = e.GeometricExtents; } catch { continue; }
                                if (ex.MaxPoint.X < x0 || ex.MinPoint.X > x1 || ex.MaxPoint.Y < y0 || ex.MinPoint.Y > y1) continue;
                                string extra = "";
                                if (e is Dimension) { try { extra = ((Dimension)e).Measurement.ToString("0.#"); } catch { } }
                                bool assoc = false;
                                if (!e.ExtensionDictionary.IsNull)
                                {
                                    var xd = (DBDictionary)tr.GetObject(e.ExtensionDictionary, OpenMode.ForRead);
                                    assoc = xd.Contains("ACAD_DIMASSOC");
                                }
                                log.AppendLine("scan " + e.Handle + " " + e.GetRXClass().DxfName + " " + e.Layer + " " + extra + (assoc ? " ASSOC" : "") +
                                    " [" + ex.MinPoint.X.ToString("0") + "," + ex.MinPoint.Y.ToString("0") + " - " + ex.MaxPoint.X.ToString("0") + "," + ex.MaxPoint.Y.ToString("0") + "]");
                            }
                            continue;
                        }
                        ObjectId oid;
                        if (!db.TryGetObjectId(new Handle(Convert.ToInt64((string)o["h"], 16)), out oid) || oid.IsErased) { log.AppendLine("no handle " + o["h"]); continue; }
                        var ent = tr.GetObject(oid, OpenMode.ForWrite);
                        if (op == "pts")
                        {
                            var pl = ent as Polyline;
                            if (pl == null) { log.AppendLine(o["h"] + " not polyline: " + ent.GetType().Name); continue; }
                            var pts = (IList)o["pts"];
                            int old = pl.NumberOfVertices;
                            for (int i = 0; i < pts.Count; i++)
                            {
                                var p = P(pts[i]);
                                if (i < pl.NumberOfVertices) { pl.SetPointAt(i, new Point2d(p.X, p.Y)); pl.SetBulgeAt(i, 0); pl.SetStartWidthAt(i, 0); pl.SetEndWidthAt(i, 0); }
                                else pl.AddVertexAt(i, new Point2d(p.X, p.Y), 0, 0, 0);
                            }
                            while (pl.NumberOfVertices > pts.Count) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                            pl.Closed = Convert.ToBoolean(o["closed"]);
                            log.AppendLine(o["h"] + " pts " + old + " -> " + pl.NumberOfVertices);
                        }
                        else if (op == "dim")
                        {
                            if (!ent.ExtensionDictionary.IsNull)
                            {
                                var xd = (DBDictionary)tr.GetObject(ent.ExtensionDictionary, OpenMode.ForWrite);
                                if (xd.Contains("ACAD_DIMASSOC")) { tr.GetObject(xd.GetAt("ACAD_DIMASSOC"), OpenMode.ForWrite).Erase(); xd.Remove("ACAD_DIMASSOC"); log.AppendLine(o["h"] + " assoc removed"); }
                            }
                            var p1 = P(o["p1"]); var p2 = P(o["p2"]);
                            if (ent is RotatedDimension) { var d = (RotatedDimension)ent; d.XLine1Point = p1; d.XLine2Point = p2; }
                            else if (ent is AlignedDimension) { var d = (AlignedDimension)ent; d.XLine1Point = p1; d.XLine2Point = p2; }
                            else { log.AppendLine(o["h"] + " not linear dim: " + ent.GetType().Name); continue; }
                            if (o.ContainsKey("dl")) { var dl = P(o["dl"]); if (ent is RotatedDimension) ((RotatedDimension)ent).DimLinePoint = dl; else ((AlignedDimension)ent).DimLinePoint = dl; }
                            ((Dimension)ent).RecomputeDimensionBlock(true);
                            log.AppendLine(o["h"] + " dim = " + ((Dimension)ent).Measurement.ToString("0.#"));
                        }
                    }
                    tr.Commit();
                }
                log.AppendLine("OK");
            }
            catch (System.Exception ex) { log.AppendLine("ERR " + ex); }
            File.WriteAllText(Path.Combine(tmp, "st_log.txt"), log.ToString(), Encoding.UTF8);
        }
    }
}
