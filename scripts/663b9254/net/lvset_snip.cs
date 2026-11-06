            else if (t == "levelset")
            {
                // SPDS level mark: replace whatever value text it stores ([+-]d,ddd or d.ddd, 6 chars) with "value" (same length)
                var id = H(db, S(m, "h", ""));
                var mo = MGet(id);
                var dbe = mo.GetType().GetProperty("DbEntity").GetValue(mo, null) as McDbEntity;
                byte[] b = dbe.SerializeToBytes();
                string nv = S(m, "value", "");
                var rx = new System.Text.RegularExpressions.Regex(@"[+\-]\d[.,]\d{3}");
                int cnt = 0;
                foreach (var enc in new Encoding[] { Encoding.GetEncoding(28591), Encoding.Unicode })
                {
                    string sd = enc.GetString(b);
                    var mm = rx.Matches(sd);
                    var rb = enc.GetBytes(nv);
                    foreach (System.Text.RegularExpressions.Match q in mm)
                    {
                        if (q.Value.Length != nv.Length) continue;
                        int off = enc.GetByteCount(sd.Substring(0, q.Index));
                        if (enc == Encoding.Unicode && (off % 2) != 0) continue;
                        Array.Copy(rb, 0, b, off, rb.Length); cnt++;
                    }
                }
                var dd = mo as IDisposable; if (dd != null) dd.Dispose();
                if (cnt == 0) { log.AppendLine("levelset: no value text"); return; }
                var ne = McDbEntity.DeserializeNewFromBytes(b);
                McObjectManager.Add2Document(ne); ne.Update();
                tr.GetObject(id, OpenMode.ForWrite).Erase();
                var nid = new ObjectId(ne.ID.ToOldIdPtr());
                string tg = S(m, "tag", null);
                if (tg != null) { var ee = tr.GetObject(nid, OpenMode.ForRead) as Entity; if (ee != null) map[tg] = ee.Handle.ToString(); }
                log.AppendLine("levelset " + cnt + " " + nv);
            }
