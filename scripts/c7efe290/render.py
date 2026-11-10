import ezdxf, json, re, sys, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
from ezdxf import bbox
sys.stdout.reconfigure(encoding='utf-8')
d = ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp = d.modelspace()
fr = json.load(open("D:/_claude_work/v113/ozh/frames.json", encoding='utf-8'))
cache = bbox.Cache()
boxes = []
for e in msp:
    try:
        b = bbox.extents([e], cache=cache)
    except Exception:
        continue
    if b.has_data:
        boxes.append((b.extmin.x, b.extmin.y, b.extmax.x, b.extmax.y, e))
print('boxes', len(boxes), flush=True)
os.makedirs("D:/_claude_work/v113/ozh/png", exist_ok=True)
log = []
for f in fr:
    n = f['n']
    st = f['sttx']
    if n == 1: nm = 'Титульный лист'; no = '0'
    elif n == 2: nm = 'Лист утверждения'; no = '0'
    else:
        no = st[0] if st else '?'
        nm = ' '.join(st[1:]) if len(st) > 1 else ''
        if no.startswith('М') and len(st) > 2:
            no = st[1]; nm = ' '.join(st[2:])
    nm = re.sub(r'[\/:*?"<>|]', '_', nm)[:70].strip().replace(' ', '_')
    X0, Y0, X1, Y1 = f['x0'] - 300, f['y0'] - 300, f['x0'] + f['w'] + 300, f['y0'] + f['h'] + 300
    ids = {id(e) for (a, b, c, dd, e) in boxes if a <= X1 and c >= X0 and b <= Y1 and dd >= Y0}
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(d)
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK, lineweight_scaling=1.0)
    be = MatplotlibBackend(ax)
    try:
        Frontend(ctx, be, config=cfg).draw_layout(msp, finalize=True, filter_func=lambda e: id(e) in ids)
    except Exception as ex:
        print('ERR', n, ex)
    ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect('equal'); ax.axis('off')
    long = max(f['w'], f['h']) + 600
    sc = 3600 / long
    fig.set_size_inches((f['w'] + 600) * sc / 100, (f['h'] + 600) * sc / 100)
    fn = f"D:/_claude_work/v113/ozh/png/{n:02d}_{no}_{nm}.png"
    fig.savefig(fn, dpi=100, facecolor='white')
    plt.close(fig)
    print(fn, len(ids), flush=True)
