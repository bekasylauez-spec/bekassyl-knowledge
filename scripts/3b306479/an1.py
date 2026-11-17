# -*- coding: utf-8 -*-
"""OSM (Overpass) нәтижесін талдау: учаскеден haversine қашықтығы, санат бойынша тізім."""
import json, math, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

P = (43.68733, 76.99701)  # учаске ортасы, WGS84
R = 6371.0088  # орташа Жер радиусы, км


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def bearing(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    b = (math.degrees(math.atan2(y, x)) + 360) % 360
    names = ["С", "СШ", "Ш", "ОШ", "О", "ОБ", "Б", "СБ"]
    return names[int((b + 22.5) // 45) % 8], b


def main(path, maxn=12):
    d = json.load(open(path, encoding="utf-8"))
    els = d["elements"]
    rows = []
    for e in els:
        t = e.get("tags", {})
        if "lat" in e:
            la, lo = e["lat"], e["lon"]
        elif "center" in e:
            la, lo = e["center"]["lat"], e["center"]["lon"]
        else:
            continue
        dist = hav(P[0], P[1], la, lo)
        rows.append((dist, e["type"], e["id"], la, lo, t))
    rows.sort(key=lambda r: r[0])
    print("elements:", len(els), "with coords:", len(rows))

    def cat(t):
        for k in ("amenity", "shop", "healthcare", "railway", "place", "highway", "landuse",
                  "aeroway", "man_made", "power"):
            if k in t:
                return k + "=" + t[k]
        return "other"

    groups = {}
    for r in rows:
        groups.setdefault(cat(r[5]), []).append(r)
    for g in sorted(groups):
        lst = groups[g]
        print("\n### %s  (n=%d)" % (g, len(lst)))
        for r in lst[:maxn]:
            t = r[5]
            nm = t.get("name") or t.get("name:ru") or t.get("name:kk") or t.get("official_name") or "(атаусыз)"
            extra = []
            for k in ("name:ru", "name:kk", "operator", "brand", "religion", "denomination", "addr:city",
                      "addr:place", "addr:street", "addr:housenumber", "isced:level", "population", "ref",
                      "healthcare", "description", "opening_hours", "iata", "icao", "voltage", "substation"):
                if k in t and t[k] != nm:
                    extra.append("%s=%s" % (k, t[k]))
            dr, bd = bearing(P[0], P[1], r[3], r[4])
            print("  %6.2f км %-2s (%3.0f°) | %s | %s/%d | %.5f,%.5f | %s" % (
                r[0], dr, bd, nm, r[1], r[2], r[3], r[4], "; ".join(extra)))


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 12)
