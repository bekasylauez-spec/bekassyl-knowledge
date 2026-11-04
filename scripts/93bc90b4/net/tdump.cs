using System;
using System.IO;
using System.Text;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(TDump.Cmd))]

namespace TDump
{
    // Dumps texts (incl. inside blocks), dimensions and layouts of the current drawing to TDUMP_OUT
    public class Cmd
    {
        StreamWriter w;
        [CommandMethod("TDUMP")]
        public void Run()
        {
            var db = Application.DocumentManager.MdiActiveDocument.Database;
            w = new StreamWriter(Environment.GetEnvironmentVariable("TDUMP_OUT"), false, Encoding.UTF8);
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var dict = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                    foreach (DBDictionaryEntry de in dict)
                    {
                        var lay = (Layout)tr.GetObject(de.Value, OpenMode.ForRead);
                        var btr = (BlockTableRecord)tr.GetObject(lay.BlockTableRecordId, OpenMode.ForRead);
                        w.WriteLine("#LAYOUT\t" + lay.LayoutName + "\t" + lay.TabOrder);
                        foreach (ObjectId id in btr) Dump(tr, id, Matrix3d.Identity, lay.LayoutName, 0);
                    }
                    tr.Commit();
                }
            }
            catch (System.Exception ex) { w.WriteLine("#ERR " + ex); }
            w.Close();
        }

        void Dump(Transaction tr, ObjectId id, Matrix3d xf, string where, int depth)
        {
            var o = tr.GetObject(id, OpenMode.ForRead);
            if (o is DBText)
            {
                var t = (DBText)o; var p = t.Position.TransformBy(xf);
                w.WriteLine(string.Format("T\t{0}\t{1:F0}\t{2:F0}\t{3:F1}\t{4}\t{5}", where, p.X, p.Y, t.Height, t.Layer, t.TextString.Replace("\t", " ")));
            }
            else if (o is MText)
            {
                var t = (MText)o; var p = t.Location.TransformBy(xf);
                w.WriteLine(string.Format("M\t{0}\t{1:F0}\t{2:F0}\t{3:F1}\t{4}\t{5}", where, p.X, p.Y, t.TextHeight, t.Layer, t.Text.Replace("\t", " ").Replace("\r", " ").Replace("\n", " | ")));
            }
            else if (o is Dimension)
            {
                var d = (Dimension)o; var p = d.TextPosition.TransformBy(xf);
                string s = d.DimensionText; double m = 0; try { m = d.Measurement; } catch { }
                w.WriteLine(string.Format("D\t{0}\t{1:F0}\t{2:F0}\t{3:F1}\t{4}\t{5}", where, p.X, p.Y, m, d.Layer, s));
            }
            else if (o is BlockReference && depth < 6)
            {
                var br = (BlockReference)o;
                var btr = (BlockTableRecord)tr.GetObject(br.BlockTableRecord, OpenMode.ForRead);
                if (btr.IsFromExternalReference || btr.IsLayout) return;
                var nx = xf * br.BlockTransform;
                foreach (ObjectId a in br.AttributeCollection)
                {
                    var at = (AttributeReference)tr.GetObject(a, OpenMode.ForRead);
                    var p = at.Position.TransformBy(xf);
                    w.WriteLine(string.Format("A\t{0}\t{1:F0}\t{2:F0}\t{3:F1}\t{4}\t{5}={6}", where, p.X, p.Y, at.Height, br.Name, at.Tag, at.TextString));
                }
                foreach (ObjectId c in btr) Dump(tr, c, nx, where, depth + 1);
            }
        }
    }
}
