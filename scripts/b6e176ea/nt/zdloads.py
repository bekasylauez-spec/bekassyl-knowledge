# -*- coding: utf-8 -*-
# Design forces on Зд-1 (base of columns Ст1, stiffness 1) from LIRA РСН (ULS groups I and III), kN / kN*m
import csv, io, json, sys
W = "C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/"
G = 9.81


def rd(p):
    return list(csv.reader(io.StringIO(open(p, "rb").read().decode("cp1251", errors="replace")), delimiter=";"))


def calc(task):
    A = W + task + ".DOCS/AUTORES/"
    z = {int(r[2]): float(r[5]) for r in rd(A + "tbl01.101.csv")[1:] if len(r) > 5 and r[2].strip().isdigit()}
    cols = {}
    for r in rd(A + "tbl02.102.csv")[1:]:
        if len(r) > 13 and r[5].strip() not in ("2", "3", "4", "5", "6"):  # columns Ст1 (type 1, or 7/8 after the 70x4 change)
            ns = [int(x) for x in r[13].replace(",", " ").split()]
            nsec = int(r[4])
            cols[int(r[2])] = 1 if z[ns[0]] < z[ns[-1]] else nsec
    names = {int(r[2]): r[3] for r in rd(A + "tbl10.116.csv")[1:] if len(r) > 3 and r[2].strip().isdigit()}
    rows = []
    for r in rd(A + "tbl10.22_1.csv")[1:]:
        if len(r) < 13:
            continue
        rsn = int(r[2].split("(")[0].replace("\ufeff", "").replace("п»ї", "").strip())
        if names[rsn].split("_")[1] not in ("I", "III"):
            continue
        el, sec = int(r[5]), int(r[6])
        if cols.get(el) != sec:
            continue
        N, MY, QZ, MZ, QY = (float(r[i] or 0) * G for i in (7, 9, 10, 11, 12))
        rows.append(dict(rsn=names[rsn].rsplit("_", 1)[0], el=el, N=N, Mx=MZ, Qy=QY, My=MY, Qx=QZ))
    pick = {
        "N max": max(rows, key=lambda r: r["N"]),
        "N min": min(rows, key=lambda r: r["N"]),
        "M max": max(rows, key=lambda r: max(r["Mx"], r["My"])),
        "M min": min(rows, key=lambda r: min(r["Mx"], r["My"])),
        "Q max": max(rows, key=lambda r: max(r["Qx"], r["Qy"])),
        "Q min": min(rows, key=lambda r: min(r["Qx"], r["Qy"])),
    }
    return pick, len(cols), len(rows)


if __name__ == "__main__":
    out = {}
    for t in sys.argv[1:]:
        p, nc, nr = calc(t)
        out[t] = p
        print(t, "columns", nc, "rows", nr)
        for k, r in p.items():
            print("  %-6s N=%7.2f Mx=%6.3f Qy=%6.3f My=%6.3f Qx=%6.3f  %s el%d" % (k, r["N"], r["Mx"], r["Qy"], r["My"], r["Qx"], r["rsn"], r["el"]))
    json.dump(out, open("zd.json", "w", encoding="utf-8"), ensure_ascii=False)
