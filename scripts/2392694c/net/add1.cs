            else if (t == "plset")
            {
                var pl = (Polyline)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var pts = L(m["p"]);
                while (pl.NumberOfVertices > 1) pl.RemoveVertexAt(pl.NumberOfVertices - 1);
                pl.SetPointAt(0, P2(pts[0]));
                for (int i = 1; i < pts.Count; i++) pl.AddVertexAt(i, P2(pts[i]), 0, 0, 0);
                if (Has(m, "closed")) pl.Closed = (bool)m["closed"];
                Props(pl, m, db, tr);
                log.AppendLine("plset " + pl.Handle + " " + pts.Count);
            }
            else if (t == "einfo")
            {
                foreach (var hh in L(m["h"]))
                {
                    var e = (Entity)tr.GetObject(H(db, hh.ToString()), OpenMode.ForRead);
                    string extra = "";
                    var pl = e as Polyline; if (pl != null) { extra = " cw=" + pl.ConstantWidth + " closed=" + pl.Closed + " n=" + pl.NumberOfVertices; for (int i = 0; i < pl.NumberOfVertices && i < 8; i++) extra += " " + pl.GetPoint2dAt(i).X.ToString("0") + "," + pl.GetPoint2dAt(i).Y.ToString("0"); }
                    var br = e as BlockReference; if (br != null) extra = " blk=" + br.Name + " sc=" + br.ScaleFactors.X;
                    var h = e as Hatch; if (h != null) extra = " pat=" + h.PatternName + " sc=" + h.PatternScale + " ang=" + h.PatternAngle;
                    var mt = e as MText; if (mt != null) extra = " txt=" + mt.Contents + " h=" + mt.TextHeight;
                    log.AppendLine("einfo " + e.Handle + " " + e.GetType().Name + " lay=" + e.Layer + " lw=" + e.LineWeight + " c=" + e.Color + " lt=" + e.Linetype + " lts=" + e.LinetypeScale + extra);
                }
            }
