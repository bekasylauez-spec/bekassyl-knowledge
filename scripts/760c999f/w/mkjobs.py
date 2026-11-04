# plot jobs: one per sheet number (regex) -> smallest SPDS frame proxy around it
import ezdxf, json, os, re, sys
from ezdxf import bbox
dxf, pat, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
d = ezdxf.readfile(dxf); ms = d.modelspace()
pr = []
for e in ms.query("ACAD_PROXY_ENTITY"):
    try:
        b = bbox.extents([e])
    except Exception:
        continue
    if b.has_data and (b.extmax.y - b.extmin.y) > 10000:
        fmt = ''
        try:
            for v in e.virtual_entities():
                if v.dxftype() == 'TEXT' and re.fullmatch(r'A\d(x\d)?', v.dxf.text.strip()): fmt = v.dxf.text.strip()
        except Exception: pass
        pr.append((b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y, fmt))
nums = {}
for e in ms.query("TEXT MTEXT"):
    t = (e.dxf.text if e.dxftype() == "TEXT" else e.plain_text()).strip()
    if re.fullmatch(pat, t):
        nums.setdefault(t, []).append((e.dxf.insert.x, e.dxf.insert.y))
papers = [(420, 297, "ISO_full_bleed_A3_(420.00_x_297.00_MM)"), (297, 420, "ISO_full_bleed_A3_(297.00_x_420.00_MM)"),
          (594, 420, "ISO_full_bleed_A2_(594.00_x_420.00_MM)"), (420, 594, "ISO_full_bleed_A2_(420.00_x_594.00_MM)"),
          (707, 500, "ISO_full_bleed_B2_(707.00_x_500.00_MM)"), (1000, 707, "ISO_full_bleed_B1_(1000.00_x_707.00_MM)"),
          (707, 1000, "ISO_full_bleed_B1_(707.00_x_1000.00_MM)"), (1414, 1000, "ISO_full_bleed_B0_(1414.00_x_1000.00_MM)")]
J = []
for n, pts in sorted(nums.items(), key=lambda k: [int(v) for v in k[0].split(".")]):
    best = None
    for (x, y) in pts:
        c = [f for f in pr if f[0] < x < f[2] and f[1] < y < f[3]]
        c.sort(key=lambda f: (f[2] - f[0]) * (f[3] - f[1]))
        if c and (best is None or c[0][1] < best[1]):
            best = c[0]
    if not best:
        print("no frame", n); continue
    f = best; W_, H = f[2] - f[0], f[3] - f[1]
    sc = None
    A = {0: (841, 1189), 1: (594, 841), 2: (420, 594), 3: (297, 420), 4: (210, 297)}
    fm = re.fullmatch(r'A(\d)(?:x(\d))?', f[4] or '')
    if fm:
        sh, lg = A[int(fm.group(1))]
        if fm.group(2): sh, lg = lg, sh * int(fm.group(2))   # A3x3 = 420 x 891
        pw, ph = (lg, sh) if W_ >= H else (sh, lg)
        s1, s2 = W_ / pw, H / ph
        if abs(s1 - s2) < 0.02 * s1 and abs(s1 - round(s1)) < 0.02 * s1: sc = round(s1)
        else: print("format mismatch", n, f[4], round(W_), round(H))
    if sc is None:
        for s in (100, 75, 50, 25):
            w, h = W_ / s, H / s
            if any(abs(h - v) < 1 for v in (297, 420, 594, 841)) and w > 200:
                sc = s; break
    w, h = round(W_ / sc), round(H / sc)
    m = [p for p in papers if p[0] >= w and p[1] >= h][0][2]
    J.append({"n": n, "x0": f[0], "y0": f[1], "x1": f[2], "y1": f[3], "sc": float(sc), "w": w, "h": h, "media": m, "out": os.path.abspath(os.path.join(outdir, n + ".pdf"))})
    print(n, [round(v) for v in f[:4]], f[4], sc, w, h)
json.dump(J, open(os.path.join(outdir, "plotc.json"), "w", encoding="utf-8"), ensure_ascii=False)
