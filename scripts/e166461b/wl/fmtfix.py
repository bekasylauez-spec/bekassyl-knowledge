import sys,os,re; sys.path.insert(0,'wl'); from common import *
def nrows(h):
    gx.run([{'t':'tdump','h':h}],'td'); t=open(os.environ['TEMP']+'/gx_log.txt',encoding='utf-8').read().splitlines()
    return int(re.search(r'rows (\d+) cols (\d+)',t[0]).group(1)), int(re.search(r'cols (\d+)',t[0]).group(1))
ops=[]
for sp,st in (('184D0E','1850B3'),('163EEB','164172'),('17E05E','17E1ED')):
    r,c=nrows(sp); ops.append(dict(t='tfmtset',h=sp,cells=[[i,j] for i in range(1,r-2) for j in (11,12)]))
    r2,c2=nrows(st); ops.append(dict(t='tfmtset',h=st,cells=[[6,j] for j in range(1,c2)]))
ops.append(dict(t='save'))
print(gx.run(ops,'fx2')[-200:])
