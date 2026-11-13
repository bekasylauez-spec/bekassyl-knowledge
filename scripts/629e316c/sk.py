import sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
h1 = 4200/23; b = 250
fig, (a, p) = plt.subplots(2, 1, figsize=(11, 13), gridspec_kw={"height_ratios":[3,1]})
def flight(ax, x, z, n, h, d, c):
    xs=[x]; zs=[z]
    for i in range(n):
        z += h; xs.append(x); zs.append(z)
        if i < n-1: x += d*b; xs.append(x); zs.append(z)
    ax.plot(xs, zs, c, lw=1.6); return x, z
# marsh 1
x, z = flight(a, 0, -1000, 18, h1, 1, "b")
zi = z; a.plot([x, x+1000], [z, z], "k", lw=3)
x2, z2 = flight(a, x+1000, z, 5, h1, 1, "b"); a.plot([x2, x2+1200], [z2, z2], "k", lw=3)
h2 = (6400-zi)/22
x3, z3 = flight(a, x, zi, 22, h2, -1, "r"); a.plot([x3, x3-1200], [z3, z3], "k", lw=3)
a.plot([x3-1300, x3+900], [8700, 8500], "g", lw=2)
for lv, t in ((-1000,"-1.000 жер"),(0,"0.000 1-қабат"),(3200,"+3.200 2-қабат"),(6400,"+6.400 3-қабат"),(8600,"+8.600 навес"),(zi,f"+{zi/1000:.3f} аралық алаң")):
    a.axhline(lv, color="gray", lw=0.5, ls="--"); a.text(7700, lv+40, t, fontsize=9)
for cx in (0, 4250, 5250, 7450, x3-1200): a.plot([cx,cx],[-1000,8500],color="0.6",lw=1)
a.text(1500, 300, "М1: 18 көтерілім x 183, басқыш 250", color="b", fontsize=9, rotation=36)
a.text(5300, 2450, "М2: 5 x 183", color="b", fontsize=9)
a.text(900, 4900, f"М3: 22 x {h2:.0f}", color="r", fontsize=9)
a.set_aspect("equal"); a.set_title("Қабырға бойымен көрініс (шамамен, фотодан)"); a.set_xlim(-2600, 9800)
# plan
p.plot([-2600, 7700], [0,0], "k", lw=4); p.text(-2500, -260, "үй қабырғасы")
p.add_patch(plt.Rectangle((0,150), 4250, 800, fill=False, ec="b")); p.text(1500, 480, "М1 (жоғары →)", color="b")
p.add_patch(plt.Rectangle((4250,150), 1000, 1700, fill=False, ec="k", lw=2)); p.text(4300, 1000, "аралық\nалаң", fontsize=8)
p.add_patch(plt.Rectangle((5250,150), 1000, 800, fill=False, ec="b")); p.text(5300, 480, "М2", color="b")
p.add_patch(plt.Rectangle((6250,150), 1200, 1700, fill=False, ec="k", lw=2)); p.text(6300, 1000, "+3.200\nалаң, есік", fontsize=8)
p.add_patch(plt.Rectangle((x3,1050), 4250-x3, 800, fill=False, ec="r")); p.text(1500, 1380, "← М3 (жоғары)", color="r")
p.add_patch(plt.Rectangle((x3-1200,150), 1200, 1700, fill=False, ec="k", lw=2)); p.text(x3-1150, 1000, "+6.400\nалаң", fontsize=8)
p.set_aspect("equal"); p.set_title("Жоспар (шамамен)"); p.set_xlim(-2600, 9800); p.set_ylim(-500, 2300)
plt.tight_layout(); plt.savefig(sys.argv[1], dpi=110)
print(round(zi), round(h2,1), x3)
