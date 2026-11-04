import ezdxf, json, sys, os
from ezdxf import bbox
S = sys.argv[1]
doc = ezdxf.readfile(os.path.join(S, 'km', 'live.dxf')); msp = doc.modelspace()
def grab(x0, y0, x1, y1):
    hs = []
    for e in msp:
        try: b = bbox.extents([e])
        except Exception: continue
        if not b.has_data: continue
        cx, cy = (b.extmin.x + b.extmax.x) / 2, (b.extmin.y + b.extmax.y) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1: hs.append(e.dxf.handle)
    return hs
plan = grab(2680000, -1650000, 2700000, -1636000)
sect = grab(2675000, -1676000, 2700000, -1652000)
ops = [{"t": "maprst"}]
# лист 3: стереть план аналога, оставить рамку/штамп/примечания и заголовок 671828
ops.append({"t": "eraseregion", "win": [2617113, -1747651, 2656913, -1726551], "keep": ["671828"]})
pb, pt = [2692455, -1642499], [2637000, -1739500]
for h in plan: ops.append({"t": "clone", "h": h, "base": pb, "to": pt, "tag": "P3:" + h})
ops.append({"t": "move", "h": ["671828"], "d": [2637000 - 2625378, -1733000 - (-1727912)]})
ops.append({"t": "settext", "h": "671828", "s": "{\LПлан лестницы}"})
ops.append({"t": "settext", "h": "671846", "s": "План лестницы"})
# лист 4: стереть разрезы аналога, оставить заголовок 671CC3
ops.append({"t": "eraseregion", "win": [2659113, -1747651, 2686613, -1714251], "keep": ["671CC3"]})
sb, st = [2689204, -1663446], [2672863, -1733000]
for h in sect: ops.append({"t": "clone", "h": h, "base": sb, "to": st, "tag": "S4:" + h})
ops.append({"t": "move", "h": ["671CC3"], "d": [2672863 - 2665113, -1720800 - (-1718624)]})
ops.append({"t": "settext", "h": "671CBE", "s": "Разрез 1 - 1"})
ops.append({"t": "regen"})
json.dump(ops, open(os.path.join(S, 'net', 'o_34.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(plan), len(sect), len(ops))
