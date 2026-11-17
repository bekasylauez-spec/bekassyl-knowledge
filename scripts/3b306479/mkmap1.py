# -*- coding: utf-8 -*-
"""1-сурет: шолу картасы (OSM негізі) — учаске + жақын нысандар + бас жоспардың негізгі аймақтары."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiles
import final_data as fd

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "C:/Windows/Fonts/segoeui.ttf"
FONTB = "C:/Windows/Fonts/segoeuib.ttf"


def F(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)


def halo_text(d, xy, text, font, fill=(20, 20, 20), halo=(255, 255, 255), w=3, anchor="la"):
    lines = text.split("\n")
    if len(lines) == 1:
        d.text(xy, text, font=font, fill=fill, stroke_width=w, stroke_fill=halo, anchor=anchor)
        return
    lh = font.size + 6
    total = lh * len(lines)
    v = anchor[1]
    if v in ("t", "a"):
        y0 = xy[1]
    elif v == "m":
        y0 = xy[1] - total / 2
    else:
        y0 = xy[1] - total
    for i, ln in enumerate(lines):
        d.text((xy[0], y0 + i * lh), ln, font=font, fill=fill, stroke_width=w, stroke_fill=halo, anchor=anchor[0] + "a")


def dashed_line(d, pts, fill, width=3, dash=14, gap=9):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        L = math.hypot(x2 - x1, y2 - y1)
        if L == 0:
            continue
        n = int(L // (dash + gap)) + 1
        for i in range(n):
            a = i * (dash + gap) / L
            b = min(1.0, (i * (dash + gap) + dash) / L)
            if a >= 1:
                break
            d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a), (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=fill, width=width)


def gk_off(dx, dy):
    """Учаске ортасынан (м) ығысқан нүктенің lat/lon-ы (GK жазықтығы арқылы)."""
    return fd.gk_inv(fd.C_GK[0] + dx, fd.C_GK[1] + dy)


def main():
    S = 1.6
    base = tiles.Base("osm", 13, 43.610, 43.768, 76.912, 77.146, scale=S)
    img = base.img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(0.55)
    img = ImageEnhance.Brightness(img).enhance(1.04)
    W, H = img.size
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    XY = base.to_xy
    px, py = XY(*fd.P)
    mpp = base.m_per_px

    # --- OSM сызықтық нысандары (ЖЭ желілері, құбыр, өзен) ---
    osm = json.load(open(os.path.join(HERE, "osm2.json"), encoding="utf-8"))
    for e in osm["elements"]:
        t = e.get("tags") or {}
        if e["type"] != "way" or "geometry" not in e:
            continue
        pts = [XY(p["lat"], p["lon"]) for p in e["geometry"]]
        if t.get("power") == "line":
            v = t.get("voltage", "")
            col = (170, 0, 170, 230) if v.startswith("500") else (215, 60, 150, 220)
            d.line(pts, fill=col, width=4 if v.startswith("500") else 3)
        elif t.get("man_made") == "pipeline":
            dashed_line(d, pts, (120, 80, 20, 230), width=3, dash=10, gap=8)
        elif t.get("waterway") == "river" and (t.get("name") or "").startswith("Қаскел"):
            d.line(pts, fill=(30, 110, 220, 230), width=4)

    # --- Бас жоспар аймақтары (шартты контур: аймақтың шеткі шектері, bbox) ---
    def gp_box(dx0, dx1, dy0, dy1, col, label, lab_xy=None, fs=19):
        c = [XY(*gk_off(dx0, dy0)), XY(*gk_off(dx1, dy0)), XY(*gk_off(dx1, dy1)), XY(*gk_off(dx0, dy1))]
        d.polygon(c, fill=col[:3] + (60,))
        dashed_line(d, c + [c[0]], col[:3] + (255,), width=4, dash=12, gap=7)
        cx = sum(p[0] for p in c) / 4
        cy = sum(p[1] for p in c) / 4
        if lab_xy:
            cx, cy = lab_xy
        lines = label.split("\n") if label else []
        y0 = cy - len(lines) * (fs + 5) / 2 if not lab_xy else cy
        for i, ln in enumerate(lines):
            halo_text(d, (cx, y0 + i * (fs + 5)), ln, F(fs, True), fill=col[:3], anchor="ma")

    gp_box(-81, 640, 2034, 3528, (190, 30, 30), "ҚОРҒАНЫС\nНЫСАНДАРЫ\nАУМАҒЫ (БЖ)\n2,0 км", fs=17)
    gp_box(-2381, -1523, 1253, 3856, (90, 90, 90), "ӨНЕРКӘСІП\nАЙМАҒЫ (БЖ)\n2,0 км")
    gp_box(65, 1287, -4472, -3130, (90, 90, 90), "ӨНЕРКӘСІП\nАЙМАҒЫ (БЖ)\n3,2 км")
    gp_box(2533, 2843, 1996, 2558, (150, 60, 0), "", None)
    # жобалық теміржол дәлізі (≈966 м батыста) және магистраль (≈0,5 км батыста) — шамамен, С–О бағытында
    # осьтер ЕГКН скриншотынан (1 км масштаб, ±3,9 км) автоматты түрде алынған — corridors.py
    cor = json.load(open(os.path.join(HERE, "corridors.json")))
    rr = [XY(*gk_off(p[0], p[1])) for p in cor["rail_1km"][::3]]
    dashed_line(d, rr, (0, 0, 0, 255), width=5, dash=18, gap=10)
    for key in ("far_1km", "near_1km"):
        rd = [XY(*gk_off(p[0], p[1])) for p in cor[key][::3]]
        d.line(rd, fill=(255, 255, 255, 230), width=11, joint="curve")
        d.line(rd, fill=(105, 105, 105, 235), width=7, joint="curve")
    # жобалық әуежай аумағының ең жақын шеті (3,9 км батыста): тік үзік сызық + белгі
    ax = [XY(*gk_off(-3900, dy)) for dy in (5200, 2500, -379, -3000, -5600)]
    dashed_line(d, ax, (200, 90, 0, 255), width=6, dash=22, gap=12)

    # --- қашықтық шеңберлері ---
    for rkm in (2, 5, 10):
        r = rkm * 1000 / mpp
        steps = 180
        pts = [(px + r * math.cos(2 * math.pi * i / steps), py + r * math.sin(2 * math.pi * i / steps)) for i in range(steps + 1)]
        dashed_line(d, pts, (200, 0, 0, 170), width=2, dash=10, gap=10)
        ang = {2: 228, 5: 228, 10: 12}[rkm]  # шығыстан сағат тіліне қарсы, градус
        lx = px + r * math.cos(math.radians(ang))
        ly = py - r * math.sin(math.radians(ang))
        halo_text(d, (lx, ly), "%d км" % rkm, F(21, True), fill=(190, 0, 0), anchor="mm", w=4)

    # --- нөмірленген белгілер ---
    CAT_COL = {"білім": (25, 95, 200), "мед": (200, 30, 60), "сауда": (20, 140, 60), "діни": (0, 140, 150),
               "қызмет": (110, 70, 170), "көлік": (60, 60, 60), "ерекше": (215, 110, 0)}
    marks = [
        ("1", "білім", 43.709311, 77.040329, "№1 мектеп (Заречный) — 4,25 км"),
        ("2", "білім", 43.675162, 77.064838, "№7 мектеп (Еңбек) — 5,62 км"),
        ("3", "білім", 43.72112, 77.080799, "№32 мектеп (Құйған) — 7,71 км"),
        ("4", "білім", 43.673993, 77.101897, "№3 мектеп (Жетіген) — 8,56 км"),
        ("5", "білім", 43.664993, 77.092125, "Балабақшалар (Жетіген; ең жақыны «Азиза») — 8,0 км"),
        ("6", "мед", 43.713282, 77.0377341, "Invivo пункті (Заречный) — 4,36 км"),
        ("7", "мед", 43.683076, 77.117588, "Алатау қалалық ауруханасы, емдеу орталықтары — 9,1–9,7 км"),
        ("8", "діни", 43.696948, 77.016505, "Мешіт (саяжай, 1-я линия) — 1,90 км"),
        ("9", "сауда", 43.713229, 77.019568, "«Адель» дүкені (саяжай, 2-я линия) — 3,40 км"),
        ("10", "сауда", 43.717322, 77.029876, "«Заречный» СО, дүкендер, мешіт — 3,8–4,3 км"),
        ("11", "сауда", 43.673217, 77.10795, "Magnum, базар, дәріхана, банкомат (Жетіген) — 8,4–9,2 км"),
        ("12", "қызмет", 43.658557, 77.093702, "Almagas АЗС — 8,41 км; полиция бөлімі — 8,66 км"),
        ("13", "қызмет", 43.67913, 77.114389, "Қазпошта, әкімдік, полиция бөлімшесі — 9,2–9,7 км"),
        ("14", "көлік", 43.69466, 77.02699, "А-3-ке шығатын жер (Алматы бағыты) — түзу 2,54 км, жолмен ≈3,5 км"),
        ("15", "көлік", 43.7063684, 77.0272303, "Автобус аялдамасы (Заречное бұрылысы) — 3,22 км"),
        ("16", "көлік", 43.7294, 77.0280, "Заречное жол айрығы — 5,30 км"),
        ("17", "көлік", 43.6408, 77.0224, "Жетіген жол айрығы — 5,56 км"),
        ("18", "көлік", 43.75952, 77.03470, "Іле т/ж станциясы — 8,58 км"),
        ("19", "көлік", 43.68870, 77.12590, "Жетіген т/ж станциясы — 10,36 км"),
        ("A", "ерекше", 43.7170, 77.0365, "Түзеу мекемелері (OSM: ЛА-155/8, /11), күзет оқу орталығы — 4,4–4,6 км"),
        ("B", "ерекше", 43.7090, 77.0300, "«Пеноплекс»/БСУ алаңы; БЖ-да түзеу мекемелері аумағы — 3,1–3,5 км"),
        ("C", "ерекше", 43.72466, 77.03366, "Knauf Gips зауыты — 5,09 км"),
        ("D", "ерекше", 43.72114, 77.01442, "Мал шаруашылығы кешені — 4,01 км"),
        ("E", "ерекше", 43.68032, 77.01286, "Мал қорасы — 1,49 км"),
        ("F", "ерекше", 43.67203, 77.06844, "Зираттар (Еңбек – Жетіген арасы) — 6,0–7,0 км"),
        ("G", "ерекше", 43.62048, 76.97214, "Күн электр станциясы — 7,70 км"),
        ("H", "ерекше", 43.69000, 76.99084, "Кіші Мойынқұм құмының шеті — 0,58 км"),
    ]
    R0 = 17
    for num, cat, lat, lon, _ in marks:
        x, y = XY(lat, lon)
        col = CAT_COL[cat]
        d.ellipse([x - R0, y - R0, x + R0, y + R0], fill=col + (255,), outline=(255, 255, 255, 255), width=3)
        d.text((x, y - 1), num, font=F(19 if len(num) == 1 else 16, True), fill=(255, 255, 255), anchor="mm")

    # --- учаске ---
    d.ellipse([px - 26, py - 26, px + 26, py + 26], outline=(230, 0, 0, 255), width=5)
    d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(230, 0, 0, 255), outline=(255, 255, 255, 255), width=2)
    halo_text(d, (px + 32, py + 6), "УЧАСКЕ", F(26, True), fill=(210, 0, 0), w=4)

    # --- сызық жазулары ---
    x, y = XY(*gk_off(-985, 3050)); halo_text(d, (x - 8, y), "жобалық теміржол (БЖ)", F(18, True), fill=(0, 0, 0), anchor="rm")
    x, y = XY(*gk_off(-640, -1900)); halo_text(d, (x + 14, y), "ірі жол дәлізі (БЖ)", F(18, True), fill=(70, 70, 70), anchor="lm")
    x, y = XY(*gk_off(-3900, 4600)); halo_text(d, (x - 10, y), "← СЫРТҚЫ КӨЛІК (ӘУЕЖАЙ)\nАУМАҒЫ (БЖ), шеті 3,9 км", F(20, True), fill=(190, 80, 0), anchor="rm")
    x, y = XY(43.6650, 76.9559); halo_text(d, (x + 8, y), "500 кВ", F(18, True), fill=(150, 0, 150), anchor="lm")
    x, y = XY(43.6500, 77.0190); halo_text(d, (x + 8, y), "220 кВ", F(18, True), fill=(195, 40, 130), anchor="lm")
    x, y = XY(43.6590, 76.9660); halo_text(d, (x + 8, y), "құбыр", F(18, True), fill=(110, 70, 10), anchor="lm")
    x, y = XY(43.6790, 77.0185); halo_text(d, (x - 6, y + 14), "Қаскелең өз.", F(18, True), fill=(20, 90, 200), anchor="rm")
    x, y = XY(43.7480, 77.0290); halo_text(d, (x + 12, y), "А-3 Алматы–Қонаев", F(19, True), fill=(40, 40, 40), anchor="lm")

    for nm, la, lo, anc in (("ЗАРЕЧНОЕ", 43.7255, 77.0460, "lm"), ("ЕҢБЕК", 43.6660, 77.0668, "mt"),
                            ("ҚҰЙҒАН", 43.7290, 77.0806, "mb"), ("ЖЕТІГЕН (Алатау қ. орталығы)", 43.6935, 77.1040, "mm"),
                            ("САЯЖАЙ МАССИВІ", 43.7015, 77.0040, "mm")):
        x, y = XY(la, lo)
        halo_text(d, (x, y), nm, F(20, True), fill=(40, 40, 90), anchor=anc, w=4)
    img = Image.alpha_composite(img.convert("RGBA"), ov)

    # --- масштаб сызғышы ---
    d2 = ImageDraw.Draw(img)
    bar = 2000 / mpp
    bx, by = 30, H - 46
    d2.rectangle([bx - 10, by - 34, bx + bar + 60, by + 18], fill=(255, 255, 255, 225))
    d2.line([(bx, by), (bx + bar, by)], fill=(0, 0, 0), width=5)
    for k in (0, 0.5, 1):
        d2.line([(bx + bar * k, by - 8), (bx + bar * k, by + 8)], fill=(0, 0, 0), width=3)
    d2.text((bx, by - 32), "0", font=F(18), fill=(0, 0, 0))
    d2.text((bx + bar, by - 32), "2 км", font=F(18, True), fill=(0, 0, 0), anchor="ma")
    d2.text((W - 8, H - 6), "Негіз: © OpenStreetMap contributors", font=F(15), fill=(40, 40, 40), anchor="rb",
            stroke_width=2, stroke_fill=(255, 255, 255))

    # --- аңыз (оң жақ панель) ---
    PW = 820
    out = Image.new("RGB", (W + PW, H), (250, 250, 247))
    out.paste(img.convert("RGB"), (0, 0))
    dl = ImageDraw.Draw(out)
    x0 = W + 24
    y = 18
    dl.text((x0, y), "03-046-187-767 учаскесінің айналасы", font=F(30, True), fill=(20, 20, 20)); y += 42
    dl.text((x0, y), "«Мрия» бау-бақша серіктестігі, Алатау қаласы аумағы", font=F(20), fill=(60, 60, 60)); y += 28
    dl.text((x0, y), "43.68733° с.е., 76.99701° ш.б.  ·  қашықтық — түзу сызық (haversine)", font=F(18), fill=(60, 60, 60)); y += 36
    groups = [("білім", "Мектеп, балабақша"), ("мед", "Медицина"), ("діни", "Мешіт"), ("сауда", "Сауда"),
              ("қызмет", "Қызметтер"), ("көлік", "Көлік"), ("ерекше", "Ерекше нысандар")]
    for cat, title in groups:
        col = CAT_COL[cat]
        dl.text((x0, y), title, font=F(21, True), fill=col); y += 30
        for num, c2, lat, lon, text in marks:
            if c2 != cat:
                continue
            dl.ellipse([x0, y + 1, x0 + 26, y + 27], fill=col)
            dl.text((x0 + 13, y + 13), num, font=F(15 if len(num) == 1 else 13, True), fill=(255, 255, 255), anchor="mm")
            # ұзын мәтінді бөлу
            words, line, lines = text.split(" "), "", []
            for w in words:
                if dl.textlength(line + " " + w, font=F(18)) > PW - 80:
                    lines.append(line); line = w
                else:
                    line = (line + " " + w).strip()
            lines.append(line)
            for i, ln in enumerate(lines):
                dl.text((x0 + 36, y + 1 + i * 23), ln, font=F(18), fill=(25, 25, 25))
            y += max(30, 23 * len(lines) + 7)
        y += 8
    y += 4
    dl.text((x0, y), "Шартты белгілер", font=F(21, True), fill=(20, 20, 20)); y += 32
    leg = [((190, 30, 30), "БЖ — ЕГКН картасындағы бас жоспар аймағы (үзік контур —"),
           (None, "аймақтың шеткі шектері; сан — учаскеге ең жақын шетіне дейін)"),
           ((0, 0, 0), "жобалық теміржол дәлізі (0,97 км батыста)"),
           ((105, 105, 105), "ірі жол дәлізі, екі тармақ: жақыны ≈0,28 км, алысы ≈0,55 км"),
           ((200, 90, 0), "сыртқы көлік (әуежай) аумағының ең жақын шеті"),
           ((170, 0, 170), "500 кВ және 220 кВ әуе желілері (OSM)"),
           ((120, 80, 20), "құбыр (OSM, заты көрсетілмеген)"),
           ((200, 0, 0), "қызыл шеңберлер — учаскеден 2, 5, 10 км")]
    for col, text in leg:
        if col:
            dl.line([(x0, y + 13), (x0 + 28, y + 13)], fill=col, width=5)
        dl.text((x0 + 38, y), text, font=F(17), fill=(30, 30, 30)); y += 26
    y += 14
    dl.text((x0, y), "Бас жоспар (ЕГКН, ҚР Үкіметінің № 388 / № 727 қаулысы)", font=F(21, True), fill=(20, 20, 20)); y += 30
    dl.text((x0, y), "учаске контурынан аймақтың ең жақын шетіне дейін:", font=F(17), fill=(70, 70, 70)); y += 28
    gpl = [("0 м", "учаскенің өз аймағы — усадебная застройка (тұрғын аймақ)"),
           ("≈3 м", "көше дәлізі (автомобиль жолдары аумағы, қызыл сызық)"),
           ("99 м", "жасыл желек аймағы (жалпы және арнайы мақсаттағы)"),
           ("225 м", "қызмет көрсету мекемелерінің жобалық орны"),
           ("72 м", "квартал батысындағы ішкі көшенің қызыл сызығы"),
           ("≈0,28 км", "ірі жол дәлізі — жақын тармағы (ені ≈70–80 м)"),
           ("≈0,55 км", "ірі жол дәлізі — алыс тармағы"),
           ("0,97 км", "жобалық теміржол дәлізі; 0,99 км — резерв аумақ"),
           ("1,89 км", "білім беру мекемесінің жобалық орны"),
           ("1,91 км", "Қаскелең өзені мен жағалау жолағы"),
           ("1,99 км", "өнеркәсіп аймағы (жобалық)"),
           ("2,02 км", "қорғаныс нысандарының аумағы"),
           ("2,33 км", "А-3 тас жолының дәлізі"),
           ("2,73 км", "12 қабаттан биік тұрғын үй аймағы (жобалық)"),
           ("3,23 км", "түзеу мекемелерінің аумағы (қазіргі)"),
           ("3,90 км", "сыртқы көлік құрылыстары (әуежай) аумағы")]
    for dist, text in gpl:
        dl.text((x0 + 92, y), dist, font=F(17, True), fill=(150, 30, 30), anchor="ra")
        dl.text((x0 + 104, y), text, font=F(17), fill=(30, 30, 30)); y += 25
    y += 12
    dl.text((x0, y), "Дерек: OpenStreetMap, 2ГИС, Яндекс Карты, ЕГКН (map.gov4c.kz), 17.11.2026",
            font=F(16), fill=(90, 90, 90))
    fn = os.path.join(HERE, "1_aynalasy_sholu_kartasy.png")
    out.save(fn, optimize=True)
    print("saved", fn, out.size, "m/px %.2f" % mpp, "legend bottom y=%d of %d" % (y, H))


if __name__ == "__main__":
    main()
