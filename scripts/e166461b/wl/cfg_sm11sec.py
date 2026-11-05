# См-11 sheet 5.49 sections (analog См-6 4.22 = См-7 5.29 clone): free end -> three Х2, end at a cross wall -> Х1;Х2
J = lambda f, c: ('J', f, c)
F = lambda f: ('F', f)
SEC = dict(X=3092100.0, A0=8000.0, V='wl/sm11_vert.json', H='wl/sm11_hor.json', FREE_HOOP=('x2', [100, 300, 500], 'Х2'),
           PLANS=[dict(WL=38000, gi=0, s=0, hpos={0: 21}, pieces=[(0, -125, 22875, J(125, 0), J(22625, 22750))]),
                  dict(WL=25496, gi=1, s=1, hpos={0: 22, 1: 23, 2: 24}, pieces=[(0, -125, 2775, J(125, 0), F(2775)), (1, 5750, 15675, F(5750), F(15675)), (2, 20375, 22875, F(20375), J(22625, 22750))])])
