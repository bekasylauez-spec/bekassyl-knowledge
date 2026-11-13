import re, collections, io, sys
D=r"C:\Users\Admin\AppData\Local\Temp\claude\a7137524bdaa49d0\c55bc92b-0511-4932-9c00-c1294111057c\scratchpad\q20\\"
out=io.open(D+'a2b_out.txt','w',encoding='utf-8')
def P(*a): out.write(' '.join(str(x) for x in a)+'\n')
L=[l.rstrip('\n') for l in io.open(D+'clash_all.txt',encoding='utf-8')]
P('clash rows',len(L))
def part(name):
    n=name
    for k in ('шов','заглушка','вставка','гусет','фасонка','болт','гайка','шайба','ребро','оголовок','диафрагма','кронштейн','фланец','накладка','прокладка','плита','траверса','подливка','анкер','лист','тартпа','рельс','уголок','швеллер','брус','косынка','рыбка','тіреуіш','подколонник','тірек','жота'):
        if ' - '+k in n or n.startswith(k) or ' '+k in n: return k
    return 'other'
cat=collections.Counter(); big=[]
for l in L:
    m=re.match(r'(.*?) \| (.*?) «(.*?)» \[(\d+)\] ↔ (.*?) «(.*?)» \[(\d+)\] ([\d.]+) мм3 \((.*)\)',l)
    if not m: P('NOPARSE',l[:100]); continue
    cn,a,na,ia,b,nb,ib,v,how=m.groups(); v=float(v)
    if how.startswith('bracket'):
        lo=float(re.match(r'bracket\[([\d.]+)\.\.([\d.]+)\]',how).group(1)); hi=float(re.match(r'bracket\[([\d.]+)\.\.([\d.]+)\]',how).group(2))
        if lo<=1: cat['bracket-contact(lo<=1)']+=1; continue
    pa,pb=part(na),part(nb)
    key=(how.split('[')[0], tuple(sorted([pa,pb])))
    cat[key]+=1
    big.append((v,how,cn,na,nb,ia,ib))
for k,v in sorted(cat.items(), key=lambda t:-t[1]): P(v,k)
big.sort(reverse=True)
P('--- top 25 by volume (excl. contact)')
for b in big[:25]: P(round(b[0],2),b[1],b[3],'<->',b[4],b[5],b[6])
P('non-weld pairs:')
for b in big:
    if 'шов' not in b[3] and 'шов' not in b[4]: P(round(b[0],2),b[1],b[3],'<->',b[4],b[5],b[6])
# zfight
Z=[l.rstrip('\n').split('\t') for l in io.open(D+'zfight.tsv',encoding='utf-8')]
P('zfight rows',len(Z))
zc=collections.Counter(); zex={}
for z in Z:
    cn,ak,al,an,aid,am,bk,bl,bn,bid,bm,nx,ny,nz,area,ex,ey,ez,ins=z
    pa,pb=part(an),part(bn)
    if cn=='каркас↔каркас': pa='каркас '+an.split()[0]; pb='каркас '+bn.split()[0]
    elif an.startswith('каркас') or ak=='каркас': pa='каркас '+an.split()[0]
    elif bk=='каркас': pb='каркас '+bn.split()[0]
    key=tuple(sorted([pa,pb]))
    zc[key]+=1
    zex.setdefault(key,[]).append((float(area),an,bn,aid,bid,nx,ny,nz))
for k,v in sorted(zc.items(), key=lambda t:-t[1])[:45]:
    ex=sorted(zex[k],reverse=True)[0]
    P(v,k,'| max area',ex[0],'|',ex[1],'<->',ex[2],ex[3],ex[4],'n=',ex[5],ex[6],ex[7])
out.close()