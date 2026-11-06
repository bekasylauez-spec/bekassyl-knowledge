"""strip-grid outlines: old (ring+pads) and new (ring+pads+inner strips) relative to axis1/A"""
from shapely.geometry import box, Polygon, Point
from shapely.ops import unary_union
def old_u():
    ring=box(-325,-325,60325,12325).difference(box(175,175,59825,11825))
    pads=[box(6000*i-1000,6000*j-1000,6000*i+1000,6000*j+1000) for i in range(11) for j in range(3)]
    return unary_union([ring]+pads)
def new_u(hw=250):
    st=[box(0,6000-hw,60000,6000+hw)]+[box(6000*i-hw,0,6000*i+hw,12000) for i in range(1,10)]
    return unary_union([old_u()]+st)
def prep(u): return u.buffer(100,join_style='mitre')
def rings(u):
    out=[]
    for g in getattr(u,'geoms',[u]):
        out.append(list(g.exterior.coords)[:-1])
        for r in g.interiors: out.append(list(r.coords)[:-1])
    return out
def on(pts,g,tol=3):
    b=g.boundary
    return all(b.distance(Point(p))<tol for p in pts)
