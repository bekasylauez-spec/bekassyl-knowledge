# PDF-geometry check (oc.py analogue on the plotted PDF): text/text, line-through-text, text outside frame
import fitz, sys, collections
from shapely.geometry import box, LineString
from shapely.strtree import STRtree
sys.stdout.reconfigure(encoding='utf-8')
d = fitz.open(sys.argv[1]); K = 25.4/72
tot = collections.Counter(); out = []
for pi, p in enumerate(d):
    n = pi+1; W, H = p.rect.width*K, p.rect.height*K
    spans = []
    for bi, b in enumerate(p.get_text('dict')['blocks']):
        for li, l in enumerate(b.get('lines', [])):
            for s in l['spans']:
                t = s['text'].strip()
                if not t: continue
                x0,y0,x1,y1 = [v*K for v in s['bbox']]
                h = y1-y0; w = x1-x0
                # shrink to glyph core (bbox has ascender/descender padding)
                if w >= h: g = box(x0+0.1*h, y0+0.25*h, x1-0.1*h, y1-0.25*h)
                else:      g = box(x0+0.25*w, y0+0.1*w, x1-0.25*w, y1-0.1*w)
                spans.append((bi, li, t, g, (round(x0),round(y0))))
    # text/text
    tt = 0
    for i in range(len(spans)):
        for j in range(i+1, len(spans)):
            a, b = spans[i], spans[j]
            if (a[0], a[1]) == (b[0], b[1]): continue
            if a[3].intersects(b[3]):
                ar = a[3].intersection(b[3]).area
                if ar > 0.05*min(a[3].area, b[3].area):
                    tt += 1; out.append((n, 'TEXT/TEXT', a[2], b[2], a[4]))
    # line through text
    segs = []
    for dr in p.get_drawings():
        for it in dr['items']:
            if it[0] == 'l':
                P, Q = it[1], it[2]; segs.append(LineString([(P.x*K, P.y*K), (Q.x*K, Q.y*K)]))
            elif it[0] == 're':
                r = it[1]
                if r.width*K < 0.3 or r.height*K < 0.3: continue
                for a, b in (((r.x0,r.y0),(r.x1,r.y0)),((r.x1,r.y0),(r.x1,r.y1)),((r.x1,r.y1),(r.x0,r.y1)),((r.x0,r.y1),(r.x0,r.y0))):
                    segs.append(LineString([(a[0]*K,a[1]*K),(b[0]*K,b[1]*K)]))
    tree = STRtree(segs) if segs else None
    lt = 0
    for s in spans:
        if tree is None: break
        hit = [segs[k] for k in tree.query(s[3]) if segs[k].crosses(s[3]) or segs[k].within(s[3])]
        hit = [g for g in hit if g.intersection(s[3]).length > 0.25]
        if hit:
            lt += 1; out.append((n, 'LINE/TEXT', s[2], len(hit), s[4]))
    # outside frame (20/5/5/5 mm), «Формат» is below the frame by template
    of = 0
    for s in spans:
        x0,y0,x1,y1 = s[3].bounds
        if s[2].startswith('Формат') or s[2].startswith('А3') or s[2].startswith('А2') or s[2].startswith('A'): continue
        if x0 < 20 and not (y0 > H-150): pass
        if x0 < 19.5 or y0 < 4.5 or x1 > W-4.5 or y1 > H-4.5:
            if x0 < 19.5 and x1 < 20 and y0 > H-160: continue   # «Инв. № подл.» side column of template
            of += 1; out.append((n, 'OUT/FRAME', s[2], '', s[4]))
    tot[n] = (tt, lt, of)
for o in out: print(*o, sep=' | ')
print('=== per page (text/text, line/text, out-of-frame) ===')
T = [0,0,0]
for n in sorted(tot):
    print(n, tot[n]); T = [T[i]+tot[n][i] for i in range(3)]
print('TOTAL', sum(T), T)
