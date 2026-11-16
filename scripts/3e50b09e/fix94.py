import io
p = r"D:/_claude_work/RMC/kzh/kz94_tables.cs"
s = io.open(p, encoding="utf-8").read()
bs = chr(92)
n0 = s.count("ГОСТ 34028-2016\n(")
s = s.replace("ГОСТ 34028-2016\n(", "ГОСТ 34028-2016" + bs + "n(")
io.open(p, "w", encoding="utf-8").write(s)
print("fixed", n0)
