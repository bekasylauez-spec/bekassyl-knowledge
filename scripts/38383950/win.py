import pickle,sys,collections
L,T,lay=pickle.load(open('geo.pkl','rb'))
cx,cy,w,h=[float(v) for v in sys.argv[1:5]]
x0,x1,y0,y1=cx-w/2,cx+w/2,cy-h/2,cy+h/2
ins=lambda x,y:x0<=x<=x1 and y0<=y<=y1
ls=[l for l in L if ins(l[1],l[2]) and ins(l[3],l[4])]
ts=[t for t in T if ins(t[1],t[2])]
c=collections.Counter(l[0] for l in ls); print(c)
print(collections.Counter(t[0] for t in ts))
mode=sys.argv[5] if len(sys.argv)>5 else ''
if mode=='t':
  for t in sorted(ts,key=lambda t:(-t[2],t[1])): print('%s %.0f %.0f %r'%t)
if mode.startswith('l'):
  lay_=mode[2:]
  for l in sorted(ls,key=lambda l:(l[1],l[2])):
    if not lay_ or l[0]==lay_: print('%s %.1f %.1f %.1f %.1f'%l)
