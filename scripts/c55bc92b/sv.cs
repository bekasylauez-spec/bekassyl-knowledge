var d = document; bool was = d.IsModified; d.Save(); return "saved, was modified=" + was + ", now=" + d.IsModified + " " + d.PathName;
}
static int Dummy() { return 0;
