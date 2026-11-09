import sys,glob,os
import fitz
out=sys.argv[2]
os.makedirs(out,exist_ok=True)
for f in sorted(glob.glob(sys.argv[1])):
    n=os.path.basename(f)
    if not (n.startswith('КДС') or n.startswith('СЭЗ')): continue
    d=fitz.open(f)
    t=[]
    for i,p in enumerate(d):
        t.append(f"\n=== PAGE {i+1} ({p.rect.width:.0f}x{p.rect.height:.0f}) ===\n"+p.get_text())
    open(os.path.join(out,n+'.txt'),'w',encoding='utf-8').write(''.join(t))
    print(n, len(d), sum(len(x) for x in t))
