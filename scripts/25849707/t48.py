import mk
F = dict(mark='Рм-48', level='+7.000', h=600, b=250, u0=11750, u1=30250, endL='end', endR='end',
         sup=[(11750, 12250, 'beam', '3', 12000), (17750, 18250, 'beam', '4', 18000), (23750, 24250, 'beam', '5', 24000), (29750, 30250, 'beam', '6', 30000)],
         top=dict(n=3, d=20, pos='1'), bot=dict(n=3, d=20, pos='1'), sk=dict(d=16, pos='Ск1'), hoop=dict(d=8, pos='Х1'),
         dop=[], spl=dict(top=[(21000, 18000)], bot=[(19350, 18000)]), secs=[('1', 15000), ('1', 25200), ('1', 27000)],
         nspec={20: 12})
print(mk.fresh(0, 'R48:')[-200:])
NH, P, err = mk.make(0, 'R48:', F, '6.48', 1.65, 9, [('1', (-221000, 417700), 0, 0, None)])
print(NH, P, err[:20])
