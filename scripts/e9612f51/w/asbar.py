# ArmBars CSV (tbl*.31_1.csv) -> {el: {sec: (bot, top, asw)}} cm2 / cm2 per m
import sys, collections
def load(p):
    L=open(p,'rb').read().decode('utf-8','replace').splitlines()[1:]
    R=collections.defaultdict(lambda: collections.defaultdict(lambda:[0,0,0]))
    for l in L:
        f=l.split(';')
        if len(f)<21 or f[1].endswith('-S'): continue
        try:
            el=int(f[4]); s=int(f[5]); v=[float(x or 0) for x in f[10:21]]
        except ValueError: continue
        au1,au2,au3,au4,as1,as2,as3,as4,pc,w1,w2=v
        r=R[el][s]; r[0]=max(r[0],au1+au2+as1); r[1]=max(r[1],au3+au4+as2); r[2]=max(r[2],w1,w2)
    return R
if __name__=='__main__':
    R=load(sys.argv[1]); print(len(R)); print(list(R.items())[:3])
