# handle-level diff of two DXFs (old = 4-storey, new = 5-storey (испр)): what was removed/added/modified
import ezdxf, sys, collections
from ezdxf import bbox

def load(f):
    d = ezdxf.readfile(f)
    return d, {e.dxf.handle: e for e in d.modelspace()}

def txt(e):
    if e.dxftype() == "MTEXT":
        return e.plain_text().replace("\n", " ")
    if e.dxftype() == "TEXT":
        return e.dxf.text
    return ""

def attrs(e):
    a = dict(e.dxf.all_existing_dxf_attribs())
    a.pop("handle", None); a.pop("owner", None)
    return a

def box(e, cache):
    try:
        b = bbox.extents([e], cache=cache)
        return (round(b.extmin.x), round(b.extmin.y), round(b.extmax.x), round(b.extmax.y)) if b.has_data else None
    except Exception:
        return None

old, A = load(sys.argv[1])
new, B = load(sys.argv[2])
cache = bbox.Cache()
rem = [h for h in A if h not in B]
add = [h for h in B if h not in A]
print("old", len(A), "new", len(B), "removed", len(rem), "added", len(add))
print("removed types", collections.Counter(A[h].dxftype() for h in rem))
print("added types", collections.Counter(B[h].dxftype() for h in add))
mods = collections.Counter()
modlist = []
for h in A:
    if h not in B:
        continue
    a, b = A[h], B[h]
    if a.dxftype() == "ACAD_PROXY_ENTITY":
        continue
    da, db = attrs(a), attrs(b)
    ch = {k for k in set(da) | set(db) if str(da.get(k)) != str(db.get(k))}
    if txt(a) != txt(b):
        ch.add("TEXT")
    if a.dxftype() == "LWPOLYLINE" and list(a.get_points()) != list(b.get_points()):
        ch.add("pts")
    if ch:
        mods[(a.dxftype(), tuple(sorted(ch)))] += 1
        modlist.append((h, a, b, ch))
print("modified (non-proxy):")
for k, v in mods.most_common(40):
    print("  ", v, k)
mode = sys.argv[3] if len(sys.argv) > 3 else ""
if "t" in mode:
    for h, a, b, ch in modlist:
        if "TEXT" in ch:
            print("T", h, repr(txt(a)[:90]), "->", repr(txt(b)[:90]))
if "a" in mode:
    for h, a, b, ch in modlist:
        if "TEXT" not in ch:
            da, db = attrs(a), attrs(b)
            print("A", h, a.dxftype(), {k: (str(da.get(k))[:30], str(db.get(k))[:30]) for k in ch if k != "pts"}, "pts" if "pts" in ch else "")
if "r" in mode:
    for h in rem:
        print("R", h, A[h].dxftype(), A[h].dxf.layer, box(A[h], cache), repr(txt(A[h])[:80]))
if "n" in mode:
    for h in add:
        print("N", h, B[h].dxftype(), B[h].dxf.layer, box(B[h], cache), repr(txt(B[h])[:80]))
