import ezdxf,sys
sys.stdout.reconfigure(encoding='utf-8')
doc=ezdxf.readfile(r'D:\_claude_work\otst\src\analog.dxf')
for s in doc.dimstyles:
    if 'СПДС' in s.dxf.name or 'SPDS' in s.dxf.name:
        print(s.dxf.name,'txt',s.dxf.get('dimtxt'),'scale',s.dxf.get('dimscale'),'lfac',s.dxf.get('dimlfac'),'asz',s.dxf.get('dimasz'),'exe',s.dxf.get('dimexe'),'exo',s.dxf.get('dimexo'),'gap',s.dxf.get('dimgap'),'blk',s.dxf.get('dimblk'))
for h in ['2C3851','2C3879','28F3C4','2BE0E5','2C73EE']:
    e=doc.entitydb[h]; ov=e.dim_style_attributes() if hasattr(e,'dim_style_attributes') else None
    try:
        a=e.override(); print(h,e.dxf.dimstyle,{k:a.get(k) for k in ('dimscale','dimlfac','dimtxt')})
    except Exception as er: print(h,er)
