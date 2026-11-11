var uiapp = new Autodesk.Revit.UI.UIApplication(document.Application);
string outp = System.IO.Path.Combine(System.Environment.GetEnvironmentVariable("LOCALAPPDATA"), "rvjob", "idle_test.txt");
System.IO.Directory.CreateDirectory(System.IO.Path.GetDirectoryName(outp));
if (System.IO.File.Exists(outp)) System.IO.File.Delete(outp);
EventHandler<Autodesk.Revit.UI.Events.IdlingEventArgs> h = null;
h = (s, e) => { uiapp.Idling -= h; System.IO.File.WriteAllText(outp, "idle ok " + DateTime.Now.ToString("HH:mm:ss.fff")); };
uiapp.Idling += h;
return "queued " + DateTime.Now.ToString("HH:mm:ss.fff");
