using System;
using System.IO;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.EditorInput;
using Autodesk.AutoCAD.Geometry;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(StampTool.Cmd))]
namespace StampTool
{
    public class Cmd
    {
        const string SRC = @"C:\Users\Admin\AppData\Local\Temp\claude\D---------\0bad4b28-7a5f-4a0b-a094-8ae0f0d7847d\scratchpad\badam\st.dwg";
        const string SRCBLK = "A$C2bb4aa4d";
        const string NEWBLK = "Штамп Таза Су";
        const string OLDBLK = "крпкер";

        [CommandMethod("NEWSTAMP")]
        public void NewStamp()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            var ed = doc.Editor;
            var db = doc.Database;
            try
            {
                // 1. clone the new stamp definition from the source drawing
                ObjectId srcBtrId;
                using (var side = new Database(false, true))
                {
                    side.ReadDwgFile(SRC, FileOpenMode.OpenForReadAndAllShare, true, "");
                    using (var tr = side.TransactionManager.StartTransaction())
                    {
                        var bt = (BlockTable)tr.GetObject(side.BlockTableId, OpenMode.ForRead);
                        srcBtrId = bt[SRCBLK];
                        tr.Commit();
                    }
                    var ids = new ObjectIdCollection { srcBtrId };
                    var map = new IdMapping();
                    side.WblockCloneObjects(ids, db.BlockTableId, map, DuplicateRecordCloning.Ignore, false);
                    srcBtrId = map[srcBtrId].Value;
                }

                using (var tr = db.TransactionManager.StartTransaction())
                {
                    var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                    var nb = (BlockTableRecord)tr.GetObject(srcBtrId, OpenMode.ForWrite);
                    if (bt.Has(NEWBLK) && bt[NEWBLK] != srcBtrId) throw new System.Exception("block name exists");
                    nb.Name = NEWBLK;

                    // 2. project-specific texts for Бадам
                    ObjectId lay = ObjectId.Null, sty = ObjectId.Null;
                    foreach (ObjectId id in nb)
                    {
                        var mt = tr.GetObject(id, OpenMode.ForWrite) as MText;
                        if (mt == null) continue;
                        lay = mt.LayerId; sty = mt.TextStyleId;
                        if (mt.Contents.Contains("Ликвидация"))
                        {
                            mt.Contents = "\\pxqc;«Реконструкция Бадамского водохранилища\\Pв Туркестанской области»";
                            mt.TextHeight = 2.5;
                            mt.Attachment = AttachmentPoint.MiddleCenter;
                            mt.Location = new Point3d(-60, -17.5, 0);
                            mt.Width = 115;
                        }
                        else if (mt.Contents.Contains("028/26"))
                        {
                            mt.Contents = "\\pxqc;537-23.08.2024-ГР.КЖ";
                            mt.Attachment = AttachmentPoint.MiddleCenter;
                            mt.Location = new Point3d(-60, -5, 0);
                            mt.Width = 115;
                        }
                    }
                    var obj = new MText();
                    obj.SetDatabaseDefaults(db);
                    obj.LayerId = lay; obj.TextStyleId = sty;
                    obj.Contents = "\\pxqc;Реконструкция подводящего канала вд. Бадам";
                    obj.TextHeight = 2.5;
                    obj.Attachment = AttachmentPoint.MiddleCenter;
                    obj.Location = new Point3d(-85, -32.5, 0);
                    obj.Width = 66;
                    nb.AppendEntity(obj); tr.AddNewlyCreatedDBObject(obj, true);

                    // 3. redefine the old stamp block: new stamp scaled x100 at the old frame's top-right corner
                    var ob = (BlockTableRecord)tr.GetObject(bt[OLDBLK], OpenMode.ForWrite);
                    int erased = 0;
                    foreach (ObjectId id in ob)
                    {
                        var e = (Entity)tr.GetObject(id, OpenMode.ForWrite);
                        e.Erase(); erased++;
                    }
                    var tmp = new BlockReference(new Point3d(-982117.93, -806053.23, 0), srcBtrId);
                    tmp.ScaleFactors = new Scale3d(100);
                    var parts = new DBObjectCollection();
                    tmp.Explode(parts);
                    int added = 0;
                    foreach (DBObject o in parts)
                    {
                        var e = (Entity)o;
                        ob.AppendEntity(e); tr.AddNewlyCreatedDBObject(e, true); added++;
                    }
                    tmp.Dispose();
                    tr.Commit();
                    ed.WriteMessage("\nNEWSTAMP: erased {0}, added {1}\n", erased, added);
                }
            }
            catch (System.Exception ex)
            {
                ed.WriteMessage("\nNEWSTAMP ERROR: " + ex + "\n");
            }
        }
    }
}
