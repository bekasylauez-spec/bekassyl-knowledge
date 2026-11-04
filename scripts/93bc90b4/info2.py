import ezdxf, sys, collections
names=collections.defaultdict(list)
for n in sys.argv[2:]:
    d=ezdxf.readfile(f'{sys.argv[1]}/{n}.dxf')
    print('==',n,[ (l.dxf.name,l.dxf.color,l.dxf.linetype) for l in d.layers], [s.dxf.name for s in d.styles], [s.dxf.name for s in d.linetypes])
    for b in d.blocks:
        names[b.name].append(n)
    for l in d.layouts:
        if l.name=='Model':continue
        dl=l.dxf_layout.dxf
        print('  ',l.name, dl.plot_configuration_file if dl.hasattr('plot_configuration_file') else '', dl.get('paper_size'), dl.get('paper_width'), dl.get('paper_height'), dl.get('plot_rotation'), dl.get('plot_layout_flags'))
        for v in l.query('VIEWPORT'):
            x=v.dxf
            print('     vp', x.get('id'), 'c',tuple(round(t,1) for t in x.center)[:2],'wh',round(x.width,1),round(x.height,1),'vc',tuple(round(t,1) for t in x.view_center_point),'tgt',tuple(round(t,1) for t in x.view_target_point),'dir',tuple(x.view_direction_vector),'vh',round(x.view_height,1),'tw',x.get('view_twist_angle'),'st',x.get('status'))
dup={k:v for k,v in names.items() if len(v)>1 and not k.startswith('*')}
print('dup blocks',len(dup), list(dup.items())[:20])
