# -*- coding: utf-8 -*-
"""ЕГКН бас жоспары скриншоттарынан батыстағы ірі жол дәліздерінің (екі тармақ) осін шығару.
Кадр → метр: dx = (x - 472.5) * mpp, dy = (276 - y) * mpp; mpp = карта рұқсаты (м/пиксель) * 1,875
(1500 px көрініс 800 px кадрға кішірейтілген). Рұқсат: «200 m» 2,386; «1000 m» 9,544 м/пиксель."""
import json, math, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
CX, CY = 472.5, 276.0


def isgrey(c):
    r, g, b = c
    return abs(r - g) < 12 and abs(g - b) < 12 and 170 <= r <= 225


def row_runs(im, y, x0, x1, wmin, wmax):
    runs, s = [], None
    for x in range(x0, x1 + 1):
        v = isgrey(im.getpixel((x, y)))
        if v and s is None:
            s = x
        if (not v) and s is not None:
            if wmin <= x - s <= wmax:
                runs.append((s, x - 1))
            s = None
    return runs


def track(im, start_x, y_from, y_to, step, x0, x1, wmin, wmax, maxjump):
    pts, cur = [], start_x
    y = y_from
    while (y >= y_to) if step < 0 else (y <= y_to):
        runs = row_runs(im, y, x0, x1, wmin, wmax)
        best = None
        for a, b in runs:
            c = (a + b) / 2
            if abs(c - cur) <= maxjump and (best is None or abs(c - cur) < abs(best[0] - cur)):
                best = (c, b - a + 1)
        if best:
            cur = best[0]
            pts.append((cur, y, best[1]))
        y += step
    return pts


def main():
    out = {}
    # --- 200 м масштаб: дәл өлшем (±980 м) ---
    im = Image.open(os.path.join(HERE, "shots", "gp_200m.jpg")).convert("RGB")
    mpp = 2.386 * 1.875
    for name, sx in (("near", 397.5), ("far", 343.0)):
        up = track(im, sx, 276, 100, -4, 300, 470, 8, 40, 9)
        dn = track(im, sx, 280, 492, 4, 300, 470, 8, 40, 9)
        pts = list(reversed(up)) + dn
        out[name + "_200"] = [((x - CX) * mpp, (CY - y) * mpp, w * mpp) for x, y, w in pts]
    # --- 1 км масштаб: ұзарту (±3,9 км) ---
    im2 = Image.open(os.path.join(HERE, "shots", "gp_1km_zones.jpg")).convert("RGB")
    mpp2 = 9.544 * 1.875
    for name, sx in (("near", 452.5), ("far", 439.5)):
        up = track(im2, sx, 276, 98, -3, 380, 620, 2, 12, 6)
        dn = track(im2, sx, 279, 492, 3, 380, 620, 2, 12, 6)
        pts = list(reversed(up)) + dn
        out[name + "_1km"] = [((x - CX) * mpp2, (CY - y) * mpp2, w * mpp2) for x, y, w in pts]
    json.dump(out, open(os.path.join(HERE, "corridors.json"), "w"), indent=0)
    for k, v in out.items():
        print(k, len(v), "pts; dy %.0f..%.0f" % (min(p[1] for p in v), max(p[1] for p in v)))
        for p in v[:: max(1, len(v) // 12)]:
            print("    dx=%7.0f dy=%7.0f w=%4.0f" % p)
    # ең жақын нүкте (200 м скриншоты, тармақ осі мен шеті)
    near = out["near_200"]
    best = min(near, key=lambda p: math.hypot(p[0], p[1]))
    print("near branch axis closest: %.0f m (dx %.0f, dy %.0f), width %.0f -> edge ~%.0f m" % (
        math.hypot(best[0], best[1]), best[0], best[1], best[2], math.hypot(best[0], best[1]) - best[2] / 2))


if __name__ == "__main__":
    main()
