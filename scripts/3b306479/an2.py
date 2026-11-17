# -*- coding: utf-8 -*-
"""OSM екінші топтама: сызықтық/алаңдық нысандарға учаскеден ең жақын қашықтық.
Қашықтық: учаске маңында жергілікті жазық проекция (equirectangular, lat0 = учаске) —
нүктеден кесіндіге дейін; 30 км шегінде haversine-нен айырмасы < 0,1 %.
Нүктелік қашықтық haversine-мен қатар тексеріледі."""
import json, math, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
P = (43.68733, 76.99701)
R = 6371.0088
KX = math.cos(math.radians(P[0])) * math.pi / 180 * R  # км / градус бойлық
KY = math.pi / 180 * R  # км / градус ендік


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def xy(lat, lon):
    return ((lon - P[1]) * KX, (lat - P[0]) * KY)


def seg_dist(a, b):
    """(0,0)-ден a-b кесіндісіне дейінгі қашықтық және ең жақын нүкте."""
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, -(ax * dx + ay * dy) / L2))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(cx, cy), (cx, cy)


def inside(poly):
    """(0,0) полигон ішінде ме (ray casting)."""
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > 0) != (y2 > 0):
            xin = x1 + (0 - y1) * (x2 - x1) / (y2 - y1)
            if xin > 0:
                c = not c
    return c


def bearing_xy(x, y):
    b = (math.degrees(math.atan2(x, y)) + 360) % 360
    names = ["С", "СШ", "Ш", "ОШ", "О", "ОБ", "Б", "СБ"]
    return names[int((b + 22.5) // 45) % 8], b


def geoms(e):
    """Элементтің сызықтарын (lat,lon тізімдері) қайтарады."""
    out = []
    if e["type"] == "node":
        out.append([(e["lat"], e["lon"])])
    elif e["type"] == "way" and "geometry" in e:
        out.append([(p["lat"], p["lon"]) for p in e["geometry"]])
    elif e["type"] == "relation":
        for m in e.get("members", []):
            if "geometry" in m:
                out.append([(p["lat"], p["lon"]) for p in m["geometry"]])
            elif "lat" in m:
                out.append([(m["lat"], m["lon"])])
    return out


def nearest(e):
    best = (1e9, (0, 0))
    isin = False
    for g in geoms(e):
        pts = [xy(*p) for p in g]
        if len(pts) == 1:
            d = math.hypot(*pts[0])
            if d < best[0]:
                best = (d, pts[0])
        else:
            for i in range(len(pts) - 1):
                d, c = seg_dist(pts[i], pts[i + 1])
                if d < best[0]:
                    best = (d, c)
            if len(pts) > 3 and pts[0] == pts[-1] and inside(pts):
                isin = True
    return best[0], best[1], isin


KEYS = ["power", "man_made", "waterway", "highway", "railway", "landuse", "leisure", "natural", "water",
        "building", "office", "tourism", "craft", "shop", "amenity"]


def cat(t):
    for k in KEYS:
        if k in t:
            return k + "=" + t[k]
    return "other"


def main(path, maxn):
    d = json.load(open(path, encoding="utf-8"))
    els = [e for e in d["elements"] if e.get("tags")]
    print("elements with tags:", len(els))
    groups = {}
    for e in els:
        t = e["tags"]
        dist, c, isin = nearest(e)
        if dist > 1e8:
            continue
        lat = P[0] + c[1] / KY
        lon = P[1] + c[0] / KX
        groups.setdefault(cat(t), []).append((dist, e, lat, lon, isin, c))
    for g in sorted(groups):
        lst = sorted(groups[g], key=lambda r: r[0])
        print("\n### %s (n=%d)" % (g, len(lst)))
        for dist, e, lat, lon, isin, c in lst[:maxn]:
            t = e["tags"]
            nm = t.get("name") or t.get("name:ru") or t.get("ref") or "(атаусыз)"
            ex = []
            for k in ("name:ru", "ref", "voltage", "cables", "operator", "substance", "location", "surface",
                      "lanes", "int_ref", "description", "intermittent", "water", "landuse", "religion",
                      "addr:street", "addr:housenumber", "building", "amenity", "shop", "note", "fixme"):
                if k in t and t[k] != nm:
                    ex.append("%s=%s" % (k, t[k]))
            dr, bd = bearing_xy(*c)
            hv = hav(P[0], P[1], lat, lon)
            print("  %7.3f км (hav %7.3f) %-2s %3.0f°%s | %s | %s/%d | %.5f,%.5f | %s" % (
                dist, hv, dr, bd, " [ІШІНДЕ]" if isin else "", nm, e["type"], e["id"], lat, lon, "; ".join(ex)))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 10)
