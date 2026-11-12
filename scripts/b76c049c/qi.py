import pickle,sys
sys.stdout.reconfigure(encoding='utf-8')
D=pickle.load(open(sys.argv[1],'rb'))
i=int(sys.argv[2]);X0=-41822+59400*i;Y0=-1593693
for e in D:
    if e['t']!='INSERT': continue
    x,y=e['ex']['ins']
    if X0<=x<=X0+59400 and Y0<=y<=Y0+42000:
        print(e['h'],e['txt'],e['l'],'%.0f,%.0f'%(x-X0,y-Y0),e['bb'] and '%.0f,%.0f,%.0f,%.0f'%(e['bb'][0]-X0,e['bb'][1]-Y0,e['bb'][2]-X0,e['bb'][3]-Y0),e['ex']['att'])
