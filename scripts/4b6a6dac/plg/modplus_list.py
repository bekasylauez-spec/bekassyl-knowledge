"""Print ModPlus Revit menu groups with Russian names/descriptions of each installed function."""
import os, re, sys
import xml.etree.ElementTree as ET

mp = sys.argv[1]
menu = ET.parse(os.path.join(mp, 'Revit standard menu.xml')).getroot()
lang = open(os.path.join(mp, 'Languages', 'ru-RU.xml'), encoding='utf-8-sig').read()
installed = set(os.listdir(os.path.join(mp, 'Functions', 'Revit')))


def info(name):
    m = re.search(r'<' + name + r'\s+LocalName="([^"]*)"\s+Description="([^"]*)"(?:\s+FullDescription="([^"]*)")?', lang)
    if not m:
        return name, '', ''
    return m.group(1), m.group(2), (m.group(3) or '')


for g in menu.iter('Group'):
    print('## ' + g.get('GroupName'))
    for f in g.iter():
        if f.tag not in ('Function', 'SubFunction'):
            continue
        n = f.get('Name')
        if n not in installed:
            continue
        ln, d, fd = info(n)
        print('- **{}** ({}) — {}{}'.format(ln, n, d, (' | ' + fd[:300]) if fd and f.tag != 'SubFunction' and 'Reinforcement' in n or 'Rebar' in n else ''))
    print()
