# -*- coding: utf-8 -*-
"""2-сурет: спутниктік жақын көрініс — учаске, квартал шекарасы (қызыл сызықтар), тас жолға шығу жолы,
бас жоспардың жақын элементтері."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiles
import final_data as fd
from mkmap1 import F, halo_text, dashed_line, gk_off

HERE = os.path.dirname(os.path.abspath(__file__))

# ЕГКН GetFeatureInfo жауабынан: учаске тұрған квартал (gpzone.482125 = gpreg.97419 «Красные линии»), EPSG:10947
BLOCK = [(13661105.514, 4840778.194), (13661098.832, 4840777.588), (13661092.135, 4840777.649),
         (13661085.423, 4840778.265), (13661078.777, 4840779.550), (13661072.362, 4840781.286),
         (13661066.091, 4840783.692), (13661059.724, 4840786.762), (13660975.932, 4840832.327),
         (13660970.600, 4840835.978), (13660965.502, 4840839.969), (13660960.875, 4840844.527),
         (13660956.642, 4840849.428), (13660952.805, 4840854.672), (13660949.524, 4840860.263),
         (13660946.721, 4840866.087), (13660944.478, 4840872.148), (13660942.793, 4840878.444),
         (13660941.662, 4840885.199), (13660914.482, 4841085.991), (13661247.675, 4840931.817),
         (13661156.425, 4840808.215), (13661152.038, 4840802.772), (13661147.312, 4840797.989),
         (13661142.256, 4840793.532), (13661136.784, 4840789.620), (13661130.975, 4840786.256),
         (13661124.914, 4840783.330), (13661118.595, 4840781.066), (13661112.102, 4840779.353)]


def main():
    base = tiles.Base("esri", 16, 43.6775, 43.7015, 76.9815, 77.0300, scale=1.0)
    img = ImageEnhance.Brightness(base.img.convert("RGB")).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    W, H = img.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    XY = base.to_xy
    mpp = base.m_per_px
    px, py = XY(*fd.P)

    def G(e, n):
        return XY(*fd.gk_inv(e, n))

    # --- жобалық магистраль дәлізі (БЖ): 200 м масштабтағы скриншоттан, шамамен ±10 м ---
    cl = [gk_off(-614, 981), gk_off(-580, 500), gk_off(-547, 0), gk_off(-540, -500), gk_off(-538, -981)]
    clp = [XY(*p) for p in cl]
    d.line(clp, fill=(235, 235, 235, 95), width=int(100 / mpp), joint="curve")
    off = 50 / mpp
    dashed_line(d, [(x - off, y) for x, y in clp], (255, 60, 60, 230), width=3, dash=16, gap=10)
    dashed_line(d, [(x + off, y) for x, y in clp], (255, 60, 60, 230), width=3, dash=16, gap=10)
    # --- жобалық теміржол дәлізі (БЖ) ---
    rr = [XY(*gk_off(-985, dy)) for dy in (1560, 800, 0, -700, -1080)]
    dashed_line(d, rr, (0, 0, 0, 255), width=7, dash=26, gap=14)
    dashed_line(d, rr, (255, 255, 255, 255), width=3, dash=26, gap=14)

    # --- 220 кВ желі, өзен (OSM) ---
    osm = json.load(open(os.path.join(HERE, "osm2.json"), encoding="utf-8"))
    for e in osm["elements"]:
        t = e.get("tags") or {}
        if e["type"] != "way" or "geometry" not in e:
            continue
        pts = [XY(p["lat"], p["lon"]) for p in e["geometry"]]
        if t.get("power") == "line":
            d.line(pts, fill=(255, 90, 200, 235), width=4)
        elif t.get("waterway") == "river" and (t.get("name") or "").startswith("Қаскел"):
            d.line(pts, fill=(70, 170, 255, 200), width=4)

    # --- тас жолға шығу жолы (OSRM/OSM): Алматы бағытының алғашқы 3,54 км ---
    r = json.load(open(os.path.join(HERE, "osrm_almaty.json"), encoding="utf-8"))["routes"][0]
    coords = r["geometry"]["coordinates"]
    acc, cum = [], 0.0
    for i, (lo, la) in enumerate(coords):
        if i:
            cum += fd.hav(coords[i - 1][1], coords[i - 1][0], la, lo)
        acc.append(XY(la, lo))
        if cum > 3.56:
            break
    d.line(acc, fill=(0, 0, 0, 200), width=9, joint="curve")
    d.line(acc, fill=(0, 230, 255, 255), width=5, joint="curve")

    # --- квартал шекарасы (қызыл сызықтар) ---
    bp = [G(*p) for p in BLOCK]
    d.polygon(bp, fill=(255, 235, 60, 55))
    d.line(bp + [bp[0]], fill=(255, 40, 40, 255), width=5, joint="curve")
    # --- қызмет көрсету мекемелерінің жобалық орны (аймақтың шеткі шектері) ---
    sv = [XY(*gk_off(-46, -366)), XY(*gk_off(84, -366)), XY(*gk_off(84, -242)), XY(*gk_off(-46, -242))]
    d.polygon(sv, fill=(60, 200, 220, 90))
    dashed_line(d, sv + [sv[0]], (0, 235, 255, 255), width=4, dash=12, gap=7)

    # --- учаске ---
    pp = [G(*p) for p in fd.PLOT_GK]
    d.polygon(pp, fill=(255, 0, 0, 170))
    d.line(pp + [pp[0]], fill=(255, 255, 255, 255), width=3)
    d.ellipse([px - 46, py - 46, px + 46, py + 46], outline=(255, 255, 255, 255), width=7)
    d.ellipse([px - 46, py - 46, px + 46, py + 46], outline=(255, 0, 0, 255), width=4)

    # --- нүктелік белгілер ---
    def mark(lat, lon, text, col, anchor="lm", dx=20, dy=0, fs=24):
        x, y = XY(lat, lon)
        d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=col + (255,), outline=(255, 255, 255, 255), width=3)
        halo_text(d, (x + dx, y + dy), text, F(fs, True), fill=(255, 255, 255), halo=(0, 0, 0), w=4, anchor=anchor)

    mark(43.696948, 77.016505, "Мешіт (1-я линия) — 1,90 км", (0, 160, 170))
    mark(43.68032, 77.01286, "мал қорасы — 1,49 км", (230, 120, 0))
    mark(43.69466, 77.02699, "А-3-ке шығу —\nжолмен ≈3,5 км", (60, 60, 60), anchor="rm", dx=-20, dy=-34)
    mark(43.68860, 77.02693, "жол бойы сервисі", (20, 150, 60), anchor="rm", dx=-20, dy=6, fs=21)

    def lab(dxm, dym, text, col=(255, 255, 255), fs=24, anchor="mm", halo=(0, 0, 0)):
        x, y = XY(*gk_off(dxm, dym))
        halo_text(d, (x, y), text, F(fs, True), fill=col, halo=halo, w=4, anchor=anchor)

    lab(60, 95, "УЧАСКЕ 03-046-187-767\n600 м² (≈19,8 × 30 м)", col=(255, 80, 80), fs=30, anchor="lb", halo=(255, 255, 255))
    lab(150, -185, "квартал: усадебная застройка (БЖ);\nқызыл сызық учаскенің алдынан ≈3–4 м", col=(255, 240, 90), fs=23, anchor="lm")
    lab(100, -400, "қызмет көрсету мекемелерінің\nжобалық орны (БЖ) — 225 м", col=(120, 240, 255), fs=23, anchor="lt")
    lab(-560, 700, "жобалық магистраль\nдәлізі (БЖ), ені ≈100 м,\nучаскеден ≈0,5 км", col=(255, 200, 200), fs=23, anchor="mm")
    lab(-1000, -620, "жобалық теміржол\nдәлізі (БЖ) — 0,97 км", col=(255, 255, 255), fs=23, anchor="lm")
    lab(-1100, 1250, "Кіші Мойынқұм құмдары\n(БЖ: жасыл желек аймағы)", col=(255, 235, 170), fs=24, anchor="lm")
    lab(900, 950, "«МРИЯ» САЯЖАЙ МАССИВІ", col=(200, 255, 200), fs=30)
    lab(1150, -600, "егістік", col=(255, 255, 255), fs=24)
    x, y = XY(43.6842, 77.0206); halo_text(d, (x, y), "Қаскелең өз. — 1,94 км", F(24, True), fill=(150, 215, 255), halo=(0, 0, 0), w=4, anchor="rm")
    x, y = XY(43.6850, 77.0263); halo_text(d, (x - 14, y), "А-3 Алматы–Қонаев\n2,38 км", F(24, True), fill=(255, 255, 255), halo=(0, 0, 0), w=4, anchor="rm")
    x, y = XY(43.6990, 77.0218); halo_text(d, (x + 10, y), "220 кВ", F(22, True), fill=(255, 150, 220), halo=(0, 0, 0), w=4, anchor="lm")

    out = Image.alpha_composite(img.convert("RGBA"), ov)
    d2 = ImageDraw.Draw(out)
    # тақырып жолағы
    d2.rectangle([0, 0, W, 54], fill=(0, 0, 0, 170))
    d2.text((16, 10), "Учаске мен жақын маңы: спутник суреті + бас жоспардың (БЖ) жақын элементтері",
            font=F(28, True), fill=(255, 255, 255))
    # масштаб, солтүстік
    bar = 500 / mpp
    bx, by = 30, H - 44
    d2.rectangle([bx - 12, by - 40, bx + bar + 70, by + 20], fill=(0, 0, 0, 150))
    d2.line([(bx, by), (bx + bar, by)], fill=(255, 255, 255), width=6)
    for k in (0, 0.5, 1):
        d2.line([(bx + bar * k, by - 9), (bx + bar * k, by + 9)], fill=(255, 255, 255), width=3)
    d2.text((bx, by - 38), "0", font=F(20, True), fill=(255, 255, 255))
    d2.text((bx + bar, by - 38), "500 м", font=F(20, True), fill=(255, 255, 255), anchor="ma")
    nx, ny = W - 60, 120
    d2.polygon([(nx, ny - 44), (nx - 16, ny + 10), (nx, ny), (nx + 16, ny + 10)], fill=(255, 255, 255), outline=(0, 0, 0))
    d2.text((nx, ny + 14), "С", font=F(26, True), fill=(255, 255, 255), anchor="ma", stroke_width=3, stroke_fill=(0, 0, 0))
    d2.text((W - 8, H - 6), "Сурет: Esri World Imagery (Esri, Maxar, Earthstar Geographics). Сызықтар: ЕГКН бас жоспары, OSM/OSRM. Түсірілім күні белгісіз.",
            font=F(16), fill=(255, 255, 255), anchor="rb", stroke_width=3, stroke_fill=(0, 0, 0))
    fn = os.path.join(HERE, "2_uchaske_sputnik_bas_zhospar.jpg")
    out.convert("RGB").save(fn, quality=90)
    print("saved", fn, out.size, "m/px %.3f" % mpp)


if __name__ == "__main__":
    main()
