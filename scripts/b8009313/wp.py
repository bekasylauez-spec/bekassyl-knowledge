import sys,ezdxf
d=ezdxf.readfile(sys.argv[1]); m=d.modelspace()
ox,oy=float(sys.argv[3]),float(sys.argv[4])
e=d.entitydb[sys.argv[2]]
print(sys.argv[2],[(round(p[0]-ox,1),round(p[1]-oy,1)) for p in e.get_points()])
