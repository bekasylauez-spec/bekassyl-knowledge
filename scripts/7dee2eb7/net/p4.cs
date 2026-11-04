using System;
using System.IO;
using System.Text;
using System.Collections;
using System.Collections.Generic;
using System.Web.Script.Serialization;
using Autodesk.AutoCAD.Runtime;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;

[assembly: CommandClass(typeof(P4.Cmds))]
namespace P4
{
    // Plain-AutoCAD drawing ops for accoreconsole. Ops: %TEMP%\p4_ops.json, log: %TEMP%\p4_log.txt, tag map %TEMP%\p4_map.json
    public class Cmds
    {
        static StringBuilder log = new StringBuilder();
        static string tmp = Environment.GetEnvironmentVariable("TEMP");
        static System.Globalization.CultureInfo IC = System.Globalization.CultureInfo.InvariantCulture;
        static Dictionary<string, string> map = new Dictionary<string, string>();
        static string mapFile = Path.Combine(tmp, "p4_map.json");
        static double D(object o) { return Convert.ToDouble(o, IC); }
        static string S(Dictionary<string, object> m, string k, string def) { object v; return m.TryGetValue(k, out v) && v != null ? v.ToString() : def; }
        static bool Has(Dictionary<string, object> m, string k) { object v; return m.TryGetValue(k, out v) && v != null; }
        static IList L(object o) { return (IList)o; }
        static Point3d P(object o) { var a = L(o); return new Point3d(D(a[0]), D(a[1]), 0); }
        static Point2d P2(object o) { var a = L(o); return new Point2d(D(a[0]), D(a[1])); }

        static ObjectId H(Database db, string h)
        {
            if (map.ContainsKey(h)) h = map[h];
            ObjectId id;
            if (db.TryGetObjectId(new Handle(Convert.ToInt64(h, 16)), out id)) return id;
            throw new System.Exception("no handle " + h);
        }
        static void Tag(Dictionary<string, object> m, Entity e) { string t = S(m, "tag", null); if (t != null) map[t] = e.Handle.ToString(); }

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
                if (ltt.Has(ln)) e.Linetype = ln; else log.AppendLine("no ltype " + ln);
            }
            if (Has(m, "ltscale")) e.LinetypeScale = D(m["ltscale"]);
        }

        static Extents3d? Ext(Entity e) { try { return e.GeometricExtents; } catch { return null; } }
        static bool Inside(Extents3d x, double[] w) { return x.MinPoint.X >= w[0] && x.MinPoint.Y >= w[1] && x.MaxPoint.X <= w[2] && x.MaxPoint.Y <= w[3]; }
        static bool Cross(Extents3d x, double[] w) { return !(x.MaxPoint.X < w[0] || x.MaxPoint.Y < w[1] || x.MinPoint.X > w[2] || x.MinPoint.Y > w[3]); }
        static double[] W(object o) { var a = L(o); return new double[] { D(a[0]), D(a[1]), D(a[2]), D(a[3]) }; }

        static List<ObjectId> InWin(Database db, Transaction tr, double[] w, bool cross)
        {
            var res = new List<ObjectId>();
            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForRead);
            foreach (ObjectId id in ms)
            {
                var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                var x = Ext(e); if (x == null) continue;
                if (cross ? Cross(x.Value, w) : Inside(x.Value, w)) res.Add(id);
            }
            return res;
        }

        static string Txt(Entity e)
        {
            if (e is DBText) return ((DBText)e).TextString;
            if (e is MText) return ((MText)e).Contents;
            if (e is MLeader) { var ml = (MLeader)e; try { return ml.MText.Contents; } catch { return ""; } }
            if (e is Dimension) return ((Dimension)e).DimensionText;
            return "";
        }

        [CommandMethod("P4RUN")]
        public static void Run()
        {
            var db = HostApplicationServices.WorkingDatabase;
            log.Clear();
            if (File.Exists(mapFile)) { try { map = new JavaScriptSerializer().Deserialize<Dictionary<string, string>>(File.ReadAllText(mapFile)); } catch { } }
            var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
            var ops = js.Deserialize<ArrayList>(File.ReadAllText(Path.Combine(tmp, "p4_ops.json"), Encoding.UTF8));
            int n = 0, bad = 0;
            foreach (Dictionary<string, object> m in ops)
            {
                n++;
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    try { Op(db, tr, m); tr.Commit(); }
                    catch (System.Exception ex) { bad++; log.AppendLine("ERR op#" + n + " " + S(m, "t", "") + " " + S(m, "tag", "") + ": " + ex.Message); }
                }
            }
            log.AppendLine("done " + n + " ops, " + bad + " errors");
            File.WriteAllText(mapFile, new JavaScriptSerializer().Serialize(map));
            File.WriteAllText(Path.Combine(tmp, "p4_log.txt"), log.ToString(), Encoding.UTF8);
        }

        static void Op(Database db, Transaction tr, Dictionary<string, object> m)
        {
            string t = S(m, "t", "");
            var ms = (BlockTableRecord)tr.GetObject(SymbolUtilityServices.GetBlockModelSpaceId(db), OpenMode.ForWrite);
            if (t == "copywin")
            {
                // clone everything fully inside win (or crossing if cross) displaced by d
                var w = W(m["win"]); var d = P(m["d"]);
                var ids = InWin(db, tr, w, Has(m, "cross") && (bool)m["cross"]);
                if (Has(m, "skip")) { var sk = new HashSet<string>(); foreach (var h in L(m["skip"])) sk.Add(H(db, h.ToString()).Handle.ToString()); ids.RemoveAll(i => sk.Contains(i.Handle.ToString())); }
                var col = new ObjectIdCollection(ids.ToArray());
                var mp = new IdMapping();
                db.DeepCloneObjects(col, ms.ObjectId, mp, false);
                var mx = Matrix3d.Displacement(d.GetAsVector());
                int c = 0;
                foreach (IdPair p in mp)
                {
                    if (!p.IsPrimary || !p.IsCloned) continue;
                    var e = tr.GetObject(p.Value, OpenMode.ForWrite) as Entity; if (e == null) continue;
                    if (e.OwnerId != ms.ObjectId) continue;
                    e.TransformBy(mx); c++;
                }
                log.AppendLine("copywin " + S(m, "tag", "") + " " + c);
            }
            else if (t == "clone")
            {
                var src = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead) as Entity;
                var col = new ObjectIdCollection(new ObjectId[] { src.ObjectId });
                var mp = new IdMapping(); db.DeepCloneObjects(col, ms.ObjectId, mp, false);
                var e = (Entity)tr.GetObject(mp[src.ObjectId].Value, OpenMode.ForWrite);
                if (Has(m, "d")) e.TransformBy(Matrix3d.Displacement(P(m["d"]).GetAsVector()));
                if (Has(m, "to")) { var bp = Has(m, "from") ? P(m["from"]) : Pos(e); e.TransformBy(Matrix3d.Displacement(P(m["to"]) - bp)); }
                if (Has(m, "rot")) e.TransformBy(Matrix3d.Rotation(D(m["rot"]) * Math.PI / 180, Vector3d.ZAxis, Has(m, "to") ? P(m["to"]) : Pos(e)));
                Edit(db, tr, e, m);
                Tag(m, e);
            }
            else if (t == "edit")
            {
                var e = (Entity)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                if (Has(m, "d")) e.TransformBy(Matrix3d.Displacement(P(m["d"]).GetAsVector()));
                Edit(db, tr, e, m);
            }
            else if (t == "erasewin")
            {
                var w = W(m["win"]);
                var ids = InWin(db, tr, w, Has(m, "cross") && (bool)m["cross"]);
                var keep = new HashSet<string>(); if (Has(m, "keep")) foreach (var h in L(m["keep"])) keep.Add(h.ToString());
                string lay = S(m, "layer", null);
                int c = 0;
                foreach (var id in ids)
                {
                    if (keep.Contains(id.Handle.ToString())) continue;
                    var e = (Entity)tr.GetObject(id, OpenMode.ForWrite);
                    if (lay != null && e.Layer != lay) continue;
                    e.Erase(); c++;
                }
                log.AppendLine("erasewin " + c);
            }
            else if (t == "erase")
            {
                foreach (var h in L(m["hs"])) { try { tr.GetObject(H(db, h.ToString()), OpenMode.ForWrite).Erase(); } catch (System.Exception ex) { log.AppendLine("erase " + h + " " + ex.Message); } }
            }
            else if (t == "pl")
            {
                var pl = new Polyline(); var pts = L(m["pts"]);
                for (int i = 0; i < pts.Count; i++) pl.AddVertexAt(i, P2(pts[i]), 0, 0, 0);
                pl.Closed = Has(m, "closed") && (bool)m["closed"];
                if (Has(m, "w")) pl.ConstantWidth = D(m["w"]);
                Props(pl, m, db, tr); ms.AppendEntity(pl); tr.AddNewlyCreatedDBObject(pl, true); Tag(m, pl);
            }
            else if (t == "line")
            {
                var a = L(m["p"]); var ln = new Line(new Point3d(D(a[0]), D(a[1]), 0), new Point3d(D(a[2]), D(a[3]), 0));
                Props(ln, m, db, tr); ms.AppendEntity(ln); tr.AddNewlyCreatedDBObject(ln, true); Tag(m, ln);
            }
            else if (t == "circle")
            {
                var c = new Circle(P(m["c"]), Vector3d.ZAxis, D(m["r"]));
                Props(c, m, db, tr); ms.AppendEntity(c); tr.AddNewlyCreatedDBObject(c, true); Tag(m, c);
            }
            else if (t == "hatch")
            {
                var h = new Hatch(); ms.AppendEntity(h); tr.AddNewlyCreatedDBObject(h, true);
                Props(h, m, db, tr);
                if (Has(m, "scale")) h.PatternScale = D(m["scale"]);
                if (Has(m, "ang")) h.PatternAngle = D(m["ang"]) * Math.PI / 180;
                h.SetHatchPattern(HatchPatternType.PreDefined, S(m, "pat", "SOLID"));
                foreach (var loop in L(m["loops"]))
                {
                    var pc = new Point2dCollection(); var bc = new DoubleCollection();
                    foreach (var p in L(loop)) { pc.Add(P2(p)); bc.Add(0); }
                    pc.Add(pc[0]); bc.Add(0);
                    h.AppendLoop(HatchLoopTypes.Polyline, pc, bc);
                }
                h.EvaluateHatch(true); Tag(m, h);
            }
            else if (t == "mleader")
            {
                // clone a template mleader; set text, arrow point, landing location
                var src = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead) as MLeader;
                var col = new ObjectIdCollection(new ObjectId[] { src.ObjectId });
                var mp = new IdMapping(); db.DeepCloneObjects(col, ms.ObjectId, mp, false);
                var ml = (MLeader)tr.GetObject(mp[src.ObjectId].Value, OpenMode.ForWrite);
                if (Has(m, "d")) ml.TransformBy(Matrix3d.Displacement(P(m["d"]).GetAsVector()));
                if (Has(m, "text")) { var mt = ml.MText; mt.Contents = S(m, "text", ""); ml.MText = mt; }
                if (Has(m, "arrow")) { foreach (int ld in ml.GetLeaderIndexes()) { var lls = ml.GetLeaderLineIndexes(ld); ml.SetFirstVertex((int)lls[0], P(m["arrow"])); break; } }
                if (Has(m, "land")) { ml.SetLastVertex(0, P(m["land"])); }
                if (Has(m, "dogdir")) ml.SetDogleg(0, new Vector3d(D(m["dogdir"]), 0, 0));
                if (Has(m, "textloc")) ml.TextLocation = P(m["textloc"]);
                Props(ml, m, db, tr); Tag(m, ml);
            }
            else if (t == "ml")
            {
                // new multileader from a template's style: text at textloc, one leader line per arrow point
                var src = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead) as MLeader;
                var col = new ObjectIdCollection(new ObjectId[] { src.ObjectId });
                var mp = new IdMapping(); db.DeepCloneObjects(col, ms.ObjectId, mp, false);
                var ml = (MLeader)tr.GetObject(mp[src.ObjectId].Value, OpenMode.ForWrite);
                foreach (int li in ml.GetLeaderIndexes()) ml.RemoveLeader(li);
                var mt = ml.MText; mt.Contents = S(m, "text", ""); ml.MText = mt;
                var tl = P(m["textloc"]);
                double dir = Has(m, "dir") ? D(m["dir"]) : -1;
                int ldr = ml.AddLeader();
                ml.SetDogleg(ldr, new Vector3d(dir, 0, 0));
                foreach (var a in L(m["arrows"]))
                {
                    int ln = ml.AddLeaderLine(ldr);
                    ml.AddFirstVertex(ln, P(a));
                }
                ml.TextLocation = tl;
                Props(ml, m, db, tr); Tag(m, ml);
            }
            else if (t == "mlx")
            {
                // analog multileader moved so its text sits at textloc; its leader lines (in order) get the given arrow points
                var src = tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForRead) as MLeader;
                var col = new ObjectIdCollection(new ObjectId[] { src.ObjectId });
                var mp = new IdMapping(); db.DeepCloneObjects(col, ms.ObjectId, mp, false);
                var ml = (MLeader)tr.GetObject(mp[src.ObjectId].Value, OpenMode.ForWrite);
                ml.TransformBy(Matrix3d.Displacement(P(m["textloc"]) - ml.TextLocation));
                if (Has(m, "text")) { var mt = ml.MText; mt.Contents = S(m, "text", ""); ml.MText = mt; }
                var arr = L(m["arrows"]); int i = 0;
                foreach (int ld in ml.GetLeaderIndexes())
                    foreach (int li in ml.GetLeaderLineIndexes(ld)) { ml.SetFirstVertex(li, P(arr[Math.Min(i, arr.Count - 1)])); i++; }
                Props(ml, m, db, tr); Tag(m, ml);
            }
            else if (t == "movewin")
            {
                var w = W(m["win"]); var d = P(m["d"]); var mx = Matrix3d.Displacement(d.GetAsVector());
                var keep = new HashSet<string>(); if (Has(m, "skip")) foreach (var h in L(m["skip"])) keep.Add(H(db, h.ToString()).Handle.ToString());
                int c = 0;
                foreach (var id in InWin(db, tr, w, false)) { if (keep.Contains(id.Handle.ToString())) continue; ((Entity)tr.GetObject(id, OpenMode.ForWrite)).TransformBy(mx); c++; }
                log.AppendLine("movewin " + c);
            }
            else if (t == "repl")
            {
                var w = W(m["win"]); int c = 0;
                var pairs = L(m["pairs"]);
                foreach (var id in InWin(db, tr, w, true))
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity;
                    Func<string, string> R = s => { foreach (var p in pairs) { var a = L(p); s = s.Replace(a[0].ToString(), a[1].ToString()); } return s; };
                    if (e is DBText) { var x = (DBText)e; var n = R(x.TextString); if (n != x.TextString) { x.UpgradeOpen(); x.TextString = n; c++; } }
                    else if (e is MText) { var x = (MText)e; var n = R(x.Contents); if (n != x.Contents) { x.UpgradeOpen(); x.Contents = n; c++; } }
                    else if (e is MLeader) { var x = (MLeader)e; try { var mt = x.MText; var n = R(mt.Contents); if (n != mt.Contents) { x.UpgradeOpen(); mt.Contents = n; x.MText = mt; c++; } } catch { } }
                    else if (e is Dimension) { var x = (Dimension)e; var n = R(x.DimensionText); if (n != x.DimensionText) { x.UpgradeOpen(); x.DimensionText = n; c++; } }
                    else if (e is Table)
                    {
                        var tb = (Table)e;
                        for (int r = 0; r < tb.Rows.Count; r++) for (int cc = 0; cc < tb.Columns.Count; cc++)
                        {
                            string s; try { s = tb.Cells[r, cc].TextString; } catch { continue; }
                            var n = R(s); if (n != s) { tb.UpgradeOpen(); tb.Cells[r, cc].TextString = n; c++; }
                        }
                    }
                    else if (e is BlockReference && !(e is Table))
                    {
                        foreach (ObjectId aid in ((BlockReference)e).AttributeCollection)
                        { var a = (AttributeReference)tr.GetObject(aid, OpenMode.ForRead); var n = R(a.TextString); if (n != a.TextString) { a.UpgradeOpen(); a.TextString = n; c++; } }
                    }
                }
                log.AppendLine("repl " + S(m, "tag", "") + " " + c);
            }
            else if (t == "inscol")
            {
                var tb = (Table)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                int at = Convert.ToInt32(m["at"]);
                tb.InsertColumnsAndInherit(at, Convert.ToInt32(m["from"]), Convert.ToInt32(S(m, "n", "1")));
                tb.GenerateLayout();
            }
            else if (t == "fields2text")
            {
                // freeze every field in model space (texts, mtexts, attributes, table cells) to its current value
                int c = 0;
                foreach (ObjectId id in ms)
                {
                    var e = tr.GetObject(id, OpenMode.ForRead) as Entity; if (e == null) continue;
                    try
                    {
                        if (e is MText && e.HasFields) { e.UpgradeOpen(); ((MText)e).ConvertFieldToText(); c++; }
                        else if (e is DBText && e.HasFields) { e.UpgradeOpen(); var s0 = ((DBText)e).TextString; e.RemoveField(); ((DBText)e).TextString = s0; c++; }
                        else if (e is BlockReference && !(e is Table))
                            foreach (ObjectId aid in ((BlockReference)e).AttributeCollection)
                            { var a = (AttributeReference)tr.GetObject(aid, OpenMode.ForRead); if (a.HasFields) { a.UpgradeOpen(); var s0 = a.TextString; a.RemoveField(); a.TextString = s0; c++; } }
                        else if (e.HasFields) { e.UpgradeOpen(); e.RemoveField(); c++; }
                    }
                    catch (System.Exception ex) { log.AppendLine("f2t " + e.Handle + " " + ex.Message); }
                }
                log.AppendLine("fields2text " + c);
            }
            else if (t == "tdump")
            {
                var sb = new StringBuilder();
                foreach (var hh in L(m["hs"]))
                {
                    var tb = tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead) as Table;
                    sb.AppendLine("TABLE " + hh + " rows=" + tb.Rows.Count + " cols=" + tb.Columns.Count + " pos=" + tb.Position + " ext=" + Ext(tb));
                    for (int r = 0; r < tb.Rows.Count; r++)
                    {
                        var row = new List<string>();
                        for (int c = 0; c < tb.Columns.Count; c++) { string s; try { s = tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone); } catch { s = "?"; } row.Add(s.Replace("\n", " ")); }
                        sb.AppendLine(r + "\t" + string.Join(" | ", row));
                    }
                }
                File.WriteAllText(S(m, "out", Path.Combine(tmp, "p4_tdump.txt")), sb.ToString(), Encoding.UTF8);
            }
            else if (t == "dyninfo")
            {
                foreach (var hh in L(m["hs"]))
                {
                    var br = tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead) as BlockReference;
                    var btr = (BlockTableRecord)tr.GetObject(br.DynamicBlockTableRecord, OpenMode.ForRead);
                    log.AppendLine("BR " + hh + " dyn=" + btr.Name + " ext=" + Ext(br));
                    if (br.IsDynamicBlock) foreach (DynamicBlockReferenceProperty p in br.DynamicBlockReferencePropertyCollection)
                    {
                        var sb = new StringBuilder(); foreach (var v in p.GetAllowedValues()) sb.Append(v + ";");
                        log.AppendLine("  " + p.PropertyName + " = " + p.Value + " [" + sb + "] ro=" + p.ReadOnly);
                    }
                    foreach (ObjectId aid in br.AttributeCollection) { var a = (AttributeReference)tr.GetObject(aid, OpenMode.ForRead); log.AppendLine("  ATT " + a.Tag + "=" + a.TextString); }
                }
            }
            else if (t == "list")
            {
                var w = W(m["win"]);
                var sb = new StringBuilder();
                foreach (var id in InWin(db, tr, w, true))
                {
                    var e = (Entity)tr.GetObject(id, OpenMode.ForRead); var x = Ext(e).Value;
                    string extra = "";
                    if (e is BlockReference) { var br = (BlockReference)e; var bt = (BlockTableRecord)tr.GetObject(br.DynamicBlockTableRecord, OpenMode.ForRead); extra = bt.Name; }
                    if (e is Dimension) extra = ((Dimension)e).DimensionStyleName + "|" + ((Dimension)e).Measurement.ToString("0", IC);
                    sb.AppendLine(string.Join("\t", new string[] { e.Handle.ToString(), e.GetType().Name, e.Layer, x.MinPoint.X.ToString("0", IC), x.MinPoint.Y.ToString("0", IC), x.MaxPoint.X.ToString("0", IC), x.MaxPoint.Y.ToString("0", IC), extra, Txt(e).Replace("\t", " ").Replace("\r", " ").Replace("\n", " ") }));
                }
                File.WriteAllText(S(m, "out", Path.Combine(tmp, "p4_list.txt")), sb.ToString(), Encoding.UTF8);
            }
            else if (t == "save")
            {
                db.SaveAs(S(m, "path", ""), DwgVersion.Current);
                log.AppendLine("saved " + S(m, "path", ""));
            }
            else throw new System.Exception("unknown op " + t);
        }

        static Point3d Pos(Entity e)
        {
            if (e is BlockReference) return ((BlockReference)e).Position;
            if (e is DBText) return ((DBText)e).Position;
            if (e is MText) return ((MText)e).Location;
            var x = Ext(e); return x.HasValue ? x.Value.MinPoint : Point3d.Origin;
        }

        static void Edit(Database db, Transaction tr, Entity e, Dictionary<string, object> m)
        {
            Props(e, m, db, tr);
            if (e is DBText)
            {
                var tx = (DBText)e;
                if (Has(m, "text")) tx.TextString = S(m, "text", "");
                if (Has(m, "pos")) { var p = P(m["pos"]); if (tx.HorizontalMode == TextHorizontalMode.TextLeft && tx.VerticalMode == TextVerticalMode.TextBase) tx.Position = p; else tx.AlignmentPoint = p; }
                if (Has(m, "rotd")) tx.Rotation = D(m["rotd"]) * Math.PI / 180;
                if (Has(m, "height")) tx.Height = D(m["height"]);
                if (Has(m, "hmode")) { tx.HorizontalMode = (TextHorizontalMode)Convert.ToInt32(m["hmode"]); tx.VerticalMode = (TextVerticalMode)Convert.ToInt32(S(m, "vmode", "0")); if (Has(m, "pos")) tx.AlignmentPoint = P(m["pos"]); tx.AdjustAlignment(db); }
            }
            else if (e is MText)
            {
                var mt = (MText)e;
                if (Has(m, "text")) mt.Contents = S(m, "text", "");
                if (Has(m, "pos")) mt.Location = P(m["pos"]);
                if (Has(m, "width")) mt.Width = D(m["width"]);
                if (Has(m, "rotd")) mt.Rotation = D(m["rotd"]) * Math.PI / 180;
                if (Has(m, "height")) mt.TextHeight = D(m["height"]);
            }
            else if (e is RotatedDimension)
            {
                var d = (RotatedDimension)e;
                if (Has(m, "p1")) d.XLine1Point = P(m["p1"]);
                if (Has(m, "p2")) d.XLine2Point = P(m["p2"]);
                if (Has(m, "dl")) d.DimLinePoint = P(m["dl"]);
                if (Has(m, "rotd")) d.Rotation = D(m["rotd"]) * Math.PI / 180;
                if (Has(m, "text")) d.DimensionText = S(m, "text", "");
                if (Has(m, "tpos")) { d.TextPosition = P(m["tpos"]); }
                else if (Has(m, "p1")) d.UsingDefaultTextPosition = true;
                d.RecomputeDimensionBlock(true);
            }
            else if (e is AlignedDimension)
            {
                var d = (AlignedDimension)e;
                if (Has(m, "p1")) d.XLine1Point = P(m["p1"]);
                if (Has(m, "p2")) d.XLine2Point = P(m["p2"]);
                if (Has(m, "dl")) d.DimLinePoint = P(m["dl"]);
                if (Has(m, "text")) d.DimensionText = S(m, "text", "");
                d.RecomputeDimensionBlock(true);
            }
            else if (e is BlockReference && !(e is Table))
            {
                var br = (BlockReference)e;
                if (Has(m, "dyn") && br.IsDynamicBlock)
                {
                    var dv = (Dictionary<string, object>)m["dyn"];
                    foreach (DynamicBlockReferenceProperty p in br.DynamicBlockReferencePropertyCollection)
                        if (dv.ContainsKey(p.PropertyName))
                        {
                            object v = dv[p.PropertyName];
                            try { if (p.Value is double) p.Value = D(v); else if (p.Value is short) p.Value = Convert.ToInt16(v); else if (p.Value is int) p.Value = Convert.ToInt32(v); else p.Value = v.ToString(); }
                            catch (System.Exception ex) { log.AppendLine("dyn " + p.PropertyName + " " + ex.Message); }
                        }
                }
                if (Has(m, "att"))
                {
                    var av = (Dictionary<string, object>)m["att"];
                    foreach (ObjectId aid in br.AttributeCollection)
                    {
                        var a = (AttributeReference)tr.GetObject(aid, OpenMode.ForWrite);
                        if (av.ContainsKey(a.Tag)) a.TextString = av[a.Tag].ToString();
                    }
                }
                if (Has(m, "sx")) br.ScaleFactors = new Scale3d(D(m["sx"]), D(S(m, "sy", S(m, "sx", "1"))), 1);
            }
            else if (e is Polyline && Has(m, "pts"))
            {
                var pl = (Polyline)e; var pts = L(m["pts"]);
                while (pl.NumberOfVertices > pts.Count) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                for (int i = 0; i < pts.Count; i++) { if (i < pl.NumberOfVertices) pl.SetPointAt(i, P2(pts[i])); else pl.AddVertexAt(i, P2(pts[i]), 0, pl.GetStartWidthAt(0), pl.GetEndWidthAt(0)); }
            }
            else if (e is Line && Has(m, "p"))
            {
                var a = L(m["p"]); var ln = (Line)e; ln.StartPoint = new Point3d(D(a[0]), D(a[1]), 0); ln.EndPoint = new Point3d(D(a[2]), D(a[3]), 0);
            }
            else if (e is Table && Has(m, "cells"))
            {
                var tb = (Table)e;
                if (Has(m, "delrows")) { var a = L(m["delrows"]); tb.DeleteRows(Convert.ToInt32(a[0]), Convert.ToInt32(a[1])); }
                if (Has(m, "insrows")) { var a = L(m["insrows"]); tb.InsertRowsAndInherit(Convert.ToInt32(a[0]), Convert.ToInt32(a[1]), Convert.ToInt32(a[2])); }
                foreach (var c in L(m["cells"])) { var a = L(c); tb.Cells[Convert.ToInt32(a[0]), Convert.ToInt32(a[1])].TextString = a[2].ToString(); }
                if (Has(m, "rowh")) { var a = L(m["rowh"]); for (int r = Convert.ToInt32(a[0]); r < tb.Rows.Count; r++) tb.Rows[r].Height = D(a[1]); }
                tb.GenerateLayout();
            }
        }
    }
}
