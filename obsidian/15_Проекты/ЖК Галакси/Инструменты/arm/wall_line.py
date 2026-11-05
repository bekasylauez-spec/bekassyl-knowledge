import json,sys,collections
C=json.load(open('arm/wall_cells.json'))
ax,val=sys.argv[1],int(sys.argv[2])
LEV=[-4.65,-0.1,3.95,7.1,10.25,13.4,16.55,19.7,23.2]
sel=[c for c in C if c['pl']==[ax,val] or tuple(c['pl'])==(ax,val)]
# along-wall coordinate
key='x0' if ax=='y' else 'y0'; key1='x1' if ax=='y' else 'y1'
xs=sorted(set(round(c[key]) for c in sel)); 
print('cells',len(sel),'along',xs[0],'..',max(round(c[key1]) for c in sel))
for s in range(len(LEV)-1):
    st=[c for c in sel if LEV[s]-1e-3<=c['z0']<LEV[s+1]-1e-3]
    if not st: continue
    byx=collections.defaultdict(lambda:[0,0])
    for c in st:
        k=(round(c[key]),round(c[key1]))
        byx[k][0]=max(byx[k][0],c['As'][2],c['As'][3]); byx[k][1]=max(byx[k][1],c['As'][0],c['As'][1])
    row=' '.join('%d-%d:%.1f/%.1f'%(a,b,v[0],v[1]) for (a,b),v in sorted(byx.items()))
    print('storey %.2f'%LEV[s], row)
