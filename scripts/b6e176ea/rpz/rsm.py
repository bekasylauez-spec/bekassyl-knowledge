import struct, sys, json
W = r"C:/Users/Public/Documents/LIRA SAPR/LIRA SAPR 2024/Work/"


def read_rsm(nm, nloads=7):
    d = open(W + nm + "#rsm." + nm, "rb").read()
    cnt = struct.unpack_from("<I", d, 4)[0]
    p = 8; out = []
    for _ in range(cnt):
        n = struct.unpack_from("<I", d, p)[0]; p += 4
        loads = struct.unpack_from("<%dH" % n, d, p); p += 2 * n
        k = struct.unpack_from("<%df" % n, d, p); p += 4 * n
        row = [0.0] * nloads
        for L, c in zip(loads, k):
            row[L - 1] = round(c, 3)
        out.append(row)
    assert p == len(d), (p, len(d))
    return out


if __name__ == "__main__":
    for nm in sys.argv[1:]:
        for r in read_rsm(nm):
            print(r)
        print()
