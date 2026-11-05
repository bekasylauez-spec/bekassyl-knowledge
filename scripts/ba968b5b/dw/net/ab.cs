using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Multicad;
using Multicad.DatabaseServices;
using Multicad.Symbols;
using Multicad.Dimensions;
using MG = Multicad.Geometry;

namespace AB
{
    // Drawing ops (with СПДС/Multicad) from %TEMP%\ab_ops.json; log %TEMP%\ab_log.txt; tag->handle map %TEMP%\ab_map.json
    public class Cmds
    {
        static StringBuilder log = new StringBuilder();
        static string tmp = Environment.GetEnvironmentVariable("TEMP");
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static string S(Dictionary<string, object> m, string k, string def) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : def; }
        static bool Has(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null; }
        static IList L(object o) { return (IList)o; }
        static Point2d P2(object o) { var a = L(o); return new Point2d(D(a[0]), D(a[1])); }
        static Point3d P(object o) { var a = L(o); return new Point3d(D(a[0]), D(a[1]), 0); }
        static MG.Point3d MP(object o) { var a = L(o); return new MG.Point3d(D(a[0]), D(a[1]), 0); }
        static Dictionary<string, string> map = new Dictionary<string, string>();
        static string mapFile = Path.Combine(tmp, "ab_map.json");

        static ObjectId H(Database db, string h)
        {
            if (map.ContainsKey(h)) h = map[h];
            ObjectId id;
            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) return id;
            throw new System.Exception("no handle " + h);
        }
        static void Tag(Dictionary<string, object> m, Entity e)
        {
            string t = S(m, "tag", null);
            if (t != null) map[t] = e.Handle.ToString();
        }

        static void Props(Entity e, Dictionary<string, object> m, Database db, Transaction tr)
        {
            string lay = S(m, "layer", null);
            if (lay != null)
            {
                var lt = (LayerTable)tr.GetObject(db.LayerTableId, OpenMode.ForRead);
                if (!lt.Has(lay)) { lt.UpgradeOpen(); var r = new LayerTableRecord(); r.Name = lay; lt.Add(r); tr.AddNewlyCreatedDBObject(r, true); }
                e.Layer = lay;
            }
            if (Has(m, "color")) e.ColorIndex = Convert.ToInt32(m["color"]);
            if (Has(m, "lw")) e.LineWeight = (LineWeight)Convert.ToInt32(m["lw"]);
            if (Has(m, "ltype"))
            {
                string ln = S(m, "ltype", "ByLayer");
                var ltt = (LinetypeTable)tr.GetObject(db.LinetypeTableId, OpenMode.ForRead);
                if (ltt.Has(ln) || ln == "ByLayer") e.Linetype = ln; else log.AppendLine("no linetype " + ln);
            }
            if (Has(m, "ltscale")) e.LinetypeScale = D(m["ltscale"]);
        }

        // every McObject wrapper is disposed after its op: undisposed wrappers kept DB objects open for read and
        // after thousands of ops AutoCAD failed with eAtMaxReaders (save/DXFOUT impossible) — 04.11.2026
        static List<IDisposable> mcOpen = new List<IDisposable>();
        static McObject MGet(ObjectId id) { var o = McObjectManager.GetObject(McObjectId.FromOldIdPtr(id.OldIdPtr)); var d = o as IDisposable; if (d != null) mcOpen.Add(d); return o; }
        static void McRelease() { foreach (var d in mcOpen) { try { d.Dispose(); } catch { } } mcOpen.Clear(); }

        public static void Apply()
        {
            log.Clear();
            try { var js0 = new JavaScriptSerializer(); var mm = (Dictionary<string, object>)js0.DeserializeObject(File.ReadAllText(mapFile, Encoding.UTF8)); foreach (var kv in mm) map[kv.Key] = kv.Value.ToString(); } catch { }
            var doc = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument;
            var db = doc.Database;
            if (!db.Filename.EndsWith("КЖ Чертеж АБК ВАРИАНТ 2.dwg", StringComparison.OrdinalIgnoreCase) && !db.Filename.Contains("_abwork"))
            {
                // guard: never run ops on any other drawing; close stray documents this instance opened by itself
                var dmx = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager;
                Autodesk.AutoCAD.ApplicationServices.Document tgt = null;
                foreach (Autodesk.AutoCAD.ApplicationServices.Document dd in dmx) if (dd.Database.Filename.EndsWith("КЖ Чертеж АБК ВАРИАНТ 2.dwg", StringComparison.OrdinalIgnoreCase)) tgt = dd;
                log.AppendLine("GUARD: active db is " + db.Filename + "; nothing done");
                File.WriteAllText(Path.Combine(tmp, "ab_log.txt"), log.ToString(), Encoding.UTF8);
                return;
            }
            var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
            var ops = (IList)js.DeserializeObject(File.ReadAllText(Path.Combine(tmp, "ab_ops.json"), Encoding.UTF8));
            int nerr = 0;
            if (ops.Count > 0 && S((Dictionary<string, object>)ops[0], "t", "") == "reopen")
            {
                // discard the document (no save) and open it again from disk — resets leaked read-opens
                var dm = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager;
                string path = doc.Name;
                try { Autodesk.AutoCAD.ApplicationServices.DocumentExtension.CloseAndDiscard(doc); Autodesk.AutoCAD.ApplicationServices.DocumentCollectionExtension.Open(dm, path, false); log.AppendLine("reopened " + path); }
                catch (System.Exception ex) { nerr++; log.AppendLine("ERR reopen: " + ex.Message); }
                log.AppendLine("done, errors " + nerr);
                File.WriteAllText(Path.Combine(tmp, "ab_log.txt"), log.ToString(), Encoding.UTF8);
                return;
            }
            foreach (var o in ops)
            {
                var m = (Dictionary<string, object>)o;
                try
                {
                    using (var tr = db.TransactionManager.StartTransaction())
                    {
                        Op(db, tr, m);
                        tr.Commit();
                    }
                }
                catch (System.Exception ex) { nerr++; log.AppendLine("ERR " + S(m, "t", "?") + " " + S(m, "tag", "") + ": " + ex.Message); }
                McRelease();
            }
            log.AppendLine("done, errors " + nerr);
            File.WriteAllText(mapFile, new JavaScriptSerializer().Serialize(map), Encoding.UTF8);
            File.WriteAllText(Path.Combine(tmp, "ab_log.txt"), log.ToString(), Encoding.UTF8);
        }

        static string id2cls(Entity e) { return e.ObjectId.ObjectClass.DxfName; }
        static BlockTableRecord MS(Database db, Transaction tr)
        {
            return (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
        }

        static void Op(Database db, Transaction tr, Dictionary<string, object> m)
        {
            string t = S(m, "t", "");
            if (t == "pl")
            {
                var pl = new Polyline();
                var pts = L(m["p"]);
                IList bl = Has(m, "b") ? L(m["b"]) : null;
                for (int i = 0; i < pts.Count; i++) pl.AddVertexAt(i, P2(pts[i]), bl != null ? D(bl[i]) : 0, 0, 0);
                pl.Closed = Has(m, "closed") && (bool)m["closed"];
                pl.SetDatabaseDefaults(db);
                if (Has(m, "w")) pl.ConstantWidth = D(m["w"]);
                Props(pl, m, db, tr);
                MS(db, tr).AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true); Tag(m, pl);
            }
            else if (t == "circle")
            {
                var c = new Circle(P(m["c"]), Vector3d.ZAxis, D(m["r"]));
                c.SetDatabaseDefaults(db); Props(c, m, db, tr);
                MS(db, tr).AppendEntity(c); tr.AddNewlyCreatedDBObject(c, true); Tag(m, c);
            }
            else if (t == "hatch")
            {
                var h = new Hatch();
                h.SetDatabaseDefaults(db);
                Props(h, m, db, tr);
                MS(db, tr).AppendEntity(h); tr.AddNewlyCreatedDBObject(h, true);
                string pat = S(m, "pat", "ANSI31");
                h.SetHatchPattern(pat == "SOLID" ? HatchPatternType.PreDefined : HatchPatternType.PreDefined, pat);
                if (pat != "SOLID") { h.PatternScale = Has(m, "sc") ? D(m["sc"]) : 1; if (Has(m, "ang")) h.PatternAngle = D(m["ang"]); h.SetHatchPattern(HatchPatternType.PreDefined, pat); }
                foreach (var lp in L(m["loops"]))
                {
                    var pc = new Point2dCollection(); var bc = new DoubleCollection();
                    var pts = L(lp);
                    for (int i = 0; i < pts.Count; i++) { pc.Add(P2(pts[i])); bc.Add(0); }
                    pc.Add(P2(pts[0])); bc.Add(0);
                    h.AppendLoop(HatchLoopTypes.Polyline, pc, bc);
                }
                h.EvaluateHatch(true); Tag(m, h);
            }
            else if (t == "mtext")
            {
                var mt = new MText();
                mt.SetDatabaseDefaults(db);
                mt.Location = P(m["at"]);
                mt.TextHeight = D(m["h"]);
                if (Has(m, "w")) mt.Width = D(m["w"]);
                mt.Attachment = (AttachmentPoint)Convert.ToInt32(S(m, "att", "1"));
                var st = (TextStyleTable)tr.GetObject(db.TextStyleTableId, OpenMode.ForRead);
                string sn = S(m, "style", "");
                if (sn != "" && st.Has(sn)) mt.TextStyleId = st[sn];
                if (Has(m, "rot")) mt.Rotation = D(m["rot"]);
                mt.Contents = S(m, "s", "");
                Props(mt, m, db, tr);
                MS(db, tr).AppendEntity(mt); tr.AddNewlyCreatedDBObject(mt, true); Tag(m, mt);
            }
            else if (t == "clone")
            {
                // deep clone within drawing, then scale about base and move base->to; optional text / pts
                var src = H(db, S(m, "h", ""));
                var ids = new ObjectIdCollection(); ids.Add(src);
                var im = new IdMapping();
                db.DeepCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, false);
                foreach (IdPair p in im)
                {
                    if (!p.IsCloned || !p.IsPrimary || p.Key != src) continue;
                    var e = (Entity)tr.GetObject(p.Value, OpenMode.ForWrite);
                    var bs = Has(m, "base") ? P(m["base"]) : Point3d.Origin;
                    var to = Has(m, "to") ? P(m["to"]) : bs;
                    if (Has(m, "s")) e.TransformBy(Matrix3d.Scaling(D(m["s"]), bs));
                    e.TransformBy(Matrix3d.Displacement(to - bs));
                    if (Has(m, "text")) { if (e is MText) ((MText)e).Contents = S(m, "text", ""); else if (e is DBText) ((DBText)e).TextString = S(m, "text", ""); }
                    Props(e, m, db, tr);
                    Tag(m, e);
                    log.AppendLine("clone " + S(m, "h", "") + ">" + e.Handle + " " + S(m, "tag", ""));
                }
            }
            else if (t == "lineset")
            {
                // clone a template LINE (analog bar) and set its end points
                var src = (Line)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
                var l = (Line)src.Clone();
                l.StartPoint = P(m["s"]); l.EndPoint = P(m["e"]);
                ms.AppendEntity(l); tr.AddNewlyCreatedDBObject(l, true);
                Props(l, m, db, tr);
                if (Has(m, "ltscale")) l.LinetypeScale = D(m["ltscale"]);
                Tag(m, l);
            }
            else if (t == "dim")
            {
                // clone template RotatedDimension, set points
                var src = (RotatedDimension)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var d = (RotatedDimension)src.Clone();
                MS(db, tr).AppendEntity(d); tr.AddNewlyCreatedDBObject(d, true);
                d.XLine1Point = P(m["p1"]); d.XLine2Point = P(m["p2"]); d.DimLinePoint = P(m["dl"]);
                d.Rotation = Has(m, "rot") ? D(m["rot"]) : 0;
                if (Has(m, "dscale")) d.Dimscale = D(m["dscale"]);
                if (Has(m, "lfac")) d.Dimlfac = D(m["lfac"]);
                if (Has(m, "txt")) d.DimensionText = S(m, "txt", "");
                d.UsingDefaultTextPosition = true;
                if (Has(m, "tx")) { d.UsingDefaultTextPosition = false; d.TextPosition = P(m["tx"]); }
                Props(d, m, db, tr);
                Tag(m, d);
            }
            else if (t == "adim")
            {
                var src = (Dimension)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                var d = new AlignedDimension(P(m["p1"]), P(m["p2"]), P(m["dl"]), "", src.DimensionStyle);
                d.SetDatabaseDefaults(db);
                d.Layer = src.Layer;
                d.Dimscale = Has(m, "dscale") ? D(m["dscale"]) : src.Dimscale;
                if (Has(m, "lfac")) d.Dimlfac = D(m["lfac"]);
                MS(db, tr).AppendEntity(d); tr.AddNewlyCreatedDBObject(d, true);
                Tag(m, d);
            }
            else if (t == "note")
            {
                var np = new McNotePosition();
                np.FirstLine = S(m, "l1", ""); np.SecondLine = S(m, "l2", "");
                np.Origin = MP(m["origin"]);
                if (Has(m, "angle")) np.Angle = D(m["angle"]);
                np.DbEntity.Scale = D(m["scale"]);
                np.DbEntity.Layer = S(m, "layer", "Размеры");
                string ar = S(m, "arrow", "oblique");
                np.Arrow = ar == "arrow" ? MG.Arrows.Arrow : ar == "oblique" ? MG.Arrows.Oblique : ar == "open" ? MG.Arrows.Open : MG.Arrows.None;
                if (Has(m, "ts")) { np.TextSize = D(m["ts"]); np.SmallTextSize = D(m["ts"]); }
                if (Has(m, "style")) np.TextStyle = S(m, "style", "ГОСТ 2.304");
                try
                {
                    var pa = np.GetType().GetProperty("Align");
                    if (Has(m, "listalign")) log.AppendLine("Align enum: " + string.Join(",", Enum.GetNames(pa.PropertyType)) + " cur " + pa.GetValue(np, null));
                    pa.SetValue(np, Enum.Parse(pa.PropertyType, S(m, "align", "Center")), null);
                }
                catch (System.Exception ex) { log.AppendLine("align fail " + ex.Message); }
                McObjectManager.Add2Document(np.DbEntity);
                if (Has(m, "target")) np.Leader.AddSegment(MP(m["target"]), np.Origin);
                if (Has(m, "targets")) foreach (object q in L(m["targets"])) np.Leader.AddSegment(MP(q), np.Origin);
                np.DbEntity.Update();
                log.AppendLine("note " + S(m, "tag", "") + " " + np.FirstLine);
            }
            else if (t == "sdim")
            {
                var dm = new McLinearDimension();
                dm.SetPosition(0, MP(m["p1"])); dm.SetPosition(1, MP(m["p2"]));
                if (Has(m, "dir")) { var dv = L(m["dir"]); dm.Direction = new MG.Vector3d(D(dv[0]), D(dv[1]), 0); }
                dm.LinePosition = MP(m["dl"]);
                dm.DbEntity.Scale = D(m["scale"]);
                dm.DbEntity.Layer = S(m, "layer", "Размеры");
                McObjectManager.Add2Document(dm.DbEntity);
                dm.DbEntity.Update();
            }
            else if (t == "mcprobe")
            {
                var w = L(m["win"]);
                var ms = MS(db, tr);
                int n = 0;
                foreach (ObjectId id in ms)
                {
                    if (!id.ObjectClass.Name.Contains("Imp") && !id.ObjectClass.DxfName.StartsWith("MCS") && !id.ObjectClass.DxfName.StartsWith("SPDS")) continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MaxPoint.X > D(w[2]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.Y > D(w[3])) continue;
                    var mo = MGet(id);
                    try
                    {
                        string info = mo == null ? "null" : mo.GetType().Name;
                        var np = mo as McNotePosition;
                        if (np != null) info += " [" + np.FirstLine + "|" + np.SecondLine + "] scale " + np.DbEntity.Scale + " org " + np.Origin;
                        log.AppendLine(e.Handle + " " + id.ObjectClass.DxfName + " " + info + " ext " + x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + " " + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC));
                    }
                    finally { var dd = mo as IDisposable; if (dd != null) dd.Dispose(); }
                    if (++n > 400) break;
                }
            }
else if (t == "mcrep")
            {
                // replace substrings in FirstLine/SecondLine of SPDS notes/combs/knots inside win; optional "only": handles
                var w = L(m["win"]); var prs = L(m["pairs"]); int n = 0;
                HashSet<string> only = null; if (Has(m, "only")) { only = new HashSet<string>(); foreach (var q in L(m["only"])) only.Add(q.ToString().ToUpper()); }
                var ms = MS(db, tr); var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                foreach (var id in ids)
                {
                    string dn = id.ObjectClass.DxfName;
                    if (dn != "SPDSNOTEPOSITION" && dn != "SPDSNOTECOMB" && dn != "SPDSNOTEKNOT") continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    if (only != null && !only.Contains(e.Handle.ToString().ToUpper())) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MaxPoint.X > D(w[2]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.Y > D(w[3])) continue;
                    var mo = MGet(id); if (mo == null) continue;
                    bool ch = false;
                    foreach (var pn in new[] { "FirstLine", "SecondLine" })
                    {
                        var pi = mo.GetType().GetProperty(pn); if (pi == null || !pi.CanWrite) continue;
                        var s0 = Convert.ToString(pi.GetValue(mo, null)); if (s0 == null) continue; var s = s0;
                        foreach (var q in prs) { var a = L(q); s = s.Replace(a[0].ToString(), a[1].ToString()); }
                        if (s != s0) { pi.SetValue(mo, s, null); ch = true; }
                    }
                    if (ch) { var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity; dbe.Update(); n++; log.AppendLine("mcrep " + e.Handle); }
                }
                log.AppendLine("mcrep total " + n);
            }
else if (t == "sysvar")
            {
                string nm = S(m, "n", "");
                if (Has(m, "v")) Autodesk.AutoCAD.ApplicationServices.Core.Application.SetSystemVariable(nm, Convert.ToInt16(m["v"]));
                log.AppendLine("sysvar " + nm + " = " + Autodesk.AutoCAD.ApplicationServices.Core.Application.GetSystemVariable(nm));
            }
            else if (t == "reflect")
            {
                var asm = typeof(McNotePosition).Assembly;
                foreach (var tn in L(m["types"]))
                {
                    var ty = asm.GetType(tn.ToString());
                    if (ty == null) { log.AppendLine("no type " + tn); continue; }
                    log.AppendLine("== " + ty.FullName + " : " + ty.BaseType);
                    foreach (var pi in ty.GetProperties()) log.AppendLine("  P " + pi.PropertyType.Name + " " + pi.Name + (pi.CanWrite ? " rw" : ""));
                    foreach (var mi in ty.GetMethods(System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.DeclaredOnly)) if (!mi.IsSpecialName) log.AppendLine("  M " + mi.Name + "(" + mi.GetParameters().Length + ")");
                }
            }
            else if (t == "knotinfo")
            {
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                foreach (var pi in mo.GetType().GetProperties())
                {
                    try { log.AppendLine("  " + pi.Name + " = " + pi.GetValue(mo, null)); } catch { }
                }
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
            }
            else if (t == "mcscale")
            {
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                log.AppendLine("mcscale " + S(m, "h", "") + " was " + dbe.Scale);
                dbe.Scale = D(m["v"]);
                dbe.Update();
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
            }
            else if (t == "mtinfo")
            {
                foreach (var hh in L(m["h"]))
                {
                    var e = (Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead); double cx;
                    if (e is MText)
                    {
                        var mt = (MText)e; int col = ((int)mt.Attachment - 1) % 3; double aw = mt.ActualWidth;
                        if (mt.Contents.Contains("\\pxqc") && col == 0 && mt.Width > 0) cx = mt.Location.X + mt.Width / 2;
                        else cx = mt.Location.X + (col == 0 ? aw / 2 : (col == 1 ? 0 : -aw / 2));
                        log.AppendLine("MTI\t" + e.Handle + "\t" + cx.ToString("0.0", IC) + "\t" + aw.ToString("0.0", IC) + "\t" + mt.Location.Y.ToString("0.0", IC) + "\t" + mt.ActualHeight.ToString("0.0", IC));
                    }
                    else { var x = e.GeometricExtents; log.AppendLine("MTI\t" + e.Handle + "\t" + ((x.MinPoint.X + x.MaxPoint.X) / 2).ToString("0.0", IC) + "\t" + (x.MaxPoint.X - x.MinPoint.X).ToString("0.0", IC) + "\t" + x.MaxPoint.Y.ToString("0.0", IC) + "\t" + (x.MaxPoint.Y - x.MinPoint.Y).ToString("0.0", IC)); }
                }
            }
            else if (t == "mtcenter")
            {
                // атауды көрінетін мәтін ортасы x = target болатындай көлденең жылжыту (MText: ActualWidth + Attachment + \pxqc)
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite); double tx = D(m["x"]); double cx;
                if (e is MText)
                {
                    var mt = (MText)e; int col = ((int)mt.Attachment - 1) % 3; double aw = mt.ActualWidth;
                    if (mt.Contents.Contains("\\pxqc") && col == 0 && mt.Width > 0) cx = mt.Location.X + mt.Width / 2;
                    else cx = mt.Location.X + (col == 0 ? aw / 2 : (col == 1 ? 0 : -aw / 2));
                }
                else { var x = e.GeometricExtents; cx = (x.MinPoint.X + x.MaxPoint.X) / 2; }
                e.TransformBy(Matrix3d.Displacement(new Vector3d(tx - cx, 0, 0)));
                log.AppendLine("mtcenter " + e.Handle + " dx=" + (tx - cx).ToString("0.0", IC));
            }
            else if (t == "move")
            {
                var dv = L(m["d"]);
                foreach (var h in L(m["h"])) ((Entity)tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite)).TransformBy(Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0)));
            }
            else if (t == "txtrep")
            {
                // replace substrings in MTEXT/TEXT/table cells/dimension overrides inside win: pairs [[old,new],...]
                var w = L(m["win"]); var prs = L(m["pairs"]); int n = 0;
                var ms = MS(db, tr); var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                Func<string, string> rep = s0 => { var s = s0; foreach (var q in prs) { var a = L(q); s = s.Replace(a[0].ToString(), a[1].ToString()); } return s; };
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MaxPoint.X > D(w[2]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.Y > D(w[3])) continue;
                    if (e is MText) { var mt = (MText)e; var s = rep(mt.Contents); if (s != mt.Contents) { e.UpgradeOpen(); mt.Contents = s; n++; } }
                    else if (e is DBText) { var dt = (DBText)e; var s = rep(dt.TextString); if (s != dt.TextString) { e.UpgradeOpen(); dt.TextString = s; n++; } }
                    else if (e is Dimension) { var dm = (Dimension)e; var s = rep(dm.DimensionText ?? ""); if (s != (dm.DimensionText ?? "")) { e.UpgradeOpen(); dm.DimensionText = s; n++; } }
                    else if (e is Table)
                    {
                        var tb = (Table)e; bool up = false;
                        for (int r = 0; r < tb.Rows.Count; r++) for (int c = 0; c < tb.Columns.Count; c++)
                        {
                            string s0; try { s0 = tb.Cells[r, c].TextString; } catch { continue; }
                            if (string.IsNullOrEmpty(s0)) continue;
                            var s = rep(s0); if (s != s0) { if (!up) { e.UpgradeOpen(); up = true; } tb.Cells[r, c].TextString = s; n++; }
                        }
                    }
                }
                log.AppendLine("txtrep " + n);
            }
            else if (t == "settext")
            {
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                if (e is MText) ((MText)e).Contents = S(m, "s", ""); else if (e is DBText) ((DBText)e).TextString = S(m, "s", "");
                if (Has(m, "w") && e is MText) ((MText)e).Width = D(m["w"]);
            }
            else if (t == "eraseregion")
            {
                var w = L(m["win"]);
                var keep = new HashSet<string>(); if (Has(m, "keep")) foreach (var k in L(m["keep"])) { string kk = k.ToString(); if (map.ContainsKey(kk)) kk = map[kk]; keep.Add(kk.ToUpper()); }
                var ms = MS(db, tr); int n = 0; var ids = new List<ObjectId>();
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    if (keep.Contains(e.Handle.ToString())) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    bool inside = x.MinPoint.X >= D(w[0]) && x.MaxPoint.X <= D(w[2]) && x.MinPoint.Y >= D(w[1]) && x.MaxPoint.Y <= D(w[3]);
                    bool hit = x.MaxPoint.X >= D(w[0]) && x.MinPoint.X <= D(w[2]) && x.MaxPoint.Y >= D(w[1]) && x.MinPoint.Y <= D(w[3]);
                    if (S(m, "mode", "inside") == "intersect" ? hit : inside) ids.Add(id);
                }
                foreach (var id in ids) { tr.GetObject(id, OpenMode.ForWrite).Erase(); n++; }
                log.AppendLine("eraseregion " + n);
            }
            else if (t == "import")
            {
                var bs = P(m["base"]); var to = P(m["to"]);
                var xf = Matrix3d.Displacement(to - bs);
                string pre = S(m, "pre", "I:");
                using (var side = new Database(false, true))
                {
                    side.ReadDwgFile(S(m, "file", ""), FileOpenMode.OpenForReadAndAllShare, true, "");
                    side.CloseInput(true);
                    var ids = new ObjectIdCollection(); var olds = new List<string>();
                    if (Has(m, "h")) foreach (var h in L(m["h"])) { ObjectId id; if (side.TryGetObjectId(new Handle(Convert.ToInt64(h.ToString(), 16)), out id)) { ids.Add(id); olds.Add(h.ToString().ToUpper()); } else log.AppendLine("import: no " + h); }
                    if (Has(m, "wins"))
                    {
                        HashSet<string> skip = new HashSet<string>(); if (Has(m, "skip")) foreach (var q in L(m["skip"])) skip.Add(q.ToString().ToUpper());
                        using (var str = side.TransactionManager.StartTransaction())
                        {
                            var sms = (BlockTableRecord)str.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(side), OpenMode.ForRead);
                            foreach (ObjectId id in sms)
                            {
                                var e = str.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                                if (skip.Contains(e.Handle.ToString().ToUpper())) continue;
                                Extents3d x; bool okx = true; try { x = e.GeometricExtents; } catch { okx = false; x = new Extents3d(); }
                                if (id.ObjectClass.DxfName == "OLE2FRAME") continue;
                                if (!okx)
                                {

                                    var pc = new Point3dCollection(); try { e.GetStretchPoints(pc); } catch { }
                                    if (pc.Count == 0) { try { e.GetGripPoints(pc, new IntegerCollection(), new IntegerCollection()); } catch { } }
                                    if (pc.Count == 0) { log.AppendLine("noext " + e.Handle + " " + id.ObjectClass.DxfName); continue; }
                                    x = new Extents3d(pc[0], pc[0]); foreach (Point3d q in pc) x.AddPoint(q);
                                }
                                foreach (var wq in L(m["wins"]))
                                {
                                    var w = L(wq);
                                    if (x.MinPoint.X >= D(w[0]) && x.MaxPoint.X <= D(w[2]) && x.MinPoint.Y >= D(w[1]) && x.MaxPoint.Y <= D(w[3])) { ids.Add(id); olds.Add(e.Handle.ToString().ToUpper()); log.AppendLine("sel " + e.Handle + " " + id.ObjectClass.DxfName + " " + x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + "," + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC)); break; }
                                }
                            }
                            str.Commit();
                        }
                    }
                    if (Has(m, "dry")) { log.AppendLine("dry " + ids.Count); return; }
                    var im = new IdMapping();
                    side.WblockCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, DuplicateRecordCloning.Ignore, false);
                    int n = 0;
                    for (int i = 0; i < ids.Count; i++)
                    {
                        if (!im.Contains(ids[i])) continue;
                        var e = tr.GetObject(im[ids[i]].Value, OpenMode.ForWrite) as Entity; if (e == null) continue;
                        e.TransformBy(xf);
                        map[pre + olds[i]] = e.Handle.ToString(); n++;
                    }
                    log.AppendLine("import " + n + " of " + ids.Count);
                }
            }
            else if (t == "frames")
            {
                var ms = MS(db, tr);
                foreach (ObjectId id in ms)
                {
                    if (id.ObjectClass.DxfName != "SPDSFORMAT") continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    log.AppendLine("FRAME " + e.Handle + " " + x.MinPoint.X.ToString("0.#", IC) + " " + x.MinPoint.Y.ToString("0.#", IC) + " " + x.MaxPoint.X.ToString("0.#", IC) + " " + x.MaxPoint.Y.ToString("0.#", IC));
                }
            }
            else if (t == "sp_get")
            {
                foreach (var hh in L(m["h"]))
                {
                    var e = (Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead);
                    var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                    var sb = new StringBuilder("SP " + hh + " " + e.GetType().Name + " " + id2cls(e) + ":");
                    for (int i = 0; i < pc.Count; i++) sb.Append(" [" + i + "]" + pc[i].X.ToString("0.#", IC) + "," + pc[i].Y.ToString("0.#", IC));
                    log.AppendLine(sb.ToString());
                    if (Has(m, "props"))
                    {
                        var mo = MGet(e.ObjectId);
                        if (mo != null)
                        {
                            foreach (var pi in mo.GetType().GetProperties())
                            {
                                if (pi.GetIndexParameters().Length > 0) continue;
                                string n = pi.Name; if (n == "GeometryCache" || n.Contains("Contour") || n == "BeforeCutGeometry") continue;
                                try { log.AppendLine("   " + n + " = " + pi.GetValue(mo, null) + (pi.CanWrite ? "  (rw)" : "")); } catch { }
                            }
                            var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                        }
                    }
                }
            }
            else if (t == "sp_set")
            {
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                foreach (var q in L(m["pts"]))
                {
                    var a = L(q); int i = Convert.ToInt32(a[0]);
                    var target = new Point3d(D(a[1]), D(a[2]), 0);
                    var cur = new Point3dCollection(); e.GetStretchPoints(cur);
                    var ic = new IntegerCollection(); ic.Add(i);
                    e.MoveStretchPointsAt(ic, target - cur[i]);
                }
            }
            else if (t == "xform")
            {
                // move base->to, rotate by ang (rad) about to, uniform scale s about to
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var bs = P(m["base"]); var to = P(m["to"]);
                e.TransformBy(Matrix3d.Displacement(to - bs));
                if (Has(m, "ang")) e.TransformBy(Matrix3d.Rotation(D(m["ang"]), Vector3d.ZAxis, to));
                if (Has(m, "mirror")) e.TransformBy(Matrix3d.Mirroring(new Line3d(to, to + Vector3d.YAxis)));
                if (Has(m, "s")) e.TransformBy(Matrix3d.Scaling(D(m["s"]), to));
            }
            else if (t == "mcset")
            {
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var mo = MGet(e.ObjectId);
                foreach (var kv in (Dictionary<string, object>)m["set"])
                {
                    object target = mo; string prop = kv.Key;
                    if (prop == "Scale") { var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity; dbe.Scale = D(kv.Value); continue; }
                    var pi = mo.GetType().GetProperty(prop);
                    if (pi == null) { log.AppendLine("no prop " + prop); continue; }
                    object v = kv.Value;
                    if (pi.PropertyType == typeof(double)) v = D(v);
                    else if (pi.PropertyType == typeof(int)) v = Convert.ToInt32(v);
                    else if (pi.PropertyType == typeof(bool)) v = Convert.ToBoolean(v);
                    else if (pi.PropertyType == typeof(MG.Point3d)) v = MP(v);
                    else if (pi.PropertyType.IsEnum) v = Enum.Parse(pi.PropertyType, v.ToString());
                    else v = v.ToString();
                    pi.SetValue(mo, v, null);
                }
                var dbe2 = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity; dbe2.Update();
                var d3 = mo as IDisposable; if (d3 != null) d3.Dispose();
            }
            else if (t == "levelval")
            {
                // byte-replace value text inside a cloned SPDS level mark (same length), re-create, erase old
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                int cnt = 0; var outb = new List<byte>(b);
                foreach (var enc in new Encoding[] { Encoding.GetEncoding(28591), Encoding.Unicode })
                {
                    var a = enc.GetBytes(S(m, "old", "")); var r = enc.GetBytes(S(m, "value", ""));
                    var cur = outb.ToArray(); outb = new List<byte>();
                    for (int i = 0; i < cur.Length; i++)
                    {
                        bool eq = i <= cur.Length - a.Length;
                        if (eq) for (int k = 0; k < a.Length; k++) if (cur[i + k] != a[k]) { eq = false; break; }
                        if (eq) { outb.AddRange(r); i += a.Length - 1; cnt++; } else outb.Add(cur[i]);
                    }
                }
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                if (cnt == 0) { log.AppendLine("levelval: pattern not found"); return; }
                var ne = McDbEntity.DeserializeNewFromBytes(outb.ToArray());
                McObjectManager.Add2Document(ne); ne.Update();
                tr.GetObject(id, OpenMode.ForWrite).Erase();
                var nid = new ObjectId(ne.ID.ToOldIdPtr());
                string tg = S(m, "tag", null);
                if (tg != null) { var ee = tr.GetObject(nid, OpenMode.ForRead) as Entity; if (ee != null) map[tg] = ee.Handle.ToString(); }
                log.AppendLine("levelval " + cnt);
            }
            else if (t == "ltload")
            {
                var ltt = (LinetypeTable)tr.GetObject(db.LinetypeTableId, OpenMode.ForRead);
                foreach (var n in L(m["names"])) if (!ltt.Has(n.ToString())) { db.LoadLineTypeFile(n.ToString(), "acadiso.lin"); log.AppendLine("loaded " + n); }
            }
            else if (t == "stretchwin")
            {
                // AutoCAD STRETCH: entities touching 'sel' window; stretch points inside 'win' move by d
                var w = L(m["win"]); var sw = Has(m, "sel") ? L(m["sel"]) : w;
                var dv = L(m["d"]); var vec = new Vector3d(D(dv[0]), D(dv[1]), 0);
                Func<Point3d, IList, bool> inb = (p, b) => p.X >= D(b[0]) && p.X <= D(b[2]) && p.Y >= D(b[1]) && p.Y <= D(b[3]);
                var ms = MS(db, tr); int nm = 0, ns = 0;
                var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(sw[0]) || x.MinPoint.X > D(sw[2]) || x.MaxPoint.Y < D(sw[1]) || x.MinPoint.Y > D(sw[3])) continue;
                    if (e is Hatch) { if (inb(x.MinPoint, w) && inb(x.MaxPoint, w)) { e.UpgradeOpen(); e.TransformBy(Matrix3d.Displacement(vec)); nm++; } continue; }
                    var pc = new Point3dCollection();
                    try { e.GetStretchPoints(pc); } catch { continue; }
                    if (pc.Count == 0) continue;
                    var ic = new IntegerCollection();
                    for (int i = 0; i < pc.Count; i++) if (inb(pc[i], w)) ic.Add(i);
                    if (ic.Count == 0) continue;
                    e.UpgradeOpen();
                    if (ic.Count == pc.Count || e is DBText || e is MText || e is BlockReference) { e.TransformBy(Matrix3d.Displacement(vec)); nm++; }
                    else { try { e.MoveStretchPointsAt(ic, vec); ns++; } catch (System.Exception ex) { log.AppendLine("stretch fail " + e.Handle + " " + ex.Message); } }
                }
                log.AppendLine("stretchwin moved " + nm + " stretched " + ns);
            }
            else if (t == "widen")
            {
                // move stretch points away from an axis line (a, dir) by delta on each side
                var a = P(m["a"]); var dv = L(m["dir"]); var d = new Vector3d(D(dv[0]), D(dv[1]), 0).GetNormal();
                var nrm = new Vector3d(-d.Y, d.X, 0); double dl = D(m["delta"]);
                var boxes = Has(m, "only") ? L(m["only"]) : null;
                int n = 0;
                foreach (var hh in L(m["h"]))
                {
                    Entity e; try { e = (Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite); } catch { log.AppendLine("widen: no " + hh); continue; }
                    var pc = new Point3dCollection(); try { e.GetStretchPoints(pc); } catch { continue; }
                    var pos = new IntegerCollection(); var neg = new IntegerCollection();
                    for (int i = 0; i < pc.Count; i++)
                    {
                        if (boxes != null)
                        {
                            bool inside = false;
                            foreach (var bo in boxes) { var b = L(bo); if (pc[i].X >= D(b[0]) && pc[i].X <= D(b[2]) && pc[i].Y >= D(b[1]) && pc[i].Y <= D(b[3])) inside = true; }
                            if (!inside) continue;
                        }
                        double sd = (pc[i] - a).DotProduct(nrm);
                        if (sd > 0.5) pos.Add(i); else if (sd < -0.5) neg.Add(i);
                    }
                    try
                    {
                        if (pos.Count > 0) e.MoveStretchPointsAt(pos, nrm * dl);
                        if (neg.Count > 0) e.MoveStretchPointsAt(neg, nrm * -dl);
                        n++;
                    }
                    catch (System.Exception ex) { log.AppendLine("widen fail " + hh + " " + ex.Message); }
                }
                log.AppendLine("widen " + n);
            }
            else if (t == "movewin")
            {
                // move every entity whose extents centre lies inside win by d (whole sheets)
                var w = L(m["win"]); var dv = L(m["d"]); var mx = Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0));
                var ms = MS(db, tr); var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                int n = 0, nf = 0;
                var skip = new HashSet<string>(); if (Has(m, "skip")) foreach (var k in L(m["skip"])) skip.Add(k.ToString().ToUpper());
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    double cx = (x.MinPoint.X + x.MaxPoint.X) / 2, cy = (x.MinPoint.Y + x.MaxPoint.Y) / 2;
                    if (cx < D(w[0]) || cx > D(w[2]) || cy < D(w[1]) || cy > D(w[3])) continue;
                    if (skip.Contains(e.Handle.ToString().ToUpper())) continue;
                    try { e.UpgradeOpen(); e.TransformBy(mx); n++; } catch (System.Exception ex) { nf++; log.AppendLine("movewin fail " + e.Handle + " " + ex.Message); }
                }
                log.AppendLine("movewin " + n + " fail " + nf);
            }
            else if (t == "dimdef")
            {
                foreach (var hh in L(m["h"])) { try { var d = (Dimension)tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite); d.UsingDefaultTextPosition = true; d.RecomputeDimensionBlock(true); } catch { } }
            }
            else if (t == "blkerase")
            {
                // erase entities inside a block definition: texts whose plain text starts with any of 'texts', inserts whose block name starts with any of 'blocks'
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var btr = (BlockTableRecord)tr.GetObject(bt[S(m, "name", "")], OpenMode.ForRead);
                var txs = new List<string>(); if (Has(m, "texts")) foreach (var q in L(m["texts"])) txs.Add(q.ToString());
                var bls = new List<string>(); if (Has(m, "blocks")) foreach (var q in L(m["blocks"])) bls.Add(q.ToString());
                int n = 0;
                foreach (ObjectId id in btr)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    string s = null;
                    if (e is MText) s = ((MText)e).Text; else if (e is DBText) s = ((DBText)e).TextString;
                    bool hit = false;
                    if (s != null) { s = s.Trim(); foreach (var a in txs) if (s.StartsWith(a)) hit = true; }
                    if (e is BlockReference) { var nm = ((BlockReference)e).Name; foreach (var a in bls) if (nm.StartsWith(a)) hit = true; }
                    if (hit) { e.UpgradeOpen(); e.Erase(); n++; }
                }
                log.AppendLine("blkerase " + n);
                // regen all references
                foreach (ObjectId rid in btr.GetBlockReferenceIds(true, false)) { var br = (BlockReference)tr.GetObject(rid, OpenMode.ForWrite); br.RecordGraphicsModified(true); }
            }
            else if (t == "dimtx")
            {
                var d = (Dimension)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                d.UsingDefaultTextPosition = false; d.TextPosition = P(m["at"]); d.RecomputeDimensionBlock(true);
            }
            else if (t == "scalegrp")
            {
                var mx = Matrix3d.Scaling(D(m["s"]), P(m["base"]));
                int n = 0;
                foreach (var hh in L(m["h"])) { try { ((Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite)).TransformBy(mx); n++; } catch (System.Exception ex) { log.AppendLine("scalegrp fail " + hh + " " + ex.Message); } }
                log.AppendLine("scalegrp " + n);
            }
            else if (t == "dimset")
            {
                foreach (var hh in L(m["h"]))
                {
                    var d = tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite) as Dimension; if (d == null) continue;
                    if (Has(m, "lfac")) d.Dimlfac = D(m["lfac"]);
                    if (Has(m, "dscale")) d.Dimscale = D(m["dscale"]);
                    if (Has(m, "tmove")) d.Dimtmove = Convert.ToInt32(m["tmove"]);
                }
            }
            else if (t == "movegrp")
            {
                var dv = L(m["d"]); var mx = Matrix3d.Displacement(new Vector3d(D(dv[0]), D(dv[1]), 0));
                foreach (var hh in L(m["h"])) { try { ((Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite)).TransformBy(mx); } catch { log.AppendLine("movegrp: no " + hh); } }
            }
            else if (t == "arcrad")
            {
                var e = (Arc)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite); e.Radius = e.Radius + D(m["dr"]);
            }
            else if (t == "addleader")
            {
                var id = H(db, S(m, "h", ""));
                var np = MGet(id) as McNotePosition;
                np.Leader.AddSegment(MP(m["target"]), Has(m, "from") ? MP(m["from"]) : np.Origin);
                np.DbEntity.Update();
            }
            else if (t == "comb")
            {
                // comb leader: first segment origin->k (no arrow), child segments k->targets with arrows
                var id = H(db, S(m, "h", ""));
                var np = MGet(id) as McNotePosition;
                var k = MP(m["k"]);
                Multicad.Symbols.McBLSegment seg = null;
                foreach (Multicad.Symbols.McBLSegment c in np.Leader.Childs) { seg = c; break; }
                string ar = S(m, "arrow", "oblique");
                var arr = ar == "arrow" ? MG.Arrows.Arrow : ar == "oblique" ? MG.Arrows.Oblique : MG.Arrows.None;
                seg.Arrow = Has(m, "karrow") ? arr : MG.Arrows.None;
                foreach (object q in L(m["targets"])) seg.AddSegment(MP(q), k);
                foreach (Multicad.Symbols.McBLSegment c in seg.Childs) c.Arrow = arr;
                log.AppendLine("comb " + S(m, "h", "") + " start " + seg.Start + " end " + seg.End + " childs " + seg.Childs.Count);
                np.DbEntity.Update();
            }
            else if (t == "dimpts")
            {
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var ad = e as AlignedDimension; var rd = e as RotatedDimension;
                if (ad != null) { ad.XLine1Point = P(m["p1"]); ad.XLine2Point = P(m["p2"]); if (Has(m, "dl")) ad.DimLinePoint = P(m["dl"]); }
                if (rd != null) { rd.XLine1Point = P(m["p1"]); rd.XLine2Point = P(m["p2"]); if (Has(m, "dl")) rd.DimLinePoint = P(m["dl"]); }
            }
            else if (t == "erasenear")
            {
                var c = P(m["c"]); double r = D(m["r"]); int n = 0;
                var types = new HashSet<string>(); foreach (var q in L(m["types"])) types.Add(q.ToString());
                var ms = MS(db, tr); var ids = new List<ObjectId>();
                foreach (ObjectId id in ms)
                {
                    if (!types.Contains(id.ObjectClass.Name)) continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    if (Has(m, "layer") && e.Layer != S(m, "layer", "")) continue;
                    if (Has(m, "lw") && (int)e.LineWeight != Convert.ToInt32(m["lw"])) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X >= c.X - r && x.MaxPoint.X <= c.X + r && x.MinPoint.Y >= c.Y - r && x.MaxPoint.Y <= c.Y + r) ids.Add(id);
                }
                foreach (var id in ids) { tr.GetObject(id, OpenMode.ForWrite).Erase(); n++; }
                log.AppendLine("erasenear " + n);
            }
            else if (t == "notepull")
            {
                // shorten note leaders: origin -> target + (origin - target) * f, or explicit offset 'off' from the target
                foreach (var hh in L(m["h"]))
                {
                    var e = (Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead);
                    var pc = new Point3dCollection(); e.GetStretchPoints(pc); if (pc.Count < 2) continue;
                    var np = MGet(e.ObjectId) as McNotePosition; if (np == null) continue;
                    double f = Has(m, "f") ? D(m["f"]) : 0.5;
                    double nx = pc[1].X + (pc[0].X - pc[1].X) * f, ny = pc[1].Y + (pc[0].Y - pc[1].Y) * f;
                    np.Origin = MP(new ArrayList { nx, ny });
                    np.DbEntity.Update();
                    log.AppendLine("notepull " + hh + " " + np.FirstLine);
                }
            }
            else if (t == "noteset")
            {
                var w = L(m["win"]); int n = 0;
                var ms = MS(db, tr);
                foreach (ObjectId id in ms)
                {
                    if (id.ObjectClass.DxfName != "SPDSNOTEPOSITION") continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MinPoint.X < D(w[0]) || x.MaxPoint.X > D(w[2]) || x.MinPoint.Y < D(w[1]) || x.MaxPoint.Y > D(w[3])) continue;
                    var np = MGet(id) as McNotePosition;
                    if (np == null) continue;
                    if (np.FirstLine == S(m, "from", "")) { np.FirstLine = S(m, "to", ""); if (Has(m, "l2")) np.SecondLine = S(m, "l2", ""); np.DbEntity.Update(); n++; }
                    var dd = (object)np as IDisposable; if (dd != null) dd.Dispose();
                }
                log.AppendLine("noteset " + S(m, "from", "") + " " + n);
            }
            else if (t == "erase")
            {
                foreach (var h in L(m["h"])) { try { tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite).Erase(); } catch (System.Exception ex) { log.AppendLine("erase " + h + ": " + ex.Message); } }
            }
            else if (t == "wblock")
            {
                using (var nd = db.Wblock()) nd.SaveAs(S(m, "file", ""), DwgVersion.Current);
            }
            else if (t == "dxfout")
            {
                db.DxfOut(S(m, "file", ""), 16, DwgVersion.Current);
            }
            else if (t == "regen")
            {
                Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument.SendStringToExecute("_.REGENALL\n", true, false, false);
            }
            else if (t == "dimtext")
            {
                var d = (Dimension)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite); d.DimensionText = S(m, "s", "");
            }
            else if (t == "setblock")
            {
                // point a block reference at another block definition (same base point)
                var br = (BlockReference)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                br.BlockTableRecord = bt[S(m, "name", "")];
                if (Has(m, "at")) br.Position = P(m["at"]);
            }
            else if (t == "tdump")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                log.AppendLine("TABLE rows " + tb.Rows.Count + " cols " + tb.Columns.Count);
                for (int r = 0; r < tb.Rows.Count; r++)
                {
                    var sb = new StringBuilder("R" + r + " h" + tb.Rows[r].Height.ToString("0", IC) + ":");
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c]; string f = "";
                        try { string ed = cell.GetTextString(FormatOption.ForEditing); if (ed != cell.TextString) f = "{" + ed + "}"; } catch { }
                        string mg = ""; try { var rg = cell.GetMergeRange(); if (rg != null) mg = "<" + rg.TopRow + "," + rg.LeftColumn + "-" + rg.BottomRow + "," + rg.RightColumn + ">"; } catch { }
                        sb.Append(" | " + cell.TextString.Replace("\n", "\\n") + f + mg);
                    }
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "tset")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"]))
                {
                    var a = L(q); int r = Convert.ToInt32(a[0]), c = Convert.ToInt32(a[1]); string v = a[2].ToString();
                    tb.Cells[r, c].TextString = v;
                }
            }
            else if (t == "tform")
            {
                // formulas / values of every non-empty cell: r,c  formula  value
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead);
                log.AppendLine("TFORM " + tb.Handle + " objid " + tb.ObjectId.OldIdPtr.ToInt64());
                for (int r = 0; r < tb.Rows.Count; r++)
                    for (int c = 0; c < tb.Columns.Count; c++)
                    {
                        var cell = tb.Cells[r, c]; string f = "";
                        try { if (cell.Contents.Count > 0) f = cell.Contents[0].Formula ?? ""; } catch { }
                        string fs = ""; try { fs = cell.GetTextString(FormatOption.FormatOptionNone); } catch { }
                        if (f != "" || (fs.Contains("%<") )) log.AppendLine("F " + r + "," + c + "\t" + f + "\t" + fs + "\t" + cell.TextString);
                    }
            }
            else if (t == "tformula")
            {
                // cells [[r,c,"formula without =", (optional) "text"]]; {T:handle} -> %<\_ObjId ptr>% of that table
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"]))
                {
                    var a = L(q); var cell = tb.Cells[Convert.ToInt32(a[0]), Convert.ToInt32(a[1])];
                    string f = a[2].ToString();
                    var rx = new System.Text.RegularExpressions.Regex(@"\{T:([0-9A-Fa-f]+)\}");
                    f = rx.Replace(f, mm => "%<\\_ObjId " + H(db, mm.Groups[1].Value).OldIdPtr.ToInt64() + ">%");
                    double th = 0; try { th = cell.Contents[0].TextHeight; } catch { }
                    string fmt = null; try { fmt = cell.DataFormat; } catch { }
                    cell.TextString = "";
                    if (f.StartsWith("TEXT:"))
                    {
                        cell.Contents.Clear(); cell.Contents.Add();
                        cell.DataType = new DataTypeParameter(DataType.String, UnitType.Unitless);
                        cell.TextString = f.Substring(5);
                    }
                    else
                    {
                        if (cell.Contents.Count == 0) cell.Contents.Add();
                        cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                        cell.Contents[0].Formula = "=" + f;
                        if (fmt != null) try { cell.DataFormat = fmt; } catch { }
                    }
                    if (th > 0) try { cell.Contents[0].TextHeight = th; } catch { }
                }
                tb.GenerateLayout();
            }
            else if (t == "tfmtcopy")
            {
                // copy DataFormat (and text height) from source cell [sh,sr,sc] to cells [[r,c]] of h
                var st = (Table)tr.GetObject(H(db, S(m, "sh", "")), OpenMode.ForRead);
                var sa = L(m["src"]); var sCell = st.Cells[Convert.ToInt32(sa[0]), Convert.ToInt32(sa[1])];
                string fmt = sCell.DataFormat;
                log.AppendLine("fmt '" + fmt + "'");
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"])) { var a = L(q); tb.Cells[Convert.ToInt32(a[0]), Convert.ToInt32(a[1])].DataFormat = fmt; }
                tb.GenerateLayout();
            }
            else if (t == "viewset" || t == "viewrestore")
            {
                // viewset: remember the user's view, show window win; viewrestore: put the remembered view back
                var ed = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument.Editor;
                string vf = Path.Combine(tmp, "rr_view.txt");
                if (t == "viewset")
                {
                    using (var v0 = ed.GetCurrentView())
                        File.WriteAllText(vf, v0.CenterPoint.X.ToString(IC) + "," + v0.CenterPoint.Y.ToString(IC) + "," + v0.Width.ToString(IC) + "," + v0.Height.ToString(IC));
                    var w = L(m["win"]);
                    using (var v = ed.GetCurrentView())
                    {
                        v.CenterPoint = new Point2d((D(w[0]) + D(w[2])) / 2 - v.Target.X, (D(w[1]) + D(w[3])) / 2 - v.Target.Y);
                        double ww = D(w[2]) - D(w[0]), hh = D(w[3]) - D(w[1]), ar = v.Width / v.Height;
                        if (ww / hh > ar) { v.Width = ww; v.Height = ww / ar; } else { v.Height = hh; v.Width = hh * ar; }
                        ed.SetCurrentView(v);
                    }
                }
                else
                {
                    var a = File.ReadAllText(vf).Split(',');
                    using (var v = ed.GetCurrentView())
                    {
                        v.CenterPoint = new Point2d(double.Parse(a[0], IC), double.Parse(a[1], IC));
                        v.Width = double.Parse(a[2], IC); v.Height = double.Parse(a[3], IC);
                        ed.SetCurrentView(v);
                    }
                }
            }
            else if (t == "dyn")
            {
                // set one dynamic property (no listing of allowed values — that leaked read-opens, eAtMaxReaders 04.11)
                var br = (BlockReference)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pc = br.DynamicBlockReferencePropertyCollection;
                foreach (DynamicBlockReferenceProperty p in pc)
                {
                    if (Has(m, "prop") && p.PropertyName == S(m, "prop", ""))
                    {
                        object v = p.Value is string ? (object)S(m, "value", "") : (object)D(m["value"]);
                        if (!p.Value.Equals(v)) p.Value = v;
                    }
                    else if (!Has(m, "prop")) log.AppendLine("DYN " + p.PropertyName + " = " + Convert.ToString(p.Value, IC));
                }
            }
            else if (t == "evalf")
            {
                db.EvaluateFields();
            }
            else if (t == "tnum")
            {
                // write plain numbers (no formula): cells [[r,c,value,format]]
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["cells"]))
                {
                    var a = L(q); var cell = tb.Cells[Convert.ToInt32(a[0]), Convert.ToInt32(a[1])];
                    double th = 0; try { th = cell.Contents[0].TextHeight; } catch { }
                    cell.Contents.Clear(); cell.Contents.Add();
                    cell.DataType = new DataTypeParameter(DataType.Double, UnitType.Unitless);
                    cell.Value = D(a[2]);
                    if (a.Count > 3) cell.DataFormat = a[3].ToString();
                    if (th > 0) cell.Contents[0].TextHeight = th;
                }
            }
            else if (t == "trows")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                string mode = S(m, "mode", "del"); int at = Convert.ToInt32(m["at"]), n = Convert.ToInt32(m["n"]);
                if (mode == "del") tb.DeleteRows(at, n); else tb.InsertRowsAndInherit(at, Convert.ToInt32(m["from"]), n);
            }
            else if (t == "explode")
            {
                // explode a block reference into model space (keeps layers); tag new entities with prefix
                var br = (BlockReference)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var col = new DBObjectCollection(); br.Explode(col);
                var ms = MS(db, tr); int n = 0; string pre = S(m, "pre", null);
                foreach (DBObject o in col) { var en = o as Entity; if (en == null) continue; ms.AppendEntity(en); tr.AddNewlyCreatedDBObject(en, true); if (pre != null) map[pre + n] = en.Handle.ToString(); n++; }
                br.Erase(); log.AppendLine("explode " + n);
            }
            else if (t == "tcols")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                tb.DeleteColumns(Convert.ToInt32(m["at"]), Convert.ToInt32(m["n"]));
            }
            else if (t == "theight")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                foreach (var q in L(m["rows"])) { var a = L(q); tb.Rows[Convert.ToInt32(a[0])].Height = D(a[1]); }
            }
            else if (t == "tmerge")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var a = L(m["r"]); var rg = CellRange.Create(tb, Convert.ToInt32(a[0]), Convert.ToInt32(a[1]), Convert.ToInt32(a[2]), Convert.ToInt32(a[3]));
                if (S(m, "mode", "merge") == "merge") tb.MergeCells(rg); else tb.UnmergeCells(rg);
            }
            else if (t == "list")
            {
                // every entity whose extents touch win: dxfname, handle, layer, extents, stretch points
                var w = L(m["win"]);
                var ms = MS(db, tr);
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x;
                    try { x = e.GeometricExtents; }
                    catch
                    {
                        // no extents (some SPDS proxies): report by the first stretch point so imports do not miss them
                        var pn = new Point3dCollection(); try { e.GetStretchPoints(pn); } catch { }
                        if (pn.Count > 0 && pn[0].X >= D(w[0]) && pn[0].X <= D(w[2]) && pn[0].Y >= D(w[1]) && pn[0].Y <= D(w[3]))
                            log.AppendLine("N\t" + id.ObjectClass.DxfName + "\t" + e.Handle + "\t" + e.Layer + "\t" + pn[0].X.ToString("0", IC) + "," + pn[0].Y.ToString("0", IC));
                        continue;
                    }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    var sb = new StringBuilder("L\t" + id.ObjectClass.DxfName + "\t" + e.Handle + "\t" + e.Layer + "\tE" + x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + "," + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC));
                    var pc = new Point3dCollection(); try { e.GetStretchPoints(pc); } catch { }
                    for (int i = 0; i < pc.Count && i < 12; i++) sb.Append("\t" + pc[i].X.ToString("0", IC) + "," + pc[i].Y.ToString("0", IC));
                    log.AppendLine(sb.ToString());
                }
            }
            else if (t == "notelist")
            {
                // все выноски СПДС: тип, текст, точки, выравнивание, угол
                var ms = MS(db, tr);
                foreach (ObjectId id in ms)
                {
                    string dn = id.ObjectClass.DxfName;
                    if (dn != "SPDSNOTEPOSITION" && dn != "SPDSNOTEKNOT") continue;
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    var pc = new Point3dCollection(); try { e.GetStretchPoints(pc); } catch { }
                    var mo = MGet(id);
                    var sb = new StringBuilder("N\t" + e.Handle + "\t" + dn);
                    Func<string, string> pv = (nm) => { try { var p = mo.GetType().GetProperty(nm); return p == null ? "" : Convert.ToString(p.GetValue(mo, null), IC); } catch { return "?"; } };
                    sb.Append("\t" + pv("FirstLine") + "\t" + pv("SecondLine") + "\t" + pv("Knot") + "\t" + pv("Align") + "\t" + pv("Angle") + "\t" + pv("Arrow"));
                    for (int i = 0; i < pc.Count; i++) sb.Append("\t" + pc[i].X.ToString("0", IC) + "," + pc[i].Y.ToString("0", IC));
                    Extents3d x; try { x = e.GeometricExtents; sb.Append("\tE" + x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + "," + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC)); } catch { }
                    log.AppendLine(sb.ToString());
                    var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                }
            }
            else if (t == "knotalign")
            {
                // полка выноски узла — от круга наружу: Rack левее центра -> Align Left, правее -> Right
                var ms = MS(db, tr); int n = 0;
                foreach (ObjectId id in ms)
                {
                    if (id.ObjectClass.DxfName != "SPDSNOTEKNOT") continue;
                    var mo = MGet(id);
                    if (mo == null) continue;
                    var ty = mo.GetType();
                    var rack = (MG.Point3d)ty.GetProperty("Rack").GetValue(mo, null);
                    var cen = (MG.Point3d)ty.GetProperty("Center").GetValue(mo, null);
                    var pa = ty.GetProperty("Align");
                    pa.SetValue(mo, Enum.Parse(pa.PropertyType, rack.X < cen.X ? "Left" : "Right"), null);
                    var dbe = ty.GetProperty("DbEntity").GetValue(mo, null) as McDbEntity; dbe.Update();
                    var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                    n++;
                }
                log.AppendLine("knotalign " + n);
            }
            else if (t == "maprst")
            {
                map.Clear();
            }
            else if (t == "axis")
            {
                // SPDS axis: start s, end e (marker at end), value, scale
                var id = H(db, S(m, "h", ""));
                var a = MGet(id) as McAxisEntity;
                try
                {
                    if (Has(m, "scale")) a.DbEntity.Scale = D(m["scale"]);
                    var lin = a.Axis.Methods as McBasicAxis.McAxisSpecificLinear;
                    lin.setPoints(MP(m["s"]), MP(m["e"]));
                    if (Has(m, "val")) a.Axis.Methods.Markers.First.Value = S(m, "val", "");
                    a.DbEntity.Update();
                    log.AppendLine("AXIS " + S(m, "h", "") + " " + S(m, "val", "") + " S=" + lin.StartPoint + " E=" + lin.EndPoint);
                }
                finally { var dd = (object)a as IDisposable; if (dd != null) dd.Dispose(); }
            }
            else if (t == "levbase")
            {
                // SPDS level mark: replace stored zero-level Y (double near 'old') by 'new', re-create, erase old
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                double oldv = D(m["old"]), newv = D(m["new"]), tol = Has(m, "tol") ? D(m["tol"]) : 5;
                int cnt = 0; var sb = new StringBuilder();
                for (int i = 0; i + 8 <= b.Length; i++)
                {
                    double v = BitConverter.ToDouble(b, i);
                    if (Math.Abs(v - oldv) < tol) { Array.Copy(BitConverter.GetBytes(newv), 0, b, i, 8); cnt++; sb.Append(" @" + i + "=" + v.ToString("0.###", IC)); i += 7; }
                }
                log.AppendLine("levbase " + cnt + sb);
                if (cnt == 0) return;
                var ne = McDbEntity.DeserializeNewFromBytes(b);
                McObjectManager.Add2Document(ne); ne.Update();
                tr.GetObject(id, OpenMode.ForWrite).Erase();
                var nid = new ObjectId(ne.ID.ToOldIdPtr());
                string tg = S(m, "tag", null);
                if (tg != null) { var ee = tr.GetObject(nid, OpenMode.ForRead) as Entity; if (ee != null) map[tg] = ee.Handle.ToString(); }
            }
            else if (t == "dimfix")
            {
                // set text position of existing rotated dims found by their two extension points (any order)
                var items = L(m["items"]); var ms = MS(db, tr); int n = 0;
                var dims = new List<RotatedDimension>();
                foreach (ObjectId id in ms) { if (id.ObjectClass.DxfName != "DIMENSION") continue; var d = tr.GetObject(id, OpenMode.ForRead) as RotatedDimension; if (d != null) dims.Add(d); }
                foreach (var it in items)
                {
                    var q = (Dictionary<string, object>)it; var a = P(q["p1"]); var b = P(q["p2"]); bool hit = false;
                    foreach (var d in dims)
                    {
                        bool eq = (d.XLine1Point.DistanceTo(a) < 1 && d.XLine2Point.DistanceTo(b) < 1) || (d.XLine1Point.DistanceTo(b) < 1 && d.XLine2Point.DistanceTo(a) < 1);
                        if (!eq) continue;
                        d.UpgradeOpen(); d.UsingDefaultTextPosition = false; d.TextPosition = P(q["tx"]); n++; hit = true;
                    }
                    if (!hit) log.AppendLine("dimfix miss " + a + " " + b);
                }
                log.AppendLine("dimfix " + n);
            }
            else if (t == "moveto")
            {
                // move entity so that its stretch point idx lands on 'to'
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                int i = Has(m, "idx") ? Convert.ToInt32(m["idx"]) : 0;
                e.TransformBy(Matrix3d.Displacement(P(m["to"]) - pc[i]));
            }
            else if (t == "geomdump")
            {
                // explode every SPDS (custom) entity inside a window and dump its real plotted geometry:
                // segments "S|handle|dxf|x1|y1|x2|y2" and texts "T|handle|dxf|x0|y0|x1|y1|text" (extents) - oc.py reads this
                // instead of proxy graphics, which ezdxf cannot parse for some SPDS classes (SPDSSECTION)
                var w = L(m["win"]); double wx0 = D(w[0]), wy0 = D(w[1]), wx1 = D(w[2]), wy1 = D(w[3]);
                var outp = new StringBuilder(); int ne = 0, nfail = 0;
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                foreach (ObjectId oid in ms)
                {
                    var dxf = oid.ObjectClass.DxfName ?? "";
                    if (!(dxf.StartsWith("SPDS") || dxf == "DIMENSION") || dxf == "SPDSFORMAT") continue;   // dims too: moved texts as AutoCAD draws them
                    var ent = (Entity)tr.GetObject(oid, OpenMode.ForRead);
                    Extents3d ex; try { ex = ent.GeometricExtents; } catch { continue; }
                    if (ex.MaxPoint.X < wx0 || ex.MinPoint.X > wx1 || ex.MaxPoint.Y < wy0 || ex.MinPoint.Y > wy1) continue;
                    string hh = ent.Handle.ToString(); ne++;
                    var stack = new List<Entity> { ent }; int guard = 0;
                    try
                    {
                        while (stack.Count > 0 && guard++ < 20000)
                        {
                            var cur = stack[stack.Count - 1]; stack.RemoveAt(stack.Count - 1);
                            if (cur is Line) { var ln = (Line)cur; outp.AppendLine(string.Format(System.Globalization.CultureInfo.InvariantCulture, "S|{0}|{1}|{2:F1}|{3:F1}|{4:F1}|{5:F1}", hh, dxf, ln.StartPoint.X, ln.StartPoint.Y, ln.EndPoint.X, ln.EndPoint.Y)); continue; }
                            if (cur is Polyline) { var pl = (Polyline)cur; int nv = pl.NumberOfVertices; int ns = pl.Closed ? nv : nv - 1;
                                for (int i = 0; i < ns; i++) { var p1 = pl.GetPoint2dAt(i); var p2 = pl.GetPoint2dAt((i + 1) % nv);
                                    outp.AppendLine(string.Format(System.Globalization.CultureInfo.InvariantCulture, "S|{0}|{1}|{2:F1}|{3:F1}|{4:F1}|{5:F1}", hh, dxf, p1.X, p1.Y, p2.X, p2.Y)); } continue; }
                            if (cur is DBText || cur is MText)
                            {
                                string s = cur is DBText ? ((DBText)cur).TextString : ((MText)cur).Text;
                                try { var e2 = cur.GeometricExtents; outp.AppendLine(string.Format(System.Globalization.CultureInfo.InvariantCulture, "T|{0}|{1}|{2:F1}|{3:F1}|{4:F1}|{5:F1}|{6}", hh, dxf, e2.MinPoint.X, e2.MinPoint.Y, e2.MaxPoint.X, e2.MaxPoint.Y, (s ?? "").Replace("|", "/").Replace("\n", " "))); } catch { }
                                continue;
                            }
                            if (cur is Hatch || cur is Solid || cur is Circle || cur is Arc || cur is DBPoint) continue;
                            var col = new DBObjectCollection();
                            try { cur.Explode(col); } catch { if (cur == ent) nfail++; continue; }
                            foreach (DBObject o in col) if (o is Entity) stack.Add((Entity)o);
                        }
                    }
                    catch { nfail++; }
                }
                File.WriteAllText(S(m, "file", ""), outp.ToString(), Encoding.UTF8);
                log.AppendLine("geomdump entities " + ne + " failed " + nfail);
            }
            else if (t == "props")
            {
                // list public properties of an SPDS object (type, name, value) into the log
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                log.AppendLine("props " + S(m, "h", "") + " " + mo.GetType().FullName);
                foreach (var pi in mo.GetType().GetProperties())
                {
                    string v; try { v = Convert.ToString(pi.GetValue(mo, null)); } catch (Exception ex) { v = "!" + ex.GetType().Name; }
                    log.AppendLine("  " + pi.Name + " : " + pi.PropertyType.Name + " = " + v + (pi.CanWrite ? "" : " (ro)"));
                }
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
            }
            else if (t == "serdump")
            {
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                File.WriteAllBytes(S(m, "file", ""), b);
                log.AppendLine("serdump " + b.Length);
            }
            else if (t == "serfix")
            {
                // serialized-bytes edit of an SPDS object: doubles [[old,new,tol],...] and same-length ASCII strings [[old,new],...]; re-create, erase old
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                int cnt = 0;
                if (Has(m, "d")) foreach (var it in L(m["d"]))
                {
                    var q = L(it); double oldv = D(q[0]), newv = D(q[1]), tol = D(q[2]);
                    for (int i = 0; i + 8 <= b.Length; i++) { double v = BitConverter.ToDouble(b, i); if (!double.IsNaN(v) && Math.Abs(v - oldv) < tol) { Array.Copy(BitConverter.GetBytes(newv), 0, b, i, 8); cnt++; i += 7; } }
                }
                if (Has(m, "s")) foreach (var it in L(m["s"]))
                {
                    var q = L(it); var a = Encoding.GetEncoding(28591).GetBytes(q[0].ToString()); var r = Encoding.GetEncoding(28591).GetBytes(q[1].ToString());
                    if (a.Length != r.Length) { log.AppendLine("serfix: length differs " + q[0] + " " + q[1]); continue; }
                    for (int i = 0; i + a.Length <= b.Length; i++)
                    {
                        bool eq = true; for (int k = 0; k < a.Length; k++) if (b[i + k] != a[k]) { eq = false; break; }
                        if (eq) { Array.Copy(r, 0, b, i, r.Length); cnt++; i += a.Length - 1; }
                    }
                }
                if (Has(m, "raw")) foreach (var it in L(m["raw"]))
                {
                    var q = L(it); Func<string, byte[]> hx = (s) => { s = s.Replace(" ", ""); var r = new byte[s.Length / 2]; for (int k = 0; k < r.Length; k++) r[k] = Convert.ToByte(s.Substring(2 * k, 2), 16); return r; };
                    var a = hx(q[0].ToString()); var r2 = hx(q[1].ToString());
                    var lst = new List<byte>(b); int pos = -1;
                    for (int i = 0; i + a.Length <= b.Length && pos < 0; i++) { bool eq = true; for (int k = 0; k < a.Length; k++) if (b[i + k] != a[k]) { eq = false; break; } if (eq) pos = i; }
                    if (pos < 0) { log.AppendLine("serfix raw not found " + q[0]); continue; }
                    lst.RemoveRange(pos, a.Length); lst.InsertRange(pos, r2); b = lst.ToArray(); cnt++;
                    int delta = r2.Length - a.Length;
                    if (delta != 0) { int hv = BitConverter.ToInt32(b, 8); Array.Copy(BitConverter.GetBytes(hv + delta), 0, b, 8, 4); }
                }
                log.AppendLine("serfix " + S(m, "h", "") + " repl " + cnt);
                if (cnt == 0) return;
                var ne = McDbEntity.DeserializeNewFromBytes(b);
                McObjectManager.Add2Document(ne); ne.Update();
                tr.GetObject(id, OpenMode.ForWrite).Erase();
                var nid = new ObjectId(ne.ID.ToOldIdPtr());
                string tg = S(m, "tag", null);
                if (tg != null) { var ee = tr.GetObject(nid, OpenMode.ForRead) as Entity; if (ee != null) map[tg] = ee.Handle.ToString(); }
            }
            else if (t == "movept")
            {
                // shift stretch point idx (default 0 = СПДС note origin / shelf) by a delta
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var dv = L(m["d"]); int idx = Has(m, "idx") ? Convert.ToInt32(m["idx"]) : 0;
                var ic = new IntegerCollection(); ic.Add(idx);
                e.MoveStretchPointsAt(ic, new Vector3d(D(dv[0]), D(dv[1]), 0));
            }
            else if (t == "spmove")
            {
                // move individual stretch points: items [[idx,x,y],...]; "list":true logs the points
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pc0 = new Point3dCollection(); e.GetStretchPoints(pc0);
                var sb = new StringBuilder(); foreach (Point3d q in pc0) sb.Append(" (" + q.X.ToString("0.#", IC) + "," + q.Y.ToString("0.#", IC) + ")");
                log.AppendLine("spmove " + S(m, "h", "") + " pts" + sb);
                if (Has(m, "items")) foreach (var it in L(m["items"]))
                {
                    var q = L(it); int idx = Convert.ToInt32(q[0]);
                    var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                    var ic = new IntegerCollection(); ic.Add(idx);
                    e.MoveStretchPointsAt(ic, new Point3d(D(q[1]), D(q[2]), 0) - pc[idx]);
                }
            }
            else if (t == "secset")
            {
                // SPDS section mark: points [[x,y],...], Word, Dir, scale
                var id = H(db, S(m, "h", ""));
                var sv = MGet(id) as McSectionVS;
                try
                {
                    if (Has(m, "scale")) sv.DbEntity.Scale = D(m["scale"]);
                    if (Has(m, "pts"))
                    {
                        var pc = sv.Points; var pl = L(m["pts"]);
                        log.AppendLine("secset had " + pc.Count);
                        pc.Clear();
                        for (int i = 0; i < pl.Count; i++) pc.Add(MP(pl[i]));
                        sv.Points = pc;
                    }
                    if (Has(m, "get")) { var sb2 = new StringBuilder("SECPTS " + S(m, "h", "")); foreach (var q in sv.Points) sb2.Append("	" + q.X.ToString("0.0", IC) + "," + q.Y.ToString("0.0", IC)); log.AppendLine(sb2.ToString()); return; }
                    if (Has(m, "word")) sv.Word = S(m, "word", "1");
                    if (Has(m, "dir")) sv.Dir = Convert.ToInt32(m["dir"]);
                    sv.DbEntity.Update();
                    log.AppendLine("secset " + S(m, "h", "") + " n=" + sv.Points.Count + " " + sv.Points[0] + " " + sv.Points[sv.Points.Count - 1]);
                }
                finally { var dd = (object)sv as IDisposable; if (dd != null) dd.Dispose(); }
            }
            else if (t == "relink")
            {
                // level mark h: replace reference to relation mark 'oldrel' (handle) with 'newrel' (handle) in serialized bytes
                Func<string, Guid> gid = (hh) =>
                {
                    var rid = H(db, hh);
                    var ro = MGet(rid);
                    var gp = ro.GetType().GetProperty("ID").GetValue(ro, null);
                    var dr = ro as IDisposable; if (dr != null) dr.Dispose();
                    return new Guid(gp.ToString());
                };
                Guid go = gid(S(m, "oldrel", "")), gn = gid(S(m, "newrel", ""));
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                int cnt = 0;
                var pairs = new List<byte[][]> {
                    new byte[][] { go.ToByteArray(), gn.ToByteArray() },
                    new byte[][] { Encoding.Unicode.GetBytes(go.ToString("B").ToUpper()), Encoding.Unicode.GetBytes(gn.ToString("B").ToUpper()) },
                    new byte[][] { Encoding.ASCII.GetBytes(go.ToString("B").ToUpper()), Encoding.ASCII.GetBytes(gn.ToString("B").ToUpper()) } };
                foreach (var pr in pairs)
                    for (int i = 0; i + pr[0].Length <= b.Length; i++)
                    {
                        bool eq = true; for (int k = 0; k < pr[0].Length; k++) if (b[i + k] != pr[0][k]) { eq = false; break; }
                        if (eq) { Array.Copy(pr[1], 0, b, i, pr[1].Length); cnt++; }
                    }
                if (Has(m, "old"))
                {
                    double oldv = D(m["old"]), newv = D(m["new"]);
                    for (int i = 0; i + 8 <= b.Length; i++) { double v = BitConverter.ToDouble(b, i); if (Math.Abs(v - oldv) < 2) { Array.Copy(BitConverter.GetBytes(newv), 0, b, i, 8); cnt += 100; i += 7; } }
                }
                log.AppendLine("relink " + S(m, "h", "") + " " + go + ">" + gn + " repl " + cnt);
                if (cnt == 0) return;
                var ne = McDbEntity.DeserializeNewFromBytes(b);
                McObjectManager.Add2Document(ne); ne.Update();
                tr.GetObject(id, OpenMode.ForWrite).Erase();
                var nid = new ObjectId(ne.ID.ToOldIdPtr());
                string tg = S(m, "tag", null);
                if (tg != null) { var ee = tr.GetObject(nid, OpenMode.ForRead) as Entity; if (ee != null) map[tg] = ee.Handle.ToString(); }
            }
            else if (t == "pmap")
            {
                // piecewise-linear remap of every stretch point inside win along x (or y): pairs [[from,to],...] sorted
                var w = L(m["win"]); double wx0 = D(w[0]), wy0 = D(w[1]), wx1 = D(w[2]), wy1 = D(w[3]);
                bool ax = S(m, "axis", "x") == "x";
                var pr = new List<double[]>(); foreach (var q in L(m["pairs"])) { var a = L(q); pr.Add(new double[] { D(a[0]), D(a[1]) }); }
                Func<double, double> f = v =>
                {
                    if (v <= pr[0][0]) return v + pr[0][1] - pr[0][0];
                    for (int i = 1; i < pr.Count; i++)
                        if (v <= pr[i][0]) { double k = (v - pr[i - 1][0]) / (pr[i][0] - pr[i - 1][0]); return pr[i - 1][1] + k * (pr[i][1] - pr[i - 1][1]); }
                    return v + pr[pr.Count - 1][1] - pr[pr.Count - 1][0];
                };
                Func<Point3d, bool> inW = q => q.X >= wx0 && q.X <= wx1 && q.Y >= wy0 && q.Y <= wy1;
                int nm = 0, ns = 0, nf = 0;
                var ms = MS(db, tr);
                var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < wx0 || x.MinPoint.X > wx1 || x.MaxPoint.Y < wy0 || x.MinPoint.Y > wy1) continue;
                    try
                    {
                        var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                        if (pc.Count == 0) continue;
                        var dl = new double[pc.Count]; bool any = false, same = true; int nin = 0;
                        for (int i = 0; i < pc.Count; i++)
                        {
                            if (!inW(pc[i])) { dl[i] = double.NaN; same = false; continue; }
                            nin++;
                            double v = ax ? pc[i].X : pc[i].Y; dl[i] = f(v) - v;
                            if (Math.Abs(dl[i]) > 0.01) any = true;
                            if (i > 0 && !double.IsNaN(dl[0]) && Math.Abs(dl[i] - dl[0]) > 0.01) same = false;
                        }
                        if (!any) continue;
                        e.UpgradeOpen();
                        bool inside = x.MinPoint.X >= wx0 && x.MaxPoint.X <= wx1 && x.MinPoint.Y >= wy0 && x.MaxPoint.Y <= wy1;
                        if (same && nin == pc.Count && (inside || pc.Count == 1 || e is Dimension || e is Hatch || e is Polyline || e is Line))
                        { e.TransformBy(Matrix3d.Displacement(ax ? new Vector3d(dl[0], 0, 0) : new Vector3d(0, dl[0], 0))); nm++; }
                        else if (same && nin == pc.Count && !(e is Curve) && !(e is Dimension))
                        { e.TransformBy(Matrix3d.Displacement(ax ? new Vector3d(dl[0], 0, 0) : new Vector3d(0, dl[0], 0))); nm++; }
                        else
                        {
                            for (int i = 0; i < pc.Count; i++)
                            {
                                if (double.IsNaN(dl[i]) || Math.Abs(dl[i]) < 0.01) continue;
                                var ic = new IntegerCollection(); ic.Add(i);
                                e.MoveStretchPointsAt(ic, ax ? new Vector3d(dl[i], 0, 0) : new Vector3d(0, dl[i], 0));
                            }
                            ns++;
                        }
                    }
                    catch (System.Exception ex) { nf++; log.AppendLine("pmap fail " + e.Handle + " " + e.GetType().Name + " " + ex.Message); }
                }
                log.AppendLine("pmap moved " + nm + " remapped " + ns + " failed " + nf);
            }
            else if (t == "stretch")
            {
                // like STRETCH with a crossing window: stretch points inside win move by d; entities wholly inside move
                var w = L(m["win"]); double wx0 = D(w[0]), wy0 = D(w[1]), wx1 = D(w[2]), wy1 = D(w[3]);
                var dv = L(m["d"]); var vec = new Vector3d(D(dv[0]), D(dv[1]), 0);
                Func<Point3d, bool> inW = q => q.X >= wx0 && q.X <= wx1 && q.Y >= wy0 && q.Y <= wy1;
                int nm = 0, ns = 0, nf = 0;
                var ms = MS(db, tr);
                var ids = new List<ObjectId>(); foreach (ObjectId id in ms) ids.Add(id);
                foreach (var id in ids)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < wx0 || x.MinPoint.X > wx1 || x.MaxPoint.Y < wy0 || x.MinPoint.Y > wy1) continue;
                    try
                    {
                        if (x.MinPoint.X >= wx0 && x.MaxPoint.X <= wx1 && x.MinPoint.Y >= wy0 && x.MaxPoint.Y <= wy1)
                        { e.UpgradeOpen(); e.TransformBy(Matrix3d.Displacement(vec)); nm++; continue; }
                        var pc = new Point3dCollection(); e.GetStretchPoints(pc);
                        var idx = new IntegerCollection(); bool all = pc.Count > 0;
                        for (int i = 0; i < pc.Count; i++) { if (inW(pc[i])) idx.Add(i); else all = false; }
                        if (idx.Count == 0) continue;
                        e.UpgradeOpen();
                        if (all) { e.TransformBy(Matrix3d.Displacement(vec)); nm++; }
                        else { e.MoveStretchPointsAt(idx, vec); ns++; }
                    }
                    catch (System.Exception ex) { nf++; log.AppendLine("stretch fail " + e.Handle + " " + e.GetType().Name + " " + ex.Message); }
                }
                log.AppendLine("stretch moved " + nm + " stretched " + ns + " failed " + nf);
            }
            else if (t == "closeother")
            {
                // close (discard, nothing was edited there) every other document opened in THIS instance
                var dmx = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager;
                var lst = new List<Autodesk.AutoCAD.ApplicationServices.Document>();
                foreach (Autodesk.AutoCAD.ApplicationServices.Document dd in dmx) if (dd.Database != db) lst.Add(dd);
                foreach (var dd in lst) { string nm = dd.Name; if (dd.CommandInProgress != "") { log.AppendLine("busy " + nm); continue; } Autodesk.AutoCAD.ApplicationServices.DocumentExtension.CloseAndDiscard(dd); log.AppendLine("closed " + nm); }
            }
            else if (t == "docs")
            {
                foreach (Autodesk.AutoCAD.ApplicationServices.Document dd in Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager)
                    log.AppendLine("DOC " + dd.Name + (dd == Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument ? " *active" : ""));
                log.AppendLine("db " + db.Filename);
            }
            else if (t == "extdump")
            {
                // every model entity (optionally inside win): H|dxf|layer|minx|miny|maxx|maxy|kind-specific|pts
                IList w = Has(m, "win") ? L(m["win"]) : null;
                var sb = new StringBuilder();
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                Func<Point3d, string> fp = q => q.X.ToString("0.###", IC) + "," + q.Y.ToString("0.###", IC);
                foreach (ObjectId oid in ms)
                {
                    var e = tr.GetObject(oid, OpenMode.ForRead) as Entity; if (e == null) continue;
                    string ext = "||||";
                    try
                    {
                        var x = e.GeometricExtents;
                        if (w != null && (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3]))) continue;
                        ext = x.MinPoint.X.ToString("0.#", IC) + "|" + x.MinPoint.Y.ToString("0.#", IC) + "|" + x.MaxPoint.X.ToString("0.#", IC) + "|" + x.MaxPoint.Y.ToString("0.#", IC);
                    }
                    catch { if (w != null) continue; }
                    string info = "";
                    try
                    {
                        if (e is Dimension)
                        {
                            var dd = (Dimension)e;
                            string dp = "";
                            if (e is RotatedDimension) { var r = (RotatedDimension)e; dp = fp(r.XLine1Point) + ";" + fp(r.XLine2Point) + ";" + fp(r.DimLinePoint) + ";rot=" + r.Rotation.ToString("0.####", IC); }
                            else if (e is AlignedDimension) { var r = (AlignedDimension)e; dp = fp(r.XLine1Point) + ";" + fp(r.XLine2Point) + ";" + fp(r.DimLinePoint) + ";al"; }
                            info = "meas=" + dd.Measurement.ToString("0.###", IC) + ";txt=" + (dd.DimensionText ?? "").Replace("|", "/") + ";sty=" + dd.DimensionStyleName + ";lfac=" + dd.Dimlfac.ToString("0.###", IC) + ";dsc=" + dd.Dimscale.ToString("0.###", IC) + ";udt=" + (dd.UsingDefaultTextPosition ? "1" : "0") + ";tp=" + fp(dd.TextPosition).Replace(",", "_") + ";" + dp;
                        }
                        else if (e is MText) info = "txt=" + ((MText)e).Contents.Replace("|", "/").Replace("\n", "\\n") + ";ins=" + fp(((MText)e).Location) + ";h=" + ((MText)e).TextHeight.ToString("0.##", IC);
                        else if (e is DBText) info = "txt=" + ((DBText)e).TextString.Replace("|", "/") + ";ins=" + fp(((DBText)e).Position) + ";h=" + ((DBText)e).Height.ToString("0.##", IC);
                        else if (e is BlockReference) { var br = (BlockReference)e; string bn = br.IsDynamicBlock ? ((BlockTableRecord)tr.GetObject(br.DynamicBlockTableRecord, OpenMode.ForRead)).Name : br.Name; info = "blk=" + bn + ";ins=" + fp(br.Position) + ";rot=" + br.Rotation.ToString("0.####", IC) + ";sx=" + br.ScaleFactors.X.ToString("0.###", IC) + ";sy=" + br.ScaleFactors.Y.ToString("0.###", IC); }
                        else if (e is Polyline) { var pl = (Polyline)e; var pb = new StringBuilder("pl" + (pl.Closed ? "c" : "") + "="); for (int i = 0; i < pl.NumberOfVertices; i++) { var q = pl.GetPoint2dAt(i); pb.Append(q.X.ToString("0.###", IC) + "," + q.Y.ToString("0.###", IC) + "," + pl.GetBulgeAt(i).ToString("0.###", IC) + ";"); } info = pb.ToString() + "cw=" + pl.ConstantWidth.ToString("0.##", IC); }
                        else if (e is Line) info = "ln=" + fp(((Line)e).StartPoint) + ";" + fp(((Line)e).EndPoint);
                        else if (e is Circle) info = "ci=" + fp(((Circle)e).Center) + ";r=" + ((Circle)e).Radius.ToString("0.###", IC);
                        else if (e is Hatch)
                        {
                            var hh = (Hatch)e; var hb = new StringBuilder("hl=");
                            for (int li = 0; li < hh.NumberOfLoops; li++)
                            {
                                var lp = hh.GetLoopAt(li);
                                if (li > 0) hb.Append("#");
                                if (lp.IsPolyline) { foreach (BulgeVertex bv in lp.Polyline) hb.Append(bv.Vertex.X.ToString("0.###", IC) + "," + bv.Vertex.Y.ToString("0.###", IC) + "," + bv.Bulge.ToString("0.####", IC) + ";"); }
                                else foreach (Curve2d c in lp.Curves)
                                {
                                    double b = 0;
                                    var ca = c as CircularArc2d;
                                    if (ca != null) { double sw = ca.EndAngle - ca.StartAngle; if (sw < 0) sw += 2 * Math.PI; b = Math.Tan(sw / 4) * (ca.IsClockWise ? -1 : 1); }
                                    var q = c.StartPoint; hb.Append(q.X.ToString("0.###", IC) + "," + q.Y.ToString("0.###", IC) + "," + b.ToString("0.####", IC) + ";");
                                }
                            }
                            info = hb.ToString() + "|pat=" + hh.PatternName + ";sc=" + hh.PatternScale.ToString("0.###", IC);
                        }
                    }
                    catch (System.Exception ex) { info = "!" + ex.Message; }
                    string sp = "";
                    if (!(e is Polyline) && !(e is Line) && !(e is Hatch))
                    {
                        try { var pc = new Point3dCollection(); e.GetStretchPoints(pc); var pb = new StringBuilder(); foreach (Point3d q in pc) pb.Append(fp(q) + ";"); sp = pb.ToString(); } catch { }
                    }
                    sb.AppendLine(e.Handle + "|" + (oid.ObjectClass.DxfName ?? "") + "|" + e.Layer + "|" + ext + "|" + info.Replace("\r", "").Replace("\n", "\\n") + "|" + sp);
                }
                File.WriteAllText(S(m, "file", ""), sb.ToString(), Encoding.UTF8);
                log.AppendLine("extdump ok");
            }
            else if (t == "clonexf")
            {
                // deep-clone a set of entities together (keeps their mutual SPDS links), displace by d; log old>new
                var ids = new ObjectIdCollection();
                foreach (var h in L(m["hs"])) ids.Add(H(db, h.ToString()));
                var im = new IdMapping();
                db.DeepCloneObjects(ids, SymbolUtilityServices.GetBlockModelSpaceId(db), im, false);
                var dv = L(m["d"]); var vec = new Vector3d(D(dv[0]), D(dv[1]), 0);
                string pre = S(m, "pre", null);
                var sbm = new StringBuilder();
                foreach (IdPair p in im)
                {
                    if (!p.IsCloned || !p.IsPrimary) continue;
                    bool top = false; foreach (ObjectId q in ids) if (q == p.Key) { top = true; break; }
                    if (!top) continue;
                    var e = (Entity)tr.GetObject(p.Value, OpenMode.ForWrite);
                    e.TransformBy(Matrix3d.Displacement(vec));
                    var ke = (Entity)tr.GetObject(p.Key, OpenMode.ForRead);
                    if (pre != null) map[pre + ke.Handle] = e.Handle.ToString();
                    sbm.Append(ke.Handle + ">" + e.Handle + " ");
                }
                log.AppendLine("clonexf " + S(m, "pre", "") + " " + sbm);
            }
            else if (t == "axisinfo")
            {
                IList w = L(m["win"]);
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                var lst = new List<ObjectId>(); foreach (ObjectId oid in ms) if (oid.ObjectClass.DxfName == "SPDSCONSTRUCTIONLINE") lst.Add(oid);
                foreach (var oid in lst)
                {
                    var e = (Entity)tr.GetObject(oid, OpenMode.ForRead);
                    Extents3d x; try { x = e.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    var a = MGet(oid) as McAxisEntity; if (a == null) continue;
                    string vals = "";
                    try { foreach (var mk in a.Axis.Methods.Markers) vals += mk.Value + ","; } catch (System.Exception ex) { vals = "!" + ex.Message; }
                    log.AppendLine("AX " + e.Handle + " " + vals);
                }
            }
            else if (t == "axisval")
            {
                var a = MGet(H(db, S(m, "h", ""))) as McAxisEntity;
                foreach (var mk in a.Axis.Methods.Markers) mk.Value = S(m, "val", "");
                a.DbEntity.Update();
            }
            else if (t == "disassoc")
            {
                // drop dimension associativity (ACAD_DIMASSOC) for dims inside win so later geometry edits do not drag them
                IList w = L(m["win"]); int n = 0;
                var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
                foreach (ObjectId oid in ms)
                {
                    var d = tr.GetObject(oid, OpenMode.ForRead) as Dimension; if (d == null) continue;
                    Extents3d x; try { x = d.GeometricExtents; } catch { continue; }
                    if (x.MaxPoint.X < D(w[0]) || x.MinPoint.X > D(w[2]) || x.MaxPoint.Y < D(w[1]) || x.MinPoint.Y > D(w[3])) continue;
                    if (d.ExtensionDictionary.IsNull) continue;
                    var dic = (DBDictionary)tr.GetObject(d.ExtensionDictionary, OpenMode.ForRead);
                    if (!dic.Contains("ACAD_DIMASSOC")) continue;
                    var aid = dic.GetAt("ACAD_DIMASSOC"); dic.UpgradeOpen(); dic.Remove(aid);
                    try { tr.GetObject(aid, OpenMode.ForWrite).Erase(); } catch { }
                    n++;
                }
                log.AppendLine("disassoc " + n);
            }
            else if (t == "lnset")
            {
                var l = (Line)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                l.StartPoint = P(m["p1"]); l.EndPoint = P(m["p2"]);
            }
            else if (t == "hatchset")
            {
                // replace all loops of a hatch with polyline loops [[x,y,bulge],...]
                var hh = (Hatch)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                hh.Associative = false;
                while (hh.NumberOfLoops > 0) hh.RemoveLoopAt(0);
                int li = 0;
                foreach (var lp in L(m["loops"]))
                {
                    var pc = new Point2dCollection(); var bc = new DoubleCollection();
                    var pts = L(lp);
                    for (int i = 0; i < pts.Count; i++) { var q = L(pts[i]); pc.Add(new Point2d(D(q[0]), D(q[1]))); bc.Add(q.Count > 2 ? D(q[2]) : 0); }
                    if (pc[0].GetDistanceTo(pc[pc.Count - 1]) > 1e-6) { pc.Add(pc[0]); bc.Add(0); }
                    hh.AppendLoop(li == 0 ? HatchLoopTypes.External | HatchLoopTypes.Polyline : HatchLoopTypes.Polyline, pc, bc);
                    li++;
                }
                hh.EvaluateHatch(true);
            }
            else if (t == "dimset2")
            {
                // rotated/aligned dim: xline points, dim line point, optional custom text position
                var e = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite) as Dimension;
                var ad = e as AlignedDimension; var rd = e as RotatedDimension;
                if (ad != null) { ad.XLine1Point = P(m["p1"]); ad.XLine2Point = P(m["p2"]); ad.DimLinePoint = P(m["dl"]); }
                if (rd != null) { rd.XLine1Point = P(m["p1"]); rd.XLine2Point = P(m["p2"]); rd.DimLinePoint = P(m["dl"]); }
                if (Has(m, "tx")) { e.UsingDefaultTextPosition = false; e.TextPosition = P(m["tx"]); }
                e.RecomputeDimensionBlock(true);
            }
            else if (t == "plset")
            {
                var pl = (Polyline)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pts = L(m["p"]); IList bl = Has(m, "b") ? L(m["b"]) : null;
                while (pl.NumberOfVertices > 2) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                for (int i = 0; i < pts.Count; i++)
                {
                    if (i < pl.NumberOfVertices) { pl.SetPointAt(i, P2(pts[i])); pl.SetBulgeAt(i, bl != null ? D(bl[i]) : 0); }
                    else pl.AddVertexAt(i, P2(pts[i]), bl != null ? D(bl[i]) : 0, pl.GetStartWidthAt(0), pl.GetEndWidthAt(0));
                }
                while (pl.NumberOfVertices > pts.Count) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                if (Has(m, "closed")) pl.Closed = (bool)m["closed"];
            }
            else if (t == "cmd")
            {
                Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument.SendStringToExecute(S(m, "s", ""), true, false, false);
            }
            else if (t == "docinfo")
            {
                var dd = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument;
                log.AppendLine("doc " + dd.Name + " readonly=" + dd.IsReadOnly + " filename=" + db.Filename + " ver=" + db.OriginalFileVersion);
            }
            else if (t == "saveas")
            {
                var dd = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument;
                db.SaveAs(S(m, "file", ""), false, DwgVersion.Current, dd.Database.SecurityParameters);
                log.AppendLine("saved as " + S(m, "file", ""));
            }
            else if (t == "save")
            {
                var doc = Autodesk.AutoCAD.ApplicationServices.Core.Application.DocumentManager.MdiActiveDocument;
                db.SaveAs(doc.Name, true, DwgVersion.Current, doc.Database.SecurityParameters);
                log.AppendLine("saved " + doc.Name);
            }
            else if (t == "medialist")
            {
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                var lo = (Layout)tr.GetObject(ld.GetAt(S(m, "layout", "1.1")), OpenMode.ForWrite);
                var psv = PlotSettingsValidator.Current;
                psv.SetPlotConfigurationName(lo, S(m, "dev", "DWG To PDF.pc3"), null);
                psv.RefreshLists(lo);
                foreach (var nm in psv.GetCanonicalMediaNameList(lo)) log.AppendLine("MEDIA	" + nm + "\t" + psv.GetLocaleMediaName(lo, nm));
            }
            else if (t == "vpset")
            {
                // layout -> plot device/media, viewport shows model window win at 1:scale, paper-space origin at 0,0
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                var lo = (Layout)tr.GetObject(ld.GetAt(S(m, "layout", "")), OpenMode.ForWrite);
                var psv = PlotSettingsValidator.Current;
                Action<string, Action> stp = (nm, a) => { try { a(); } catch (System.Exception ex) { log.AppendLine("vpset step " + nm + ": " + ex.Message); } };
                stp("cfg", () => psv.SetPlotConfigurationName(lo, S(m, "dev", "DWG To PDF.pc3"), S(m, "media", "")));
                stp("refresh", () => psv.RefreshLists(lo));
                stp("units", () => psv.SetPlotPaperUnits(lo, PlotPaperUnit.Millimeters));
                stp("rot", () => psv.SetPlotRotation(lo, Has(m, "rot") ? (PlotRotation)Convert.ToInt32(m["rot"]) : PlotRotation.Degrees000));
                stp("type", () => psv.SetPlotType(lo, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout));
                stp("std", () => psv.SetUseStandardScale(lo, true));
                stp("scale", () => psv.SetStdScaleType(lo, StdScaleType.StdScale1To1));
                stp("center", () => psv.SetPlotCentered(lo, false));
                stp("origin", () => psv.SetPlotOrigin(lo, new Point2d(0, 0)));
                stp("ctb", () => psv.SetCurrentStyleSheet(lo, S(m, "ctb", "monochrome.ctb")));
                var w = L(m["win"]); double sc = D(m["scale"]);
                double W = (D(w[2]) - D(w[0])) / sc, Hh = (D(w[3]) - D(w[1])) / sc;
                var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForRead);
                Viewport vp = null;
                foreach (ObjectId id in btr) { var v = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (v != null && v.Number != 1 && vp == null) vp = v; }
                if (vp == null) { log.AppendLine("vpset: no viewport " + lo.LayoutName); return; }
                vp.UpgradeOpen();
                vp.ViewDirection = Vector3d.ZAxis; vp.TwistAngle = 0; vp.ViewTarget = Point3d.Origin;
                vp.CenterPoint = new Point3d(W / 2, Hh / 2, 0); vp.Width = W; vp.Height = Hh;
                vp.ViewCenter = new Point2d((D(w[0]) + D(w[2])) / 2, (D(w[1]) + D(w[3])) / 2);
                vp.ViewHeight = D(w[3]) - D(w[1]);
                vp.CustomScale = 1.0 / sc;
                vp.Locked = true;
                log.AppendLine("vpset " + lo.LayoutName + " " + W.ToString("0") + "x" + Hh.ToString("0") + " " + lo.CanonicalMediaName);
            }
            else if (t == "vplist")
            {
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                foreach (DBDictionaryEntry en in ld)
                {
                    var lo = (Layout)tr.GetObject(en.Value, OpenMode.ForRead);
                    var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForRead);
                    int k = 0;
                    foreach (ObjectId id in btr)
                    {
                        var vp = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (vp == null) continue;
                        log.AppendLine("VPL	" + lo.LayoutName + "\t" + (k++) + "\t" + vp.Handle + "	n" + vp.Number + "	c" + vp.CenterPoint.X.ToString("0", IC) + "," + vp.CenterPoint.Y.ToString("0", IC) + "	w" + vp.Width.ToString("0", IC) + "	h" + vp.Height.ToString("0", IC) + "	vc" + vp.ViewCenter.X.ToString("0", IC) + "," + vp.ViewCenter.Y.ToString("0", IC) + "	vh" + vp.ViewHeight.ToString("0", IC) + "	t" + vp.ViewTarget.X.ToString("0", IC) + "," + vp.ViewTarget.Y.ToString("0", IC) + "	on" + vp.On);
                    }
                }
            }
            else if (t == "vpset2")
            {
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                var lo = (Layout)tr.GetObject(ld.GetAt(S(m, "layout", "")), OpenMode.ForWrite);
                var psv = PlotSettingsValidator.Current;
                Action<string, Action> stp = (nm, a) => { try { a(); } catch (System.Exception ex) { log.AppendLine("vpset2 step " + nm + ": " + ex.Message); } };
                stp("cfg", () => psv.SetPlotConfigurationName(lo, "DWG To PDF.pc3", S(m, "media", "")));
                stp("refresh", () => psv.RefreshLists(lo));
                stp("units", () => psv.SetPlotPaperUnits(lo, PlotPaperUnit.Millimeters));
                stp("rot", () => psv.SetPlotRotation(lo, PlotRotation.Degrees000));
                stp("type", () => psv.SetPlotType(lo, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout));
                stp("std", () => psv.SetUseStandardScale(lo, true));
                stp("scale", () => psv.SetStdScaleType(lo, StdScaleType.StdScale1To1));
                stp("origin", () => psv.SetPlotOrigin(lo, new Point2d(0, 0)));
                stp("ctb", () => psv.SetCurrentStyleSheet(lo, "monochrome.ctb"));
                var w = L(m["win"]); double sc = D(m["scale"]);
                double W = (D(w[2]) - D(w[0])) / sc, Hh = (D(w[3]) - D(w[1])) / sc;
                var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForRead);
                var vps = new List<Viewport>();
                foreach (ObjectId id in btr) { var v = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (v != null) vps.Add(v); }
                if (vps.Count < 2) { log.AppendLine("vpset2: viewports " + vps.Count + " in " + lo.LayoutName); return; }
                var ov = vps[0]; ov.UpgradeOpen();
                ov.ViewDirection = Vector3d.ZAxis; ov.TwistAngle = 0; ov.ViewTarget = Point3d.Origin;
                ov.CenterPoint = new Point3d(W / 2, Hh / 2, 0); ov.Width = W * 1.4; ov.Height = Hh * 1.4;
                ov.ViewCenter = new Point2d(W / 2, Hh / 2); ov.ViewHeight = Hh * 1.4;
                var vp = vps[1]; vp.UpgradeOpen();
                vp.ViewDirection = Vector3d.ZAxis; vp.TwistAngle = 0; vp.ViewTarget = Point3d.Origin;
                vp.CenterPoint = new Point3d(W / 2, Hh / 2, 0); vp.Width = W; vp.Height = Hh;
                vp.ViewCenter = new Point2d((D(w[0]) + D(w[2])) / 2, (D(w[1]) + D(w[3])) / 2);
                vp.ViewHeight = D(w[3]) - D(w[1]);
                vp.CustomScale = 1.0 / sc; vp.Locked = true; stp("on", () => { ov.On = true; vp.On = true; });
                for (int i = 2; i < vps.Count; i++) { var x = vps[i]; x.UpgradeOpen(); x.Erase(); }
                log.AppendLine("vpset2 " + lo.LayoutName + " " + W.ToString("0") + "x" + Hh.ToString("0") + " extra " + (vps.Count - 2));
            }
            else if (t == "blkrename")
            {
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                string a = S(m, "from", ""), b = S(m, "to", "");
                if (!bt.Has(a)) { log.AppendLine("blkrename: no " + a); return; }
                var r = (BlockTableRecord)tr.GetObject(bt[a], OpenMode.ForWrite); r.Name = b;
                log.AppendLine("blkrename " + a + " -> " + b);
            }
            else if (t == "mkblock")
            {
                // new block definition from model entities (cloned, base -> origin), originals erased
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForWrite);
                string nm = S(m, "name", "");
                if (bt.Has(nm)) { log.AppendLine("mkblock: exists " + nm); return; }
                var btr = new BlockTableRecord(); btr.Name = nm; btr.Origin = Point3d.Origin;
                bt.Add(btr); tr.AddNewlyCreatedDBObject(btr, true);
                var xf = Matrix3d.Displacement(Point3d.Origin - P(m["base"]));
                int n = 0;
                foreach (var hh in L(m["h"]))
                {
                    var e = tr.GetObject(H(db, hh.ToString()), OpenMode.ForWrite) as Entity; if (e == null) continue;
                    var c = (Entity)e.Clone(); c.TransformBy(xf); btr.AppendEntity(c); tr.AddNewlyCreatedDBObject(c, true); e.Erase(); n++;
                }
                log.AppendLine("mkblock " + nm + " " + n);
            }
            else if (t == "laydel")
            {
                LayoutManager.Current.DeleteLayout(S(m, "name", ""));
                log.AppendLine("laydel " + S(m, "name", ""));
            }
            else if (t == "laycopy")
            {
                LayoutManager.Current.CopyLayout(S(m, "src", ""), S(m, "dst", ""));
                log.AppendLine("laycopy " + S(m, "src", "") + " -> " + S(m, "dst", ""));
            }
            else if (t == "layouts")
            {
                var ld = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                foreach (DBDictionaryEntry en in ld)
                {
                    var lo = (Layout)tr.GetObject(en.Value, OpenMode.ForRead);
                    var sb = new StringBuilder("LAYOUT\t" + lo.LayoutName + "\ttab" + lo.TabOrder + "\t" + lo.CanonicalMediaName + "\t" + lo.PlotPaperSize.X.ToString("0", IC) + "x" + lo.PlotPaperSize.Y.ToString("0", IC));
                    var btr = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForRead);
                    foreach (ObjectId id in btr)
                    {
                        var vp = tr.GetObject(id, OpenMode.ForRead) as Viewport; if (vp == null || vp.Number == 1) continue;
                        sb.Append("\tVP c" + vp.ViewCenter.X.ToString("0", IC) + "," + vp.ViewCenter.Y.ToString("0", IC) + " h" + vp.ViewHeight.ToString("0", IC) + " sc" + vp.CustomScale.ToString("0.#####", IC) + " t" + vp.ViewTarget.X.ToString("0", IC) + "," + vp.ViewTarget.Y.ToString("0", IC) + " w" + vp.Width.ToString("0", IC) + " hh" + vp.Height.ToString("0", IC));
                    }
                    log.AppendLine(sb.ToString());
                }
            }
        }
    }
}
