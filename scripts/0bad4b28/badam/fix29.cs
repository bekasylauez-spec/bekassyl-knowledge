using System;
using System.Collections.Generic;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;

[assembly: CommandClass(typeof(Fix29.Cmd))]
namespace Fix29
{
    public class Cmd
    {
        const string OLD = "План траба под плотины";
        const string NEW = "План трапа под плотиной";

        static ObjectId ById(Database db, string h)
        {
            return db.GetObjectId(false, new Handle(Convert.ToInt64(h, 16)), 0);
        }

        [CommandMethod("FIX29")]
        public void Run()
        {
            var doc = Application.DocumentManager.MdiActiveDocument;
            var ed = doc.Editor;
            var db = doc.Database;
            try
            {
                using (var tr = db.TransactionManager.StartTransaction())
                {
                    foreach (var h in new[] { "13E01E", "13E189" })
                    {
                        var mt = (MText)tr.GetObject(ById(db, h), OpenMode.ForWrite);
                        mt.Contents = mt.Contents.Replace(OLD, NEW);
                        ed.WriteMessage("\nMTEXT {0}: {1}", h, mt.Contents);
                    }

                    var tb = (Table)tr.GetObject(ById(db, "1285AD"), OpenMode.ForWrite);
                    var before = new Dictionary<string, string>();
                    for (int r = 0; r < tb.Rows.Count; r++)
                        for (int c = 0; c < tb.Columns.Count; c++)
                            before[r + "," + c] = tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone);
                    int hits = 0;
                    for (int r = 0; r < tb.Rows.Count; r++)
                        for (int c = 0; c < tb.Columns.Count; c++)
                        {
                            var s = before[r + "," + c];
                            if (s.Contains(OLD))
                            {
                                tb.Cells[r, c].TextString = s.Replace(OLD, NEW);
                                hits++;
                                ed.WriteMessage("\nCELL {0},{1}: {2}", r, c, tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone));
                            }
                        }
                    tb.GenerateLayout();
                    int changed = 0;
                    for (int r = 0; r < tb.Rows.Count; r++)
                        for (int c = 0; c < tb.Columns.Count; c++)
                        {
                            var s = tb.Cells[r, c].GetTextString(FormatOption.FormatOptionNone);
                            if (s != before[r + "," + c] && !s.Contains(NEW)) { changed++; ed.WriteMessage("\nUNEXPECTED {0},{1}: '{2}' -> '{3}'", r, c, before[r + "," + c], s); }
                        }
                    tr.Commit();
                    ed.WriteMessage("\nFIX29: table hits {0}, other changes {1}\n", hits, changed);
                }
            }
            catch (System.Exception ex)
            {
                ed.WriteMessage("\nFIX29 ERROR: " + ex + "\n");
            }
        }
    }
}
