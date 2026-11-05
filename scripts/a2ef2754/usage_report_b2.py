# Claude Code токен/модель есебі -> HTML график (Chart.js)
# Іске қосу:  python "D:\РАБОЧКА\.claude\usage_report.py" [күн саны, әдепкі 30]
# Нәтиже:     D:\РАБОЧКА\.claude\usage_report.html
import json, os, sys, glob, datetime as dt
from collections import defaultdict

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
ROOT = os.path.expanduser(r"~\.claude\projects")
OUT = "D:/Бекасыл КЖ КМ/_Стандарт_КЖ/usage_report_BEKA-2.html"
# $/1M токен шамамен (input, output, cache_read, cache_write) — салыстыру үшін ғана
PRICE = {"opus": (5, 25, 0.5, 6.25), "sonnet": (3, 15, 0.3, 3.75), "haiku": (1, 5, 0.1, 1.25)}
since = dt.date.today() - dt.timedelta(days=DAYS - 1)

def fam(m):
    m = (m or "").lower()
    for k in PRICE:
        if k in m: return k
    return None

seen = set()
day = defaultdict(lambda: defaultdict(float))      # date -> fam -> $
tok = defaultdict(lambda: defaultdict(int))        # fam -> kind -> tokens
main_vs_sub = defaultdict(float)
for f in glob.glob(os.path.join(ROOT, "**", "*.jsonl"), recursive=True):
    if os.path.getmtime(f) < dt.datetime.combine(since, dt.time()).timestamp(): continue
    is_sub = os.sep + "subagents" + os.sep in f
    with open(f, encoding="utf-8", errors="ignore") as fh:
        for ln in fh:
            if '"usage"' not in ln: continue
            try: r = json.loads(ln)
            except Exception: continue
            msg = r.get("message") or {}
            u, mid = msg.get("usage"), msg.get("id")
            fm = fam(msg.get("model"))
            if not u or not fm or not mid or mid in seen: continue
            seen.add(mid)
            ts = (r.get("timestamp") or "")[:10]
            try: d = dt.date.fromisoformat(ts)
            except Exception: continue
            if d < since: continue
            i, o = u.get("input_tokens", 0), u.get("output_tokens", 0)
            cr, cw = u.get("cache_read_input_tokens", 0), u.get("cache_creation_input_tokens", 0)
            p = PRICE[fm]
            usd = (i * p[0] + o * p[1] + cr * p[2] + cw * p[3]) / 1e6
            day[d.isoformat()][fm] += usd
            for k, v in (("input", i), ("output", o), ("cache_read", cr), ("cache_write", cw)): tok[fm][k] += v
            main_vs_sub["Субагенттер" if is_sub or r.get("isSidechain") else "Негізгі сессия"] += usd

dates = [(since + dt.timedelta(days=k)).isoformat() for k in range(DAYS)]
COL = {"opus": "#7c5cff", "sonnet": "#2fa4a9", "haiku": "#e3a33b"}
ds = [{"label": f, "data": [round(day[x][f], 2) for x in dates], "backgroundColor": COL[f]} for f in PRICE]
tot = {f: sum(day[x][f] for x in dates) for f in PRICE}
rows = "".join(f"<tr><td>{f}</td><td>{tok[f]['output']:,}</td><td>{tok[f]['input']+tok[f]['cache_read']+tok[f]['cache_write']:,}</td><td>${tot[f]:.2f}</td></tr>" for f in PRICE)
html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Claude шығыны</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>:root{{--bg:#fff;--fg:#1d1d1f;--mut:#666;--card:#f5f5f7}}
@media (prefers-color-scheme:dark){{:root{{--bg:#141416;--fg:#eee;--mut:#999;--card:#1f1f23}}}}
body{{background:var(--bg);color:var(--fg);font:15px system-ui,sans-serif;margin:0;padding:16px;max-width:1000px;margin:auto}}
.card{{background:var(--card);border-radius:12px;padding:16px;margin:12px 0}} table{{width:100%;border-collapse:collapse}}
td,th{{padding:6px;text-align:right}} td:first-child,th:first-child{{text-align:left}} small{{color:var(--mut)}}</style></head><body>
<h2>Claude Code — модель бойынша шығын, соңғы {DAYS} күн</h2>
<small>Жаңартылды {dt.datetime.now():%Y-%m-%d %H:%M}. $ — API бағасымен шамамен, тек салыстыру үшін (жазылымда шот басқа).</small>
<div class="card"><canvas id="c1" height="110"></canvas></div>
<div class="card" style="display:flex;gap:16px;flex-wrap:wrap"><div style="flex:1;min-width:260px"><canvas id="c2"></canvas></div>
<div style="flex:2;min-width:260px"><table><tr><th>Модель</th><th>Output токен</th><th>Input+кэш токен</th><th>$</th></tr>{rows}</table></div></div>
<script>
new Chart(c1,{{type:'bar',data:{{labels:{json.dumps([x[5:] for x in dates])},datasets:{json.dumps(ds)}}},options:{{scales:{{x:{{stacked:true}},y:{{stacked:true,title:{{display:true,text:'$'}}}}}}}}}});
new Chart(c2,{{type:'doughnut',data:{{labels:{json.dumps(list(main_vs_sub))},datasets:[{{data:{json.dumps([round(v,2) for v in main_vs_sub.values()])},backgroundColor:['#7c5cff','#2fa4a9']}}]}}}});
</script></body></html>"""
open(OUT, "w", encoding="utf-8").write(html)
print(OUT); print({f: round(v, 2) for f, v in tot.items()}, dict((k, round(v, 2)) for k, v in main_vs_sub.items()))
