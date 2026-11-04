using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(KmModel.Cmd))]

namespace KmModel
{
    // Lays every layout out in model space: paper content x S, viewport content clipped to the viewport and
    // brought to the sheet through model->paper->sheet. S = scale of the main view (or DEFS for sheets without one).
    public class Cmd
    {
        StreamWriter log;
        void L(string s) { log.WriteLine(s); log.Flush(); }
        Transaction tr; BlockTableRecord ms; int added;
        double S;

        class Props { public Autodesk.AutoCAD.Colors.Color color; public ObjectId layer; public ObjectId ltype; public LineWeight lw; }

        [CommandMethod("KMMODEL")]
        public void Run()
        {
            var conf = File.ReadAllLines(Environment.GetEnvironmentVariable("KMMODEL_CONF"), Encoding.UTF8);
            string outPath = null; double defS = 100, gap = 0.15;
            var sheets = new List<string[]>();
            foreach (var c in conf)
            {
                var p = c.Split('|');
                if (p[0] == "LOG") log = new StreamWriter(p[1], false, Encoding.UTF8);
                else if (p[0] == "OUT") outPath = p[1];
                else if (p[0] == "DEFS") defS = double.Parse(p[1]);
                else if (p[0] == "SHEET") sheets.Add(p);   // SHEET|layout|W|H
            }
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                var orig = new List<ObjectId>();
                var ext = new Dictionary<ObjectId, Extents3d>();
                using (var t = db.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)t.GetObject(db.BlockTableId, OpenMode.ForRead);
                    var m = (BlockTableRecord)t.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead);
                    foreach (ObjectId id in m)
                    {
                        orig.Add(id);
                        var e = (Entity)t.GetObject(id, OpenMode.ForRead);
                        try { ext[id] = e.GeometricExtents; } catch { }
                    }
                    t.Commit();
                }
                L("model entities " + orig.Count);
                double x0 = 0;
                foreach (var sh in sheets)
                {
                    double W = double.Parse(sh[2]), H = double.Parse(sh[3]); double OX = sh.Length > 4 ? double.Parse(sh[4], System.Globalization.CultureInfo.InvariantCulture) : 0, OY = sh.Length > 5 ? double.Parse(sh[5], System.Globalization.CultureInfo.InvariantCulture) : 0;
                    using (tr = db.TransactionManager.StartTransaction())
                    {
                        var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                        ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                        var dict = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                        var lay = (Layout)tr.GetObject(dict.GetAt(sh[1]), OpenMode.ForRead);
                        var ps = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForRead);
                        var vps = new List<Viewport>();
                        var paper = new List<Entity>();
                        bool first = true; int offs = 0;
                        foreach (ObjectId id in ps)
                        {
                            var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                            if (e is Viewport) { if (first) { first = false; continue; } var v = (Viewport)e; if (OnSheet(v, OX, OY, W, H)) vps.Add(v); continue; }
                            try
                            {
                                var pe = e.GeometricExtents;
                                if (pe.MaxPoint.X < OX || pe.MinPoint.X > OX + W || pe.MaxPoint.Y < OY || pe.MinPoint.Y > OY + H) { offs++; continue; }
                            }
                            catch { }
                            paper.Add(e);
                        }
                        // main scale
                        Viewport main = null; foreach (var v in vps) if (main == null || v.Width * v.Height > main.Width * main.Height) main = v;
                        S = defS;
                        if (main != null) { double s = main.ViewHeight / main.Height; if (s > 1.5) S = Math.Round(s, 3); }
                        var p2s = Matrix3d.Displacement(new Vector3d(x0 - OX * S, -OY * S, 0)) * Matrix3d.Scaling(S, Point3d.Origin);
                        added = 0;
                        foreach (var v in vps)
                        {
                            double sc = v.Height / v.ViewHeight;
                            var t = v.ViewTarget + new Vector3d(v.ViewCenter.X, v.ViewCenter.Y, 0);
                            var r = new Extents3d(new Point3d(t.X - v.Width / 2 / sc, t.Y - v.Height / 2 / sc, -1e9), new Point3d(t.X + v.Width / 2 / sc, t.Y + v.Height / 2 / sc, 1e9));
                            var m2p = Matrix3d.Displacement(new Vector3d(v.CenterPoint.X, v.CenterPoint.Y, 0)) * Matrix3d.Scaling(sc, Point3d.Origin) * Matrix3d.Displacement(-t.GetAsVector());
                            var xf = p2s * m2p;
                            double tol = 0.05 / sc;
                            int before = added;
                            foreach (var id in orig)
                            {
                                Extents3d ex; if (!ext.TryGetValue(id, out ex)) continue;
                                if (ex.MaxPoint.X < r.MinPoint.X || ex.MinPoint.X > r.MaxPoint.X || ex.MaxPoint.Y < r.MinPoint.Y || ex.MinPoint.Y > r.MaxPoint.Y) continue;
                                Emit((Entity)tr.GetObject(id, OpenMode.ForRead), xf, r, tol, null);
                            }
                            L(string.Format(System.Globalization.CultureInfo.InvariantCulture, "VP|{0}|c={1:F3},{2:F3}|wh={3:F3},{4:F3}|sc={5:R}|tgt={6:F3},{7:F3}|n={8}", sh[1], v.CenterPoint.X, v.CenterPoint.Y, v.Width, v.Height, sc, t.X, t.Y, added - before));
                        }
                        int va = added;
                        foreach (var e in paper) Emit(e, p2s, null, 0, null);   // paper on top, as in the layout
                        int pa = added - va;
                        L(string.Format(System.Globalization.CultureInfo.InvariantCulture, "SHEET|{0}|x0={1:F1}|S={2}|W={3}|H={4}|paper={5}|total={6}|offsheet={7}", sh[1], x0, S, W, H, pa, added, offs));
                        tr.Commit();
                    }
                    x0 += W * S * (1 + gap);
                }
                // drop the old model content and the layouts
                using (var t = db.TransactionManager.StartTransaction())
                {
                    foreach (var id in orig) { var e = t.GetObject(id, OpenMode.ForWrite); e.Erase(); }
                    t.Commit();
                }
                var lm = LayoutManager.Current;
                lm.CurrentLayout = "Model";
                try { lm.CreateLayout("Лист1"); } catch (System.Exception ex) { L("create " + ex.Message); }
                foreach (var sh in sheets) { try { lm.DeleteLayout(sh[1]); } catch (System.Exception ex) { L("del " + sh[1] + " " + ex.Message); } }
                lm.CurrentLayout = "Model";
                db.SaveAs(outPath, DwgVersion.Current);
                L("SAVED " + outPath);
            }
            catch (System.Exception ex) { L("ERR " + ex); }
            log.Close();
        }

        static bool OnSheet(Viewport v, double OX, double OY, double W, double H)
        {
            var c = v.CenterPoint;
            return !(c.X + v.Width / 2 < OX + 1 || c.X - v.Width / 2 > OX + W - 1 || c.Y + v.Height / 2 < OY + 1 || c.Y - v.Height / 2 > OY + H - 1);
        }

        static bool Inside(Extents3d e, Extents3d r, double tol)
        {
            return e.MinPoint.X >= r.MinPoint.X - tol && e.MaxPoint.X <= r.MaxPoint.X + tol && e.MinPoint.Y >= r.MinPoint.Y - tol && e.MaxPoint.Y <= r.MaxPoint.Y + tol;
        }
        static bool CenterIn(Extents3d e, Extents3d r)
        {
            double cx = (e.MinPoint.X + e.MaxPoint.X) / 2, cy = (e.MinPoint.Y + e.MaxPoint.Y) / 2;
            return cx >= r.MinPoint.X && cx <= r.MaxPoint.X && cy >= r.MinPoint.Y && cy <= r.MaxPoint.Y;
        }

        void Inherit(Entity e, Props p)
        {
            if (p == null) return;
            try { if (e.ColorIndex == 0) e.Color = p.color; } catch { }
            try { if (e.Layer == "0") e.LayerId = p.layer; } catch { }
            try { if (e.Linetype == "ByBlock") e.LinetypeId = p.ltype; } catch { }
            try { if (e.LineWeight == LineWeight.ByBlock) e.LineWeight = p.lw; } catch { }
        }

        // e: entity in the coordinate space where clip r is defined; xf: that space -> model sheet
        void Emit(Entity e, Matrix3d xf, Extents3d? r, double tol, Props parent)
        {
            if (e is AttributeDefinition) return;
            if (e is BlockReference)
            {
                var br = (BlockReference)e;
                var btr = (BlockTableRecord)tr.GetObject(br.BlockTableRecord, OpenMode.ForRead);
                if (btr.IsFromExternalReference || btr.IsLayout) return;
                var pr = new Props { color = br.Color, layer = br.LayerId, ltype = br.LinetypeId, lw = br.LineWeight };
                if (parent != null)
                {
                    if (br.ColorIndex == 0) pr.color = parent.color;
                    if (br.Layer == "0") pr.layer = parent.layer;
                    if (br.Linetype == "ByBlock") pr.ltype = parent.ltype;
                    if (br.LineWeight == LineWeight.ByBlock) pr.lw = parent.lw;
                }
                var objs = new DBObjectCollection();
                try { br.Explode(objs); } catch (System.Exception ex) { L("explode " + br.Name + " " + ex.Message); return; }
                foreach (DBObject o in objs)
                {
                    var c = o as Entity;
                    if (c != null) { Emit(c, xf, r, tol, pr); }
                    if (!kept.Contains(o)) o.Dispose();
                }
                return;
            }
            Entity outE = null;
            if (r == null) { outE = Copy(e); }
            else
            {
                var rr = r.Value;
                Extents3d ex;
                try { ex = e.GeometricExtents; } catch { return; }
                if (ex.MaxPoint.X < rr.MinPoint.X || ex.MinPoint.X > rr.MaxPoint.X || ex.MaxPoint.Y < rr.MinPoint.Y || ex.MinPoint.Y > rr.MaxPoint.Y) return;
                bool inside = Inside(ex, rr, tol);
                if (inside) outE = Copy(e);
                else if (e is Line)
                {
                    var ln = (Line)e;
                    Point3d a, b;
                    if (!Clip(ln.StartPoint, ln.EndPoint, rr, out a, out b)) return;
                    var nl = new Line(a, b); nl.SetPropertiesFrom(ln); outE = nl;
                }
                else if (e is Polyline || e is Polyline2d)
                {
                    var objs = new DBObjectCollection();
                    try { e.Explode(objs); } catch { return; }
                    foreach (DBObject o in objs) { var c = o as Entity; if (c != null) Emit(c, xf, r, tol, parent); if (!kept.Contains(o)) o.Dispose(); }
                    return;
                }
                else if (e is DBText || e is MText) return;   // crossing texts already have full copies on the sheet
                else if (CenterIn(ex, rr)) outE = Copy(e);
                else return;
            }
            if (outE == null) return;
            Inherit(outE, parent);
            try { outE.TransformBy(xf); } catch (System.Exception ex) { L("xf " + e.GetType().Name + " " + ex.Message); return; }
            try { outE.LinetypeScale = outE.LinetypeScale * S; } catch { }
            ms.AppendEntity(outE); tr.AddNewlyCreatedDBObject(outE, true);
            kept.Add(outE);
            added++;
        }

        HashSet<DBObject> kept = new HashSet<DBObject>();

        Entity Copy(Entity e)
        {
            if (!e.ObjectId.IsNull) return (Entity)e.Clone();
            return e;   // exploded, not yet in a database: use it directly
        }

        // Liang-Barsky in XY
        static bool Clip(Point3d p0, Point3d p1, Extents3d r, out Point3d a, out Point3d b)
        {
            double t0 = 0, t1 = 1, dx = p1.X - p0.X, dy = p1.Y - p0.Y;
            a = p0; b = p1;
            double[] p = { -dx, dx, -dy, dy };
            double[] q = { p0.X - r.MinPoint.X, r.MaxPoint.X - p0.X, p0.Y - r.MinPoint.Y, r.MaxPoint.Y - p0.Y };
            for (int i = 0; i < 4; i++)
            {
                if (Math.Abs(p[i]) < 1e-12) { if (q[i] < 0) return false; continue; }
                double t = q[i] / p[i];
                if (p[i] < 0) { if (t > t1) return false; if (t > t0) t0 = t; }
                else { if (t < t0) return false; if (t < t1) t1 = t; }
            }
            if (t1 - t0 < 1e-9) return false;
            a = new Point3d(p0.X + t0 * dx, p0.Y + t0 * dy, p0.Z + t0 * (p1.Z - p0.Z));
            b = new Point3d(p0.X + t1 * dx, p0.Y + t1 * dy, p0.Z + t1 * (p1.Z - p0.Z));
            return true;
        }
    }
}
