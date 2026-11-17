# -*- coding: utf-8 -*-
"""3-сурет: ЕГКН картасының «Генеральный план — Функциональные зоны» қабатының скриншоттары, белгілерімен."""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mkmap1 import F

HERE = os.path.dirname(os.path.abspath(__file__))
X0, Y0, X1, Y1 = 155, 57, 790, 495  # скриншоттағы карта аумағы
K = 3


def panel(src, marks, title, legend, cols=2):
    im = Image.open(os.path.join(HERE, "shots", src)).convert("RGB").crop((X0, Y0, X1, Y1))
    im = im.resize((im.width * K, im.height * K), Image.LANCZOS)
    im = ImageEnhance.Sharpness(im).enhance(1.4)
    d = ImageDraw.Draw(im)
    for num, x, y, col in marks:
        cx, cy = (x - X0) * K, (y - Y0) * K
        if num == "У":
            d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(230, 0, 0), width=7)
            d.text((cx + 48, cy - 4), "УЧАСКЕ", font=F(40, True), fill=(210, 0, 0), anchor="lm",
                   stroke_width=5, stroke_fill=(255, 255, 255))
            continue
        r = 25
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col, outline=(255, 255, 255), width=4)
        d.text((cx, cy - 2), num, font=F(28 if len(num) == 1 else 24, True), fill=(255, 255, 255), anchor="mm")
    W = im.width
    # тақырып
    th = 64
    lines = legend
    per_col = (len(lines) + cols - 1) // cols
    lh = 40
    lg_h = per_col * lh + 30
    out = Image.new("RGB", (W, th + im.height + lg_h), (252, 252, 250))
    do = ImageDraw.Draw(out)
    do.rectangle([0, 0, W, th], fill=(35, 35, 40))
    do.text((18, th // 2), title, font=F(32, True), fill=(255, 255, 255), anchor="lm")
    out.paste(im, (0, th))
    colw = W // cols
    for i, (num, col, text) in enumerate(lines):
        c, r_ = divmod(i, per_col)
        x = 20 + c * colw
        y = th + im.height + 16 + r_ * lh
        if num == "У":
            do.ellipse([x + 2, y + 2, x + 32, y + 32], outline=(230, 0, 0), width=5)
        else:
            do.ellipse([x, y, x + 34, y + 34], fill=col)
            do.text((x + 17, y + 16), num, font=F(20 if len(num) == 1 else 17, True), fill=(255, 255, 255), anchor="mm")
        do.text((x + 46, y + 17), text, font=F(24), fill=(25, 25, 25), anchor="lm")
    return out


RED, GRY, BLK, GRN, BLU, ORG, PUR, BRN = (200, 30, 30), (90, 90, 90), (20, 20, 20), (30, 130, 60), (25, 95, 200), (215, 110, 0), (120, 70, 170), (140, 80, 20)

A_marks = [("У", 472, 276, RED), ("1", 540, 190, ORG), ("2", 447, 302, GRY), ("3", 418, 150, BLK), ("4", 362, 300, ORG),
           ("5", 359, 277, PUR), ("6", 362, 130, GRY), ("7", 488, 120, RED), ("8", 455, 140, GRN), ("9", 573, 108, PUR),
           ("10", 607, 300, GRY), ("11", 622, 150, BRN), ("12", 680, 100, BLU), ("13", 700, 400, RED),
           ("14", 522, 468, GRY), ("15", 215, 300, ORG), ("16", 267, 150, GRN), ("17", 563, 333, BLU)]
A_leg = [("У", RED, "учаске 03-046-187-767 — «усадебная застройка» аймағында"),
         ("1", ORG, "саяжай массиві: сары — усадебная застройка (тұрғын аймақ)"),
         ("2", GRY, "ірі жол дәлізі, екі тармақ — ≈0,28 км және ≈0,55 км батыста"),
         ("3", BLK, "жобалық теміржол дәлізі — 0,97 км батыста (+ резерв аумақ)"),
         ("4", ORG, "жаңа тұрғын кварталдар (усадебная) — 2,2 км батыста"),
         ("5", PUR, "білім беру мекемесінің орны (күлгін) — 1,9 км батыста"),
         ("6", GRY, "өнеркәсіп аймағы (сұр) — 2,0 км солтүстік-батыста"),
         ("7", RED, "қорғаныс нысандарының аумағы — 2,0 км солтүстікте"),
         ("8", GRN, "жасыл желек аймақтары (ең жақыны учаскеден 99 м)"),
         ("9", PUR, "мектеп және денсаулық сақтау орындары — 3,0–3,4 км ССШ"),
         ("10", GRY, "А-3 Алматы–Қонаев тас жолының дәлізі — 2,3 км шығыста"),
         ("11", BRN, "түзеу мекемелерінің аумағы (қазіргі) — 3,2 км СШ"),
         ("12", BLU, "Заречное — қазіргі ауыл (тұрғын үйлер)"),
         ("13", RED, "жаңа қала бөлігі: 12 қабаттан биік үйлер (қызғылт) — 2,7 км"),
         ("14", GRY, "өнеркәсіп аймағы (оңтүстік) — 3,2 км"),
         ("15", ORG, "сыртқы көлік құрылыстары (әуежай) аумағы — 3,9 км-ден әрі"),
         ("16", GRN, "орман шаруашылығы / жасыл белдеу (Мойынқұм) — 2,4–4,2 км"),
         ("17", BLU, "Қаскелең өзені мен жағалау жолағы — 1,9 км ОШ")]

B_marks = [("У", 472, 273, RED), ("1", 532, 292, RED), ("2", 428, 318, GRY), ("3", 322, 250, GRY),
           ("8", 214, 300, GRY),
           ("4", 478, 414, BLU), ("5", 560, 150, ORG), ("6", 640, 425, GRN), ("7", 690, 185, BLK)]
B_leg = [("У", RED, "учаске (қызыл контур) — квартал ішінде, көше жағында"),
         ("1", RED, "көше дәлізі: қызыл сызық учаскенің алдынан ≈3–4 м өтеді"),
         ("2", GRY, "квартал батысындағы ішкі көше — қызыл сызығы 72 м"),
         ("3", GRY, "ірі жол дәлізі, жақын тармағы (ені ≈70–80 м) — ≈0,28 км"),
         ("8", GRY, "ірі жол дәлізі, алыс тармағы — ≈0,55 км батыста"),
         ("4", BLU, "қызмет көрсету мекемелерінің жобалық орны — 225 м оңтүстікте"),
         ("5", ORG, "сары — усадебная застройка аймағы"),
         ("6", GRN, "бозғылт — жасыл желек аймағы"),
         ("7", BLK, "көк контурлар — тіркелген телімдер; бір бөлігі жол дәлізіне түседі")]


def main():
    a = panel("gp_1km_zones.jpg", A_marks,
              "А. Бас жоспар: функционалдық аймақтар, учаскеден ±5,7 км (ЕГКН, масштаб белгісі 1 км)", A_leg)
    b = panel("gp_100m_lands.jpg", B_marks,
              "Ә. Учаске тұрған квартал: аймақтар, қызыл сызықтар және тіркелген телімдер (масштаб белгісі 100 м)", B_leg)
    W = max(a.width, b.width)
    foot = 46
    out = Image.new("RGB", (W, a.height + b.height + foot), (252, 252, 250))
    out.paste(a, (0, 0))
    out.paste(b, (0, a.height))
    d = ImageDraw.Draw(out)
    d.text((18, a.height + b.height + 8),
           "Дереккөз: map.gov4c.kz/egkn — «Генеральный план» қабаты (ҚР Үкіметінің 17.05.2024 № 388 қаулысы, 09.09.2025 № 727 редакциясы); скриншот 17.11.2026. Қашықтықтар аймақ контурынан есептелген.",
           font=F(20), fill=(80, 80, 80))
    fn = os.path.join(HERE, "3_bas_zhospar_egkn.png")
    out.save(fn, optimize=True)
    print("saved", fn, out.size)


if __name__ == "__main__":
    main()
