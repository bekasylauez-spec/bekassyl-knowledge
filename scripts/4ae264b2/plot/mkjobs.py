import json, os
S = os.path.dirname(os.path.abspath(__file__))
P = r"C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad"
J = json.load(open(os.path.join(P, "w", "rg", "p72", "plotc.json"), encoding="utf-8-sig"))
for j in J:
    j["out"] = os.path.join(S, j["n"] + ".pdf")
json.dump(J, open(os.path.join(S, "plotc.json"), "w", encoding="utf-8"), ensure_ascii=False)
print(len(J), J[0]["out"])
