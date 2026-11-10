var uiapp = new UIApplication(document.Application);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> hnd = null;
hnd = (s, e) => { uiapp.Idling -= hnd; string r; try { uiapp.ActiveUIDocument.Document.Save(); r = "saved"; } catch (Exception ex) { r = "ERR " + ex.Message; }
  System.IO.File.WriteAllText(@"C:\Users\beka\AppData\Local\Temp\claude\208a25b89c99599c\b9d48af9-f7a2-4623-89d1-541fa9dfc459\scratchpad\save.txt", r); };
uiapp.Idling += hnd; return "queued";
