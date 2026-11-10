# -*- coding: utf-8 -*-
"""Плита арматурасы — 3D анимация кадрларын PIL-мен салып, ffmpeg-ке жібереді."""
import os, sys, json, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from scenes import SCENES
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(__file__)
DUR = json.load(open(os.path.join(HERE, "audio", "dur.json")))
PAD = 1.2                      # әр сахна соңындағы үнсіздік, с
FPS = 25
W, H = 1280, 720
SS = 2                         # supersample
WS, HS = W * SS, H * SS
PREVIEW = "--preview" in sys.argv

# ---------------- геометрия (мм) ----------------
L = 7200.0                     # плита өлшемі
T = 220.0                      # қалыңдығы
VS = 4.0                       # биіктік масштабы (тек плита ішінде)
COLS = [(600.0, 600.0), (6600.0, 600.0), (600.0, 6600.0), (6600.0, 6600.0)]
CH = 200.0                     # колонна жарты өлшемі
zBX, zBY, zTX, zTY = 36.0, 48.0, 172.0, 184.0
SP = 200.0
D_EFF = 180.0

def Z(z):
    return z * VS if z >= 0 else z

# топтар: name -> list of (polyline pts (N,3) real, colour, dia)
C_BOT = (40, 110, 220); C_TOP = (210, 45, 45); C_FROG = (235, 175, 0)
C_DOP = (255, 120, 20); C_PUN = (20, 165, 70); C_U = (140, 60, 200); C_CHAIR = (90, 90, 90)
G = {}
def add(g, pts, col, dia=12.0):
    G.setdefault(g, []).append((np.array(pts, float), col, dia))

pos = np.arange(100.0, L, SP)            # 100..7100
for y in pos: add("botX", [(30, y, zBX), (L - 30, y, zBX)], C_BOT)
for x in pos: add("botY", [(x, 30, zBY), (x, L - 30, zBY)], C_BOT)
for y in pos: add("topX", [(30, y, zTX), (L - 30, y, zTX)], C_TOP)
for x in pos: add("topY", [(x, 30, zTY), (x, L - 30, zTY)], C_TOP)
# стульчиктер — шаг 800, төменгі X стерженьдерінің астында
for i, y in enumerate(pos[::4]):
    for x in np.arange(400.0, L, 800.0):
        add("chair", [(x - 25, y, 0), (x, y, zBX - 6), (x + 25, y, 0)], C_CHAIR, 10)
# лягушкалар Ф-1: шахмат 800x800
for j, y in enumerate(pos[2::4]):
    off = 400.0 if j % 2 else 0.0
    for x in np.arange(800.0 + off, L - 600, 800.0):
        if any(abs(x - cx) < 500 and abs(y - cy) < 500 for cx, cy in COLS):
            continue
        add("frog", [(x - 450, y, 60), (x - 150, y, 60), (x - 150, y, 160), (x + 150, y, 160),
                     (x + 150, y, 60), (x + 450, y, 60)], C_FROG)
# қосымша жоғарғы — колонна үстінде, негізгілер арасында (y = 200k)
for cx, cy in COLS:
    for y in np.arange(200.0, L, SP):
        if abs(y - cy) <= 1400:
            add("dopT", [(max(30, cx - 1800), y, zTX), (min(L - 30, cx + 1800), y, zTX)], C_DOP)
    for x in np.arange(200.0, L, SP):
        if abs(x - cx) <= 1400:
            add("dopT", [(x, max(30, cy - 1800), zTY), (x, min(L - 30, cy + 1800), zTY)], C_DOP)
# қосымша төменгі — аралықта
for y in np.arange(200.0, L, SP):
    if abs(y - 3600) <= 1200: add("dopB", [(2000, y, zBX), (5200, y, zBX)], C_DOP)
for x in np.arange(200.0, L, SP):
    if abs(x - 3600) <= 1200: add("dopB", [(x, 2000, zBY), (x, 5200, zBY)], C_DOP)
# продавливание шпилькалары
for cx, cy in COLS:
    for r in (90.0, 225.0, 360.0, 495.0):
        a = CH + r
        n = max(2, int(round(2 * a / 150.0)))
        ring = []
        for k in range(n):
            t = -a + 2 * a * k / n
            ring += [(cx + t, cy - a), (cx + a, cy + t), (cx - t, cy + a), (cx - a, cy - t)]
        for px, py in ring:
            if not (60 < px < L - 60 and 60 < py < L - 60): continue
            add("pun", [(px + 45, py, 192), (px, py, 192), (px, py, 26), (px - 45, py, 26)], C_PUN, 10)
# П-скобалар шеттерде
for y in pos:
    add("ubar", [(600, y + 50, zTX), (30, y + 50, zTX), (30, y + 50, zBX), (600, y + 50, zBX)], C_U)
    add("ubar", [(L - 600, y + 50, zTX), (L - 30, y + 50, zTX), (L - 30, y + 50, zBX), (L - 600, y + 50, zBX)], C_U)
for x in pos:
    add("ubar", [(x + 50, 600, zTY), (x + 50, 30, zTY), (x + 50, 30, zBY), (x + 50, 600, zBY)], C_U)
    add("ubar", [(x + 50, L - 600, zTY), (x + 50, L - 30, zTY), (x + 50, L - 30, zBY), (x + 50, L - 600, zBY)], C_U)

ORDER = ["chair", "botX", "botY", "dopB", "pun", "frog", "topX", "topY", "dopT", "ubar"]

# ---------------- камера ----------------
class Cam:
    def __init__(s, tgt, yaw, pitch, dist, fov=1.0):
        s.T = np.array(tgt, float)
        a, p = math.radians(yaw), math.radians(pitch)
        s.C = s.T + dist * np.array([math.cos(p) * math.cos(a), math.cos(p) * math.sin(a), math.sin(p)])
        f = s.T - s.C; s.f = f / np.linalg.norm(f)
        r = np.cross(s.f, [0, 0, 1.0]); s.r = r / np.linalg.norm(r)
        s.u = np.cross(s.r, s.f)
        s.F = WS * 0.5 / math.tan(math.radians(28)) * fov
    def proj(s, P):   # P (N,3) visual coords
        d = P - s.C
        x = d @ s.r; y = d @ s.u; z = d @ s.f
        z = np.maximum(z, 1.0)
        return np.stack([WS / 2 + s.F * x / z, HS / 2 - s.F * y / z], 1), z

def vis(P):
    P = np.array(P, float).copy()
    P[:, 2] = np.where(P[:, 2] >= 0, P[:, 2] * VS, P[:, 2])
    return P

def ease(t):
    t = min(1, max(0, t)); return t * t * (3 - 2 * t)

def lerp(a, b, t): return a + (b - a) * t

# ---------------- салу примитивтері ----------------
def draw_poly3(dr, cam, pts, fill, outline=None, w=1):
    s, _ = cam.proj(vis(pts))
    dr.polygon([tuple(p) for p in s], fill=fill, outline=outline)
    if outline and w > 1:
        dr.line([tuple(p) for p in s] + [tuple(s[0])], fill=outline, width=w)

def shade(c, k):
    return tuple(int(max(0, min(255, v * k))) for v in c[:3]) + tuple(c[3:])

def draw_bar(dr, cam, pts, col, dia, dz=0.0, alpha=1.0, hl=1.0):
    P = pts.copy(); P[:, 2] += dz
    s, z = cam.proj(vis(P))
    wpx = max(2, int(cam.F * dia * 1.6 / float(np.mean(z))))
    c = shade(col, hl)
    pl = [tuple(p) for p in s]
    dr.line(pl, fill=c, width=wpx, joint="curve")

def draw_columns(dr, cam):
    faces = []
    for cx, cy in COLS:
        x0, x1, y0, y1 = cx - CH, cx + CH, cy - CH, cy + CH
        zb, zt = -2600.0, 0.0
        sides = [([(x0, y0, zb), (x1, y0, zb), (x1, y0, zt), (x0, y0, zt)], 0.85),
                 ([(x1, y0, zb), (x1, y1, zb), (x1, y1, zt), (x1, y0, zt)], 0.7),
                 ([(x1, y1, zb), (x0, y1, zb), (x0, y1, zt), (x1, y1, zt)], 0.6),
                 ([(x0, y1, zb), (x0, y0, zb), (x0, y0, zt), (x0, y1, zt)], 0.75)]
        for f, k in sides:
            c = np.array(f).mean(0); d = np.linalg.norm(vis([c])[0] - cam.C)
            faces.append((d, f, k))
    faces.sort(key=lambda t: -t[0])
    for d, f, k in faces:
        draw_poly3(dr, cam, f, shade((150, 150, 155), k), outline=(70, 70, 75))

def slab_faces(z0, z1):
    return [([(0, 0, z1), (L, 0, z1), (L, L, z1), (0, L, z1)], 1.0),
            ([(0, 0, z0), (L, 0, z0), (L, 0, z1), (0, 0, z1)], 0.8),
            ([(L, 0, z0), (L, L, z0), (L, L, z1), (L, 0, z1)], 0.68),
            ([(L, L, z0), (0, L, z0), (0, L, z1), (L, L, z1)], 0.6),
            ([(0, L, z0), (0, 0, z0), (0, 0, z1), (0, L, z1)], 0.74)]

def draw_slab(img, cam, alpha, ztop=T, col=(185, 185, 180)):
    if alpha <= 0: return img
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fs = slab_faces(0.0, ztop)
    fs = sorted(fs, key=lambda t: -np.linalg.norm(vis([np.array(t[0]).mean(0)])[0] - cam.C))
    for f, k in fs:
        draw_poly3(d, cam, f, shade(col, k) + (int(255 * alpha),), outline=(100, 100, 100, int(255 * alpha)))
    return Image.alpha_composite(img, lay)

def draw_formwork(img, cam, alpha):
    if alpha <= 0: return img
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    m = 300
    draw_poly3(d, cam, [(-m, -m, -1), (L + m, -m, -1), (L + m, L + m, -1), (-m, L + m, -1)],
               (214, 180, 120, int(235 * alpha)), outline=(150, 115, 60, int(255 * alpha)))
    # фанера парақтары
    for x in np.arange(-m, L + m + 1, 1220):
        s, _ = cam.proj(vis([(x, -m, 0), (x, L + m, 0)]))
        d.line([tuple(s[0]), tuple(s[1])], fill=(170, 135, 80, int(200 * alpha)), width=2)
    for cx, cy in COLS:
        draw_poly3(d, cam, [(cx - CH, cy - CH, 0), (cx + CH, cy - CH, 0), (cx + CH, cy + CH, 0), (cx - CH, cy + CH, 0)],
                   (120, 120, 125, int(255 * alpha)))
    return Image.alpha_composite(img, lay)

# ---------------- деформация (s2) ----------------
def wdef(x, y, A):
    u = (x - 600) / 6000.0; v = (y - 600) / 6000.0
    return A * ((1 - np.cos(2 * np.pi * u)) + (1 - np.cos(2 * np.pi * v))) / 4.0

def draw_deformed(img, cam, A, colorize):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    N = 30; xs = np.linspace(0, L, N + 1)
    quads = []
    for i in range(N):
        for j in range(N):
            x0, x1, y0, y1 = xs[i], xs[i + 1], xs[j], xs[j + 1]
            cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
            pts = [(x, y, T - wdef(x, y, A) / VS) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
            dd = np.linalg.norm(vis([(cxm, cym, T)])[0] - cam.C)
            m = math.cos(2 * math.pi * (cxm - 600) / 6000) + math.cos(2 * math.pi * (cym - 600) / 6000)
            quads.append((dd, pts, m))
    quads.sort(key=lambda t: -t[0])
    for dd, pts, m in quads:
        base = np.array([190, 190, 185], float)
        if colorize > 0:
            if m > 0: tgt = np.array([230, 70, 60]) ; k = min(1, m / 1.2)
            else: tgt = np.array([60, 110, 230]); k = min(1, -m / 1.2)
            base = lerp(base, tgt, k * colorize)
        draw_poly3(d, cam, pts, tuple(int(v) for v in base) + (255,), outline=(120, 120, 120, 255))
    return Image.alpha_composite(img, lay)

def draw_loads(dr, cam, t):
    for x in np.arange(900, L, 1200):
        for y in np.arange(900, L, 1200):
            top = vis([(x, y, T + 260)])[0]; bot = vis([(x, y, T + 10)])[0]
            k = (t * 2.0) % 1.0
            off = np.array([0, 0, 120 * k])
            s, z = cam.proj(np.array([top + off, bot + off]))
            dr.line([tuple(s[0]), tuple(s[1])], fill=(30, 30, 30), width=3)
            hx = s[1]; dr.polygon([(hx[0] - 9, hx[1] - 18), (hx[0] + 9, hx[1] - 18), (hx[0], hx[1])], fill=(30, 30, 30))

def draw_mdiag(dr, fnt, a):
    """2D inset: колонна жолағы бойынша М эпюрасы (созылған талшық жағында)."""
    if a <= 0: return
    x0, y0, w, h = WS - 1060, HS - 560, 980, 420
    dr.rounded_rectangle([x0, y0, x0 + w, y0 + h], 24, fill=(255, 255, 255, int(235 * a)), outline=(60, 60, 60))
    dr.text((x0 + 30, y0 + 18), "Эпюра М (колонна жолағы)", font=fnt, fill=(20, 20, 20))
    ya = y0 + 230; xa, xb = x0 + 90, x0 + w - 90
    dr.line([(xa - 40, ya), (xb + 40, ya)], fill=(30, 30, 30), width=5)
    for xc in (xa, xb):
        dr.polygon([(xc, ya + 4), (xc - 22, ya + 46), (xc + 22, ya + 46)], fill=(120, 120, 125))
    pts_top, pts_bot = [], []
    n = 80; curve = []
    for i in range(n + 1):
        u = i / n
        m = math.cos(2 * math.pi * u)       # +: тірек (жоғары созылу) ; −: аралық
        curve.append((lerp(xa, xb, u), ya - 120 * m * a))
    poly_neg = [(xa, ya)] + curve + [(xb, ya)]
    dr.polygon(poly_neg, fill=(230, 230, 230))
    for i in range(n):
        u = (i + 0.5) / n; m = math.cos(2 * math.pi * u)
        dr.line([curve[i], curve[i + 1]], fill=(210, 50, 45) if m > 0 else (45, 95, 215), width=6)
    for i in range(0, n + 1, 4):
        dr.line([(curve[i][0], ya), curve[i]], fill=(150, 150, 150), width=2)
    dr.text((xa + 10, ya - 175), "−M (жоғары созылу)", font=fnt, fill=(200, 40, 40))
    dr.text((xa + 290, ya + 70), "+M (төмен созылу)", font=fnt, fill=(40, 80, 200))

def draw_cone(img, cam, alpha):
    if alpha <= 0: return img
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for cx, cy in COLS:
        a0, a1 = CH, CH + 2 * D_EFF
        b = [(cx - a0, cy - a0, 0), (cx + a0, cy - a0, 0), (cx + a0, cy + a0, 0), (cx - a0, cy + a0, 0)]
        t = [(cx - a1, cy - a1, T), (cx + a1, cy - a1, T), (cx + a1, cy + a1, T), (cx - a1, cy + a1, T)]
        for i in range(4):
            j = (i + 1) % 4
            draw_poly3(d, cam, [b[i], b[j], t[j], t[i]], (230, 40, 40, int(90 * alpha)), outline=(200, 20, 20, int(255 * alpha)))
        s, _ = cam.proj(vis(t))
        d.line([tuple(p) for p in s] + [tuple(s[0])], fill=(200, 20, 20, int(255 * alpha)), width=5)
    return Image.alpha_composite(img, lay)

# ---------------- сахна логикасы ----------------
HOME = ((3600, 3600, 250), -58, 34, 15500)
CAMS = {
 "s1": (((3600, 3600, 0), -30, 26, 17000), ((3600, 3600, 0), -75, 34, 15500)),
 "s2": (((3600, 3600, 0), -60, 26, 15000), ((3600, 3600, 0), -48, 30, 14500)),
 "s3": (HOME, ((3600, 3600, 250), -70, 40, 14000)),
 "s4": (((3600, 3600, 250), -70, 40, 14000), ((3400, 3300, 400), -78, 24, 5600)),
 "s5": (((3400, 3300, 400), -78, 24, 5600), HOME),
 "s6": (HOME, ((3600, 3600, 250), -45, 50, 14500)),
 "s7": (((3600, 3600, 250), -45, 50, 14500), ((700, 700, 350), -120, 26, 3800)),
 "s8": (((700, 700, 350), -120, 26, 3800), ((1800, 1800, 300), -150, 28, 9000)),
 "s9": (((1800, 1800, 300), -150, 28, 9000), ((3600, 3600, 0), -40, 32, 16500)),
}
# s4 ішінде: жақындатып, соңында кері шығамыз; s7: колоннаға жақындау
APPEAR = {  # group: (scene, s0, s1)
 "chair": ("s3", 0.08, 0.25), "botX": ("s3", 0.28, 0.50), "botY": ("s3", 0.50, 0.70),
 "frog": ("s4", 0.08, 0.40), "topX": ("s5", 0.05, 0.30), "topY": ("s5", 0.30, 0.55),
 "dopT": ("s6", 0.10, 0.40), "dopB": ("s6", 0.45, 0.62),
 "pun": ("s7", 0.42, 0.80), "ubar": ("s8", 0.10, 0.55),
}
SIDS = [s[0] for s in SCENES]
LEG = {"botX": ("Төменгі тор", C_BOT), "frog": ("Фиксатор Ф-1", C_FROG), "topX": ("Жоғарғы тор", C_TOP),
       "dopT": ("Қосымша арматура", C_DOP), "pun": ("Көлденең арматура", C_PUN), "ubar": ("П-скоба", C_U)}

def cam_at(sid, p):
    (a, b) = CAMS[sid]
    if sid == "s4":   # 0..0.55 жақындау, 0.55..1 сол жерде
        k = ease(p / 0.45)
    elif sid == "s7":
        k = ease(p / 0.35)
    else:
        k = ease(p)
    tg = lerp(np.array(a[0], float), np.array(b[0], float), k)
    return Cam(tg, lerp(a[1], b[1], k), lerp(a[2], b[2], k), lerp(a[3], b[3], k))

def group_progress(g, si, p):
    sc, a, b = APPEAR[g]; gi = SIDS.index(sc)
    if si > gi: return 1.0
    if si < gi: return 0.0
    return min(1, max(0, (p - a) / (b - a)))

FONT = "C:/Windows/Fonts/segoeui.ttf"; FONTB = "C:/Windows/Fonts/segoeuib.ttf"
fT = ImageFont.truetype(FONTB, 50); fB = ImageFont.truetype(FONT, 38); fS = ImageFont.truetype(FONT, 32)
fBig = ImageFont.truetype(FONTB, 76)

def captions(img, si, p, tg):
    sid, _, title, bullets = SCENES[si]
    d = ImageDraw.Draw(img, "RGBA")
    if sid == "s1" and p < 0.95:
        # үлкен атау
        a = min(1, p / 0.08)
        d.rounded_rectangle([90, 120, WS - 90, 330], 30, fill=(15, 25, 45, int(215 * a)))
        d.text((WS / 2, 195), "Монолит плита на колоннах", font=fBig, fill=(255, 255, 255, int(255 * a)), anchor="mm")
        d.text((WS / 2, 280), "жұмысы және арматуралау тәртібі", font=fT, fill=(200, 220, 255, int(255 * a)), anchor="mm")
    else:
        tw = d.textlength(title, font=fT)
        d.rounded_rectangle([50, 40, 50 + tw + 60, 125], 20, fill=(15, 25, 45, 220))
        d.text((80, 82), title, font=fT, fill=(255, 255, 255), anchor="lm")
    y = 160 if sid != "s1" else 380
    for fr, txt in bullets:
        if p < fr: continue
        a = min(1, (p - fr) / 0.04)
        tw = d.textlength("• " + txt, font=fB)
        d.rounded_rectangle([50, y - 8, 50 + tw + 50, y + 56], 14, fill=(255, 255, 255, int(225 * a)))
        d.text((75, y + 24), "• " + txt, font=fB, fill=(15, 25, 45, int(255 * a)), anchor="lm")
        y += 76
    # легенда
    if sid not in ("s1", "s2"):
        items = [(n, c) for gk, (n, c) in LEG.items() if tg.get(gk, 0) > 0]
        yy = HS - 100 - 56 * len(items)
        if items:
            d.rounded_rectangle([WS - 500, yy - 14, WS - 40, yy + 56 * len(items) + 6], 16, fill=(255, 255, 255, 215))
        for n, c in items:
            d.rectangle([WS - 470, yy + 14, WS - 410, yy + 30], fill=c)
            d.text((WS - 390, yy + 22), n, font=fS, fill=(20, 20, 20), anchor="lm")
            yy += 56
    if sid != "s1":
        d.text((40, HS - 40), "Биіктік масштабы ×4 үлкейтілген · сызба шартты", font=fS, fill=(80, 80, 80), anchor="lm")

def bg():
    a = np.linspace(0, 1, HS)[:, None]
    top = np.array([236, 241, 248]); bot = np.array([205, 214, 226])
    g = (top * (1 - a) + bot * a).astype(np.uint8)
    arr = np.repeat(g[:, None, :], WS, 1).reshape(HS, WS, 3)
    return Image.fromarray(arr, "RGB").convert("RGBA")
BG = bg()

def frame(si, p, tsec):
    sid = SIDS[si]
    cam = cam_at(sid, p)
    img = BG.copy()
    d = ImageDraw.Draw(img, "RGBA")
    draw_columns(d, cam)
    tg = {g: group_progress(g, si, p) for g in APPEAR}
    if sid == "s1":
        img = draw_slab(img, cam, 1.0)
    elif sid == "s2":
        A = 900 * ease(p / 0.3)
        img = draw_deformed(img, cam, A, ease((p - 0.25) / 0.2))
        d = ImageDraw.Draw(img, "RGBA")
        if p < 0.6: draw_loads(d, cam, tsec)
        draw_mdiag(d, fS, ease((p - 0.65) / 0.1))
    else:
        fw = 1.0
        if sid == "s9": fw = 1.0
        img = draw_formwork(img, cam, fw)
        if sid == "s7":
            img = draw_cone(img, cam, ease((p - 0.12) / 0.1) * (1 - 0.6 * ease((p - 0.45) / 0.1)))
        d = ImageDraw.Draw(img, "RGBA")
        for g in ORDER:
            k = tg[g]
            if k <= 0: continue
            items = G[g]; n = len(items)
            hl = 1.0
            for i, (pts, col, dia) in enumerate(items):
                ti = k * (n + 6) - i      # бір-бірлеп түседі
                if ti <= 0: break
                dz = 120.0 * (1 - ease(ti / 6.0))
                draw_bar(d, cam, pts, col, dia, dz=dz)
        if sid == "s3":
            img = draw_slab(img, cam, 1 - ease(p / 0.06))
        if sid == "s9":
            pc = ease((p - 0.05) / 0.3)
            img = draw_slab(img, cam, 0.92 * pc, ztop=max(1, T * min(1, pc * 1.0)))
    captions(img, si, p, tg)
    return img.convert("RGB").resize((W, H), Image.LANCZOS)

def main():
    if PREVIEW:
        os.makedirs(os.path.join(HERE, "prev"), exist_ok=True)
        for si, sid in enumerate(SIDS):
            for p in (0.3, 0.9):
                frame(si, p, 0).save(os.path.join(HERE, "prev", f"{sid}_{int(p*100)}.png"))
        return
    out = os.path.join(HERE, "video_noaudio.mp4")
    pr = subprocess.Popen([FF, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "25", "-preset", "slow", "-tune", "animation", out],
                          stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    tot = 0
    for si, sid in enumerate(SIDS):
        dur = DUR[sid] + PAD
        nf = int(round(dur * FPS))
        for f in range(nf):
            t = f / FPS
            pr.stdin.write(frame(si, t / dur, tot + t).tobytes())
        tot += nf / FPS
        print(sid, nf, flush=True)
    pr.stdin.close(); pr.wait()
    print("done", tot)

if __name__ == "__main__":
    main()
