# См-7 sheet 5.29 sections rebuilt (analog См-6 4.22: free end -> three small hoops (analog Х3, here Х2 as in the spec), cross wall -> Х1;Х2)
J = lambda f, c: ('J', f, c)
F = lambda f: ('F', f)
SEC = dict(X=2149800.0, A0=8000.0, V='wl/sm7_vert.json', H='wl/sm7_hor.json', FREE_HOOP=('x2', [100, 300, 500], 'Х2'),
           PLANS=[dict(WL=38000, gi=0, s=0, hpos={0: 12}, pieces=[(0, -125, 22875, J(125, 0), J(22625, 22750))]),
                  dict(WL=25496, gi=1, s=1, hpos={0: 13, 1: 14, 2: 15}, pieces=[(0, -125, 3175, J(125, 0), F(3175)), (1, 5750, 17100, F(5750), F(17100)), (2, 20375, 22875, F(20375), J(22625, 22750))])])
