var d = document; if (d == null || !d.PathName.EndsWith("РМЦ-КМ.rvt")) return "ABORT " + (d == null ? "null" : d.PathName);
d.Save(); return "saved " + d.PathName + " IsModified=" + d.IsModified;
