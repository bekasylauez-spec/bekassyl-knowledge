# common helpers for rigel sheets (ЖК Галакси, analog «Ресторан 6.1 Ригель»)
import math

def zones(fL, fR):
    """hoops from face+50 to face-50: 100xN1 | 200xN2 (+ odd r) | 100xN3. Returns (h0, [(a,b,text)], lines, count)"""
    h0, h4 = fL + 50, fR - 50
    Lp = h4 - h0
    n1 = int(round(Lp / 4 / 100.0)); n3 = n1
    rest = Lp - 100 * (n1 + n3)
    n2 = int(rest // 200); r = rest - 200 * n2
    if abs(r) < 0.5: r = 0
    elif abs(r - 100) < 0.5: n3 += 1; r = 0
    elif r < 100: n2 -= 1; r += 200; n3 += 1; r -= 100
    segs = []
    x = h0
    segs.append((x, x + 100 * n1, '100х%d' % n1)); x += 100 * n1
    segs.append((x, x + 200 * n2, '200х%d' % n2)); x += 200 * n2
    if r: segs.append((x, x + r, '%d' % round(r))); x += r
    segs.append((x, x + 100 * n3, '100х%d' % n3)); x += 100 * n3
    assert abs(x - h4) < 0.5, (fL, fR, x, h4)
    lines = [h0, h0 + 100 * n1, h0 + 100 * n1 + 200 * n2 + r, h4]
    count = n1 + n2 + n3 + 1 + (1 if r else 0)
    return segs, lines, count

if __name__ == '__main__':
    for a, b in [(375, 6550), (7050, 13000), (13500, 19675), (475, 6500), (7100, 12950)]:
        print(a, b, zones(a, b))
