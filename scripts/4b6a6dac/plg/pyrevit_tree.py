"""Walk pyRevit extensions and print tab/panel/button with tooltip (ru if present, else en)."""
import os, re, sys

root = sys.argv[1]
KINDS = ('.pushbutton', '.pulldown', '.splitpushbutton', '.splitbutton', '.stack', '.smartbutton',
         '.urlbutton', '.panelbutton', '.linkbutton', '.invokebutton', '.content', '.toggle')


def tooltip(folder):
    y = os.path.join(folder, 'bundle.yaml')
    txt = ''
    if os.path.exists(y):
        s = open(y, encoding='utf-8', errors='replace').read()
        m = re.search(r'^tooltip:\s*\n((?:[ \t]+.*\n?)+)', s, re.M)
        if m:
            block = m.group(1)
            for lang in ('ru_ru', 'en_us'):
                mm = re.search(lang + r':\s*[>|]?-?\s*\n?((?:[ \t]{4,}.*\n?)+|.*)', block)
                if mm:
                    txt = mm.group(1)
                    break
            if not txt:
                txt = block
        else:
            m = re.search(r'^tooltip:\s*[>|]?-?\s*(.*(?:\n[ \t]+.*)*)', s, re.M)
            if m:
                txt = m.group(1)
    if not txt:
        sc = os.path.join(folder, 'script.py')
        if os.path.exists(sc):
            s = open(sc, encoding='utf-8', errors='replace').read()
            m = re.search(r'"""(.*?)"""', s, re.S)
            if m:
                txt = m.group(1)
    txt = ' '.join(txt.replace('"', '').split())
    return txt[:260]


def walk(folder, depth):
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        if not os.path.isdir(p):
            continue
        if name.endswith('.panel'):
            print('  ' * depth + '## ' + name[:-6])
            walk(p, depth + 1)
        elif name.endswith(KINDS):
            base, kind = os.path.splitext(name)
            if kind in ('.stack',):
                walk(p, depth)
                continue
            print('  ' * depth + '- ' + base + ' [' + kind[1:] + '] : ' + tooltip(p))
            if kind in ('.pulldown', '.splitpushbutton', '.splitbutton'):
                walk(p, depth + 1)


for ext in sorted(os.listdir(root)):
    for dp, dns, fns in os.walk(os.path.join(root, ext)):
        for d in dns:
            if d.endswith('.tab'):
                print('# ' + ext + ' / ' + d)
                walk(os.path.join(dp, d), 1)
        break
