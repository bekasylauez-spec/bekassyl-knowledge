import ezdxf, collections, sys, re
sys.stdout.reconfigure(encoding='utf-8')
d = ezdxf.readfile("D:/_claude_work/v113/ozh/ozh_km.dxf")
msp = d.modelspace()
O = []
w = O.append
w("# Инвентарь ОЗХ-1 КМ (2).dwg (только чтение; копия D:\\_claude_work\\v113\\ozh\\ozh_km.dwg -> ozh_km.dxf, R2013)\n")
w(f"DXF версия {d.dxfversion}, INSUNITS={d.header.get('$INSUNITS')}, DWGCODEPAGE={d.header.get('$DWGCODEPAGE')}, DIMSCALE={d.header.get('$DIMSCALE')}, LTSCALE={d.header.get('$LTSCALE')}\n")
w("## 1. Layouts\n")
for l in d.layouts:
    vp = list(l.viewports()) if l.name != 'Model' else []
    w(f"- {l.name}: сущностей в layout: {len(l)}; viewports: {len(vp)}")
    if l.name != 'Model':
        try:
            w(f"  - paper_width={l.dxf.paper_width}, paper_height={l.dxf.paper_height}, plot_layout_flags={l.dxf.plot_layout_flags}")
        except Exception as ex:
            w(f"  ({ex})")
w("\nВ DXF оба Layout пустые (нет viewport и нет объектов): весь чертёж лежит в Model, листы = рамки в модели, масштаб 1:100 (рамка 42000x29700 = A3 420x297 при 1:100).\n")
c = collections.Counter(e.dxftype() for e in msp)
w("## 2. Типы объектов (Model)\n")
for k, v in c.most_common():
    w(f"- {k}: {v}")
w(f"\nACAD_PROXY_ENTITY = {c.get('ACAD_PROXY_ENTITY', 0)}; классы DXF: " + ", ".join(sorted({f'{x.dxf.name}({x.dxf.cpp_class_name})' for x in d.classes}))[:1500])
w("\n## 3. Слои\n\n| имя | цвет | lineweight (1/100 мм, -3=default) | linetype | frozen/off | объектов |\n|--|--|--|--|--|--|")
lc = collections.Counter(e.dxf.layer for e in msp)
for l in d.layers:
    w(f"| {l.dxf.name} | {l.dxf.color} | {l.dxf.lineweight} | {l.dxf.linetype} | {l.is_frozen()}/{l.is_off()} | {lc.get(l.dxf.name, 0)} |")
w("\n## 4. Стили текста\n")
for s in d.styles:
    w(f"- {s.dxf.name}: font={s.dxf.font}, bigfont={s.dxf.get('bigfont', '')}, height={s.dxf.height}, width={s.dxf.width}")
w("\n## 5. Размерные стили\n")
dc = collections.Counter(e.dxf.get('dimstyle') for e in msp if e.dxftype() == 'DIMENSION')
for s in d.dimstyles:
    g = lambda k: s.dxf.get(k)
    w(f"- {s.dxf.name}: DIMTXT={g('dimtxt')}, DIMSCALE={g('dimscale')}, DIMLFAC={g('dimlfac')}, DIMTXSTY={g('dimtxsty')}, DIMASZ={g('dimasz')}, DIMEXO={g('dimexo')}, DIMEXE={g('dimexe')}, DIMDLI={g('dimdli')}; использований={dc.get(s.dxf.name, 0)}")
w("\n## 6. Блоки (вставок в Model)\n")
ic = collections.Counter(e.dxf.name for e in msp if e.dxftype() == 'INSERT')
anon = sum(v for k, v in ic.items() if k.startswith('*U'))
w(f"Анонимных *U вставок: {anon} ({sum(1 for k in ic if k.startswith('*U'))} блоков)\n")
for b in d.blocks:
    n = b.name
    if n.startswith('*'):
        continue
    w(f"- {n}: вставок {ic.get(n, 0)}, объектов {len(b)}")

frames = []
for x in (5900, 52900, 99900, 146900, 193900):
    frames.append(dict(x0=x, y0=110030, w=42000, h=29700, src='polyline ' + ('1Штамп' if x < 99900 else '1Планы-рабочие'), stamp=None))
st = []
for e in msp:
    if e.dxftype() == 'INSERT' and e.dxf.name == 'купук':
        st.append((round((e.dxf.insert.x + 248096) / 100) * 100, round((e.dxf.insert.y - 338877.2) / 100) * 100, (round(e.dxf.insert.x), round(e.dxf.insert.y))))
st.sort(key=lambda s: (s[1], s[0]))
for i, (x1, y0, sp) in enumerate(st):
    prev = st[i - 1] if i and st[i - 1][1] == y0 else None
    gap = x1 - prev[0] if prev else None
    if y0 > 100000:
        wd, ht, fmt = (21000, 29700, 'A4 портрет') if ((gap in (26000, None) or gap > 100000) and x1 > 240000 and x1 != 141400 and x1 not in (188400, 235400)) else (42000, 29700, 'A3 альбом')
    else:
        if gap == 89100: wd, ht, fmt = 84100, 59400, 'A1 альбом'
        elif gap == 47000: wd, ht, fmt = 42000, 59400, 'A2 портрет'
        else: wd, ht, fmt = (42000, 59400, 'A2 портрет') if y0 < 50000 else (84100, 59400, 'A1 альбом')
    frames.append(dict(x0=x1 + 500 - wd, y0=y0 - 500, w=wd, h=ht, src=fmt + ' (по штампу купук)', stamp=sp))
ded = []
for f in frames:
    m = [g for g in ded if abs(f['x0'] + f['w'] - g['x0'] - g['w']) < 1500 and abs(f['y0'] - g['y0']) < 1500]
    if m:
        if f['stamp']:
            m[0]['stamp'] = f['stamp']
            m[0]['src'] += ' + stamp'
        continue
    ded.append(f)
frames = sorted(ded, key=lambda f: (-round(f['y0'] / 20000), f['x0']))


def pos(e):
    t = e.dxftype()
    try:
        if t in ('TEXT', 'MTEXT', 'INSERT'):
            return e.dxf.insert
        if t in ('CIRCLE', 'ARC'):
            return e.dxf.center
        if t == 'LINE':
            return (e.dxf.start + e.dxf.end) / 2
        if t == 'DIMENSION':
            return e.dxf.get('text_midpoint') or e.dxf.defpoint
        if t == 'LWPOLYLINE':
            p = list(e.get_points('xy'))
            return ezdxf.math.Vec3(p[0][0], p[0][1])
        if t == 'HATCH' and e.seeds:
            return ezdxf.math.Vec3(e.seeds[0][0], e.seeds[0][1])
    except Exception:
        return None
    return None


ents = []
for e in msp:
    p = pos(e)
    if p is not None:
        ents.append((p.x, p.y, e))
w(f"\n## 7. Рамки листов в Model: найдено {len(frames)}; формат A3 (42000x29700 при 1:100), ярусы по y (низ рамки) 110030 / ~80330 / ~20830\n")
w("Рамка = внешний контур 42000x29700; внутренняя 39500x28700; штамп = блок «купук» (атрибутов нет). 30 прямоугольников 38920x27355 на слое «03 размер» (x 15147…2154210, y≈142205…144960) — не рамки, пустые контуры (внутри объектов нет).\n")
rx = re.compile(r'[МM]\s*1\s*:\s*(\d+)')
sheets = []
for i, f in enumerate(frames, 1):
    X0, Y0, X1, Y1 = f['x0'] - 200, f['y0'] - 200, f['x0'] + f['w'] + 200, f['y0'] + f['h'] + 200
    ins = [e for x, y, e in ents if X0 <= x <= X1 and Y0 <= y <= Y1]
    cc = collections.Counter(e.dxftype() for e in ins)
    texts = []
    for e in ins:
        if e.dxftype() == 'TEXT':
            texts.append((e.dxf.height, e.dxf.text.strip(), e.dxf.insert.x, e.dxf.insert.y))
        elif e.dxftype() == 'MTEXT':
            texts.append((e.dxf.char_height, e.plain_text().strip(), e.dxf.insert.x, e.dxf.insert.y))
    scales = collections.Counter()
    for h, t, _, _ in texts:
        for m in rx.findall(t):
            scales['1:' + m] += 1
    sttx = []
    if f['stamp']:
        sx, sy = f['stamp']
        for h, t, x, y in texts:
            if sx + 229400 <= x <= sx + 250400 and sy - 338900 <= y <= sy - 333300:
                sttx.append((round(x), round(y), t.replace(chr(10), ' / ')))
    f['sttx'] = sttx
    f.update(n=i, cc=cc, texts=texts, scales=scales, ins=ins)
    sheets.append(f)
w("\n## 8. Листы по порядку (ярус сверху вниз, слева направо; номер = порядковый в модели)\n")
w("| # | x0 | y0 | источник рамки | масштабы в тексте | объектов | топ-текст |\n|--|--|--|--|--|--|--|")
for f in sheets:
    top = sorted(f['texts'], key=lambda t: -t[0])
    tt = [t[1].replace('\n', ' / ')[:50] for t in top if len(t[1]) > 3][:2]
    w(f"| {f['n']} | {round(f['x0'])} | {round(f['y0'])} | {f['src']} | {dict(f['scales'])} | {sum(f['cc'].values())} | {tt} |")
w("\n### Тексты внутри штампа (TEXT/MTEXT в области штампа)\n")
for f in sheets:
    w(f"- {f['n']} ({f['src']}): " + " || ".join(t for x, y, t in sorted(f['sttx'], key=lambda q: (-q[1], q[0]))))
w("\n## 9. Ведомость чертежей (лист 1.3 в DWG, из TEXT)\n")
w("""1.1 Общие данные (начало)
1.2 Общие данные (конец)
1.3 (без названия)
2 Спецификация металлопроката
3 Схема расположения баз колонн на отм -0.400
4 Схема расположения колонн
5 К1.1; К1.1з; К1.1зН; К1Нз;
6 К1.2
7 К1.3
8 К1.4
9 К1.5
10 К1.6
11 К2.1; К2.1з;
12 К2.2;
13 К2.3; К2.3з;
14 К2.4; К2.4з;
15 К2.5;
16 К2.6;
17 К2.7;
18 К2.8; К2.8з;
19 К2.9;
20 Схема расположения балок перекрытия и покрытия на отм +4.500
21 Схема расположения балок перекрытия и покрытия на отм +9.000
22 Разрез 1-1; Разрез 2-2
23 Разрез 3-3; Разрез 4-4;
24 Схема расположения балок перекрытия и покрытия на отм +4.500 / Узлы 1..17
25 Схема расположения балок покрытия на отм +9.000 / Узлы 1,2,4,6,7,8
26-42 Узел-1 ... Узел-17; Разрез 1-1 (по одному узлу на лист)
43 Схема расположения профилей усиления оконных и дверных проемов.
""")
w("\n## 10. Содержание каждого листа\n")
for f in sheets:
    w(f"\n### Модель-лист {f['n']}  (x0={round(f['x0'])}, y0={round(f['y0'])}; штамп insert={f['stamp']})")
    w("объекты: " + ", ".join(f"{k}={v}" for k, v in f['cc'].most_common()))
    ib = collections.Counter(e.dxf.name for e in f['ins'] if e.dxftype() == 'INSERT' and not e.dxf.name.startswith('*'))
    w("блоки: " + str(dict(ib.most_common(10))))
    dl = collections.Counter(e.dxf.get('dimstyle') for e in f['ins'] if e.dxftype() == 'DIMENSION')
    w("размерные стили: " + str(dict(dl)))
    tb = [e for e in f['ins'] if e.dxftype() == 'ACAD_TABLE']
    if tb:
        w(f"ACAD_TABLE на листе: {len(tb)}")
    hts = collections.Counter(t[0] for t in f['texts'])
    w("высоты текстов: " + str(dict(sorted(hts.items()))))
    top = sorted(f['texts'], key=lambda t: -t[0])
    seen = set()
    lines = []
    for h, t, x, y in top:
        if t in seen or not t:
            continue
        seen.add(t)
        lines.append((h, t))
    big = [l for l in lines if l[0] >= 250]
    w("крупные тексты (h>=250): " + " ; ".join(f"[{h:g}] " + t.replace('\n', ' / ')[:300] for h, t in big[:40]))
    marks = sorted({t for h, t, x, y in f['texts'] if re.match(r'^(К|Б|СВ|Св|Ф|Р|Пр|РС|ВФ|Ст|Г|Ж|Л|Н|ПН)\d', t)})
    w("марки: " + ", ".join(marks[:80]))
    other = [l for l in lines if l[0] < 250]
    w("прочие тексты (уник.): " + " | ".join(t.replace('\n', ' / ')[:120] for h, t in other[:120]))
w("\n## 11. ACAD_TABLE\n")
for e in msp:
    if e.dxftype() == 'ACAD_TABLE':
        w(f"- insert={e.dxf.insert}, rows={e.dxf.get('n_rows')}, cols={e.dxf.get('n_cols')}")
open("D:/_claude_work/v113/ozh/inventory.md", "w", encoding="utf-8").write("\n".join(O))
print(len(frames))
for f in sheets:
    print(f['n'], round(f['x0']), round(f['y0']), dict(f['scales']), sum(f['cc'].values()))
import json
out = []
for f in sheets:
    out.append(dict(n=f['n'], x0=f['x0'], y0=f['y0'], w=f['w'], h=f['h'], src=f['src'], stamp=f['stamp'], sttx=[t for x, y, t in sorted(f['sttx'], key=lambda q: (-q[1], q[0]))]))
json.dump(out, open("D:/_claude_work/v113/ozh/frames.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
