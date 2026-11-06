# beam definitions (scheme coordinates, mm along the beam line)
BEAMS = {
 'Рм-1': dict(levels=['-0.050'], b=500, h=900, END0=-250, END1=15900, slab=0,
              sup=[dict(a=-250, b=950, ax=0, axn='А', kind='col'), dict(a=8750, b=9950, ax=9000, axn='Б', kind='col'),
                   dict(a=13550, b=14250, ax=13900, axn='В', kind='col'), dict(a=14250, b=15900, kind='wall')],
              hoop=dict(d=14, s_end=100, s_mid=100, legs=4), main=dict(top=(4, 25), bot=(4, 25)),
              dop=[dict(pos=3, top=True, n=3, d=25, u0=-230, u1=3000), dict(pos=2, top=True, n=3, d=25, u0=6000, u1=15880),
                   dict(pos=4, top=False, n=3, d=25, u0=6750, u1=15880)], parts=[dict(i0=0, i1=3, brkL=False, brkR=False, no='6.1')],
              secs=[dict(word='1', at=[4300]), dict(word='2', at=[11700], top_dop=(2, 3), bot_dop=(4, 3)), dict(word='3', at=[1050], top_dop=(3, 3))],
              qty=4),
}
