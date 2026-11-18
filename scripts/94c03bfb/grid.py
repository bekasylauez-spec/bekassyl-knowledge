import fitz
def grid(p):
    cols={};rows={}
    W=p.get_text("words")
    H=p.rect.height
    for x0,y0,x1,y1,t,*_ in W:
        if t in list("123456789") and y0>H-260 and y0<H-200 and t not in cols:
            cols[t]=(x0+x1)/2
        if t in ("А","Б","В","Г","Д","Е","Ж") and x0<110:
            rows[t]=(y0+y1)/2
    return cols,rows
def loc(p,x,y,g=None):
    cols,rows=g or grid(p)
    cs=sorted(cols.items(),key=lambda kv:kv[1]);rs=sorted(rows.items(),key=lambda kv:kv[1])
    def pos(items,v,lab):
        if not items:return "?"
        if v<items[0][1]: return f"<{items[0][0]}"
        for (a,va),(b,vb) in zip(items,items[1:]):
            if abs(v-va)<8: return a
            if va<v<vb: return f"{a}-{b}"
        if abs(v-items[-1][1])<8: return items[-1][0]
        return f">{items[-1][0]}"
    return f"{pos(rs,y,'r')}/{pos(cs,x,'c')}"
if __name__=="__main__":
    for n in range(1,9):
        p=fitz.open(f"D:/_claude_work/Kasymova/revit/_check/v10/s2.{n}.pdf")[0]
        print(n,grid(p))
