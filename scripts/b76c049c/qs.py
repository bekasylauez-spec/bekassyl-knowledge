import pickle,sys
sys.stdout.reconfigure(encoding='utf-8')
D=pickle.load(open(sys.argv[1],'rb'))
for e in D:
    t=e['txt'] or ''
    if any(k in t for k in sys.argv[2:]):
        i=None
        b=e['bb']
        if b: i=int((b[0]+41822)//59400)
        print(e['h'],e['t'],e['l'],i,b and '%.0f,%.0f'%(b[0]-(-41822+59400*i),b[1]+1593693),t[:80],e['ex'].get('h'),e['ex'].get('style'))
