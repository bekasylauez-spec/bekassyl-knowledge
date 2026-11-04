# verify rig_fx: per sheet levels, axes, long dims, zone texts; tables for #### and key values
import re, sys, subprocess, pickle
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\Admin\AppData\Local\Temp\claude\D---------\760c999f-c28c-44e9-ba81-9cb2aa467e81\scratchpad\w\rg\\'
subprocess.run([sys.executable, '-I', D + 'frames.py', D + 'rig_fx', r'6\.\d+'], capture_output=True)
subprocess.run([sys.executable, '-I', D + 'dump.py', D + 'rig_fx', r'6\.\d+'], capture_output=True)
dump = open(D + 'rig_fx_dump.txt', encoding='utf-8').read()
for s in re.split(r'\n==== SHEET ', dump)[1:]:
    hdr, body = s.split('\n', 1); sn = hdr.split()[0]
    levels = re.findall(r'^X \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([+-]\d+[.,]\d{3})\s*$', body, re.M)
    axes = re.findall(r'^X \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) ([1-9АБВ])\s*$', body, re.M)
    dims = re.findall(r'^D \w+ \((-?\d+),(-?\d+)\)-\((-?\d+),(-?\d+)\) (\d+) txt=\'(.*)\'$', body, re.M)
    big = sorted({int(d[4]) for d in dims if int(d[4]) >= 2500 and d[5] == ''})
    zones = [(int(d[4]), d[5]) for d in dims if re.match(r'(100|200)х', d[5])]
    print(sn, 'lv', [l[4] for l in levels], 'ax', ''.join(a[4] for a in sorted(axes, key=lambda a: int(a[0]))), 'big', big, 'zones', zones)
tabs = open(D + 'rig_fx.tables.txt', encoding='utf-8').read()
print('#### count:', tabs.count('####'))
for ln in tabs.splitlines():
    if re.search(r'Ригель Рм-(3|4|6|7|8|9|11|13|15|17) ', ln) or re.search(r'\| (Х1\*|1|2|Шп1\*) \|', ln) and ('пог' in ln or 'Х1' in ln or 'Шп1' in ln):
        print(re.sub(r'ГОСТ 34028-2016\(214-210-0[0-9-]*\)', 'Г', ln)[:200])
