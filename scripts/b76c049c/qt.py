import pickle,sys
sys.stdout.reconfigure(encoding='utf-8')
D=pickle.load(open(sys.argv[1],'rb'))
i=int(sys.argv[2]);X0=-41822+59400*i;Y0=-1593693
w=[float(v) for v in sys.argv[3:7]];w=[X0+w[0],Y0+w[1],X0+w[2],Y0+w[3]]
nb=0
for e in D:
    b=e['bb']
    if not b: nb+=1; continue
    if b[2]>=w[0] and b[0]<=w[2] and b[3]>=w[1] and b[1]<=w[3]:
        if (b[2]-b[0])>40000: continue
        print('%s\t%s\t%s\t%.0f,%.0f,%.0f,%.0f\t%s\t%s'%(e['h'],e['t'],e['l'],b[0]-X0,b[1]-Y0,b[2]-X0,b[3]-Y0,(e['txt'] or '')[:60],e['ex'] if e['t'] in ('TEXT','MTEXT','DIMENSION','CIRCLE') else ''))
print('nobbox total',nb)
