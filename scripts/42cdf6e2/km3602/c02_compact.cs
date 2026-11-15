// 3602: Блок 2 / Портики Блок 3 were saved from the background without shrinking (≈105 MB) — re-save compact (SaveAs over itself).
var outLog = @"C:\Users\beka\AppData\Local\Temp\claude\61d567fc0ab17a45\42cdf6e2-99f0-49e0-887d-f2503b7aa50f\scratchpad\km3602\_compact.txt";
var names = new[] { "3602-КМ_Портал Блок 2", "3602-КМ_Портики Блок 3" };
var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> h = null;
h = (s, e) => {
  uiapp.Idling -= h; var L = new System.Text.StringBuilder();
  foreach (Document d in uiapp.Application.Documents) {
    if (!names.Contains(d.Title)) continue;
    var p = d.PathName; long before = new System.IO.FileInfo(p).Length;
    try { d.SaveAs(p, new SaveAsOptions { OverwriteExistingFile = true, Compact = true, MaximumBackups = 1 }); L.AppendLine(d.Title + ": SaveAs compact " + before / 1048576 + " → " + new System.IO.FileInfo(p).Length / 1048576 + " MB"); }
    catch (Exception ex) { L.AppendLine(d.Title + ": SaveAs ERR " + ex.Message); }
  }
  System.IO.File.WriteAllText(outLog, L.ToString(), System.Text.Encoding.UTF8);
};
uiapp.Idling += h; return "queued";
