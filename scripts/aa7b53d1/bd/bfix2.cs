using System;
using Autodesk.AutoCAD.ApplicationServices.Core;
using Autodesk.AutoCAD.DatabaseServices;
using Autodesk.AutoCAD.Runtime;
[assembly: CommandClass(typeof(BFix2.Cmd))]
namespace BFix2 {
public class Cmd {
  [CommandMethod("BFIX2")]
  public void Run() {
    var doc = Application.DocumentManager.MdiActiveDocument; var ed = doc.Editor; var db = doc.Database;
    try {
      using (var tr = db.TransactionManager.StartTransaction()) {
        var id = db.GetObjectId(false, new Handle(Convert.ToInt64("12A2C9", 16)), 0);
        var m = (MText)tr.GetObject(id, OpenMode.ForWrite);
        string s = m.Contents;
        string oldS = "7. Объёмы земляных работ и каменной наброски учтены в СВОР.";
        int i = s.IndexOf(oldS, StringComparison.Ordinal);
        if (i < 0 || s.IndexOf(oldS, i + 1, StringComparison.Ordinal) >= 0) throw new System.Exception("note 7 not found/unique");
        string newS = "7. Технология производства земляных работ и устройства каменной наброски см. Альбом-3 «Гидротехнические решения», объёмы работ и расход материалов учтены в СВОР.";
        m.Contents = s.Substring(0, i) + newS + s.Substring(i + oldS.Length);
        tr.Commit(); ed.WriteMessage("\n[BFIX2] COMMIT");
      }
    } catch (System.Exception ex) { ed.WriteMessage("\n[BFIX2] ABORT " + ex.Message); }
  }
}}
