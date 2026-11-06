import plt
D=r'C:\Users\Admin\AppData\Local\Temp\claude\210ab68cad67e8c1\25849707-e40f-4af8-947c-f7481c780970\scratchpad\an\sch.dwg'
for i,x in enumerate([133817.33,217917.33,302017.33,386117.33]):
    print(plt.plot(D,'sch%d'%i,x,-1788184.13,x+84100,-1728784.13,paper='ISO без полей A1 (841.00 x 594.00 мм)',orient='_L'))
