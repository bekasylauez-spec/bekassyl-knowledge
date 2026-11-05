            else if (t == "noteh")
            {
                var np = MGet(H(db, S(m, "h", ""))) as McNotePosition;
                if (np != null) { np.FirstLine = S(m, "l1", ""); if (Has(m, "l2")) np.SecondLine = S(m, "l2", ""); np.DbEntity.Update(); }
                var dd = (object)np as IDisposable; if (dd != null) dd.Dispose();
            }
