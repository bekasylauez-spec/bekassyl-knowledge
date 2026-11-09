using System; using System.Text; using System.Collections.Generic;
using Autodesk.Revit.DB; using Autodesk.Revit.UI;
namespace RB { public class App {
 public static string LiveRun(UIApplication ua, Dictionary<string,string> J) {
  StringBuilder sb = new StringBuilder();
  foreach (Document d in ua.Application.Documents) {
   try { if (d.IsLinked) continue; sb.Append(d.Title + " mod=" + d.IsModified + " path=" + d.PathName);
     if (d.IsModified && d.PathName != "") { d.Save(); sb.Append(" SAVED"); }
     sb.Append("\n"); } catch (Exception ex) { sb.Append(" ERR " + ex.Message + "\n"); } }
  return sb.ToString(); } } }
