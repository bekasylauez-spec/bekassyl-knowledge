# -*- coding: utf-8 -*-
"""Плиткалардан карта негізін құрау (Web Mercator). Плиткалар tiles/ папкасына кэштеледі."""
import math, os, io, time
import requests
from PIL import Image

UA = {"User-Agent": "plot-surroundings-map/1.0 (one-off research render)"}
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "tiles")

SOURCES = {
    "osm": "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    "esri": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
}


def ll2px(lat, lon, z):
    n = 256 * 2 ** z
    x = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def get_tile(src, z, x, y):
    os.makedirs(os.path.join(CACHE, src, str(z)), exist_ok=True)
    fn = os.path.join(CACHE, src, str(z), "%d_%d.img" % (x, y))
    if not os.path.exists(fn) or os.path.getsize(fn) < 100:
        url = SOURCES[src].format(z=z, x=x, y=y)
        for attempt in range(3):
            r = requests.get(url, headers=UA, timeout=40)
            if r.status_code == 200 and len(r.content) > 100:
                open(fn, "wb").write(r.content)
                break
            time.sleep(1.5)
        else:
            raise RuntimeError("tile failed %s %s" % (url, r.status_code))
        time.sleep(0.15)
    return Image.open(fn).convert("RGB")


class Base:
    """lat/lon шекарасы бойынша негіз суреті; to_xy(lat, lon) — сурет пикселі (масштабталған)."""

    def __init__(self, src, z, lat_min, lat_max, lon_min, lon_max, scale=1.0):
        self.z, self.scale = z, scale
        x0, y0 = ll2px(lat_max, lon_min, z)
        x1, y1 = ll2px(lat_min, lon_max, z)
        self.x0, self.y0 = x0, y0
        tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
        mosaic = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
        n = 0
        for tx in range(tx0, tx1 + 1):
            for ty in range(ty0, ty1 + 1):
                mosaic.paste(get_tile(src, z, tx, ty), ((tx - tx0) * 256, (ty - ty0) * 256))
                n += 1
        self.ntiles = n
        crop = mosaic.crop((int(x0 - tx0 * 256), int(y0 - ty0 * 256), int(x1 - tx0 * 256), int(y1 - ty0 * 256)))
        self.w0, self.h0 = crop.size
        if scale != 1.0:
            crop = crop.resize((int(self.w0 * scale), int(self.h0 * scale)), Image.LANCZOS)
        self.img = crop
        self.w, self.h = crop.size
        # 1 пиксельдегі метр (сурет ортасының ендігінде)
        latc = (lat_min + lat_max) / 2
        self.m_per_px = 156543.03392 * math.cos(math.radians(latc)) / 2 ** z / scale

    def to_xy(self, lat, lon):
        x, y = ll2px(lat, lon, self.z)
        return (x - self.x0) * self.scale, (y - self.y0) * self.scale
