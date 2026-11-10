var app = document.Application; var uiapp = new UIApplication(app);
string log = @"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\_save.txt";
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r = "";
  try { foreach (Document d in app.Documents) { if (d.IsFamilyDocument || string.IsNullOrEmpty(d.PathName)) continue; bool m = d.IsModified; if (m) d.Save(); r += d.Title + " modified=" + m + " saved\n"; } }
  catch (Exception ex) { r += "ERR " + ex.Message; }
  System.IO.File.WriteAllText(log, r, System.Text.Encoding.UTF8); };
uiapp.Idling += hnd;
return "queued";
