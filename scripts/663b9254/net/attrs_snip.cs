            else if (t == "attrs")
            {
                // block reference attributes: log tag=value; "set": {tag: value}
                var br = (BlockReference)tr.GetObject(H(db, S(m, "h", "")), OpenMode.ForWrite);
                var sets = Has(m, "set") ? (Dictionary<string, object>)m["set"] : null;
                foreach (ObjectId aid in br.AttributeCollection)
                {
                    var ar = (AttributeReference)tr.GetObject(aid, OpenMode.ForWrite);
                    if (sets != null && sets.ContainsKey(ar.Tag)) ar.TextString = sets[ar.Tag].ToString();
                    log.AppendLine("ATTR\t" + ar.Tag + "\t" + ar.TextString);
                }
                log.AppendLine("blk " + br.Name);
            }
            else if (t == "blkitems")
            {
                // entities inside a block definition: type, handle, layer, text; "set": {handle: text}; "erase": [handles]
                var bt = (BlockTable)tr.GetObject(db.BlockTableId, OpenMode.ForRead);
                var btr = (BlockTableRecord)tr.GetObject(bt[S(m, "name", "")], OpenMode.ForRead);
                var sets = Has(m, "set") ? (Dictionary<string, object>)m["set"] : null;
                var er = new HashSet<string>(); if (Has(m, "erase")) foreach (var q in L(m["erase"])) er.Add(q.ToString().ToUpper());
                foreach (ObjectId id in btr)
                {
                    var e = (Entity)tr.GetObject(id, OpenMode.ForRead);
                    string hs = e.Handle.ToString().ToUpper();
                    if (er.Contains(hs)) { e.UpgradeOpen(); e.Erase(); log.AppendLine("erased " + hs); continue; }
                    string txt = "";
                    if (e is DBText) txt = ((DBText)e).TextString; else if (e is MText) txt = ((MText)e).Contents;
                    else if (e is AttributeDefinition) txt = "ATTDEF " + ((AttributeDefinition)e).Tag + "=" + ((AttributeDefinition)e).TextString;
                    else if (e is BlockReference) txt = "INS " + ((BlockReference)e).Name;
                    if (sets != null && sets.ContainsKey(hs))
                    {
                        e.UpgradeOpen();
                        if (e is MText) ((MText)e).Contents = sets[hs].ToString(); else if (e is DBText) ((DBText)e).TextString = sets[hs].ToString();
                        txt = "SET " + sets[hs];
                    }
                    Extents3d x; string ex = ""; try { x = e.GeometricExtents; ex = x.MinPoint.X.ToString("0", IC) + "," + x.MinPoint.Y.ToString("0", IC) + "," + x.MaxPoint.X.ToString("0", IC) + "," + x.MaxPoint.Y.ToString("0", IC); } catch { }
                    log.AppendLine("BI\t" + id.ObjectClass.DxfName + "\t" + hs + "\t" + e.Layer + "\t" + ex + "\t" + txt.Replace("\n", " "));
                }
            }
