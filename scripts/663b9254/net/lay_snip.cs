            else if (t == "mklayout")
            {
                // one layout per sheet: name, media (full-bleed), page w/h (mm), model frame win, scale sc -> one locked viewport = whole page at 1:sc
                string name = S(m, "name", "");
                var lm = LayoutManager.Current;
                var dict = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                if (dict.Contains(name)) lm.DeleteLayout(name);
                var lid = lm.CreateLayout(name);
                var lo = (Layout)tr.GetObject(lid, OpenMode.ForWrite);
                var v = Autodesk.AutoCAD.DatabaseServices.PlotSettingsValidator.Current;
                v.SetPlotConfigurationName(lo, "DWG To PDF.pc3", null); v.RefreshLists(lo);
                string media = S(m, "media", ""); string found = null;
                foreach (string mn in v.GetCanonicalMediaNameList(lo)) { if (mn == media || v.GetLocaleMediaName(lo, mn) == media) { found = mn; break; } }
                if (found == null) { log.AppendLine("media? " + media); return; }
                v.SetPlotConfigurationName(lo, "DWG To PDF.pc3", found);
                v.SetPlotPaperUnits(lo, PlotPaperUnit.Millimeters);
                v.SetPlotRotation(lo, PlotRotation.Degrees000);
                v.SetPlotType(lo, Autodesk.AutoCAD.DatabaseServices.PlotType.Layout);
                v.SetUseStandardScale(lo, true); v.SetStdScaleType(lo, StdScaleType.StdScale1To1);
                v.SetPlotOrigin(lo, new Point2d(0, 0)); v.SetPlotCentered(lo, false);
                v.SetCurrentStyleSheet(lo, "monochrome.ctb");
                lm.CurrentLayout = name;
                var ps = (BlockTableRecord)tr.GetObject(lo.BlockTableRecordId, OpenMode.ForWrite);
                foreach (ObjectId id in ps) { var en = tr.GetObject(id, OpenMode.ForWrite) as Viewport; if (en != null && en.Number != 1) en.Erase(); }
                double W = D(m["w"]), Hh = D(m["h"]), sc = D(m["sc"]); var w = L(m["win"]);
                var vp = new Viewport();
                ps.AppendEntity(vp); tr.AddNewlyCreatedDBObject(vp, true);
                vp.CenterPoint = new Point3d(W / 2, Hh / 2, 0); vp.Width = W; vp.Height = Hh;
                vp.ViewTarget = Point3d.Origin; vp.ViewDirection = Vector3d.ZAxis;
                vp.ViewCenter = new Point2d((D(w[0]) + D(w[2])) / 2, (D(w[1]) + D(w[3])) / 2);
                vp.CustomScale = 1.0 / sc;
                vp.Layer = "0";
                vp.On = true; vp.Locked = true;
                log.AppendLine("mklayout " + name + " " + found + " 1:" + sc);
            }
            else if (t == "plotlayout")
            {
                // plot a layout 1:1 (its page setup) to PDF
                string name = S(m, "name", "");
                Autodesk.AutoCAD.ApplicationServices.Core.Application.SetSystemVariable("BACKGROUNDPLOT", 0);
                var lm = LayoutManager.Current; lm.CurrentLayout = name;
                var lo = (Layout)tr.GetObject(lm.GetLayoutId(name), OpenMode.ForRead);
                var pi = new Autodesk.AutoCAD.PlottingServices.PlotInfo(); pi.Layout = lo.ObjectId;
                var piv = new Autodesk.AutoCAD.PlottingServices.PlotInfoValidator(); piv.MediaMatchingPolicy = Autodesk.AutoCAD.PlottingServices.MatchingPolicy.MatchEnabled; piv.Validate(pi);
                using (var pe = Autodesk.AutoCAD.PlottingServices.PlotFactory.CreatePublishEngine())
                {
                    var ppi = new Autodesk.AutoCAD.PlottingServices.PlotPageInfo();
                    pe.BeginPlot(null, null);
                    pe.BeginDocument(pi, "doc", null, 1, true, S(m, "file", ""));
                    pe.BeginPage(ppi, pi, true, null); pe.BeginGenerateGraphics(null); pe.EndGenerateGraphics(null);
                    pe.EndPage(null); pe.EndDocument(null); pe.EndPlot(null);
                }
                log.AppendLine("plotlayout " + name + " -> " + S(m, "file", ""));
            }
            else if (t == "dellayout")
            {
                var lm = LayoutManager.Current; string name = S(m, "name", "");
                var dict = (DBDictionary)tr.GetObject(db.LayoutDictionaryId, OpenMode.ForRead);
                if (dict.Contains(name)) { lm.CurrentLayout = "Model"; lm.DeleteLayout(name); log.AppendLine("dellayout " + name); }
            }
            else if (t == "tomodel")
            {
                LayoutManager.Current.CurrentLayout = "Model";
            }
