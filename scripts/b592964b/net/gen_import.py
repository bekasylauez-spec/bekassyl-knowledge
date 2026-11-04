import json, os, sys
S = sys.argv[1]
res = json.load(open(os.path.join(S, 'km', 'bait_sheets.json')))
f = os.path.normpath(os.path.join(S, 'km', 'bait.dwg'))
ops = [{"t": "import", "file": f, "base": [0, 0], "to": [0, 0], "h": hs, "pre": "B" + k + ":"} for k, hs in res.items()]
json.dump(ops, open(os.path.join(S, 'net', 'o_import.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(len(ops), f)
