p='net/p4.cs'; s=open(p,encoding='utf-8').read()
old='''                h.SetHatchPattern(HatchPatternType.PreDefined, S(m, "pat", "SOLID"));
                if (Has(m, "scale")) h.PatternScale = D(m["scale"]);
                if (Has(m, "ang")) h.PatternAngle = D(m["ang"]) * Math.PI / 180;'''
new='''                if (Has(m, "scale")) h.PatternScale = D(m["scale"]);
                if (Has(m, "ang")) h.PatternAngle = D(m["ang"]) * Math.PI / 180;
                h.SetHatchPattern(HatchPatternType.PreDefined, S(m, "pat", "SOLID"));'''
assert old in s; s=s.replace(old,new); open(p,'w',encoding='utf-8').write(s)
p='w/gen.py'; s=open(p,encoding='utf-8').read()
old="""                out.append(dict(f=z['f'], d=z['d'], pos=run, n=len(run), L0=a, L1=b, L=int(math.ceil((b - a) / 50.0) * 50)))"""
new="""                a2 = math.ceil(a / 10.0) * 10; Lr = int((b - a2) // 100 * 100)      # bar inside the slab, length to 100 mm
                out.append(dict(f=z['f'], d=z['d'], pos=run, n=len(run), L0=a2, L1=a2 + Lr, L=Lr))"""
assert old in s; s=s.replace(old,new)
old="""d = z['d']; L = int(math.ceil(z['L'] / 300.0) * 300); p = pos_of(sh.k, d, L)"""
assert old in s; s=s.replace(old,"""d = z['d']; L = z['L']; p = pos_of(sh.k, d, L)""")
old="""        add(t='mlx', h='BCEC4EDB', textloc=[e + 4 * 900, yt - 2600], arrows=[[e + 4 * 600, yb1]])
        add(t='mlx', h='BCEE9DC1', text='Площадка\\Pлестницы', textloc=[e + 4 * 900, yt + 2200], arrows=[[e + 4 * 1000, yt - 400]])"""
assert old in s
s=s.replace(old,"""        add(t='mlx', h='BCEC4EDB', textloc=[e + 4 * 1100, yt - 3800], arrows=[[e + 4 * 600, yb1]])
        add(t='mlx', h='BCEE9DC1', text='Площадка\\Pлестницы', textloc=[R + 1300, yt + 1500], arrows=[[R - 1200, yt - 400]])""")
open(p,'w',encoding='utf-8').write(s)
p='w/asm.py'; s=open(p,encoding='utf-8').read()
old="""    pairs = [['Блок 2', 'Блок 4'], [N70[i][0], N70[i][1]]]"""
assert old in s; s=s.replace(old,"""    pairs = [['Блок 2', 'Блок 4'], [N70[i][0], N70[i][1]], ['КЖ-2,5.', N70[i][1]]]""")
open(p,'w',encoding='utf-8').write(s)
print('ok')
