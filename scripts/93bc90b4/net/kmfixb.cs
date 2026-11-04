using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(KmFix.Cmd))]

namespace KmFix
{
    // Ops (model units), one per line:
    //  MIRROR|xa|ya|xb|yb|V or H|c|band|exYa|exYb   copy entities inside window mirrored about x=c (V) or y=c (H);
    //        texts are moved (not flipped); entities inside |coord-c|<band are skipped; texts/wipeouts inside y [exYa,exYb] skipped
    //  SHIFT|xa|ya|xb|yb|dx|dy|text   copy texts == text and wipeouts inside window, shifted
    //  TEXT|x|y|tol|old|new          replace text strings whose position is within tol of (x,y)
    public class Cmd
    {
        StreamWriter log;
        void L(string s) { log.WriteLine(s); log.Flush(); }
        static double D(string s) { return double.Parse(s, CultureInfo.InvariantCulture); }

        [CommandMethod("KMFIXB")]
        public void Run()
        {
            var cfg = Environment.GetEnvironmentVariable("KMFIX_CONF"); if (string.IsNullOrEmpty(cfg)) cfg = Path.Combine(Path.GetTempPath(), "kmfix_conf.txt");
            var lines = File.ReadAllLines(cfg, Encoding.UTF8);
            string outPath = null, copyPath = null;
            foreach (var c in lines) { var p = c.Split('|'); if (p[0] == "LOG") log = new StreamWriter(p[1], false, Encoding.UTF8); if (p[0] == "OUT") outPath = p[1]; if (p[0] == "COPY") copyPath = p[1]; }
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            try
            {
                // cache extents of all model entities once
                var ents = new List<KeyValuePair<ObjectId, Extents3d>>();
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                    var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead);
                    foreach (ObjectId id in ms) { var e = (Entity)tr.GetObject(id, OpenMode.ForRead); try { ents.Add(new KeyValuePair<ObjectId, Extents3d>(id, e.GeometricExtents)); } catch { } }
                    tr.Commit();
                }
                foreach (var c in lines)
                {
                    var p = c.Split('|');
                    if (p[0] == "MIRROR") Mirror(db, ents, p);
                    else if (p[0] == "SHIFT") Shift(db, ents, p);
                    else if (p[0] == "TEXT") Text(db, ents, p);
                    else if (p[0] == "MIRROR2") Mirror2(db, ents, p);
                    else if (p[0] == "ERASE") Erase(db, ents, p);
                    else if (p[0] == "DIM") Dim(db, ents, p);
                    else if (p[0] == "LABEL") Label(db, ents, p);
                    else if (p[0] == "CONSOLE") Console(db, ents, p);
                    else if (p[0] == "MOVEY") MoveY(db, ents, p);
                    else if (p[0] == "MOVET") MoveT(db, ents, p);
                    else if (p[0] == "IMPORT") Import(db, p);
                    else if (p[0] == "DELTXT") DelTxt(db, ents, p);
                    else if (p[0] == "ADDTXT") AddTxt(db, ents, p);
                    else if (p[0] == "SETTXT") SetTxt(db, ents, p);
                    else if (p[0] == "ADDLINE") AddLine(db, ents, p);
                    else if (p[0] == "CLOUD") Cloud(db, ents, p);
                    else if (p[0] == "IBEAM") IBeam(db, ents, p);
                    else if (p[0] == "LOWER") Lower(db, ents, p);
                    else if (p[0] == "CRANEMOVE") CraneMove(db, ents, p);
                }
                if (outPath != null) { db.SaveAs(outPath, DwgVersion.Current); L("SAVED " + outPath); }
                if (copyPath != null) { using (var w = db.Wblock()) w.SaveAs(copyPath, DwgVersion.Current); L("COPY " + copyPath); }
                L("DONE");
            }
            catch (System.Exception ex) { L("ERR " + ex); }
            log.Close();
        }

        static bool In(Extents3d e, double xa, double ya, double xb, double yb)
        { return e.MinPoint.X >= xa && e.MaxPoint.X <= xb && e.MinPoint.Y >= ya && e.MaxPoint.Y <= yb; }

        void Mirror(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]); bool vert = p[5] == "V"; double c = D(p[6]), band = D(p[7]);
            double exa = p.Length > 8 ? D(p[8]) : 1e18, exb = p.Length > 9 ? D(p[9]) : -1e18;
            var m = vert ? Matrix3d.Mirroring(new Line3d(new Point3d(c, 0, 0), new Point3d(c, 1, 0))) : Matrix3d.Mirroring(new Line3d(new Point3d(0, c, 0), new Point3d(1, c, 0)));
            int n = 0, nt = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    if (!In(ex, xa, ya, xb, yb)) continue;
                    double lo = vert ? ex.MinPoint.X : ex.MinPoint.Y, hi = vert ? ex.MaxPoint.X : ex.MaxPoint.Y;
                    if (lo > c - band && hi < c + band) continue;
                    var e = (Entity)tr.GetObject(kv.Key, OpenMode.ForRead);
                    bool isText = e is DBText || e is MText;
                    if ((isText || e is Wipeout) && ex.MinPoint.Y >= exa && ex.MaxPoint.Y <= exb) continue;
                    var cp = (Entity)e.Clone();
                    if (isText)
                    {
                        double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2, cy = (ex.MinPoint.Y + ex.MaxPoint.Y) / 2;
                        cp.TransformBy(vert ? Matrix3d.Displacement(new Vector3d(2 * (c - cx), 0, 0)) : Matrix3d.Displacement(new Vector3d(0, 2 * (c - cy), 0)));
                        nt++;
                    }
                    else cp.TransformBy(m);
                    ms.AppendEntity(cp); tr.AddNewlyCreatedDBObject(cp, true); n++;
                }
                tr.Commit();
            }
            L(string.Format("MIRROR {0} {1} -> {2} copies ({3} texts)", p[5], c, n, nt));
        }

        void Shift(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), dx = D(p[5]), dy = D(p[6]); string txt = p[7];
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                foreach (var kv in ents)
                {
                    if (!In(kv.Value, xa, ya, xb, yb)) continue;
                    var e = (Entity)tr.GetObject(kv.Key, OpenMode.ForRead);
                    bool ok = (e is DBText && ((DBText)e).TextString == txt) || e is Wipeout;
                    if (!ok) continue;
                    var cp = (Entity)e.Clone(); cp.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0)));
                    ms.AppendEntity(cp); tr.AddNewlyCreatedDBObject(cp, true); n++;
                }
                tr.Commit();
            }
            L("SHIFT " + txt + " -> " + n);
        }


        // MIRROR2|xa|ya|xb|yb|c|skipHya|skipHyb|cols(;)  KN callouts: mirror about y=c and about the nearest column x.
        // Takes texts, wipeouts, slanted lines and horizontal lines outside [skipHya,skipHyb]; vertical lines are skipped.
        void Mirror2(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), c = D(p[5]), sa = D(p[6]), sb = D(p[7]);
            var cols = new List<double>(); foreach (var t in p[8].Split(';')) cols.Add(D(t));
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    if (!In(ex, xa, ya, xb, yb)) continue;
                    var e = (Entity)tr.GetObject(kv.Key, OpenMode.ForRead);
                    bool isText = e is DBText || e is MText;
                    if (e is Line)
                    {
                        var ln = (Line)e; double dx = Math.Abs(ln.EndPoint.X - ln.StartPoint.X), dy = Math.Abs(ln.EndPoint.Y - ln.StartPoint.Y);
                        if (dx < 1e-6) continue;
                        if (dy < 1e-6 && ln.StartPoint.Y >= sa && ln.StartPoint.Y <= sb) continue;
                        if (dy > 1e-6 && p.Length > 9 && ln.Length < D(p[9])) continue;
                    }
                    else if (!isText && !(e is Wipeout)) continue;
                    double col = cols[0]; foreach (var x in cols) if (Math.Abs(x - ex.MinPoint.X) < Math.Abs(col - ex.MinPoint.X)) col = x;
                    var cp = (Entity)e.Clone();
                    if (isText)
                    {
                        double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2, cy = (ex.MinPoint.Y + ex.MaxPoint.Y) / 2;
                        cp.TransformBy(Matrix3d.Displacement(new Vector3d(2 * (col - cx), 2 * (c - cy), 0)));
                    }
                    else
                    {
                        cp.TransformBy(Matrix3d.Mirroring(new Line3d(new Point3d(0, c, 0), new Point3d(1, c, 0))));
                        cp.TransformBy(Matrix3d.Mirroring(new Line3d(new Point3d(col, 0, 0), new Point3d(col, 1, 0))));
                    }
                    ms.AppendEntity(cp); tr.AddNewlyCreatedDBObject(cp, true); n++;
                }
                tr.Commit();
            }
            L("MIRROR2 " + c + " -> " + n);
        }

        // ERASE|xa|ya|xb|yb|what   what = LINES (lines inside), TEXT:<s> (texts == s touching window), WIPEOUT>h (wipeouts inside, taller than h)
        void Erase(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]); string w = p[5];
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    var o = tr.GetObject(kv.Key, OpenMode.ForRead, true);
                    if (o.IsErased) continue;
                    bool hit = false;
                    if (w == "LINES") hit = o is Line && In(ex, xa, ya, xb, yb);
                    else if (w.StartsWith("TEXT:")) hit = o is DBText && ((DBText)o).TextString == w.Substring(5) && !(ex.MaxPoint.X < xa || ex.MinPoint.X > xb || ex.MaxPoint.Y < ya || ex.MinPoint.Y > yb);
                    else if (w.StartsWith("HLINEX:")) { var q = w.Split(':'); var ln = o as Line; hit = ln != null && Math.Abs(ln.StartPoint.Y - ln.EndPoint.Y) < 1e-6 && Math.Abs(ex.MinPoint.X - D(q[1])) < D(q[2]) && ex.MinPoint.Y >= ya && ex.MaxPoint.Y <= yb; }
                    else if (w.StartsWith("HSEG:")) { var q = w.Split(':'); var ln = o as Line; hit = ln != null && Math.Abs(ln.StartPoint.Y - ln.EndPoint.Y) < 1e-6 && ex.MinPoint.X >= D(q[1]) && ex.MinPoint.X <= D(q[2]) && ex.MaxPoint.X >= D(q[3]) && ex.MaxPoint.X <= D(q[4]) && ex.MinPoint.Y >= ya && ex.MaxPoint.Y <= yb; }
                    else if (w.StartsWith("WIPEOUT>")) hit = o is Wipeout && In(ex, xa, ya, xb, yb) && (ex.MaxPoint.Y - ex.MinPoint.Y) > D(w.Substring(8));
                    if (!hit) continue;
                    o.UpgradeOpen(); o.Erase(); n++;
                }
                tr.Commit();
            }
            L("ERASE " + w + " -> " + n);
        }

        // DIM|x|tick|xExt|gap|textTpl x;y;tol|lineTpl x;y;tol|y1;y2;y3|unit  vertical chain at x, texts rotated 90 left of the line
        void Dim(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double x = D(p[1]), tick = D(p[2]), xf = D(p[3]), gap = D(p[4]);
            var tt = p[5].Split(';'); var lt = p[6].Split(';');
            var ys = new List<double>(); foreach (var t in p[7].Split(';')) ys.Add(D(t));
            ys.Sort();
            double unit = D(p[8]);
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                DBText ttpl = null; Line ltpl = null;
                foreach (var kv in ents)
                {
                    var o = tr.GetObject(kv.Key, OpenMode.ForRead, true);
                    var ex = kv.Value;
                    if (ttpl == null && o is DBText && Math.Abs(((DBText)o).Position.X - D(tt[0])) < D(tt[2]) && Math.Abs(((DBText)o).Position.Y - D(tt[1])) < D(tt[2])) ttpl = (DBText)o;
                    if (ltpl == null && o is Line && Math.Abs(ex.MinPoint.X - D(lt[0])) < D(lt[2]) && Math.Abs(ex.MinPoint.Y - D(lt[1])) < D(lt[2])) ltpl = (Line)o;
                }
                if (ttpl == null || ltpl == null) { L("DIM template not found " + (ttpl == null) + " " + (ltpl == null)); return; }
                Action<Point3d, Point3d> add = (a, b) => { var l = (Line)ltpl.Clone(); l.StartPoint = a; l.EndPoint = b; ms.AppendEntity(l); tr.AddNewlyCreatedDBObject(l, true); };
                add(new Point3d(x, ys[0], 0), new Point3d(x, ys[ys.Count - 1], 0));
                foreach (var y in ys)
                {
                    add(new Point3d(xf, y, 0), new Point3d(x + tick, y, 0));
                    add(new Point3d(x - tick / 2, y - tick / 2, 0), new Point3d(x + tick / 2, y + tick / 2, 0));
                }
                for (int i = 0; i + 1 < ys.Count; i++)
                {
                    var t = (DBText)ttpl.Clone();
                    t.TextString = Math.Round(Math.Abs(ys[i + 1] - ys[i]) / unit).ToString();
                    ms.AppendEntity(t); tr.AddNewlyCreatedDBObject(t, true);
                    var e = t.GeometricExtents; double len = e.MaxPoint.Y - e.MinPoint.Y, wid = e.MaxPoint.X - e.MinPoint.X;
                    double ty = i == 0 ? ys[0] - gap - len : ys[ys.Count - 1] + gap;
                    t.TransformBy(Matrix3d.Displacement(new Vector3d((x - gap - wid) - e.MinPoint.X, ty - e.MinPoint.Y, 0)));
                    if (i == 0) add(new Point3d(x, ys[0], 0), new Point3d(x, ty, 0)); else add(new Point3d(x, ys[ys.Count - 1], 0), new Point3d(x, ty + len, 0));
                }
                tr.Commit();
            }
            L("DIM at " + x + " " + p[7]);
        }


        // LABEL|xa|ya|xb|yb|c|shelfOld|shelfNew|tol  copy callouts (leader + shelf + text + wipeout) to the other side of axis y=c:
        // shelf, text and wipeout are moved by (shelfNew - shelfOld); the leader keeps its shelf end x, its column end is mirrored about c.
        void Label(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), c = D(p[5]), so = D(p[6]), sn = D(p[7]), tol = D(p[8]);
            var mv = Matrix3d.Displacement(new Vector3d(0, sn - so, 0));
            int nl = 0, ns = 0, nt = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    bool pin = ex.MinPoint.X >= xa && ex.MinPoint.X <= xb && ex.MinPoint.Y >= ya && ex.MinPoint.Y <= yb; if (!In(ex, xa, ya, xb, yb) && !pin) continue;
                    var e = (Entity)tr.GetObject(kv.Key, OpenMode.ForRead); if (!In(ex, xa, ya, xb, yb) && !(e is DBText)) continue;
                    Entity cp = null;
                    if (e is Line)
                    {
                        var ln = (Line)e; var a = ln.StartPoint; var b = ln.EndPoint;
                        bool hor = Math.Abs(a.Y - b.Y) < 1e-6, ver = Math.Abs(a.X - b.X) < 1e-6;
                        if (hor && Math.Abs(a.Y - so) < tol) { cp = (Entity)ln.Clone(); cp.TransformBy(mv); ns++; }
                        else if (!hor && !ver && (Math.Abs(a.Y - so) < tol || Math.Abs(b.Y - so) < tol))
                        {
                            var sh = Math.Abs(a.Y - so) < tol ? a : b; var co = Math.Abs(a.Y - so) < tol ? b : a;
                            var l2 = (Line)ln.Clone(); l2.StartPoint = new Point3d(sh.X, sn, 0); l2.EndPoint = new Point3d(co.X, 2 * c - co.Y, 0); cp = l2; nl++;
                        }
                    }
                    else if (e is DBText && ((DBText)e).TextString == "КН") { cp = (Entity)e.Clone(); cp.TransformBy(mv); nt++; }
                    else if (e is Wipeout && (ex.MaxPoint.Y - ex.MinPoint.Y) < 4 * tol * 10) { cp = (Entity)e.Clone(); cp.TransformBy(mv); }
                    if (cp != null) { ms.AppendEntity(cp); tr.AddNewlyCreatedDBObject(cp, true); }
                }
                tr.Commit();
            }
            L(string.Format("LABEL c={0}: leaders {1}, shelves {2}, texts {3}", c, nl, ns, nt));
        }


        // CONSOLE|xa|ya|xb|yb|c|dy|thr|dx|old=new;old=new
        // everything inside the window goes up by dy; points farther than thr from x=c move dx toward c (texts/wipeouts by their centre)
        void Console(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), c = D(p[5]), dy = D(p[6]), thr = D(p[7]), dx = D(p[8]);
            var rep = new Dictionary<string, string>();
            if (p.Length > 9 && p[9].Length > 0) foreach (var kv in p[9].Split(';')) { var a = kv.Split('='); rep[a[0]] = a[1]; }
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    if (!In(ex, xa, ya, xb, yb)) continue;
                    if (p.Length > 11 && Math.Abs(ex.MinPoint.X - c) < D(p[10]) && Math.Abs(ex.MaxPoint.X - c) < D(p[10]) && ex.MinPoint.Y >= D(p[11])) continue;
                    var e = (Entity)tr.GetObject(kv.Key, OpenMode.ForWrite);
                    if (e is Line)
                    {
                        var ln = (Line)e;
                        Func<Point3d, Point3d> f = q => new Point3d(Math.Abs(q.X - c) > thr ? q.X - dx * Math.Sign(q.X - c) : q.X, q.Y + dy, q.Z);
                        var s0 = f(ln.StartPoint); var s1 = f(ln.EndPoint); ln.StartPoint = s0; ln.EndPoint = s1;
                    }
                    else
                    {
                        double cx = (ex.MinPoint.X + ex.MaxPoint.X) / 2;
                        double mx = Math.Abs(cx - c) > thr ? -dx * Math.Sign(cx - c) : 0;
                        if (e is DBText && rep.ContainsKey(((DBText)e).TextString))
                        {
                            var t = (DBText)e; double w0 = ex.MaxPoint.X - ex.MinPoint.X;
                            t.TextString = rep[t.TextString];
                            try { var e2 = t.GeometricExtents; double w1 = e2.MaxPoint.X - e2.MinPoint.X; if (cx < c) mx += w0 - w1; } catch { }
                        }
                        e.TransformBy(Matrix3d.Displacement(new Vector3d(mx, dy, 0)));
                    }
                    n++;
                }
                tr.Commit();
            }
            L("CONSOLE c=" + c + " -> " + n);
        }

        // MOVEY|xa|xb|yold|ynew|tol  move every line endpoint lying on y=yold (x in [xa,xb]) to y=ynew
        void MoveY(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), xb = D(p[2]), yo = D(p[3]), yn = D(p[4]), tol = D(p[5]);
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    if (ex.MinPoint.X < xa || ex.MaxPoint.X > xb) continue;
                    if (ex.MaxPoint.Y < yo - tol || ex.MinPoint.Y > yo + tol) continue;
                    var ln = tr.GetObject(kv.Key, OpenMode.ForRead) as Line;
                    if (ln == null) continue;
                    var a = ln.StartPoint; var b = ln.EndPoint;
                    bool ma = Math.Abs(a.Y - yo) < tol, mb = Math.Abs(b.Y - yo) < tol;
                    if (!ma && !mb) continue;
                    ln.UpgradeOpen();
                    if (ma) ln.StartPoint = new Point3d(a.X, yn, a.Z);
                    if (mb) ln.EndPoint = new Point3d(b.X, yn, b.Z);
                    n++;
                }
                tr.Commit();
            }
            L("MOVEY " + yo + "->" + yn + ": " + n);
        }

        // MOVET|xa|ya|xb|yb|dx|dy|text|old=new   move texts (== text, or any if *) and small wipeouts inside the window
        void MoveT(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), dx = D(p[5]), dy = D(p[6]); string txt = p[7];
            string ro = null, rn = null; if (p.Length > 8 && p[8].Contains("=")) { ro = p[8].Split('=')[0]; rn = p[8].Split('=')[1]; }
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    if (!In(kv.Value, xa, ya, xb, yb)) continue;
                    var e = tr.GetObject(kv.Key, OpenMode.ForRead) as Entity;
                    bool ok = (e is DBText && (txt == "*" || ((DBText)e).TextString == txt)) || e is Wipeout || (txt == "*" && e is Line);
                    if (!ok) continue;
                    e.UpgradeOpen();
                    if (ro != null && e is DBText && ((DBText)e).TextString == ro) ((DBText)e).TextString = rn;
                    e.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0))); n++;
                }
                tr.Commit();
            }
            L("MOVET " + txt + " -> " + n);
        }


        // IMPORT|src.dwg|xa|ya|xb|yb|railL|railR|railBase|dx|dy|exLayers(;)|exBlocks(;)
        // copies the crane drawn between two rails from another drawing (model space), moved by dx,dy.
        // Skips dims, texts, listed layers/blocks and anything below the rail base near the rails (consoles, symbols).
        void Import(Database db, string[] p)
        {
            string src = p[1];
            double xa = D(p[2]), ya = D(p[3]), xb = D(p[4]), yb = D(p[5]), rl = D(p[6]), rr = D(p[7]), rb = D(p[8]), dx = D(p[9]), dy = D(p[10]);
            var exL = new HashSet<string>(p[11].Split(';')); var exB = new HashSet<string>(p[12].Split(';'));
            var tnames = new HashSet<string>();
            using (var t0 = db.TransactionManager.StartTransaction())
            {
                foreach (ObjectId bid in (BlockTable)t0.GetObject(db.BlockTableId, OpenMode.ForRead)) tnames.Add(((BlockTableRecord)t0.GetObject(bid, OpenMode.ForRead)).Name);
                t0.Commit();
            }
            using (var side = new Database(false, true))
            {
                side.ReadDwgFile(src, FileShare.Read, true, ""); side.CloseInput(true);
                var ids = new ObjectIdCollection();
                using (var tr = side.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(side.BlockTableId, OpenMode.ForRead);
                    var ms = (BlockTableRecord)tr.GetObject(bt[BlockTableRecord.ModelSpace], OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                        if (e is Dimension || e is DBText || e is MText || e is Leader || e is MLeader) continue;
                        if (exL.Contains(e.Layer)) continue;
                        if (e is BlockReference && exB.Contains(((BlockReference)e).Name)) continue;
                        Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                        if (!In(ex, xa, ya, xb, yb)) continue;
                        if (ex.MaxPoint.Y < rb - 20 && (ex.MinPoint.X < rl + 600 || ex.MaxPoint.X > rr - 600)) continue;
                        ids.Add(id);
                    }
                    // avoid block-name clashes with the target drawing
                    foreach (ObjectId bid in bt)
                    {
                        var btr = (BlockTableRecord)tr.GetObject(bid, OpenMode.ForRead);
                        if (btr.IsLayout || btr.IsAnonymous) continue;
                        if (tnames.Contains(btr.Name) && !btr.Name.EndsWith("_ТХ")) { btr.UpgradeOpen(); btr.Name = btr.Name + "_ТХ"; }
                    }
                    tr.Commit();
                }
                ObjectId msId;
                using (var t = db.TransactionManager.StartTransaction())
                { msId = ((BlockTable)t.GetObject(db.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace]; t.Commit(); }
                var map = new IdMapping();
                side.WblockCloneObjects(ids, msId, map, DuplicateRecordCloning.Ignore, false);
                using (var t = db.TransactionManager.StartTransaction())
                {
                    foreach (ObjectId id in ids) { var e = (Entity)t.GetObject(map[id].Value, OpenMode.ForWrite); e.TransformBy(Matrix3d.Displacement(new Vector3d(dx, dy, 0))); }
                    t.Commit();
                }
                L("IMPORT " + ids.Count + " from " + Path.GetFileName(src) + " x " + xa + ".." + xb);
            }
        }


        DBText FindText(Transaction tr, List<KeyValuePair<ObjectId, Extents3d>> ents, double x, double y, double tol)
        {
            foreach (var kv in ents)
            {
                var ex = kv.Value;
                if (ex.MaxPoint.X < x - tol * 40 || ex.MinPoint.X > x + tol * 40 || ex.MaxPoint.Y < y - tol * 4 || ex.MinPoint.Y > y + tol * 4) continue;
                var t = tr.GetObject(kv.Key, OpenMode.ForRead, true) as DBText;
                if (t == null || t.IsErased) continue;
                if (Math.Abs(t.Position.X - x) < tol && Math.Abs(t.Position.Y - y) < tol) return t;
            }
            return null;
        }

        // DELTXT|xa|ya|xb|yb  erase texts (and their wipeouts) whose insertion point is inside the window
        void DelTxt(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]); int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var o = tr.GetObject(kv.Key, OpenMode.ForRead, true) as Entity;
                    if (o == null || o.IsErased) continue;
                    bool hit = false;
                    if (o is DBText) { var q = ((DBText)o).Position; hit = q.X >= xa && q.X <= xb && q.Y >= ya && q.Y <= yb; }
                    else if (o is Wipeout) hit = In(kv.Value, xa, ya, xb, yb);
                    if (!hit) continue;
                    o.UpgradeOpen(); o.Erase(); n++;
                }
                tr.Commit();
            }
            L("DELTXT -> " + n);
        }

        // ADDTXT|tplx|tply|tol|x|y|text   new text cloned from the template text (style, height, layer), left-baseline at x,y
        void AddTxt(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var tpl = FindText(tr, ents, D(p[1]), D(p[2]), D(p[3]));
                if (tpl == null) { L("ADDTXT template not found " + p[6]); return; }
                var ms = (BlockTableRecord)tr.GetObject(((BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                var t = (DBText)tpl.Clone();
                t.HorizontalMode = TextHorizontalMode.TextLeft; t.VerticalMode = TextVerticalMode.TextBase;
                t.Position = new Point3d(D(p[4]), D(p[5]), 0); t.TextString = p[6];
                ms.AppendEntity(t); tr.AddNewlyCreatedDBObject(t, true);
                tr.Commit();
            }
        }

        // SETTXT|x|y|tol|prefix|new   replace the string of the text at x,y whose string starts with prefix
        void SetTxt(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var t = FindText(tr, ents, D(p[1]), D(p[2]), D(p[3]));
                if (t == null || !t.TextString.StartsWith(p[4])) { L("SETTXT not found: " + p[4]); return; }
                t.UpgradeOpen(); t.TextString = p[5];
                tr.Commit();
            }
            L("SETTXT " + p[5]);
        }

        // ADDLINE|tplx|tply|tol|x1|y1|x2|y2   line with the properties of the template line found by its start corner
        void AddLine(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            using (var tr = db.TransactionManager.StartTransaction())
            {
                Line tpl = null;
                foreach (var kv in ents)
                {
                    if (Math.Abs(kv.Value.MinPoint.X - D(p[1])) > D(p[3]) || Math.Abs(kv.Value.MinPoint.Y - D(p[2])) > D(p[3])) continue;
                    tpl = tr.GetObject(kv.Key, OpenMode.ForRead, true) as Line; if (tpl != null) break;
                }
                if (tpl == null) { L("ADDLINE template not found"); return; }
                var ms = (BlockTableRecord)tr.GetObject(((BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                var l = (Line)tpl.Clone(); l.StartPoint = new Point3d(D(p[4]), D(p[5]), 0); l.EndPoint = new Point3d(D(p[6]), D(p[7]), 0);
                ms.AppendEntity(l); tr.AddNewlyCreatedDBObject(l, true);
                tr.Commit();
            }
        }

        // CLOUD|x0|y0|x1|y1|arc|tplx|tply|tol   revision cloud (polyline of outward arcs) around a rectangle, props from a template line
        void Cloud(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double x0 = D(p[1]), y0 = D(p[2]), x1 = D(p[3]), y1 = D(p[4]), a = D(p[5]);
            using (var tr = db.TransactionManager.StartTransaction())
            {
                Line tpl = null;
                foreach (var kv in ents)
                {
                    if (Math.Abs(kv.Value.MinPoint.X - D(p[6])) > D(p[8]) || Math.Abs(kv.Value.MinPoint.Y - D(p[7])) > D(p[8])) continue;
                    tpl = tr.GetObject(kv.Key, OpenMode.ForRead, true) as Line; if (tpl != null) break;
                }
                var pts = new List<Point2d>();
                Action<double, double, double, double> side = (ax, ay, bx, by) =>
                {
                    double len = Math.Sqrt((bx - ax) * (bx - ax) + (by - ay) * (by - ay)); int n = Math.Max(1, (int)Math.Round(len / a));
                    for (int i = 0; i < n; i++) pts.Add(new Point2d(ax + (bx - ax) * i / n, ay + (by - ay) * i / n));
                };
                // counter-clockwise; negative bulge bulges outward
                side(x0, y0, x1, y0); side(x1, y0, x1, y1); side(x1, y1, x0, y1); side(x0, y1, x0, y0);
                var pl = new Polyline();
                double bul = p.Length > 9 ? D(p[9]) : 0.4; for (int i = 0; i < pts.Count; i++) pl.AddVertexAt(i, pts[i], bul, 0, 0);
                pl.Closed = true;
                if (tpl != null) { pl.LayerId = tpl.LayerId; pl.Color = tpl.Color; pl.LineWeight = tpl.LineWeight; }
                var ms = (BlockTableRecord)tr.GetObject(((BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                ms.AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true);
                tr.Commit();
            }
            L("CLOUD " + p[1] + "," + p[2]);
        }


        // IBEAM|slantDeg|flangeK|spaces   texts "I<digit>..." -> the letter I is replaced by spaces and a drawn I-beam sign
        // (stem + two flanges, text height, slanted like GOST type A italic), same layer/colour as the text
        void IBeam(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double t = Math.Tan(D(p[1]) * Math.PI / 180), k = D(p[2]); string sp = p[3].Replace("_", " ");
            int n = 0, skip = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                var ms = (BlockTableRecord)tr.GetObject(((BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace], OpenMode.ForWrite);
                foreach (var kv in ents)
                {
                    var tx = tr.GetObject(kv.Key, OpenMode.ForRead, true) as DBText;
                    if (tx == null || tx.IsErased) continue;
                    var s = tx.TextString;
                    if (s.Length < 2 || s[0] != 'I' || !char.IsDigit(s[1])) continue;
                    if (tx.HorizontalMode != TextHorizontalMode.TextLeft || (tx.VerticalMode != TextVerticalMode.TextBase && tx.VerticalMode != TextVerticalMode.TextBottom)) { skip++; L("IBEAM skip (align) " + s); continue; }
                    double H = tx.Height, wf = k * H, x0 = 0.05 * H;
                    var o = tx.Position; double r = tx.Rotation;
                    var xf = Matrix3d.Displacement(o.GetAsVector()) * Matrix3d.Rotation(r, Vector3d.ZAxis, Point3d.Origin);
                    Action<double, double, double, double> add = (ax, ay, bx, by) =>
                    {
                        var l = new Line(new Point3d(ax, ay, 0), new Point3d(bx, by, 0));
                        l.LayerId = tx.LayerId; l.Color = tx.Color; l.LineWeight = tx.LineWeight;
                        l.TransformBy(xf);
                        ms.AppendEntity(l); tr.AddNewlyCreatedDBObject(l, true);
                    };
                    double cx = x0 + wf / 2;
                    add(cx, 0, cx + t * H, H);                       // stem
                    add(x0, 0, x0 + wf, 0);                          // bottom flange
                    add(x0 + t * H, H, x0 + wf + t * H, H);          // top flange
                    tx.UpgradeOpen(); tx.TextString = sp + s.Substring(1);
                    n++;
                }
                tr.Commit();
            }
            L("IBEAM " + n + " marks, skipped " + skip);
        }


        // LOWER|xa|ya|xb|yb|c|dy|exRmin|exRmax|exYmin|exYmax  move everything inside the window by dy,
        // except small items lying entirely at exRmin..exRmax from x=c and within exYmin..exYmax (struts at the column)
        void Lower(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[1]), ya = D(p[2]), xb = D(p[3]), yb = D(p[4]), c = D(p[5]), dy = D(p[6]);
            double r0 = D(p[7]), r1 = D(p[8]), e0 = D(p[9]), e1 = D(p[10]);
            int n = 0, ex = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var o = tr.GetObject(kv.Key, OpenMode.ForRead, true) as Entity;
                    if (o == null || o.IsErased) continue;
                    Extents3d e; try { e = o.GeometricExtents; } catch { continue; }
                    if (!In(e, xa, ya, xb, yb)) continue;
                    double a0 = Math.Abs(e.MinPoint.X - c), a1 = Math.Abs(e.MaxPoint.X - c);
                    bool sameSide = (e.MinPoint.X - c) * (e.MaxPoint.X - c) > 0;
                    if (sameSide && Math.Min(a0, a1) >= r0 && Math.Max(a0, a1) <= r1 && e.MinPoint.Y >= e0 && e.MaxPoint.Y <= e1) { ex++; continue; }
                    o.UpgradeOpen(); o.TransformBy(Matrix3d.Displacement(new Vector3d(0, dy, 0))); n++;
                }
                tr.Commit();
            }
            L("LOWER c=" + c + " -> " + n + " (kept " + ex + ")");
        }

        // CRANEMOVE|src|xa|ya|xb|yb|railL|railR|railBase|dx|dy|exLayers|exBlocks|ddy
        // finds the entities once copied by IMPORT (same type and extents) and moves them by ddy
        void CraneMove(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double xa = D(p[2]), ya = D(p[3]), xb = D(p[4]), yb = D(p[5]), rl = D(p[6]), rr = D(p[7]), rb = D(p[8]), dx = D(p[9]), dy = D(p[10]), ddy = D(p[13]);
            var exL = new HashSet<string>(p[11].Split(';')); var exB = new HashSet<string>(p[12].Split(';'));
            var want = new List<KeyValuePair<string, Extents3d>>();
            using (var side = new Database(false, true))
            {
                side.ReadDwgFile(p[1], FileShare.Read, true, ""); side.CloseInput(true);
                using (var tr = side.TransactionManager.StartTransaction())
                {
                    var ms = (BlockTableRecord)tr.GetObject(((BlockTable)tr.GetObject(side.BlockTableId, OpenMode.ForRead))[BlockTableRecord.ModelSpace], OpenMode.ForRead);
                    foreach (ObjectId id in ms)
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                        if (e is Dimension || e is DBText || e is MText || e is Leader || e is MLeader) continue;
                        if (exL.Contains(e.Layer)) continue;
                        if (e is BlockReference && exB.Contains(((BlockReference)e).Name)) continue;
                        Extents3d ex; try { ex = e.GeometricExtents; } catch { continue; }
                        if (!In(ex, xa, ya, xb, yb)) continue;
                        if (ex.MaxPoint.Y < rb - 20 && (ex.MinPoint.X < rl + 600 || ex.MaxPoint.X > rr - 600)) continue;
                        Extents3d sh; try { sh = new Extents3d(ex.MinPoint + new Vector3d(dx, dy, 0), ex.MaxPoint + new Vector3d(dx, dy, 0)); } catch (System.Exception q) { L("ext " + q.Message); continue; }
                        want.Add(new KeyValuePair<string, Extents3d>(e.GetRXClass().Name, sh));
                    }
                    tr.Commit();
                }
            }
            int n = 0;
            var used = new HashSet<ObjectId>();
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var w in want)
                {
                    foreach (var kv in ents)
                    {
                        var c = kv.Value;
                        if (Math.Abs(c.MinPoint.X - w.Value.MinPoint.X) > 50 || Math.Abs(c.MinPoint.Y - w.Value.MinPoint.Y) > 50) continue;
                        if (used.Contains(kv.Key)) continue;
                        var o = tr.GetObject(kv.Key, OpenMode.ForRead, true) as Entity;
                        if (o == null || o.IsErased || o.GetRXClass().Name != w.Key) continue;
                        Extents3d e; try { e = o.GeometricExtents; } catch { continue; }
                        if (Math.Abs(e.MinPoint.X - w.Value.MinPoint.X) > 0.5 || Math.Abs(e.MinPoint.Y - w.Value.MinPoint.Y) > 0.5 ||
                            Math.Abs(e.MaxPoint.X - w.Value.MaxPoint.X) > 0.5 || Math.Abs(e.MaxPoint.Y - w.Value.MaxPoint.Y) > 0.5) continue;
                        try { o.UpgradeOpen(); o.TransformBy(Matrix3d.Displacement(new Vector3d(0, ddy, 0))); used.Add(kv.Key); n++; } catch (System.Exception q) { L("mv " + o.GetType().Name + " " + q.Message); }
                        break;
                    }
                }
                tr.Commit();
            }
            L("CRANEMOVE " + n + " of " + want.Count);
        }

        void Text(Database db, List<KeyValuePair<ObjectId, Extents3d>> ents, string[] p)
        {
            double x = D(p[1]), y = D(p[2]), tol = D(p[3]); string o = p[4], nw = p[5];
            int n = 0;
            using (var tr = db.TransactionManager.StartTransaction())
            {
                foreach (var kv in ents)
                {
                    var ex = kv.Value;
                    if (ex.MaxPoint.X < x - tol || ex.MinPoint.X > x + tol || ex.MaxPoint.Y < y - tol || ex.MinPoint.Y > y + tol) continue;
                    var t = tr.GetObject(kv.Key, OpenMode.ForRead) as DBText;
                    if (t == null || t.TextString != o) continue;
                    var pos = t.Position;
                    if (Math.Abs(pos.X - x) > tol || Math.Abs(pos.Y - y) > tol) continue;
                    t.UpgradeOpen();
                    if (t.HorizontalMode == TextHorizontalMode.TextLeft && t.VerticalMode == TextVerticalMode.TextBase)
                    {
                        // keep the right edge where it was (numbers in the table are right-aligned by eye)
                        double w0 = ex.MaxPoint.X - ex.MinPoint.X;
                        t.TextString = nw;
                        double w1 = 0; try { var e2 = t.GeometricExtents; w1 = e2.MaxPoint.X - e2.MinPoint.X; } catch { }
                        if (p.Length > 6 && p[6] == "R" && w1 > 0) t.Position = new Point3d(pos.X - (w1 - w0), pos.Y, pos.Z);
                        if (p.Length > 6 && p[6] == "C" && w1 > 0) t.Position = new Point3d(pos.X - (w1 - w0) / 2, pos.Y, pos.Z);
                    }
                    else t.TextString = nw;
                    n++;
                }
                tr.Commit();
            }
            L(string.Format("TEXT {0}->{1} at {2:F0},{3:F0}: {4}", o, nw, x, y, n));
        }
    }
}
