# -*- coding: utf-8 -*-
"""2-сурет: спутниктік жақын көрініс + ЕГКН бас жоспары қабатының (жол дәліздері, қызыл сызықтар, аймақтар)
скриншоттан координатаға байланып салынған үстеме қабаты; учаске, квартал, тас жолға шығу жолы."""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

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

FCX, FCY = 472.5, 276.0  # скриншот кадрындағы карта ортасы = учаске ортасы


def classify(shot):
    """Скриншотты (RGB) бас жоспар элементтерінің RGBA қабатына айналдыру."""
    a = np.asarray(shot.convert("RGB")).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    grey = (np.abs(r - g) < 14) & (np.abs(g - b) < 14) & (r >= 168) & (r <= 226)
    red = (r > 140) & (g < 110) & (b < 110) & (r - g > 60)
    cyan = (r < 212) & (g > 205) & (b > 208) & (b - r > 12)
    purple = (r > 170) & (r < 215) & (g > 150) & (g < 190) & (b > 195) & (b - g > 20)
    black = (r < 80) & (g < 80) & (b < 80)
    yellow = (r > 236) & (g > 240) & (b > 185) & (b < 222) & (g - b > 25)
    pink = (r > 220) & (g > 160) & (g < 200) & (b > 160) & (b < 200) & (r - g > 35)

    red = (r - g > 45) & (r - b > 45) & (g < 125) & (r > 95)

    def clean(m, k=3):
        im = Image.fromarray((m * 255).astype(np.uint8))
        im = im.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))
        return np.asarray(im) > 127

    def close(m, k=3):
        im = Image.fromarray((m * 255).astype(np.uint8))
        im = im.filter(ImageFilter.MaxFilter(k)).filter(ImageFilter.MinFilter(k))
        return np.asarray(im) > 127

    # UI элементтері мен карта жиегі
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W]
    ui = (xx < 157) | (xx > 788) | (yy < 59) | (yy > 493)
    ui |= (xx >= 163) & (xx <= 394) & (yy >= 66) & (yy <= 94)
    ui |= (xx >= 750) & (yy <= 254)
    ui |= (xx >= 640) & (yy >= 446)
    ui |= (xx <= 192) & (yy >= 462)
    # (маска, түс, альфа) — салу реті бойынша
    layers = [(clean(yellow), (255, 240, 90), 72), (clean(pink), (255, 120, 120), 80),
              (clean(cyan), (60, 210, 230), 110), (clean(purple), (175, 110, 225), 125),
              (close(grey) & ~red, (242, 242, 242), 135), (red, (255, 40, 40), 235), (black, (0, 0, 0), 235)]
    return [((m & ~ui), col, al) for m, col, al in layers]


UP = 4  # маскаларды тегістеу үшін үлкейту еселігі


def reproject(base, mask, mpp):
    """Скриншот маскасын (кадр координатасы) спутник суретінің торына көшіру (аффиндік жуықтау).
    Маска алдымен UP есе билинейлі үлкейтіледі — жиектері тегіс шығады. Қайтарады: альфа (0..255), қалдық (м)."""
    mi = Image.fromarray((mask * 255).astype(np.uint8)).resize((mask.shape[1] * UP, mask.shape[0] * UP), Image.BILINEAR)
    rgba = np.asarray(mi)
    mpp = mpp / UP
    fcx, fcy = FCX * UP + (UP - 1) / 2.0, FCY * UP + (UP - 1) / 2.0
    W, H = base.img.size
    n = 256 * 2 ** base.z
    A, BE, BN = [], [], []
    for u in np.linspace(0, W - 1, 6):
        for v in np.linspace(0, H - 1, 6):
            xg, yg = base.x0 + u / base.scale, base.y0 + v / base.scale
            lon = xg / n * 360.0 - 180.0
            lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * yg / n))))
            e, nn = fd.gk_fwd(lat, lon)
            A.append([u, v, 1.0]); BE.append(e); BN.append(nn)
    A = np.array(A)
    cE = np.linalg.lstsq(A, np.array(BE), rcond=None)[0]
    cN = np.linalg.lstsq(A, np.array(BN), rcond=None)[0]
    resid = max(np.abs(A @ cE - BE).max(), np.abs(A @ cN - BN).max())
    uu, vv = np.meshgrid(np.arange(W, dtype=np.float64), np.arange(H, dtype=np.float64))
    E = cE[0] * uu + cE[1] * vv + cE[2]
    N = cN[0] * uu + cN[1] * vv + cN[2]
    xs = np.rint(fcx + (E - fd.C_GK[0]) / mpp).astype(np.int32)
    ys = np.rint(fcy - (N - fd.C_GK[1]) / mpp).astype(np.int32)
    ok = (xs >= 0) & (xs < rgba.shape[1]) & (ys >= 0) & (ys < rgba.shape[0])
    out = np.zeros((H, W), np.uint8)
    out[ok] = rgba[ys[ok], xs[ok]]
    return out, resid


def gp_layer(base, shot_file, res, cover=None):
    """Бір скриншоттан бас жоспар қабатын (RGBA сурет) құрау; cover — қабат қолданылатын аумақ маскасы."""
    W, H = base.img.size
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    resid = 0.0
    for mask, col, al in classify(Image.open(os.path.join(HERE, "shots", shot_file))):
        alpha, resid = reproject(base, mask, res * 1.875)
        alpha = (alpha.astype(np.float32) * al / 255.0)
        if cover is not None:
            alpha = alpha * cover
        solid = Image.new("RGBA", (W, H), col + (255,))
        lay = Image.composite(solid, lay, Image.fromarray(alpha.astype(np.uint8)))  # жоғарғы қабат басым
    return lay, resid


def main():
    base = tiles.Base("esri", 16, 43.6775, 43.7015, 76.9815, 77.0300, scale=1.0)
    img = ImageEnhance.Brightness(base.img.convert("RGB")).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.05)
    W, H = img.size
    XY = base.to_xy
    mpp = base.m_per_px
    px, py = XY(*fd.P)

    def G(e, n):
        return XY(*fd.gk_inv(e, n))

    # --- бас жоспар қабаты: алдымен 500 м скриншоты (кең), үстінен 200 м скриншоты (дәлірек) ---
    # 200 м скриншоты жабатын аумақ (кадрдың карта бөлігі, UI жолағынан төмен)
    e0, e1 = (157 - FCX) * 2.386 * 1.875, (750 - FCX) * 2.386 * 1.875
    n0, n1 = (FCY - 493) * 2.386 * 1.875, (FCY - 96) * 2.386 * 1.875
    c = [XY(*gk_off(e0, n0)), XY(*gk_off(e1, n0)), XY(*gk_off(e1, n1)), XY(*gk_off(e0, n1))]
    cm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(cm).polygon(c, fill=255)
    cover = (np.asarray(cm) > 0).astype(np.float32)
    lay500, r1 = gp_layer(base, "gp_500m.jpg", 4.772, cover=1.0 - cover)
    lay200, r2 = gp_layer(base, "gp_200m.jpg", 2.386, cover=cover)
    gp = Image.alpha_composite(lay500, lay200)
    print("affine residual, m: %.2f / %.2f" % (r1, r2))

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

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

    # --- квартал шекарасы (ЕГКН координатасынан, дәл) ---
    bp = [G(*p) for p in BLOCK]
    d.line(bp + [bp[0]], fill=(255, 255, 255, 255), width=7, joint="curve")
    d.line(bp + [bp[0]], fill=(255, 30, 30, 255), width=4, joint="curve")
    # --- қызмет көрсету мекемелерінің жобалық орны (аймақтың шеткі шектері, дәл) ---
    sv = [XY(*gk_off(-46, -366)), XY(*gk_off(84, -366)), XY(*gk_off(84, -242)), XY(*gk_off(-46, -242))]
    dashed_line(d, sv + [sv[0]], (0, 235, 255, 255), width=4, dash=12, gap=7)

    # --- учаске ---
    pp = [G(*p) for p in fd.PLOT_GK]
    d.polygon(pp, fill=(255, 0, 0, 190))
    d.line(pp + [pp[0]], fill=(255, 255, 255, 255), width=3)
    d.ellipse([px - 46, py - 46, px + 46, py + 46], outline=(255, 255, 255, 255), width=7)
    d.ellipse([px - 46, py - 46, px + 46, py + 46], outline=(255, 0, 0, 255), width=4)

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

    def arrow(dx0, dy0, dx1, dy1, col=(255, 255, 255, 255)):
        a, b = XY(*gk_off(dx0, dy0)), XY(*gk_off(dx1, dy1))
        d.line([a, b], fill=(0, 0, 0, 255), width=6)
        d.line([a, b], fill=col, width=3)
        d.ellipse([b[0] - 6, b[1] - 6, b[0] + 6, b[1] + 6], fill=col, outline=(0, 0, 0, 255))

    lab(60, 95, "УЧАСКЕ 03-046-187-767\n600 м² (≈19,8 × 30 м)", col=(255, 80, 80), fs=30, anchor="lb", halo=(255, 255, 255))
    lab(175, -150, "учаскенің кварталы (қызыл сызықтар ішінде);\nалдыңғы қызыл сызық учаскеден ≈3–4 м,\nбатыстағысы 72 м", col=(255, 240, 90), fs=22, anchor="lt")
    lab(110, -385, "қызмет көрсету мекемелерінің\nжобалық орны (БЖ) — 225 м", col=(120, 240, 255), fs=22, anchor="lt")
    # ірі жол дәлізінің екі тармағы
    lab(-1215, 330, "ірі жол дәлізі (БЖ):\nжақын тармағы — учаскеден\n≈0,28 км, ені ≈70–80 м", col=(255, 255, 255), fs=23, anchor="lm")
    arrow(-760, 250, -330, 110)
    lab(-1215, 1010, "алыс тармағы —\n≈0,55–0,6 км батыста", col=(255, 255, 255), fs=23, anchor="lm")
    arrow(-860, 960, -670, 860)
    lab(-930, -300, "← жобалық теміржол\nдәлізі (БЖ) — 0,97 км", col=(255, 255, 255), fs=22, anchor="lm")
    lab(-1180, 1420, "Кіші Мойынқұм құмдары (БЖ: жасыл желек аймағы)", col=(255, 235, 170), fs=23, anchor="lm")
    lab(900, 1010, "«МРИЯ» САЯЖАЙ МАССИВІ\n(БЖ: усадебная застройка — сары реңк)", col=(200, 255, 200), fs=26)
    lab(1150, -600, "егістік (БЖ: жасыл желек аймағы)", col=(255, 255, 255), fs=22)
    x, y = XY(43.6842, 77.0206); halo_text(d, (x, y), "Қаскелең өз. — 1,94 км", F(24, True), fill=(150, 215, 255), halo=(0, 0, 0), w=4, anchor="rm")
    x, y = XY(43.6850, 77.0263); halo_text(d, (x - 14, y), "А-3 Алматы–Қонаев\n2,38 км", F(24, True), fill=(255, 255, 255), halo=(0, 0, 0), w=4, anchor="rm")
    x, y = XY(43.6990, 77.0218); halo_text(d, (x + 10, y), "220 кВ", F(22, True), fill=(255, 150, 220), halo=(0, 0, 0), w=4, anchor="lm")

    out = Image.alpha_composite(img.convert("RGBA"), gp)
    out = Image.alpha_composite(out, ov)
    d2 = ImageDraw.Draw(out, "RGBA")
    d2.rectangle([0, 0, W, 54], fill=(0, 0, 0, 185))
    d2.text((16, 10), "Учаске мен жақын маңы: спутник суреті + ЕГКН бас жоспары қабаты (жол дәліздері, қызыл сызықтар, аймақтар)",
            font=F(27, True), fill=(255, 255, 255))
    # аңыз
    lx, ly = 22, H - 318
    d2.rectangle([lx - 10, ly - 10, lx + 560, ly + 232], fill=(0, 0, 0, 165))
    items = [((238, 238, 238), "жол және көше дәліздері (БЖ)"), ((255, 45, 45), "қызыл сызықтар (БЖ, № 727, 09.09.2025)"),
             ((255, 240, 90), "усадебная застройка аймағы (БЖ)"), ((60, 210, 230), "қызмет көрсету мекемелерінің орны (БЖ)"),
             ((0, 0, 0), "жобалық теміржол (БЖ)"), ((0, 230, 255), "тас жолға шығатын жол (OSM/OSRM)"),
             ((255, 90, 200), "220 кВ желі;  көк — Қаскелең өзені (OSM)")]
    for i, (col, text) in enumerate(items):
        yy = ly + i * 32
        d2.rectangle([lx, yy + 4, lx + 34, yy + 22], fill=col + (255,), outline=(255, 255, 255, 255))
        d2.text((lx + 46, yy), text, font=F(20), fill=(255, 255, 255))
    bar = 500 / mpp
    bx, by = 30, H - 44
    d2.rectangle([bx - 12, by - 40, bx + bar + 70, by + 20], fill=(0, 0, 0, 165))
    d2.line([(bx, by), (bx + bar, by)], fill=(255, 255, 255), width=6)
    for k in (0, 0.5, 1):
        d2.line([(bx + bar * k, by - 9), (bx + bar * k, by + 9)], fill=(255, 255, 255), width=3)
    d2.text((bx, by - 38), "0", font=F(20, True), fill=(255, 255, 255))
    d2.text((bx + bar, by - 38), "500 м", font=F(20, True), fill=(255, 255, 255), anchor="ma")
    nx, ny = W - 60, 120
    d2.polygon([(nx, ny - 44), (nx - 16, ny + 10), (nx, ny), (nx + 16, ny + 10)], fill=(255, 255, 255), outline=(0, 0, 0))
    d2.text((nx, ny + 14), "С", font=F(26, True), fill=(255, 255, 255), anchor="ma", stroke_width=3, stroke_fill=(0, 0, 0))
    d2.text((W - 8, H - 6), "Сурет: Esri World Imagery (түсірілім күні белгісіз). БЖ қабаты: map.gov4c.kz/egkn скриншоты, координатаға байланған (дәлдігі ≈5–10 м).",
            font=F(16), fill=(255, 255, 255), anchor="rb", stroke_width=3, stroke_fill=(0, 0, 0))
    fn = os.path.join(HERE, "2_uchaske_sputnik_bas_zhospar.jpg")
    out.convert("RGB").save(fn, quality=90)
    print("saved", fn, out.size, "m/px %.3f" % mpp)


if __name__ == "__main__":
    main()
