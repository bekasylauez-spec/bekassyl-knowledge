# plot jobs for Выпуск sheets 3.9-3.11 (windows from the 5-storey album jobs)
import json, os, sys
w = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(w, "pt")
os.makedirs(out, exist_ok=True)
J = [
    {"n": "s39", "x0": 736399.3350914121, "y0": -649167.435383603, "x1": 825574.3350914121, "y1": -617667.435383603, "sc": 75.0, "media": "ISO_full_bleed_B0_(1414.00_x_1000.00_MM)"},
    {"n": "s310", "x0": 825574.3350914121, "y0": -649167.435383603, "x1": 855274.3350914121, "y1": -628167.435383603, "sc": 50.0, "media": "ISO_full_bleed_A2_(594.00_x_420.00_MM)"},
    {"n": "s311", "x0": 855274.3350914121, "y0": -649167.435383603, "x1": 862699.3350914121, "y1": -638667.435383603, "sc": 25.0, "media": "ISO_full_bleed_A3_(297.00_x_420.00_MM)"},
]
for j in J:
    j["out"] = os.path.join(out, j["n"] + ".pdf")
json.dump(J, open(os.path.join(out, "plotc.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(out)
