using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(PrepOps.Cmd))]
namespace PrepOps
{
    public class Cmd
    {
        const string OPS = @"C:\Users\Admin\AppData\Local\Temp\claude\D---------\0bad4b28-7a5f-4a0b-a094-8ae0f0d7847d\scratchpad\badam\prep_ops.json";
        const string LOG = @"C:\Users\Admin\AppData\Local\Temp\claude\D---------\0bad4b28-7a5f-4a0b-a094-8ae0f0d7847d\scratchpad\badam\prep_log.txt";

        static double D(object o) { return Convert.ToDouble(o); }
        static Point3d P(object o) { var l = (IList)o; return new Point3d(D(l[0]), D(l[1]), 0); }
        static ObjectId ById(Database db, string h) { return db.GetObjectId(false, new Handle(Convert.ToInt64(h, 16)), 0); }

        [CommandMethod("PREPOPS")]
        public void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            var db = doc.Database;
            var log = new List<string>();
            var ops = (IList)new JavaScriptSerializer { MaxJsonLength = int.MaxValue }.DeserializeObject(File.ReadAllText(OPS));
            var keys = new Dictionary<string, ObjectId>();
            int ok = 0, fail = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                int bad = 0;
                foreach (Dictionary<string, object> op in ops)
                {
                    if ((string)op["op"] != "check") continue;
                    try
                    {
                        var ent = (Entity)tr.GetObject(ById(db, (string)op["h"]), OpenMode.ForRead);
                        if (op.ContainsKey("ext"))
                        {
                            var ex = ent.GeometricExtents; var e = (IList)op["ext"];
                            if (Math.Abs(ex.MinPoint.X - D(e[0])) > 3 || Math.Abs(ex.MinPoint.Y - D(e[1])) > 3 || Math.Abs(ex.MaxPoint.X - D(e[2])) > 3 || Math.Abs(ex.MaxPoint.Y - D(e[3])) > 3)
                            { bad++; log.Add("CHECK ext " + op["h"] + " " + ex.MinPoint + " " + ex.MaxPoint); }
                        }
                        else
                        {
                            var dm = (RotatedDimension)ent;
                            if (dm.XLine1Point.DistanceTo(P(op["p2"])) > 1 || dm.XLine2Point.DistanceTo(P(op["p3"])) > 1)
                            { bad++; log.Add("CHECK dim " + op["h"]); }
                        }
                    }
                    catch (System.Exception ex) { bad++; log.Add("CHECK missing " + op["h"] + " " + ex.Message); }
                }
                if (bad > 0)
                {
                    log.Add("PREPOPS aborted, checks failed: " + bad);
                    File.WriteAllLines(LOG, log);
                    doc.Editor.WriteMessage("\nPREPOPS aborted: {0} checks failed\n", bad);
                    return;
                }
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
                var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
                foreach (Dictionary<string, object> op in ops)
                {
                    string kind = (string)op["op"];
                    if (kind == "check") continue;
                    try
                    {
                        if (kind == "pline")
                        {
                            var pl = new Polyline();
                            pl.SetDatabaseDefaults(db);
                            int i = 0;
                            foreach (var p in (IList)op["pts"]) { var q = (IList)p; pl.AddVertexAt(i++, new Point2d(D(q[0]), D(q[1])), 0, 0, 0); }
                            pl.Closed = true;
                            pl.Layer = (string)op["layer"];
                            pl.LineWeight = (LineWeight)Convert.ToInt32(op["lw"]);
                            var id = ms.AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true);
                            keys[(string)op["key"]] = id;
                            log.Add("pline " + op["key"] + " " + pl.Handle);
                        }
                        else if (kind == "hatch")
                        {
                            var src = keys[(string)op["src"]];
                            var h = new Hatch();
                            h.SetDatabaseDefaults(db);
                            h.Layer = (string)op["layer"];
                            var hid = ms.AppendEntity(h); tr.AddNewlyCreatedDBObject(h, true);
                            h.SetHatchPattern(HatchPatternType.PreDefined, (string)op["pattern"]);
                            h.PatternScale = D(op["scale"]);
                            h.PatternAngle = D(op["angle"]) * Math.PI / 180;
                            h.Associative = true;
                            h.AppendLoop(HatchLoopTypes.Outermost, new ObjectIdCollection { src });
                            h.EvaluateHatch(true);
                            log.Add("hatch " + op["src"] + " " + h.Handle);
                        }
                        else if (kind == "dimclone")
                        {
                            var src = (RotatedDimension)tr.GetObject(ById(db, (string)op["src"]), OpenMode.ForRead);
                            var nd = (RotatedDimension)src.Clone();
                            nd.XLine1Point = P(op["x1"]);
                            nd.XLine2Point = P(op["x2"]);
                            nd.DimLinePoint = P(op["dl"]);
                            ms.AppendEntity(nd); tr.AddNewlyCreatedDBObject(nd, true);
                            nd.TextPosition = P(op["tp"]);
                            nd.RecomputeDimensionBlock(true);
                            log.Add("dim " + op["src"] + " -> " + nd.Handle + " m=" + nd.Measurement.ToString("0.0"));
                        }
                        else if (kind == "dimset")
                        {
                            var dm = (RotatedDimension)tr.GetObject(ById(db, (string)op["h"]), OpenMode.ForWrite);
                            double m0 = dm.Measurement;
                            dm.XLine1Point = P(op["x1"]);
                            dm.XLine2Point = P(op["x2"]);
                            dm.DimLinePoint = P(op["dl"]);
                            dm.RecomputeDimensionBlock(true);
                            log.Add("dimset " + op["h"] + " m=" + m0.ToString("0.0") + " -> " + dm.Measurement.ToString("0.0"));
                        }
                        ok++;
                    }
                    catch (System.Exception ex) { fail++; log.Add("FAIL " + kind + " " + ex.Message); }
                }
                tr.Commit();
            }
            log.Add("PREPOPS ok=" + ok + " fail=" + fail);
            File.WriteAllLines(LOG, log);
            doc.Editor.WriteMessage("\nPREPOPS ok={0} fail={1}\n", ok, fail);
        }
    }
}
