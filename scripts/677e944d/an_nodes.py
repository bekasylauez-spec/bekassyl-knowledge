import csv, collections, math, sys
D = r"C:\Users\Admin\AppData\Local\Temp\claude\f4c3a78720b97f45\677e944d-f832-4f85-987d-aa96db42c8c8\scratchpad\n"
def rd(n): return list(csv.DictReader(open(D + "\\" + n, encoding="utf-8-sig"), delimiter="\t"))
def pt(s): return tuple(float(v) for v in s.split(","))
def kv(s):
    out = {}
    for it in s.split(";"):
        if "=" in it:
            k, v = it.rsplit("=", 1); out[k] = float(v.rstrip("h"))
    return out
def cls(lab):
    p = lab.split("|")
    return p[1] if p[0] == "M" else "лист"
plates = {}
for r in rd("plates.tsv"):
    i = int(r["idx"]); e = kv(r["edge"]); per = float(r["per"])
    fa_tot, fa = r["faceA"].split(":", 1); fb_tot, fb = r["faceB"].split(":", 1)
    V = [pt(v) for v in r["verts"].split(";")]
    plates[i] = dict(key=r["key"], t=float(r["t"]), area=float(r["area_cm2"]), V=V, per=per, edge=e, fa=kv(fa), fb=kv(fb), tot=max(1, int(fa_tot)), n=pt(r["normal"]))
edges = collections.defaultdict(list)
for r in rd("edges.tsv"):
    edges[int(r["idx"])].append((float(r["x"]), float(r["y"]), float(r["z"]), float(r["w"]), r["labs"]))
bolts = []
for r in rd("bolts.tsv"):
    bolts.append(dict(key=r["key"], a=pt(r["a"]), b=pt(r["b"]), d=float(r["d"]), L=float(r["len"]), p=kv(r["pierced"])))

def dims(p):
    V = p["V"]; n = p["n"]
    # in-plane bbox along longest edge direction
    best = None
    for i in range(len(V)):
        a, b = V[i], V[(i + 1) % len(V)]; L = math.dist(a, b)
        if best is None or L > best[0]: best = (L, a, b)
    L, a, b = best; u = tuple((b[i] - a[i]) / L for i in range(3)); v = (n[1]*u[2]-n[2]*u[1], n[2]*u[0]-n[0]*u[2], n[0]*u[1]-n[1]*u[0])
    us = [sum((q[i]-a[i])*u[i] for i in range(3)) for q in V]; vs = [sum((q[i]-a[i])*v[i] for i in range(3)) for q in V]
    return round(max(us)-min(us)), round(max(vs)-min(vs))

print("=== БОЛТТАР: узел | саны | өзек нені тесіп өтеді")
bk = collections.defaultdict(collections.Counter)
for b in bolts:
    sig = "+".join(sorted(collections.Counter(cls(k) for k in b["p"]).elements())) or "ЕШТЕҢЕ"
    bk[b["key"]][(round(b["d"]), sig, len(b["p"]))] += 1
for k in sorted(bk):
    print(k, sum(bk[k].values()))
    for (d, sig, n), c in sorted(bk[k].items(), key=lambda t: -t[1]): print("    %4d × Ø%d  денелер %d: %s" % (c, d, n, sig))

print("\n=== ЛИСТТЕР: узел | t × a × b | саны | қыр жанасуы % | бет жанасуы % | жанасатын элементтер")
pk = collections.defaultdict(lambda: collections.defaultdict(list))
for i, p in plates.items():
    a, b = dims(p); pk[p["key"]][(round(p["t"]), max(a, b), min(a, b))].append(i)
for k in sorted(pk):
    print(k, sum(len(v) for v in pk[k].values()))
    for (t, a, b), ids in sorted(pk[k].items(), key=lambda t: -len(t[1])):
        es = []; fs = []; who = collections.Counter(); nob = 0
        for i in ids:
            p = plates[i]; sup = p["per"] - p["edge"].get("-", 0)
            es.append(100 * sup / p["per"]); fc = max(sum(p["fa"].values()), sum(p["fb"].values())) / p["tot"] * 100; fs.append(min(100, fc))
            for lab in list(p["edge"]) + list(p["fa"]) + list(p["fb"]):
                if lab != "-": who[cls(lab)] += 1
            if not any(i == int(l.split("|")[1]) for bb in bolts for l in bb["p"] if l.startswith("P|")): nob += 1
        flag = ""
        if min(es) < 1 and min(fs) < 1: flag = "  <-- ЕШТЕҢЕГЕ ТИМЕЙДІ (%d дана)" % sum(1 for x, y in zip(es, fs) if x < 1 and y < 1)
        print("    −%d×%d×%d  %3d дана | қыр %3.0f…%3.0f%% | бет %3.0f…%3.0f%% | болтсыз %d | %s%s" % (t, a, b, len(ids), min(es), max(es), min(fs), max(fs), nob, ", ".join("%s" % w for w, _ in who.most_common(4)), flag))

print("\n=== ФАСОНКА ШЫҒЫСЫ: болттан ең жақын пісірілген қырға дейін (мм), t, шығыс/t")
pb = collections.defaultdict(list)
for bb in bolts:
    mid = tuple((bb["a"][i] + bb["b"][i]) / 2 for i in range(3))
    for l in bb["p"]:
        if l.startswith("P|"): pb[int(l.split("|")[1])].append((mid, bb))
out = collections.defaultdict(list)
for i, lst in pb.items():
    p = plates[i]; sup = [e for e in edges.get(i, [])]
    if not sup: out[(p["key"], round(p["t"]), dims(p))].append((None, i)); continue
    far = 0
    for mid, bb in lst:
        dmin = min(math.dist(mid, e[:3]) for e in sup); far = max(far, dmin)
    # free edge: max distance of any vertex from supported edge
    vfar = max(min(math.dist(v, e[:3]) for e in sup) for v in p["V"])
    suplen = sum(e[3] for e in sup)
    out[(p["key"], round(p["t"]), dims(p))].append((far, i, vfar, suplen, ";".join(sorted(set(cls(x) for e in sup for x in e[4].split(";"))))))
for k in sorted(out):
    v = [x for x in out[k] if x[0] is not None]; nos = len(out[k]) - len(v)
    if not v: print(k, "пісірілген қыры ЖОҚ, тек болт/бет:", nos); continue
    fmax = max(x[0] for x in v); vmax = max(x[2] for x in v); sl = min(x[3] for x in v)
    print("%s −%d %s  %d дана | болтқа дейін шығыс max %.0f (%.0f t) | бұрышқа дейін %.0f | пісірілген қыр ұзындығы min %.0f | тірек: %s%s" % (k[0], k[1], k[2], len(v), fmax, fmax / k[1], vmax, sl, v[0][4], (" | тіреусіз %d" % nos) if nos else ""))
