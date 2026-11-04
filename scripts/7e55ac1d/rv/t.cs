using System;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
namespace T { public class A : IExternalApplication {
 public Result OnStartup(UIControlledApplication a){ return Result.Succeeded; }
 public Result OnShutdown(UIControlledApplication a){ return Result.Succeeded; } } }
