import math
def loc(pts,i0,i1,flipx=False):
    # rotate so edge pts[i0]->pts[i1] is +x axis, origin = min
    (x0,y0),(x1,y1)=pts[i0],pts[i1]
    a=math.atan2(y1-y0,x1-x0)
    c,s=math.cos(-a),math.sin(-a)
    q=[((x-x0)*c-(y-y0)*s,(x-x0)*s+(y-y0)*c) for x,y in pts]
    mx=min(p[0] for p in q); my=min(p[1] for p in q)
    return math.degrees(a),[(round(p[0]-mx,1),round(p[1]-my,1)) for p in q]
print('n1 rib',loc([(891,2236),(1041,2239),(1040,2259),(906,2437),(886,2436)],0,1))
print('n2 rib',loc([(579,633),(579,653),(704,837),(724,837),(729,637)],4,0))
print('n4 rib',loc([(1027,2307),(1177,2311),(1176,2331),(1042,2508),(1022,2507)],0,1))
print('n1 brace gusset',loc([(3291,2118),(3379,2023),(3488,2123),(3488,2252),(3437,2252)],2,3))
print('n4 gusset',loc([(3038,2076),(3258,2076),(3270,2017),(3171,1918),(3038,2000)],0,1))
print('n4 bracket',loc([(1313,1834),(1313,1985),(1413,1987),(1413,1967),(1333,1834)],0,1))
